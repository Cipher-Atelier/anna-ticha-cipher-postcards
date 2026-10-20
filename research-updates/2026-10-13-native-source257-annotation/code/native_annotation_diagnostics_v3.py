"""Read-only actual native annotation schema validation.
CLI INPUT OUTPUT [--legacy]. Native required top-level: units, classes, scope,
correlated_partition_and_mark_owner_alternatives, unallocated_marks, source_quality.
Required unit fields and exact types are declared in UNIT_TYPES below. Unknown
cipher role is permitted; physical completeness does not imply cipher membership.
Uses only JSON and standard library; no images or private files required.
"""
import argparse, hashlib, json
from collections import Counter
from pathlib import Path
# Exact own bbox helper extracted from the earlier utility; standalone, no legacy import.
def bbox_errors(box, width=1785, height=1175):
    if not isinstance(box,list) or len(box)!=4 or any(type(v) is not int for v in box):return ['bbox must contain four native integers']
    x0,y0,x1,y1=box; errors=[]
    if x0>=x1 or y0>=y1:errors.append('bbox is reversed or empty; xyxy is half-open')
    if not (0<=x0<=width and 0<=x1<=width and 0<=y0<=height and 0<=y1<=height):errors.append('bbox extends outside native image')
    return errors

UNIT_TYPES={'id':str,'local_order':int,'native_bbox_xyxy_halfopen':list,'bbox_precision_native_pixels':dict,'geometric_features':str,'physical_extent_status':str,'single_cipher_unit_identity':str,'owned_parts':str,'detached_mark_ownership':dict,'exemplar_role':str,'repeated_class_validation':bool,'evidence_views':list,'separator_evidence':dict}
def diagnose_native(d):
    errors=[]
    def error(field,cause):errors.append({'field':field,'cause':cause})
    units=d.get('units');classes=d.get('classes')
    if not isinstance(units,list):error('units','missing or malformed list');units=[]
    if not isinstance(classes,list):error('classes','missing or malformed list');classes=[]
    if not isinstance(d.get('scope'),str):error('scope','missing or malformed scope string')
    for key,typ in [('correlated_partition_and_mark_owner_alternatives',dict),('unallocated_marks',list),('source_quality',list)]:
        if not isinstance(d.get(key),typ):error(key,'missing or malformed '+typ.__name__)
    ids=set();cids=set();unitmap={};classmap={}
    for label,records,seen,lookup in [('units',units,ids,unitmap),('classes',classes,cids,classmap)]:
        for i,r in enumerate(records):
            if not isinstance(r,dict):error(f'{label}[{i}]','record must be object');continue
            ident=r.get('id')
            if not isinstance(ident,str) or not ident:error(f'{label}[{i}].id','missing or invalid ID')
            elif ident in seen:error(f'{label}[{i}].id','duplicate ID')
            else:seen.add(ident);lookup[ident]=r
    for i,u in enumerate(units):
        if not isinstance(u,dict):continue
        path=f'units[{i}]'
        for key,typ in UNIT_TYPES.items():
            if type(u.get(key)) is not typ:error(path+'.'+key,'missing or malformed '+typ.__name__)
        for e in bbox_errors(u.get('native_bbox_xyxy_halfopen')):error(path+'.native_bbox_xyxy_halfopen',e)
        if 'equivalence_class' not in u:error(path+'.equivalence_class','required nullable class reference missing')
        ref=u.get('equivalence_class')
        if ref is not None:
            if not isinstance(ref,str) or ref not in cids:error(path+'.equivalence_class','undefined or malformed class reference')
            elif not isinstance(classmap[ref].get('members'),list):error(path+'.equivalence_class','referenced class members is not a list')
            elif u.get('id') not in classmap[ref]['members']:error(path+'.equivalence_class','class membership not reciprocal')
        # Cipher-unit role UNKNOWN is explicitly valid and never a geometric schema failure.
    for i,c in enumerate(classes):
        if not isinstance(c,dict):continue
        if not isinstance(c.get('role'),str):error(f'classes[{i}].role','missing or malformed role')
        members=c.get('members')
        if not isinstance(members,list):error(f'classes[{i}].members','missing or malformed list');continue
        for member in members:
            if not isinstance(member,str) or member not in ids:error(f'classes[{i}].members','undefined or malformed unit reference')
            elif unitmap[member].get('equivalence_class')!=c.get('id'):error(f'classes[{i}].members','unit class reference not reciprocal')
    def walk(value,path):
        if isinstance(value,dict):
            for key,v in value.items():
                if key in ('bbox','native_bbox_xyxy_halfopen','candidate_internal_boundary_interval_xyxy_halfopen'):
                    for e in bbox_errors(v):error(path+'.'+key,e)
                walk(v,path+'.'+key)
        elif isinstance(value,list):
            for i,v in enumerate(value):walk(v,f'{path}[{i}]')
    # Preserved original reader alternatives use their original namespaces, not canonical unit IDs.
    for key in ('correlated_partition_and_mark_owner_alternatives','unallocated_marks','source_quality'):walk(d.get(key),key)
    roles=Counter(u.get('exemplar_role','MISSING') for u in units if isinstance(u,dict));physical=Counter(u.get('physical_extent_status','MISSING') for u in units if isinstance(u,dict));cipher=Counter(u.get('single_cipher_unit_identity','MISSING') for u in units if isinstance(u,dict))
    return {'schema':'native-annotation-diagnostics-v1','typed_structure_valid':not errors,'errors':errors,'raw_units':len(units),'class_records':len(classes),'role_counts':dict(roles),'physical_extent_counts':dict(physical),'cipher_unit_role_counts':dict(cipher),'positive_whole_singleton_exemplars':roles.get('POSITIVE_WHOLE_GEOMETRY_SINGLETON',0),'unresolved_span_records':roles.get('PROVISIONAL_SPAN',0),'validated_repeated_equivalence_classes':len({u.get('equivalence_class') for u in units if isinstance(u,dict) and u.get('repeated_class_validation') is True and isinstance(u.get('equivalence_class'),str) and u.get('equivalence_class') in cids}),'scope':d.get('scope'),'limits':d.get('limits',[]),'detached_mark_ownership_records':{u['id']:u.get('detached_mark_ownership') for u in units if isinstance(u,dict) and isinstance(u.get('id'),str)},'preserved_correlated_partition_and_mark_owner_alternatives':d.get('correlated_partition_and_mark_owner_alternatives'),'unallocated_marks':d.get('unallocated_marks'),'source_quality':d.get('source_quality'),'scientific_readiness_information':['Cipher-unit role not established by source-only data; UNKNOWN does not invalidate physical annotation schema.','First-band partial scope is not global-card coverage.','Singleton exemplar classes are physical geometry records; no conversion to a cipher alphabet, fixed class count or solver packet.'],'procedure':'No scorer executed. Historical or external certification is not required to annotate physical constructions or execute a future explicit hypothesis.'}
def diagnose_legacy_v2(d):
    issues=[]
    classes=d.get('classes');variants=d.get('variants');common=d.get('common_identity_stable_occurrences')
    if not isinstance(classes,list):issues.append({'field':'classes','cause':'missing or malformed list'})
    elif len(classes)==0:issues.append({'field':'classes','cause':'original empty list gives zero classes; first numeric class-count guard requires 7..27'})
    if not isinstance(variants,list) or not variants:issues.append({'field':'variants','cause':'finite transcription variants UNESTABLISHED; original [] is unavailable, not established zero interpretations'})
    if type(common) is not int:issues.append({'field':'common_identity_stable_occurrences','cause':'raw common field is '+type(common).__name__+' rather than integer','raw_value':common})
    return {'schema':'old-input-diagnosis-v2','numerical_input_issues':issues,'class_count':len(classes) if isinstance(classes,list) else None,'variants_status':'UNESTABLISHED' if variants==[] else 'not inferred','raw_common_field_type':type(common).__name__,'scientific_readiness_information':{'coverage':'whole-card coverage not established; separate from numerical code guards','role':'cipher-unit role not established by source-only data; no external historical authority prerequisite','physical_annotation_permitted':True},'source_integrity':'No corrupt source bytes or decode observed in verified provenance. Input-field issues do not imply bad image.','policy':'No scorer rerun, automatic physical-to-cipher conversion or hidden masking.'}
def main():
    p=argparse.ArgumentParser();p.add_argument('input');p.add_argument('output');p.add_argument('--legacy',action='store_true');a=p.parse_args();raw=Path(a.input).read_bytes();d=json.loads(raw)
    result=diagnose_legacy_v2(d) if a.legacy else diagnose_native(d);result['input_sha256']=hashlib.sha256(raw).hexdigest();Path(a.output).write_text(json.dumps(result,indent=2));print(json.dumps({'output_sha256':hashlib.sha256(Path(a.output).read_bytes()).hexdigest(),'typed_structure_valid':result.get('typed_structure_valid'),'errors':result.get('errors')}))
if __name__=='__main__':main()
