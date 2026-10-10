"""Tests only the project's preset composition and transformations."""
import sys,json,hashlib,os
from pathlib import Path
HERE=Path(__file__).resolve().parent
sys.path.insert(0,str(HERE/'public'/'engine'))
from preset_engine import preset
source=Path(os.environ['DW3_PRIVATE_FIXTURE']).read_bytes()
result={};cases={}
for name,mode,mixed in [('legal','legal',False),('overlimit','overlimit',False),('mixed','overlimit',True)]:
 output,report=preset(source,mode,mixed);cases[name]=output
 repeated,_=preset(output,mode,mixed)
 assert repeated==output,f'{name}: repeated patch differs'
 result[name]={'sha256':hashlib.sha256(output).hexdigest(),'idempotent':True}
 print(name,'idempotence passed',flush=True)
for origin in cases:
 for target,mode,mixed in [('legal','legal',False),('overlimit','overlimit',False),('mixed','overlimit',True)]:
  if origin==target:continue
  switched,_=preset(cases[origin],mode,mixed)
  assert switched==cases[target],f'{origin} -> {target}: differs from direct patch'
  print(origin,'->',target,'canonical output passed',flush=True)
  result[origin+'->'+target]=True
private=HERE/'.acceptance-private';private.mkdir(exist_ok=True)
for name,data in cases.items():(private/(name+'.sav')).write_bytes(data)
(HERE/'ACCEPTANCE_NATIVE.json').write_text(json.dumps({'upstream_retested':False,'results':result},indent=2),encoding='utf8')
print('All native composition acceptance tests passed',flush=True)
