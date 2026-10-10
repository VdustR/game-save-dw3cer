"""Private-fixture regressions for this project's fresh-save compatibility."""
import os
import struct
import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE / 'public' / 'engine'))
from models import SaveError, fields
from preset_engine import validate, initialize_music_defaults, apply_updates
import collection_editor as collection

raw = Path(os.environ['DW3_PRIVATE_FIXTURE']).read_bytes()
source = validate(raw)
assert not any(source.properties['EngiClearCharaArray']['value']['values'])
assert not any(source.properties['ClearScenarioArray']['value']['values'])
locked = next(i for i, row in enumerate(source.records('PCSaveDataArray')[:42])
              if fields(row)['WeaponDataID']['value'] == -1)
assert not source.properties['CanUseCharaArray']['value']['values'][locked]

def must_reject(data):
    try:
        validate(data)
    except SaveError:
        return
    raise AssertionError('Invalid equipment reference was accepted.')

field = fields(source.records('PCSaveDataArray')[locked])['WeaponDataID']
must_reject(apply_updates(source, leaf_updates=[(field, struct.pack('<i', -2))]).encrypted)
unlock = source.properties['CanUseCharaArray']
values = list(unlock['value']['values'])
values[locked] = 1
must_reject(apply_updates(source, leaf_updates=[
    (unlock, struct.pack('<i', len(values)) + bytes(values))]).encrypted)

before = {prop['name']: prop['value'] for prop in source.properties['OptionData']['value']}
assert 'Sound' not in before
initialized = initialize_music_defaults(source)
after = {prop['name']: prop['value'] for prop in initialized.properties['OptionData']['value']}
assert set(after) == set(before) | {'Sound'}
def values_only(value):
    if isinstance(value, list) and value and isinstance(value[0], dict):
        return {prop['name']: values_only(prop['value']) for prop in value}
    if isinstance(value, dict) and 'values' in value:
        return value['values']
    return value
assert {k: values_only(v) for k, v in before.items()} == {
    k: values_only(after[k]) for k in before}
assert not any(collection._array(initialized, collection.DATA['music'])[3])
assert initialize_music_defaults(initialized) is initialized
assert source.encrypted == raw
print('Fresh-save defaults, existing-option preservation, and invalid-reference rejection passed.')
