"""Browser-local AES bridge; envelope rules match the native editor codec."""
import struct
from js import dwAES
SAVE_KEY=bytes.fromhex('757347635a517044474b474b676d53766b3553637a637973314e6b774d503267')
def _validate(data):
 if not data or len(data)%16 or len(data)>16*1024*1024:raise ValueError('Empty, truncated or oversized save.')
def _envelope(plain):
 size=struct.unpack_from('>I',plain)[0]
 if not len(plain)-19<=size<=len(plain)-4 or plain[4:8]!=b'GVAS' or any(plain[4+size:]):raise ValueError('Invalid save envelope, signature or padding.')
def decrypt(raw):
 _validate(raw);plain=bytes.fromhex(str(dwAES(raw.hex(),SAVE_KEY.hex(),'decrypt')));_envelope(plain);return plain
def encrypt(plain):
 _validate(plain);_envelope(plain);return bytes.fromhex(str(dwAES(plain.hex(),SAVE_KEY.hex(),'encrypt')))
