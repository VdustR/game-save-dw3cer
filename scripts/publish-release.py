"""Publish only the approved, hashed save bundles; never upload local backups."""
import argparse
import base64
import hashlib
import json
import os
from pathlib import Path
import re
import subprocess
import tempfile
import zipfile

ROOT = Path(__file__).resolve().parents[1]
NAMES = {
    'DW3CER_0_Percent_Original.zip',
    'DW3CER_100_Percent_Perfect.zip',
    'DW3CER_101_Percent_Overlimit.zip',
}


def gh(*args):
    return subprocess.check_output(['gh', *args])


def api(path):
    return json.loads(gh('api', path))


def verify_bundle(path, spec):
    data = path.read_bytes()
    if len(data) != spec['size'] or hashlib.sha256(data).hexdigest() != spec['sha256']:
        raise ValueError(f"ZIP integrity failed: {path.name}")
    with zipfile.ZipFile(path) as archive:
        if set(archive.namelist()) != {'GameStatusData.sav', 'README.txt', 'SHA256SUMS.txt'} or len(archive.infolist()) != 3:
            raise ValueError('Unexpected bundle contents.')
        if any(item.file_size > 8 * 1024 * 1024 for item in archive.infolist()):
            raise ValueError('Unexpected bundle payload size.')
        save = archive.read('GameStatusData.sav')
        if hashlib.sha256(save).hexdigest() != spec['save_sha256']:
            raise ValueError('The bundled save differs from the accepted file.')
        if archive.read('SHA256SUMS.txt').decode('ascii').strip() != spec['save_sha256'] + '  GameStatusData.sav':
            raise ValueError('The bundled checksum is incorrect.')


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('--tag', default=os.environ.get('RELEASE_TAG'))
    parser.add_argument('--verify-directory', type=Path)
    args = parser.parse_args()
    if not args.tag or not re.fullmatch(r'steam-build-\d+', args.tag):
        raise ValueError('Use an approved Steam-build tag.')
    manifest = json.loads((ROOT / 'releases' / (args.tag + '.json')).read_text(encoding='utf8'))
    if manifest['tag'] != args.tag or {row['name'] for row in manifest['assets']} != NAMES or len(manifest['assets']) != 3:
        raise ValueError('Unexpected release manifest.')
    if args.verify_directory:
        for spec in manifest['assets']:
            verify_bundle(args.verify_directory / spec['name'], spec)
        print('All three release bundles match their ZIP and save checksums.')
        return
    repo = os.environ['GH_REPO']
    if repo != 'VdustR/game-save-dw3cer':
        raise ValueError('Unexpected publishing repository.')
    # Drafts do not have a published tag endpoint yet. Resolve their release ID.
    release = next((row for row in api(f'repos/{repo}/releases?per_page=100')
                    if row['tag_name'] == args.tag), None)
    if release is not None and not release['draft']:
        raise ValueError('This release is already public; refusing to replace it.')
    with tempfile.TemporaryDirectory(prefix='dw3cer-release-') as directory:
        folder = Path(directory)
        paths = []
        for spec in manifest['assets']:
            entry = api(f"repos/{repo}/contents/{spec['name']}?ref={manifest['assets_commit']}")
            if entry['sha'] != spec['blob_sha'] or entry['encoding'] != 'base64':
                raise ValueError('Unexpected staged Git blob.')
            path = folder / spec['name']
            path.write_bytes(base64.b64decode(entry['content']))
            verify_bundle(path, spec)
            paths.append(str(path))
        if release is None:
            gh('release', 'create', args.tag, '--repo', repo, '--target', os.environ['GITHUB_SHA'],
               '--title', manifest['title'], '--notes-file', str(ROOT / 'releases' / (args.tag + '.md')), '--draft')
            release = next(row for row in api(f'repos/{repo}/releases?per_page=100')
                           if row['tag_name'] == args.tag)
        gh('release', 'edit', args.tag, '--repo', repo, '--target', os.environ['GITHUB_SHA'],
           '--title', manifest['title'], '--notes-file', str(ROOT / 'releases' / (args.tag + '.md')), '--draft')
        gh('release', 'upload', args.tag, *paths, '--repo', repo, '--clobber')
        uploaded = api(f"repos/{repo}/releases/{release['id']}")
        if {item['name'] for item in uploaded['assets']} != NAMES or len(uploaded['assets']) != 3:
            raise ValueError('The draft does not contain exactly the three approved assets.')
        for spec in manifest['assets']:
            item = next(item for item in uploaded['assets'] if item['name'] == spec['name'])
            if item['size'] != spec['size'] or item['state'] != 'uploaded':
                raise ValueError('Incomplete release upload.')
            downloaded = gh('api', f"repos/{repo}/releases/assets/{item['id']}", '-H', 'Accept: application/octet-stream')
            path = folder / ('downloaded-' + spec['name'])
            path.write_bytes(downloaded)
            verify_bundle(path, spec)
        gh('release', 'edit', args.tag, '--repo', repo, '--draft=false', '--latest')
        print(f'https://github.com/{repo}/releases/tag/{args.tag}')


if __name__ == '__main__':
    main()
