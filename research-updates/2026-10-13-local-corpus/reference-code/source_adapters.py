"""Explicit read-only metadata adapters. Frozen source bytes are never rewritten.
Currently supports reader A's source-multi-region/face-observations-v1 package.
It changes only container metadata; class/status/units/coordinates/order are not adapted.
"""
import copy,json
from pathlib import Path

def multi_region_views(source_manifest,manifest_path,freeze,case,selected,read_ref,require):
 card=case['card_id'];require(source_manifest.get('schema')=='anna-source-multi-region-manifest-v1' and source_manifest.get('card')==card,'Unsupported source manifest adapter')
 require(source_manifest.get('key_projection_performed') is False and source_manifest.get('target_literal_seen') is False,'Source manifest must precede target projection')
 require(freeze.get('card')==card and freeze.get('key_projection_performed') is False and freeze.get('source_manifest_sha256')==case['source_manifest']['sha256'],'Source package freeze identity/binding mismatch')
 documents=source_manifest.get('documents');require(isinstance(documents,list),'Required full source document manifest')
 refs={}
 for d in documents:
  p=(manifest_path.parent/d['path']).resolve();ref={'path':str(p),'sha256':d['sha256']}
  require(d['path']not in refs and freeze['hashes'].get(d['path'])==d['sha256'],'Source document missing/duplicated in package freeze')
  refs[d['path']]=ref
 # The source manifest's graphical documents must match the released geometric order exactly.
 cipher=[d for d in documents if d['role']=='cipher'];profiles=case['faces']['picture']['cipher_ledgers']
 require([d['region_id']for d in cipher]==source_manifest['editorial_region_order']==[region for p in profiles for region in p['region_ids']],'Frozen geometric/editorial source order mismatch')
 require(len(cipher)==len(profiles),'Omitted or added source cipher document')
 for d,p in zip(cipher,profiles):
  require(d['sha256']==p['ledger']['sha256'] and d['orientation']==p['orientation'] and d['source_sha256']==selected['picture']['sha256'],'Source cipher document/frame binding mismatch')
 survey=[d for d in documents if d['role']=='survey'];require(len(survey)==1,'Exactly one complete both-face source survey required')
 require(survey[0]['sha256']==case['observations']['sha256'],'Case observations differ from frozen source manifest')
 raw=read_ref(refs[survey[0]['path']],'Frozen source survey')
 require(raw.get('schema_version')=='source_face_observations_v1' and raw.get('card')==card and raw.get('orientation')=='NONE','Unsupported explicit source survey schema')
 require(raw.get('selection_sha256')==case['selection']['sha256'],'Source survey selection binding mismatch')
 faces=[];ordinary_faces=[]
 for name in ('picture','address'):
  face=raw.get(name);require(isinstance(face,dict),'Complete source survey face missing')
  require(raw['source_sha256_by_face'][name]==selected[name]['sha256'],'Survey source-face hash mismatch')
  presence=face.get('cipher_presence');require(presence in {'cipher_observed','no_cipher_observed'},'Unsupported survey cipher-presence value')
  ordinary=[d for d in documents if d['role']=='ordinary_'+name];require(len(ordinary)==1,'Complete direct ordinary source document required')
  doc=ordinary[0];require(doc['sha256']==case['diplomatic_documents'][name]['sha256'] and doc['source_sha256']==selected[name]['sha256'],'Frozen ordinary document binding mismatch')
  body=read_ref(refs[doc['path']],'Frozen ordinary '+name)
  require(body.get('schema_version')=='source_diplomatic_ordinary_v1' and body.get('card')==card and body.get('source_sha256')==selected[name]['sha256'],'Unsupported ordinary source container')
  records=body.get('records');require(isinstance(records,list),'Complete direct ordinary records required')
  blocks=face.get('ordinary_blocks');require(isinstance(blocks,list) and all(b.get('diplomatic_path')==doc['path'] for b in blocks),'Every ordinary observation must bind exact source transcription document')
  blocks=ordinary_index_view(blocks,records,require)
  entry={'face':name,'source':{k:selected[name][k]for k in ('sha256','bytes','dimensions','source_url')},'orientation':'NONE','oriented_dimensions':selected[name]['dimensions'],'cipher_present':presence=='cipher_observed','cipher_regions':face.get('cipher_regions',[]),'ordinary_handwritten_blocks':blocks,'edge_survey':face.get('edge_survey')}
  faces.append(entry)
  declaration=case['faces'][name]['ordinary_orientation']
  ordinary_faces.append({'face':name,'sha256':body['source_sha256'],'orientation':'PER_RECORD'if isinstance(declaration,dict)else body['orientation'],'records':records})
 return {'card':card,'source_first_procedural':True,'key_projection_performed':False,'faces':faces},{'card':card,'key_projection_performed':False,'faces':ordinary_faces}

def ordinary_index_view(blocks,records,require):
 # source_face_observations_v1 explicitly records zero-based indices into records[].
 require([b.get('diplomatic_record_index')for b in blocks]==list(range(len(records))),'Complete zero-based source ordinary index coverage required')
 converted=[]
 for block,record in zip(blocks,records):
  require(block.get('id')==record.get('id')and block.get('bbox_xyxy')==record.get('bbox_xyxy')and block.get('orientation')==record.get('orientation'),'Source ordinary index/ID/window/frame mismatch')
  view=copy.deepcopy(block);view['original_zero_based_diplomatic_record_index']=block['diplomatic_record_index'];view['diplomatic_record_index']=block['diplomatic_record_index']+1;view['index_view_operation']='Explicit zero-based source records[] index to one-based canonical coverage; original survey hash-bound.';converted.append(view)
 return converted

def cipher_metadata_view(document,expected_source,adapter,require):
 if adapter=='canonical':return document
 if adapter=='source_terminal_group_punctuation_v1_card213':
  require(document.get('card')==213 and document.get('orientation')=='NONE','Explicit native card213 punctuation container required')
  view=dict(document);view['rows']=[]
  for row in document['rows']:
   rowview=dict(row);rowview['groups']=[]
   for group in row['groups']:
    groupview=dict(group);marks=[]
    for index,mark in enumerate(group.get('punctuation',[]),1):
     require(isinstance(mark,dict)and set(mark)=={'mark','ownership','bbox_xyxy'}and mark['ownership']=='terminal_group','Exact recorded terminal-group punctuation schema required')
     require(mark['mark']in {'.',',','-'}and group.get('units'),'Unsupported saved terminal punctuation or missing target unit')
     require(len(group.get('punctuation',[]))==1,'Multiple terminal marks require separately reviewed source order')
     marks.append({'id':group['id']+'-RECORDED-MARK-'+str(index),'literal':mark['mark'],'status':'recorded','after_unit_id':group['units'][-1]['id'],'bbox_xyxy':mark['bbox_xyxy'],'original_source_punctuation_record':copy.deepcopy(mark),'metadata_view_operation':'Source-recorded terminal_group mark projected to canonical boundary metadata; no source certainty or glyph ownership upgrade.'})
    groupview['punctuation']=marks;rowview['groups'].append(groupview)
   view['rows'].append(rowview)
  return view
 require(adapter=='source_graphical_ledger_v1_card211'and document.get('schema_version')=='source_graphical_ledger_v1'and document.get('card')==211,'Unsupported explicit cipher metadata adapter')
 source=document.get('source_metadata');require(isinstance(source,dict),'Explicit card211 source metadata dictionary required')
 for field in ('sha256','bytes','dimensions','source_url'):require(source.get(field)==expected_source[field],'Card211 source metadata '+field+' mismatch')
 require(document.get('source_dimensions')==expected_source['dimensions']and document.get('physical_glyph_total')is None,'Card211 native source dimensions/physical total mismatch')
 # Only the container header is projected into the canonical metadata interface.
 # The rows/groups/units are passed unchanged, preserving identity, order and values.
 view={k:v for k,v in document.items()if k not in {'schema_version','source_metadata'}}
 view['source']=source;view['physical_body_count']=None
 return view
