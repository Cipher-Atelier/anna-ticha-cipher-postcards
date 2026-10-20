"""Offline manifest-driven replay of root-released frozen cases only."""
import argparse,hashlib,importlib.util,json,sys
from pathlib import Path
from collections import Counter
from urllib.parse import urlparse
import shared_replay as core
import source_adapters
import source_preflight
ROOT=Path(__file__).resolve().parent
TASK=ROOT.parent
sys.dont_write_bytecode=True
KEY_SHA='fe0a7272d6e372eefd4710b86f502e8c666fa5dfe8d1a17cc06df5e25deb0d95'
BASELINES={'engine':('anna-corpus-local-20261012/replay_batch.py','1154f4ca23dc6b3bf2f8c2f8c968616db5c9ffd1e4baaa721f66e06256980d1d'),'helper':('anna-corpus-local-20261012/build_inventory.py','712cd65bcd4e6a2b2d494571349a47b2f8dc3bfa9e6a045a288c83c25511662a'),'key':('anna-card330-research/verification/anna-ticha/data/key.csv',KEY_SHA),'atlas':('anna-card330-research/verification/anna-ticha/data/glyph_atlas.json','c517adfffa74588f9751fbc3fbd2f28ee707fd41c6ca4b961497c57321fd770b'),'reviewed_core':('anna-card210-local-20261012/native210_replay.py','a7aeedc7ab42eba8039de5022d6f11ec0591fa54da92e7dbd7fb75bda01f09f2'),'reviewed_wrapper':('anna-card210-local-20261012/replay_card210.py','42b9c5ae925cb624e6ed346e6e932e29299c0b182b8b91bb83a52f27a0ef9cb8')}
def require(ok,message):
 if not ok:raise ValueError(message)
def sha(path):return hashlib.sha256(Path(path).read_bytes()).hexdigest()
def path_in_root(value):
 p=(ROOT/value).resolve();require(p.is_relative_to(ROOT),'Case evidence must remain inside completion root');return p
def read_ref(ref,label):
 require(isinstance(ref,dict) and set(ref)=={'path','sha256'},label+': exact path/hash reference required')
 p=path_in_root(ref['path']);require(sha(p)==ref['sha256'],label+' fingerprint mismatch');return json.loads(p.read_text())
def load_engine():
 for label,(name,digest) in BASELINES.items():require(sha(TASK/name)==digest,'Protected baseline drift: '+label)
 folder=TASK/'anna-corpus-local-20261012';sys.path.insert(0,str(folder))
 try:
  spec=importlib.util.spec_from_file_location('immutable_completion_engine',folder/'replay_batch.py');engine=importlib.util.module_from_spec(spec);spec.loader.exec_module(engine)
 finally:sys.path.remove(str(folder))
 require(Path(sys.modules['build_inventory'].__file__).resolve()==(folder/'build_inventory.py').resolve(),'Unexpected cached helper module identity')
 return engine

def validate_selection(selection,card,protocol,engine):
 require(selection.get('card_id')==card and selection.get('packet_sha256')==protocol,'Selection card/protocol mismatch')
 require(selection.get('collector_pixels_viewed') is False,'Collector exposure declaration mismatch')
 check=selection['metadata'];metadata=Path(check['metadata_path']);require(metadata.resolve().is_relative_to(ROOT),'Catalogue snapshot outside completion root')
 require(sha(metadata)==check['metadata_sha256'],'Catalogue metadata drift')
 data=json.loads(metadata.read_text())['data'];ident=data.get('id')
 require(type(ident)is int and data.get('name')==f'pc_hcp_{card}' and data.get('recipient')=={'id':403,'name':'Anna Tichá'},'Exact catalogue affiliation mismatch')
 require(check['requested_record_id']==ident==check['returned_record_id'] and check['Anna_affiliation_verified'] is True,'Selection catalogue identity mismatch')
 faces=selection.get('faces');require(isinstance(faces,list) and len(faces)==2 and {f.get('face') for f in faces}=={'picture','address'},'Both unique source faces required')
 originals=[]
 for group in data.get('datagroups',[]):
  for item in group.get('data',[]):
   if item.get('type')=='image':originals.append(item.get('image',{}).get('original'))
 for f in faces:
  require(f.get('card_id')==card and originals.count(f.get('source_url'))==1,'Exact metadata-listed original source required')
  suffix='pic' if f['face']=='picture' else 'adr'
  require(Path(urlparse(f['source_url']).path).name==f'pc_hcp_{card}_{suffix}.JPG','Source URL does not match declared picture/address face')
  p=Path(f['local_path']);require(p.resolve().is_relative_to(ROOT),'Selected source outside completion root')
  require(sha(p)==f['sha256'] and p.stat().st_size==f['bytes'],'Source fingerprint/bytes drift')
  require(engine.jpeg_dimensions(p)==f['dimensions'],'Source header dimensions drift')
 declaration=path_in_root(f'cards/card{card}/source-selection-declaration.json')
 require(sha(declaration)==selection['declaration_sha256'],'Pre-download declaration drift')
 saved=json.loads(declaration.read_text());require(saved.get('card_id')==card and saved.get('packet_sha256')==protocol and saved.get('metadata')==check,'Pre-download card/metadata/protocol mismatch')
 require(isinstance(saved.get('assets'),dict) and set(saved['assets'])==set(f['face'] for f in faces) and all(saved['assets'][f['face']]['url']==f['source_url'] for f in faces),'Pre-download exact face asset declaration mismatch')
 return {f['face']:f for f in faces}

def ordinary_frame(profile,index):
 declaration=profile['ordinary_orientation']
 if isinstance(declaration,str):return declaration
 require(isinstance(declaration,dict) and str(index) in declaration,'Explicit per-record ordinary frame missing')
 orientation=declaration[str(index)];core.frame_dimensions(orientation,[1,1]);return orientation

def validate_observations(observations,card,faces,profiles,engine):
 require(observations.get('card')==card and observations.get('source_first_procedural') is True and observations.get('key_projection_performed') is False,'Required source-first both-face observation identity')
 items=observations.get('faces');require(isinstance(items,list) and len(items)==2 and {f.get('face') for f in items}=={'picture','address'},'Both observation faces required')
 result={f['face']:f for f in items}
 for name,o in result.items():
  profile=profiles[name];source=o.get('source');require(isinstance(source,dict),'Observation source required')
  for field in ('sha256','bytes','dimensions','source_url'):require(source.get(field)==faces[name][field],name+' observation/source '+field+' mismatch')
  require(o.get('orientation')=='NONE' and o.get('oriented_dimensions')==faces[name]['dimensions'],'Whole-face survey must declare native source frame; region frames are separate')
  require(type(o.get('cipher_present'))is bool and o['cipher_present']==profile['cipher_present'],'Cipher-face scope mismatch')
  regions=o.get('cipher_regions');require(isinstance(regions,list),'Complete cipher region list required')
  require(bool(regions)==o['cipher_present'],'Cipher presence/observed region mismatch')
  expected_regions=[rid for ledger in profile['cipher_ledgers'] for rid in ledger['region_ids']]
  require([r.get('region_id') for r in regions]==expected_regions,'Every observed cipher region and geometric display order must be retained')
  ledger_map={rid:ledger for ledger in profile['cipher_ledgers'] for rid in ledger['region_ids']}
  require(len(ledger_map)==len(expected_regions),'Duplicate per-face cipher region profile')
  for region in regions:
   require(isinstance(region.get('region_id'),str)and bool(region['region_id'])and isinstance(region.get('role'),str)and bool(region['role']),'Source region ID and role must be nonempty strings')
   ledger=ledger_map[region['region_id']];dims=core.frame_dimensions(ledger['orientation'],faces[name]['dimensions'])
   require(region.get('orientation')==ledger['orientation'] and region.get('oriented_dimensions')==dims,'Independent region frame mismatch')
   engine.validate_declared_windows(region,dims,'region observation '+region['region_id']);engine.box(region.get('bbox_xyxy'),dims,'region observation')
  survey=o.get('edge_survey');require(isinstance(survey,dict) and set(survey)=={'top','bottom','left','right'} and all(isinstance(v,str) and v for v in survey.values()),'Complete four-edge survey required')
  blocks=o.get('ordinary_handwritten_blocks');require(isinstance(blocks,list),'Ordinary survey blocks required, explicit empty list allowed')
  for block in blocks:
   indices=block.get('diplomatic_record_indices',[block.get('diplomatic_record_index')])
   require(isinstance(indices,list) and indices and all(type(i)is int and i>0 for i in indices),'Explicit ordinary source block indices required')
   frames={ordinary_frame(profile,index)for index in indices};require(len(frames)==1 and block.get('orientation')in frames,'Ordinary source block frame mismatch')
   dims=core.frame_dimensions(block['orientation'],faces[name]['dimensions'])
   engine.validate_declared_windows(block,dims,'ordinary source block');engine.box(block.get('bbox_xyxy'),dims,'ordinary source block')
 return result

def validate_regions(document,binding,observed,card,face,dims,engine):
 require(binding.get('card')==card and binding.get('face')==face,'Row-region binding identity mismatch')
 regions=binding.get('regions');source=observed['cipher_regions']
 require(isinstance(regions,list) and regions,'Explicit cipher document regions required')
 source_map={r['region_id']:r for r in source};require(len(source_map)==len(source),'Duplicate observed region ID')
 require(all(r.get('region_id') in source_map for r in regions),'Cipher document region absent from full source survey')
 rows=[];row_map={}
 for r in regions:
  require(isinstance(r.get('region_id'),str)and bool(r['region_id'])and isinstance(r.get('role'),str)and bool(r['role']),'Bound region ID and role must be nonempty strings')
  original=source_map[r['region_id']];require(r.get('role')==original.get('role') and r.get('row_ids')==original.get('observed_row_ids'),'Observed region role/row completeness mismatch')
  engine.box(original.get('bbox_xyxy'),dims,'source region '+r['region_id'])
  require(isinstance(r['row_ids'],list) and r['row_ids'],'Each observed region requires rows')
  for rid in r['row_ids']:
   require(isinstance(rid,str) and rid and rid not in row_map,'Duplicate/invalid row-region ID');row_map[rid]=r['region_id'];rows.append(rid)
 require([r.get('id') for r in document.get('rows',[])]==rows,'Omitted, added or reordered observed cipher row')
 for row in document['rows']:
  engine.box(row.get('bbox_xyxy'),dims,'required row window '+row['id'])
  if 'region_id'in row:require(row['region_id']==row_map[row['id']],'Raw region label mismatch')
 return {'face':face,'regions':regions,'row_region_ids':row_map}

def validate_ordinary_record(record):
 require(isinstance(record,dict),'Ordinary record object required')
 text=record.get('transcription')
 require('transcription'in record and (isinstance(text,str)and bool(text)or text is None),'Ordinary transcription must be an exact nonempty string or explicit null')
 require('uncertainty'in record and (record['uncertainty']is None or isinstance(record['uncertainty'],str)and bool(record['uncertainty'])),'Exact ordinary uncertainty string or explicit null required')
 if text is None:require(isinstance(record.get('shape_note'),str)and bool(record['shape_note']),'Null ordinary transcription requires recorded nontext shape note')
 require(not {'class_id','units','accepted_literal','key_value'}&record.keys(),'Ordinary handwriting cannot be cipher mapped')
 return 'nontext_graphical_mark' if text is None else 'direct_transcription'

def ordinary_display(record,index):
 kind=validate_ordinary_record(record)
 if kind=='direct_transcription':
  if record.get('recorded_kind')=='direct_printed_text':return '[DIRECT PRINTED TEXT / RECORD '+str(index)+']\n'+record['transcription']
  return record['transcription']
 return '[NON-TEXT ORDINARY GRAPHICAL MARK / RECORD '+str(index)+']\nRECORDED SHAPE NOTE (not a transcription): '+record['shape_note']

def validate_diplomatic(diplomatic,card,faces,observations,profiles,counts,engine):
 require(diplomatic.get('card')==card and diplomatic.get('key_projection_performed') is False,'Direct diplomatic identity/scope mismatch')
 entries=diplomatic.get('faces');require(isinstance(entries,list) and len(entries)==2 and {e.get('face') for e in entries}=={'picture','address'},'Complete diplomatic both-face records required')
 for entry in entries:
  name=entry['face'];declaration=profiles[name]['ordinary_orientation']
  require(entry.get('sha256')==faces[name]['sha256'],'Diplomatic source fingerprint mismatch')
  require(entry.get('orientation')==('PER_RECORD' if isinstance(declaration,dict) else declaration),'Diplomatic declared source frame mismatch')
  records=entry.get('records');require(isinstance(records,list) and len(records)==counts[name],'Omitted or extra ordinary diplomatic record')
  if isinstance(declaration,dict):require(set(declaration)=={str(i)for i in range(1,len(records)+1)},'Complete independently declared ordinary frame indices required')
  for index,record in enumerate(records,1):
   orientation=ordinary_frame(profiles[name],index);dims=core.frame_dimensions(orientation,faces[name]['dimensions'])
   require(record.get('orientation',entry['orientation'])==orientation,'Ordinary record coordinate frame mismatch')
   validate_ordinary_record(record)
   engine.box(record.get('bbox_xyxy'),dims,'diplomatic '+name)
  blocks=observations[name]['ordinary_handwritten_blocks'];indexed=[b for b in blocks if 'diplomatic_record_index'in b];enclosing=[b for b in blocks if 'diplomatic_record_indices'in b]
  require(len(indexed)+len(enclosing)==len(blocks),'Every ordinary observation needs explicit indexed record coverage')
  covered=[]
  for block in indexed:
   index=block['diplomatic_record_index'];require(type(index)is int and 1<=index<=len(records),'Invalid diplomatic record index')
   require(records[index-1]['bbox_xyxy']==block.get('bbox_xyxy'),'Diplomatic window differs from indexed source block');covered.append(index)
  for block in enclosing:
   ids=block['diplomatic_record_indices'];require(isinstance(ids,list) and ids and all(type(i)is int and 1<=i<=len(records) for i in ids),'Explicit enclosing diplomatic record indices required')
   frames={ordinary_frame(profiles[name],i)for i in ids};require(len(frames)==1,'One ordinary enclosing block cannot mixcoordinateframes')
   dims=core.frame_dimensions(next(iter(frames)),faces[name]['dimensions'])
   outer=engine.box(block.get('bbox_xyxy'),dims,'ordinary enclosing block')
   for index in ids:
    b=records[index-1]['bbox_xyxy'];require(outer[0]<=b[0]<b[2]<=outer[2] and outer[1]<=b[1]<b[3]<=outer[3],'Ordinary record outside enclosing source block');covered.append(index)
  require(sorted(covered)==list(range(1,len(records)+1)),'Missing or duplicated ordinary source coverage')
 return diplomatic

def validate_masks(records,document,approved,face):
 raw={u['id']:u for row in document['rows'] for group in row['groups'] for u in group['units']};result={}
 expected=[r for r in approved if r['face']==face];source={r['unit_id']:r for r in expected};require(len(source)==len(expected),'Duplicate review mask ID')
 for r in records:
  require(set(r)=={'face','unit_id','raw_class_id','raw_status','raw_bbox_xyxy','reason','action'},'Only explicit exact-ID mask fields permitted')
  uid=r['unit_id'];require(r['face']==face and uid in source and uid not in result and uid in raw,'Wrong, duplicate or absent reviewed unit')
  u=raw[uid];a=source[uid]
  require(r['action']=='mask' and r['raw_class_id']==u['class_id']==a['raw_class_id'],'Mask raw class/action mismatch')
  require(r['raw_status']==u['status']==a['raw_status']=='provisional_known_class' and not u['alternatives'],'Review mask requires raw unmixed known proposal')
  require(r['raw_bbox_xyxy']==u['bbox_xyxy']==a['bbox_xyxy'] and r['reason']==a['reason'],'Mask window/reason mismatch')
  result[uid]=r
 require(set(result)==set(source),'Exactly all independently approved masks required')
 return result

def apply_derived_masks(result,document,mask_map):
    """Mask only derived artifacts; neither raw document nor engine is modified."""
    result['raw_baseline_counts']=dict(result['counts'])
    tokens={t['unit_id']:t for t in result['tokens']}
    groups={g['group_id']:g for g in result['groups']}
    for uid,record in mask_map.items():
        token=tokens[uid]
        require(token['provisionally_mapped_slots']==1 and token['masked_representation_slots']==0,'Review target already masked or not provisionally mapped')
        emitted_letters=token['emitted_known_letters']
        delta={'provisionally_mapped_slots':-1,'masked_representation_slots':1,'emitted_known_letters':-emitted_letters,
               'capped_ch_slots':-int(token['class_id_recorded']=='G10_CAP')}
        for key,value in delta.items():
            result['counts'][key]+=value
            groups[token['group_id']]['counts'][key]+=value
        token.update({'emitted':f'[U:{uid}]','provisionally_mapped_slots':0,'masked_representation_slots':1,'emitted_known_letters':0,
                      'masked_by_source_review_overlay':True,'source_review_mask_reason':record['reason']})
    result['counts']['additional_source_review_masks']=len(mask_map)
    result['counts']['observed_known_classes']=len({t['class_id_recorded'] for t in result['tokens'] if t['provisionally_mapped_slots']})
    marks={}
    for mark in result['punctuation']:marks.setdefault(mark['group_id'],[]).append(mark)
    lines=[]
    for row in document['rows']:
        texts=[]
        for group in row['groups']:
            before={};after={}
            for mark in marks.get(group['id'],[]):
                raw=mark['recorded']
                if 'before_unit_id' in raw:before[raw['before_unit_id']]=mark['emitted']
                else:after[raw['after_unit_id']]=mark['emitted']
            texts.append(''.join(before.get(u['id'],'')+tokens[u['id']]['emitted']+after.get(u['id'],'') for u in group['units']))
        lines.append(' '.join(texts))
    result['literal_lines']='\n'.join(lines)+'\n'
    return result


def validate_freeze(freeze,digest,label,card):
 require(isinstance(freeze,dict),'Required '+label+' freeze object')
 roles={'Review':('review','source-review',['subject_sha256','review_sha256','source_review_sha256','sha256']), 'Audit':('audit','source-audit',['subject_sha256','audit_sha256','source_audit_sha256','sha256']), 'Peer graphics':('peer','independent-fragments',['subject_sha256','independent_fragments_sha256','sha256']), 'Nominations':('nominations','fragment-nominations',['subject_sha256','fragment_nominations_sha256','original_nomination_sha256','sha256'])}
 role,suffix,fields=roles[label]
 supported=(freeze.get('schema')=='anna-completion-freeze-v1' and freeze.get('role')==role) or freeze.get('schema')==f'anna{card}-{suffix}-freeze-v1'
 require(supported,label+' freeze role/schema mismatch')
 subjects=[freeze[f] for f in fields if f in freeze];require(subjects and all(v==digest for v in subjects),label+' freeze subject fingerprint mismatch or conflicting subject fields')
 flags=[freeze[k] for k in ['key_projection_performed','key_projection_exposed','target_projection_seen','target_literal_seen','literal_exposure'] if k in freeze]
 require(flags and all(value is False for value in flags),label+' freeze must explicitly precede key/literal projection')
 return freeze

def validate_peer_stages(nominations,graphics,agreement,card,expected_ids):
 require(nominations.get('card')==card and nominations.get('nominated_before_any_key_or_literal_projection') is True,'Source-only nomination identity/stage mismatch')
 def ids(stage,field):
  entries=stage.get('fragments');require(isinstance(entries,list),'Required complete fragment-stage list')
  values=[e.get(field) for e in entries if isinstance(e,dict)]
  require(len(values)==len(entries) and all(isinstance(v,str) and v for v in values) and len(set(values))==len(values),'Duplicate or invalid fragment identity')
  return values
 source_ids=ids(nominations,'id');require(source_ids==expected_ids,'Complete frozen nominated-fragment identities/order mismatch')
 require(ids(graphics,'id')==source_ids and ids(agreement,'fragment_id')==source_ids,'Every nominated run needs peer graphics and comparison, including abstentions')
 for entry in graphics['fragments']:require(entry.get('translation_or_literal_generated') is False,'Peer graphics must precede literal/translation')
 for entry in agreement['fragments']:
  require(entry.get('literal_or_translation_consulted') is False and isinstance(entry.get('outcome'),str) and entry['outcome'],'Explicit source-only comparison/abstention outcome required')
 return source_ids

def execute_case(manifest,engine):
 require(manifest.get('schema')=='anna-released-completion-case-v1','Unreviewed case manifest schema')
 card=manifest['card_id'];require(type(card)is int and 198<=card<=460,'Numeric candidate outside requested range')
 protocol=read_ref(manifest['protocol'],'Root source protocol')
 require(card in protocol.get('acquire_next_only',[]) and card not in protocol.get('independent_control_reserve_excluded_from_acquisition_and_view',[]),'Card not released for this source stage')
 for label,ref in protocol['baselines'].items():require(sha(TASK/ref['path'])==ref['sha256'],'Frozen protocol baseline drift: '+label)
 selection=read_ref(manifest['selection'],'Source selection');faces=validate_selection(selection,card,manifest['protocol']['sha256'],engine)
 review=read_ref(manifest['review'],'Independent source review');validate_freeze(read_ref(manifest['review_freeze'],'Independent review freeze'),manifest['review']['sha256'],'Review',card)
 require(review.get('card')==card,'Source review card mismatch')
 bindings=review['bindings']
 refs={'selection':'selection_sha256','observations':'face_observations_sha256','diplomatic':'diplomatic_transcription_sha256','audit':'source_audit_sha256','audit_freeze':'source_audit_freeze_sha256'}
 for name,field in refs.items():require(manifest[name]['sha256']==bindings[field],'Independent review binding mismatch: '+name)
 require(bindings['protocol_sha256']==manifest['protocol']['sha256'],'Independent protocol review binding mismatch')
 read_ref(manifest['audit'],'Independent source audit');validate_freeze(read_ref(manifest['audit_freeze'],'Audit freeze'),manifest['audit']['sha256'],'Audit',card)
 for name,field in [('nominations','fragment_nominations_sha256'),('nominations_freeze','fragment_nominations_freeze_sha256'),('peer_graphics','independent_fragments_sha256'),('peer_freeze','independent_fragments_freeze_sha256'),('agreement','fragment_agreement_sha256')]:
  require(manifest[name]['sha256']==bindings[field],'Required peer-stage review binding mismatch: '+name);read_ref(manifest[name],'Independent peer stage '+name)
 validate_freeze(read_ref(manifest['peer_freeze'],'Peer graphics freeze'),manifest['peer_graphics']['sha256'],'Peer graphics',card)
 validate_freeze(read_ref(manifest['nominations_freeze'],'Source nomination freeze'),manifest['nominations']['sha256'],'Nominations',card)
 validate_peer_stages(read_ref(manifest['nominations'],'Complete nominations'),read_ref(manifest['peer_graphics'],'Complete peer graphics'),read_ref(manifest['agreement'],'Complete source comparison'),card,manifest['expected_nomination_ids'])
 require(manifest['expected_nomination_ids']==review['complete_nomination_ids'],'Independent complete nomination identity scope mismatch')
 require(manifest['preprojection_provenance']==review['preprojection_provenance'],'Supplemental provenance set differs from frozen independent review')
 for ref in manifest['preprojection_provenance']:read_ref(ref,'Frozen preprojection provenance')
 profiles=manifest['faces'];require(isinstance(profiles,dict) and set(profiles)=={'picture','address'},'Both explicit source geometry profiles required')
 observations=read_ref(manifest['observations'],'Complete both-face observations');observed=validate_observations(observations,card,faces,profiles,engine)
 counts=review['ordinary_transcription_scope'];require(set(counts)=={'picture_records','address_records'},'Explicit independently reviewed ordinary counts required')
 ordinary=validate_diplomatic(read_ref(manifest['diplomatic'],'Complete direct diplomatic'),card,faces,observed,profiles,{name:counts[name+'_records'] for name in faces},engine)
 overlay=read_ref(manifest['overlay'],'Required exact-ID overlay')
 require(set(overlay)=={'schema','card','raw_ledgers_sha256','key_sha256','source_review_sha256','source_faces_sha256','action','records'},'Unsupported/all-class overlay selection fields')
 require(overlay['schema']=='anna-exact-unit-review-mask-v1' and overlay['card']==card and overlay['action']=='mask_exact_reviewed_units_no_class_or_literal_replacement','Exact reviewed masking action required')
 require(overlay['key_sha256']==KEY_SHA and overlay['source_review_sha256']==manifest['review']['sha256'] and overlay['source_faces_sha256']=={f:faces[f]['sha256'] for f in faces},'Overlay source/key/review drift')
 approved=review['proposed_additional_masks'];require(isinstance(approved,list) and isinstance(overlay['records'],list),'Explicit mask lists required, empty only when independently approved')
 require(all(r.get('face')in faces and profiles[r['face']]['cipher_present'] for r in approved+overlay['records']),'Review mask refers to unobserved cipher face')
 require(all(isinstance(r.get('unit_id'),str)and bool(r['unit_id'])and isinstance(r.get('reason'),str)and bool(r['reason'])for r in approved+overlay['records']),'Exact review mask ID/nonempty reason required')
 raw_hashes={ledger['scope_id']:ledger['ledger']['sha256'] for profile in profiles.values() for ledger in profile['cipher_ledgers']}
 require(overlay['raw_ledgers_sha256']==raw_hashes,'Overlay frozen raw ledger drift')
 require(bindings['raw_ledgers_sha256']==raw_hashes,'Independently reviewed full scoped-ledger set mismatch')
 classes=source_preflight.class_identifiers(TASK);prepared=[];global_ids={name:set()for name in ('row','group','unit','punctuation')};scope_ids=set()
 for face in ('picture','address'):
  profile=profiles[face]
  require(set(profile)=={'cipher_present','ordinary_orientation','cipher_ledgers'},'Explicit source/ordinary/scoped-ledger profile required')
  require(isinstance(profile['cipher_ledgers'],list) and bool(profile['cipher_ledgers'])==profile['cipher_present'],'Cipher document presence mismatch')
  for ledger in profile['cipher_ledgers']:
   sid=ledger['scope_id'];require(isinstance(sid,str) and sid and sid not in scope_ids and '/'not in sid and '\\'not in sid,'Unique safe geometric cipher scope ID required')
   scope_ids.add(sid)
   document=read_ref(ledger['ledger'],sid+' frozen raw ledger');freeze=read_ref(ledger['freeze'],sid+' source-first freeze')
   subjects=[freeze[k]for k in ('ledger_sha256','sha256')if k in freeze]
   require(subjects and all(value==ledger['ledger']['sha256']for value in subjects) and freeze.get('key_projection_performed')is False,'Source-first ledger freeze mismatch or conflicting subject hashes')
   require(ledger['freeze']['sha256']==bindings['raw_freezes_sha256'][sid],'Independent source-first freeze binding mismatch')
   require(ledger['regions']['sha256']==bindings['row_region_bindings_sha256'][sid],'Independent complete-region fingerprint mismatch')
   region_binding=read_ref(ledger['regions'],sid+' row regions')
   require([r.get('region_id') for r in region_binding.get('regions',[])]==ledger['region_ids'],'Scoped complete-region selection mismatch')
   scope=validate_regions(document,region_binding,observed[face],card,face,core.frame_dimensions(ledger['orientation'],faces[face]['dimensions']),engine)
   projection_view=source_adapters.cipher_metadata_view(document,faces[face],ledger.get('metadata_adapter','canonical'),require)
   ids=set(source_preflight.validate_document(projection_view,faces[face],engine,card,ledger['orientation'],classes,global_ids))
   scoped_approved=[r for r in approved if r['unit_id']in ids]
   mask=validate_masks([r for r in overlay['records']if r['unit_id']in ids],document,scoped_approved,face)
   prepared.append((face,ledger,document,projection_view,scope,mask))

 require(all(r['unit_id']in global_ids['unit']for r in approved+overlay['records']),'Review mask unit absent from every frozen source document')
 require(len(overlay['records'])==len(approved),'Exact full overlay record count mismatch')
 warnings={name:review[name]for name in ['fragment_group_boundary_warnings','ordinary_transcription_warnings']}
 require(all(isinstance(v,list)for v in warnings.values()),'Frozen warning lists required')
 key=engine.load_key();results={};outputs={};scopes={};scope_order=[]
 for face,ledger,document,projection_view,scope,mask in prepared:
   sid=ledger['scope_id']
   result=core.replay_document(projection_view,key,faces[face],engine,card,face,ledger['orientation'])
   if ledger.get('metadata_adapter'):result['schema_notes'].append('Explicit read-only '+ledger['metadata_adapter']+' container metadata view; original raw bytes hash-bound, rows/groups/units unchanged.')
   apply_derived_masks(result,document,mask)
   for collection in (result['tokens'],result['groups'],result['punctuation']):
    for record in collection:record.update({'card_id':card,'face':face,'region_id':scope['row_region_ids'][record['row_id']]})
   package=core.package_bytes(result,{'key':KEY_SHA,'ledger':ledger['ledger']['sha256']},faces[face])
   for name in ['tokens.csv','literal-lines.txt']:outputs[sid+'-'+name]=package[name]
   result['original_source_punctuation_by_group']={g['id']:g.get('punctuation',[])for row in document['rows']for g in row['groups']if g.get('punctuation')}
   results[sid]=result;scopes[sid]=scope;scope_order.append(sid)
 sections=[];notes=['Source coding is uncertain; ordinary text is copied exactly. No date normalization, context repair or translation.']
 for face in ('picture','address'):
  for sid in scope_order:
   if scopes[sid]['face']!=face:continue
   row_text=dict(zip([rid for region in scopes[sid]['regions'] for rid in region['row_ids']],results[sid]['literal_lines'].splitlines()))
   for region in scopes[sid]['regions']:
    sections.append(face.upper()+' CIPHER / '+region['role']+' / '+region['region_id']+' / '+results[sid]['orientation']);sections.extend(row_text[r] for r in region['row_ids']);sections.append('')
  sections.append(face.upper()+' ORDINARY SOURCE RECORDS / DIRECT TEXT AND NON-TEXT MARKS')
  for i,record in enumerate(next(f for f in ordinary['faces'] if f['face']==face)['records'],1):
   sections.append(ordinary_display(record,i));notes.append(face+' record '+str(i)+' '+json.dumps(record['bbox_xyxy'])+': '+(record['uncertainty']if record['uncertainty']is not None else '[NO RECORDED UNCERTAINTY; source field is null, not certified certainty]'))
  sections.append('')
 for name,entries in warnings.items():
  notes.append(name);notes.extend(json.dumps(e,ensure_ascii=False,sort_keys=True,indent=2) for e in entries)
 outputs['both-face-literal.txt']=('\n'.join(sections)+'\n').encode();outputs['both-face-uncertainty-notes.txt']=('\n'.join(notes)+'\n').encode()
 refs={name:manifest[name] for name in ['protocol','selection','review','review_freeze','observations','diplomatic','audit','audit_freeze','overlay','nominations','nominations_freeze','peer_graphics','peer_freeze','agreement']}
 receipt={'schema':'anna-completion-replay-receipt-v1','status':'replayed_frozen_source_proposal','card_id':card,'source_faces':faces,'frozen_refs':refs,'preprojection_provenance':manifest['preprojection_provenance'],'faces_profiles':profiles,'geometric_editorial_scope_order':scope_order,'counts_by_cipher_document':{f:r['counts'] for f,r in results.items()},'regions':{f:scopes[f] for f in scopes},'row_source_metadata_by_document':{f:r['row_source_metadata_recorded'] for f,r in results.items()},'groups_by_document':{f:r['groups'] for f,r in results.items()},'recorded_punctuation_by_document':{f:r['punctuation'] for f,r in results.items()},'original_source_punctuation_by_document':{f:r['original_source_punctuation_by_group']for f,r in results.items()},'counts_by_region':{sid:[{'face':scopes[sid]['face'],'region_id':region['region_id'],'orientation':results[sid]['orientation'],'counts':dict(sum((Counter(g['counts']) for g in results[sid]['groups'] if g['region_id']==region['region_id']),Counter())),'physical_body_count':None} for region in scopes[sid]['regions']] for sid in scopes},'physical_body_count':None,'ordinary_records_by_face':{f['face']:f['records'] for f in ordinary['faces']},'ordinary_record_counts_by_face':{f['face']:{'recorded_scope_records':len(f['records']),'direct_transcribed_strings':sum(r['transcription']is not None for r in f['records']),'nontext_graphical_marks':sum(r['transcription']is None for r in f['records']),'direct_printed_records':sum(r.get('recorded_kind')=='direct_printed_text'for r in f['records'])} for f in ordinary['faces']},'source_review_mode':review.get('source_review_mode'),'warnings':warnings,'code_sha256':{'runner':sha(__file__),'source_adapters':sha(source_adapters.__file__),'source_preflight':sha(source_preflight.__file__),'neutral_class_atlas':source_preflight.ATLAS_SHA,'shared_core':sha(core.__file__),**{name:digest for name,(_,digest) in BASELINES.items()}},'outputs_sha256':{n:core.sha_bytes(b) for n,b in outputs.items()},'limits':['Byte, coordinate and saved-coding consistency only; no visual truth or calibrated accuracy certification.','Every alternative, unknown and exact reviewed disagreement remains masked. Group spaces preserve saved display order, not certified segmentation.','Both faces are surveyed at their stated scope; observed absence is not certified global absence. Ordinary handwriting is direct frozen transcription, never key decoded.','No total physical count, new mapping, mask resolution, postal-date upgrade or historical authentication.']}
 outputs['replay-receipt.json']=core.json_bytes(receipt);return outputs

def run_release(release_path,release_sha,output_root):
 release=read_ref({'path':str(release_path),'sha256':release_sha},'Root case release')
 require(release.get('schema')=='anna-completion-release-v1' and isinstance(release.get('cases'),list),'Root-issued exact case release required')
 require(release['runner_sha256']==sha(__file__) and release['shared_core_sha256']==sha(core.__file__) and release['source_adapters_sha256']==sha(source_adapters.__file__) and release['source_preflight_sha256']==sha(source_preflight.__file__),'Release must pin reviewed runner/core/metadata adapters')
 engine=load_engine();statuses=[];seen=set()
 for ref in release['cases']:
  try:
   manifest=read_ref(ref,'Released case');card=manifest['card_id'];require(card not in seen,'Duplicate released card');seen.add(card)
   outputs=execute_case(manifest,engine);destination=Path(output_root)/f'card{card}';require(not destination.exists(),'Output directory already exists; no overwrite')
   destination.mkdir(parents=True)
   for name,data in outputs.items():(destination/name).write_bytes(data)
   statuses.append({'card_id':card,'status':'ready_frozen_projection','outputs_sha256':{n:core.sha_bytes(b) for n,b in outputs.items()}})
  except (ValueError,KeyError,OSError,StopIteration,TypeError) as error:statuses.append({'case_ref':ref,'status':'blocked','reason':str(error)})
 return statuses

def main():
 p=argparse.ArgumentParser(description=__doc__);p.add_argument('release',type=Path);p.add_argument('--release-sha',required=True);p.add_argument('--output-root',type=Path,required=True);a=p.parse_args()
 try:print(json.dumps(run_release(a.release,a.release_sha,a.output_root),ensure_ascii=False,indent=2))
 except (ValueError,KeyError,OSError)as error:p.exit(2,'No projection: '+str(error)+'\n')
if __name__=='__main__':main()
