"""PROPOSAL: pure coordinate/container views; no key, pixels, source edits or cases.
Actual source use requires independent review. Original records remain referenced.
"""
import copy
FRAMES={'NONE','CW90','CCW90','ROTATE_180'}
def require(ok,message):
 if not ok:raise ValueError(message)
def frame_dims(frame,dims):
 require(frame in FRAMES,'Explicit supported frame required');return dims[::-1]if frame in {'CW90','CCW90'}else list(dims)
def rectangle(value,dims):
 require(isinstance(value,list)and len(value)==4 and all(type(v)is int for v in value),'Integer rectangle required')
 require(0<=value[0]<value[2]<=dims[0]and 0<=value[1]<value[3]<=dims[1],'Rectangle outside declared source frame');return value

def native_to_frame(value,dims,frame):
 x0,y0,x1,y1=rectangle(value,dims);width,height=dims
 if frame=='NONE':result=[x0,y0,x1,y1]
 elif frame=='CW90':result=[height-y1,x0,height-y0,x1]
 elif frame=='CCW90':result=[y0,width-x1,y1,width-x0]
 elif frame=='ROTATE_180':result=[width-x1,height-y1,width-x0,height-y0]
 else:raise ValueError('Unsupported exact frame transform')
 rectangle(result,frame_dims(frame,dims));return result

def views(observations,diplomatic,bindings,raw_documents,native_region_ids):
 """native_region_ids is explicit reviewed interpretation, never inferred by fit."""
 require(observations['card']==diplomatic['card']==bindings['card'],'Source view card mismatch');card=observations['card']
 require(observations['source_first_procedural']is True and observations['key_projection_performed']is False and diplomatic['key_projection_performed']is False,'Source-first metadata required')
 obs=copy.deepcopy(observations);provenance=[];seen=[];per_document={};document_faces={};profiles={}
 dip={f['face']:f for f in diplomatic['faces']};require(set(dip)=={'picture','address'}and len(dip)==len(diplomatic['faces']),'Both unique diplomatic faces required')
 original_regions={r['region_id']:r for r in bindings['regions']};require(len(original_regions)==len(bindings['regions']),'Duplicate source region binding')
 require([r['region_id']for face in obs['faces']for r in face['cipher_regions']]==list(original_regions),'Observed region order differs from frozen bindings')
 require(set(native_region_ids)<=set(original_regions),'Native-frame override not in frozen region binding')
 for face in obs['faces']:
  name=face['face'];source=face['source'];dims=source['dimensions'];require(face['orientation']=='NONE'and face['oriented_dimensions']==dims and dip[name]['sha256']==source['sha256'],'Native full-face survey identity/frame required')
  require('ordinary_coverage'in face and 'ordinary_handwritten_blocks'not in face,'Exact ordinary coverage alias required')
  coverage=face['ordinary_coverage'];records=dip[name]['records'];require([b['diplomatic_record_index']for b in coverage]==list(range(1,len(records)+1)),'Complete one-based ordinary coverage required')
  for block,record in zip(coverage,records):
   frame=record.get('orientation',dip[name]['orientation']);require(frame in FRAMES and block['orientation']==frame and block['bbox_xyxy']==record['bbox_xyxy'],'Ordinary record/coverage frame-window mismatch');rectangle(block['bbox_xyxy'],frame_dims(frame,dims))
  face['ordinary_handwritten_blocks']=copy.deepcopy(coverage)
  if 'edge_surveys'in face:
   require('edge_survey'not in face,'Conflicting edge survey aliases');face['edge_survey']=copy.deepcopy(face['edge_surveys'])
  require(set(face['edge_survey'])=={'top','bottom','left','right'},'Complete edge survey required')
  ordinary_frame={str(i):r['orientation']for i,r in enumerate(records,1)}if dip[name]['orientation']=='PER_RECORD'else dip[name]['orientation']
  profiles[name]={'cipher_present':face['cipher_present'],'ordinary_orientation':ordinary_frame,'cipher_ledgers':[]}
  for region in face['cipher_regions']:
   rid=region['region_id'];require(rid in original_regions and rid not in seen,'Unknown or duplicated observed region');seen.append(rid);binding=original_regions[rid]
   row_ids=binding.get('row_ids',binding.get('observed_row_ids'));require(region['role']==binding['role']and region['observed_row_ids']==row_ids,'Region role/row source binding mismatch')
   document_name=binding.get('raw_document',binding.get('document'))
   if document_name is None:
    require(isinstance(bindings.get('raw_documents'),list)and len(bindings['raw_documents'])==1,'Explicit source document ownership required');document_name=bindings['raw_documents'][0]
   require(document_name in raw_documents,'Observed source document missing');raw=raw_documents[document_name];frame=raw['orientation']
   require(raw['card']==card and raw['source']==source and region['orientation']==frame and region['oriented_dimensions']==raw['oriented_dimensions']==frame_dims(frame,dims),'Source document/frame identity mismatch')
   old=copy.deepcopy(region['bbox_xyxy'])
   if 'native_bbox_xyxy'in region:
    native=copy.deepcopy(region.pop('native_bbox_xyxy'));require(rid not in native_region_ids and native_to_frame(native,dims,frame)==old,'Already oriented region/native reference mismatch')
    provenance.append({'face':name,'region_id':rid,'operation':'Already oriented survey rectangle retained exactly; auxiliary native rectangle moved to separate provenance to avoid mixed-frame bound checks.','original_native_coordinates':native,'derived_coordinates':old,'derived_coordinate_frame':frame})
   if rid in native_region_ids:
    require(region.get('bbox_frame','NONE')=='NONE','Explicit native survey rectangle required')
    region['bbox_xyxy']=native_to_frame(old,dims,frame);region['bbox_frame']=frame
    provenance.append({'face':name,'region_id':rid,'operation':'Exact native-source rectangle transformed into independently declared raw coordinate frame only.','original_coordinates':old,'original_coordinate_frame':'NONE','derived_coordinates':copy.deepcopy(region['bbox_xyxy']),'derived_coordinate_frame':frame,'source_dimensions':dims})
   else:
    require(region.get('bbox_frame',frame)==frame,'Native region requires explicit reviewed transform');rectangle(region['bbox_xyxy'],frame_dims(frame,dims))
   require(document_name not in document_faces or document_faces[document_name]==name,'One source document cannot silently combine source faces');document_faces[document_name]=name
   per_document.setdefault(document_name,[]).append({'region_id':rid,'role':region['role'],'row_ids':row_ids})
 for document_name,regions in per_document.items():
  raw=raw_documents[document_name];require([r['id']for r in raw['rows']]==[rid for region in regions for rid in region['row_ids']],'Omitted/added/reordered source rows')
 require(set(raw_documents)==set(per_document)and set(seen)==set(original_regions),'Every source document/region must be retained')
 for order_field in ['document_order','raw_documents']:
  if order_field in bindings:require(isinstance(bindings[order_field],list)and list(per_document)==bindings[order_field],'Observed document order differs from frozen '+order_field)
 require(set(profiles)=={'picture','address'}and len(obs['faces'])==2,'Both unique source faces required')
 return {'observations':obs,'region_bindings_by_document':{name:{'card':card,'face':document_faces[name],'regions':regions}for name,regions in per_document.items()},'ordinary_profiles':profiles,'transform_provenance':provenance,'raw_documents_preserved':raw_documents}
