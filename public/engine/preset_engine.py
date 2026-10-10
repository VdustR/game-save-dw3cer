"""Explicit legal/experimental presets, reusable on native Python and Pyodide."""
import hashlib,struct
from models import fields,Change,SaveError
from save_parser import parse_bytes
from save_writer import serialize,CAPS,ITEMS,ITEM_CAPS,UNIQUE_WEAPONS
import save_codec,officer_weapon_editor as ow,bodyguard_editor as bg,bodyguard_growth as growth
import progression_editor as progression,weapon_collection as wc,collection_editor as collection,bodyguard_customization as custom

PRIORITY=[0,4,5,3,11,12,26,7,10]
OVER={0:255,4:99,5:99,3:150,11:255,12:255,26:255,7:99,10:99}
TESTED_ENVIRONMENT={'platform':'Windows Steam','app_id':3841510,'steam_build_id':25630985,'executable_version':'1.0.2.0','executable_sha256':'ca1a65a53242a7cf42493bd2006b8c555d87597387468e4b7a07c52d4eefe92e','save_engine':'5.6.1','serialization_versions':{'GVAS':3,'UE4':522,'UE5':1017},'acceptance_date':'2026-10-10','scope':'Reference test environment; the Steam build cannot be inferred from an uploaded save header.'}

def validate(raw):
 d=parse_bytes(raw)
 if len(d.records('PCSaveDataArray'))<42:raise SaveError('Missing playable officer records.')
 if len(d.records('EquipItemDataArray'))<43 or len(d.records('GuardEquipItemDataArray'))<10:raise SaveError('Missing item inventory records.')
 if len(d.records('CollectedWeaponDataArray'))<193:raise SaveError('Missing weapon gallery records.')
 if serialize(d,[])[0]!=raw:raise SaveError('No-edit roundtrip failed.')
 for name in ['WeaponDataArray','UniqueWeaponDataArray','GuardWeaponDataArray']:
  for i,r in enumerate(d.records(name)):
   f=fields(r)
   if len(f['Skill']['value']['records'])!=9:raise SaveError('Unsupported skill layout.')
   if f['WeaponID']['value']=='EWeaponID::NUM':continue
   if f['ID']['value']!=f['WeaponID']['value'] or f['DataID']['value']!=i+(10000 if name=='UniqueWeaponDataArray' else 0):raise SaveError('Invalid weapon identity/reference.')
   if name=='GuardWeaponDataArray' and f['WeaponID']['value'] not in bg.WEAPON_IDS:raise SaveError('Unknown guard weapon.')
   if name!='GuardWeaponDataArray' and f['WeaponID']['value'] not in ow.WEAPON_IDS:raise SaveError('Unknown officer weapon.')
 fifth={u['officer_id']:u for u in UNIQUE_WEAPONS.values() if u['tier']==5}
 if set(fifth)!=set(range(42)):raise SaveError('Incomplete five-star mapping.')
 for i,r in enumerate(d.records('PCSaveDataArray')[:42]):
  ref=fields(r)['WeaponDataID']['value'];name='UniqueWeaponDataArray' if ref>=10000 else 'WeaponDataArray';idx=ref-10000 if ref>=10000 else ref
  if ref==-1 and not d.properties['CanUseCharaArray']['value']['values'][i]:continue
  if not 0<=idx<len(d.records(name)) or fields(d.records(name)[idx])['WeaponID']['value']=='EWeaponID::NUM':raise SaveError(f'Officer {i} has invalid equipment reference.')
 return d

def apply_updates(d,record_updates=(),leaf_updates=()):
 patches=[];deltas={}
 for name,index,updates in record_updates:
  a=d.properties[name];r=d.records(name)[index];before=wc._record_bytes(d,r,a);after=wc._render_record(d,r,a,updates)
  if before!=after:patches.append((r[0]['tag_offset'],len(before),after));deltas[a['size_offset']]=deltas.get(a['size_offset'],0)+len(after)-len(before)
 for p,after in leaf_updates:
  if len(after)!=p['data_size']:raise SaveError('Leaf resizing requires record rendering.')
  before=d.plaintext[p['data_offset']:p['data_offset']+p['data_size']]
  if before!=after:patches.append((p['data_offset'],len(before),after))
 for off,delta in deltas.items():
  if delta:patches.append((off,4,struct.pack('<i',struct.unpack_from('<i',d.plaintext,off)[0]+delta)))
 size=struct.unpack_from('>I',d.plaintext)[0];plain=bytearray(d.plaintext[:size+4])
 for off,length,after in sorted(patches,reverse=True):plain[off:off+length]=after
 struct.pack_into('>I',plain,0,len(plain)-4);plain.extend(bytes((-len(plain))%16))
 raw=save_codec.encrypt(bytes(plain));out=parse_bytes(raw)
 if out.plaintext!=bytes(plain):raise SaveError('Output reparse differs.')
 return out

def initialize_music_defaults(d):
 """Create only the native omitted Sound struct; retain every other option."""
 spec=collection.DATA['music'];owner=d.properties.get('OptionData')
 if owner is None or owner['type']!=spec['struct_types'][0] or owner['flags']!=0 or owner['array_index']!=0 or not isinstance(owner['value'],list):raise SaveError('Unsupported option layout.')
 if any(p['name']=='Sound' for p in owner['value']):return d
 # Default-valued structs are omitted by UE serialization in a fresh save.
 payload=collection._make_tag(d,None,[],spec,[False]*spec['total'])+wc._string('None')
 def typename(name,children=()):return wc._string(name)+struct.pack('<i',len(children))+b''.join(children)
 tag=wc._string('Sound')+typename('StructProperty',[typename('OptionSound',[typename('/Script/Refine')])])+struct.pack('<iB',len(payload),0)+payload
 offset=collection._insert_at(owner,owner['value'],d)
 size=struct.unpack_from('>I',d.plaintext)[0];plain=bytearray(d.plaintext[:size+4])
 plain[offset:offset]=tag
 struct.pack_into('<i',plain,owner['size_offset'],owner['data_size']+len(tag))
 struct.pack_into('>I',plain,0,len(plain)-4);plain.extend(bytes((-len(plain))%16))
 result=parse_bytes(save_codec.encrypt(bytes(plain)))
 collection._array(result,spec)
 return result

def preset(raw,mode='legal',mixed_elements=False):
 if mode not in ['legal','overlimit']:raise SaveError('Unknown preset.')
 if type(mixed_elements) is not bool:raise SaveError('Element option must be boolean.')
 if mode=='legal' and mixed_elements:raise SaveError('Four-element mixing requires Overlimit mode.')
 original=initialize_music_defaults(validate(raw));changes=[]
 for i in range(42):
  changes.extend(Change('officer',i,k,v) for k,v in CAPS.items() if k!='MaxMusou')
 changes.extend(Change('unique_weapon',wid,'Owned',True) for wid in UNIQUE_WEAPONS)
 for i,item in ITEMS.items():
  changes.append(Change('item',i,'Owned',True))
  if item['kind']=='normal':changes.append(Change('item',i,'Value',ITEM_CAPS[i]))
 for i,item in bg.GUARD_ITEMS.items():
  changes.append(Change('guard_item',i,'Owned',True))
  if item['kind']=='normal':changes.append(Change('guard_item',i,'Value',item['max_value']))
 changes.extend(Change('guard_weapon',i,'Owned',True) for i in bg.GUARD_WEAPONS)
 for i in range(len(original.records('GuardDataArray'))):changes.extend([Change('bodyguard',i,'SPoint',99999),Change('bodyguard',i,'BGLevels',growth.safe_preset())])
 changes.extend(wc.all_collection_changes()+wc.tactics_costume_changes()+collection.unlock_music_changes(original)+collection.unlock_movie_changes(original))
 changes.extend(progression.side_story_changes()+progression.musou_clear_changes(original))
 changes.append(progression.elixir_count_change(999))
 for field,count in [('CanUseCharaArray',42),('CanUseScenarioArray',108)]:
  if len(original.properties[field]['value']['values'])<count:raise SaveError('Incomplete unlock layout.')
  changes.extend(Change('unlock',i,field,True) for i in range(count))
 for field,spec in custom.FAMILIES.items():changes.extend(Change('guard_customization',i,field,True) for i in range(spec['base_count'],spec['base_count']+spec['count']))
 base=parse_bytes(serialize(original,changes)[0]);updates=[];leaves=[];weapon_count=0;guard_count=0
 for name in ['WeaponDataArray','UniqueWeaponDataArray','CollectedWeaponDataArray']:
  for i,r in enumerate(base.records(name)):
   f=fields(r);enum=f['WeaponID']['value']
   if enum=='EWeaponID::NUM':continue
   wid=ow.WEAPON_IDS[enum];rule=ow.RULES['weapon_rules'].get(str(wid))
   if not rule:
    if name=='CollectedWeaponDataArray' and enum in bg.WEAPON_IDS:continue
    raise SaveError('Unsupported officer weapon rank.')
   rares={};slots=f['Skill']['value']['records']
   for j,s in enumerate(slots):
    sf=fields(s);item=ow.ITEM_IDS.get(sf['EquipItemID']['value'])
    if sf['GuardEquipItemID']['value']!='EGuardEquipItemID::NUM':raise SaveError('Foreign weapon bonus type.')
    if sf['EquipItemID']['value']!='EEquipItemID::NUM' and item is None:raise SaveError('Unknown bonus identity.')
    if item is not None and ITEMS[item]['kind']=='rare':
     if item not in ow.RARE_ITEMS or sf['Value']['value']!=0:raise SaveError('Unsupported rare bonus.')
     rares[j]={'id':item,'value':0}
   if len(rares)>1:raise SaveError('Multiple rare bonuses unsupported.')
   count=min(rule['max_blue'],9-len(rares)) if mode=='legal' else 9-len(rares)
   chosen=iter(PRIORITY[:count]);newskills=[];ups=[]
   for j,s in enumerate(slots):
    sf=fields(s)
    if j in rares:skill=rares[j]
    else:
     item=next(chosen,None)
     cap=0 if item is None else ow.NORMAL_ITEMS[item]['max']
     if item is not None and wid in UNIQUE_WEAPONS:
      cap=max([cap]+[x['value'] for x in UNIQUE_WEAPONS[wid]['skill_slots'] if x['item_id']==item])
     skill={'id':item,'value':0 if item is None else (cap if mode=='legal' else OVER[item])}
    newskills.append(skill);enum2='EEquipItemID::NUM' if skill['id'] is None else 'EEquipItemID::'+ITEMS[skill['id']]['enum']
    ups.extend([(sf['EquipItemID'],wc._string(enum2)),(sf['Value'],struct.pack('<i',skill['value']))])
   if mode=='legal':
    info={'owned':True,'blue_limit':rule['max_blue'],'blue_minimum':0,'red_minimum':len(rares),'skills':newskills,'array':'UniqueWeaponDataArray' if wid in UNIQUE_WEAPONS else 'WeaponDataArray','weapon_id':wid}
    ow.validate_skills(info,newskills)
   stock=UNIQUE_WEAPONS.get(wid,{}).get('attribute_bitmask',0)&ow.ELEMENT_MASK
   selected=ow.ELEMENT_MASK if mixed_elements else (stock if stock in [4,8,16,32] else 8)
   ups.append((f['Attr'],struct.pack('<q',(f['Attr']['value']&~ow.ELEMENT_MASK)|selected)))
   updates.append((name,i,ups))
   if name!='CollectedWeaponDataArray':weapon_count+=1
 for name in ['GuardWeaponDataArray','CollectedWeaponDataArray']:
  for i,r in enumerate(base.records(name)):
   f=fields(r);enum=f['WeaponID']['value']
   if enum=='EWeaponID::NUM' or (name=='CollectedWeaponDataArray' and enum not in bg.WEAPON_IDS):continue
   wid=bg.WEAPON_IDS[enum];meta=bg.GUARD_WEAPONS[wid]
   skills=meta['max_bonus_profile'] if mode=='legal' else [{'id':k,'value':255} for k in ([0,2,3] if meta['family_index']<3 else [0,4,3])]
   if mode=='legal':bg.validate_skills(wid,skills)
   ups=[(f['Attr'],struct.pack('<q',0))]
   for j,s in enumerate(f['Skill']['value']['records']):
    sf=fields(s);skill=skills[j] if j<len(skills) else {'id':None,'value':0}
    ups.extend([(sf['EquipItemID'],wc._string('EEquipItemID::NUM')),(sf['GuardEquipItemID'],wc._string('EGuardEquipItemID::NUM' if skill['id'] is None else bg.GUARD_ITEMS[skill['id']]['enum'])),(sf['Value'],struct.pack('<i',skill['value']))])
   updates.append((name,i,ups))
   if name=='GuardWeaponDataArray':guard_count+=1
 # Equip each officer's own fifth weapon, never derive refs from display order.
 fifth={u['officer_id']:u for u in UNIQUE_WEAPONS.values() if u['tier']==5}
 for i,u in fifth.items():leaves.append((fields(base.records('PCSaveDataArray')[i])['WeaponDataID'],struct.pack('<i',u['data_id'])))
 refs=[]
 for family in range(5):
  wid=173+family*3+2;candidates=[i for i,r in enumerate(base.records('GuardWeaponDataArray')) if fields(r)['WeaponID']['value']==bg.GUARD_WEAPONS[wid]['enum']]
  if not candidates:raise SaveError('Missing third-tier guard weapon.')
  refs.append(candidates[0])
 for i,r in enumerate(base.records('GuardDataArray')):
  f=fields(r);arr=f['MemberWeapon']['value']['values'];leaves.append((f['MemberWeapon'],struct.pack('<11i',10,*(refs+arr[5:]))))
  if mode=='overlimit':leaves.append((f['BGLevels'],struct.pack('<7i',6,11,11,11,3,3,3)))
 if mode=='overlimit':
  for i,item in bg.GUARD_ITEMS.items():
   if item['kind']=='normal' and i!=1:leaves.append((fields(base.records('GuardEquipItemDataArray')[i])['Value'],struct.pack('<i',255)))
  for i,item in ITEMS.items():
   if item['kind']=='normal' and i!=2:leaves.append((fields(base.records('EquipItemDataArray')[i])['Value'],struct.pack('<i',max(ITEM_CAPS[i],255))))
 out=apply_updates(base,updates,leaves);validate(out.encrypted)
 for i,u in fifth.items():
  assert fields(out.records('PCSaveDataArray')[i])['WeaponDataID']['value']==u['data_id']
  assert fields(out.records('UniqueWeaponDataArray')[u['unique_save_index']])['WeaponID']['value']==u['weapon_enum']
  assert fields(out.records('PCSaveDataArray')[i])['MaxMusou']['value']==fields(original.records('PCSaveDataArray')[i])['MaxMusou']['value']
 for i in range(len(out.records('GuardDataArray'))):
  team=bg.team_state(out,i)
  assert team['MemberWeapon'][:5]==refs
  if mode=='legal':growth.validate_growth(team['SPoint'],team['BGLevels'])
 # Equip items in a second bounded transaction to avoid overlapping record patches.
 equipment_updates=[];equipment_priority=[17,18,39,36,38,28,22,37,16]
 for i,r in enumerate(out.records('PCSaveDataArray')[:42]):
  f=fields(r);ref=f['WeaponDataID']['value'];weapon=fields(out.records('UniqueWeaponDataArray')[ref-10000])
  rare={ow.ITEM_IDS.get(fields(s)['EquipItemID']['value']) for s in weapon['Skill']['value']['records']}
  chosen=[x for x in equipment_priority if x not in rare][:5]
  payload=struct.pack('<i',5)+b''.join(wc._string('EEquipItemID::'+ITEMS[x]['enum']) for x in chosen)
  equipment_updates.append(('PCSaveDataArray',i,[(f['SkillItemID'],payload)]))
 for i,r in enumerate(out.records('GuardDataArray')):equipment_updates.append(('GuardDataArray',i,[(fields(r)['MemberItem'],wc._string(bg.GUARD_ITEMS[9]['enum']))]))
 out=apply_updates(out,equipment_updates)
 return out.encrypted,{'mode':mode,'mixed_elements':mixed_elements,'reference_test_environment':TESTED_ENVIRONMENT,'source_sha256':hashlib.sha256(raw).hexdigest(),'output_sha256':hashlib.sha256(out.encrypted).hexdigest(),'officers_equipped_five_star':42,'officer_weapons':weapon_count,'guard_weapons':guard_count,'guard_teams':len(out.records('GuardDataArray')),'guard_equipped_tier':3,'guard_levels':growth.safe_preset() if mode=='legal' else [11,11,11,3,3,3],'officers_equipped_items':42,'guard_item':'Healing Scroll (one self-heal)','roundtrip_verified':True,'gameplay_validation':'User tested the initial-save Legal Max candidate without reported issues and the prior Overlimit numeric profile; the initial-save Overlimit candidate was tested in-game without reported issues on 2026-10-11; the mixed-element option has not been separately tested in-game.','warnings':out.compatibility_warnings}
