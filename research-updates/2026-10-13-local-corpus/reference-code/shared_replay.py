"""Shared plain port of reviewed native210 a7ae; mapping loop is retained.
Only explicit card/face/frame parameters and output metadata are generalized.
This file is source code reviewed locally, not runtime rewriting of old modules.
"""
import csv,hashlib,io,json
from collections import Counter

def sha_bytes(data):return hashlib.sha256(data).hexdigest()
def json_bytes(data):return (json.dumps(data,ensure_ascii=False,sort_keys=True,indent=2)+'\n').encode('utf-8')

def frame_dimensions(orientation,source_dimensions):
    if orientation in {'NONE','ROTATE_180'}:return list(source_dimensions)
    if orientation in {'CCW90','CW90'}:return list(reversed(source_dimensions))
    raise ValueError('Unreviewed geometric frame: '+str(orientation))

def replay_document(document,key,expected_source,engine,card,face,orientation):
    require=engine.require
    box=engine.box
    unique_id=engine.unique_id
    validate_alternatives=engine.validate_alternatives
    validate_declared_windows=engine.validate_declared_windows
    KNOWN_STATUSES=engine.KNOWN_STATUSES
    UNKNOWN_STATUSES=engine.UNKNOWN_STATUSES
    PUNCTUATION_LITERALS=engine.PUNCTUATION_LITERALS
    require(isinstance(document,dict),'Ledger must be an object; raw schema not reinterpreted')
    require(document.get('card')==card and 'schema' not in document and 'schema_version' not in document,'Expected explicit canonical rows/groups/units schema for approved card')
    require(isinstance(document.get('source'),dict),'Required native source metadata missing')
    metadata={'source':document['source'],'orientation':document.get('orientation'),'oriented_dimensions':document.get('oriented_dimensions'),'schema_notes':['Shared explicit port of reviewed a7ae native210 core; declared geometry only. Raw rows/groups/units and key/status/alternative/punctuation/count rules retained.']}
    source=metadata['source']
    require(source.get('sha256')==expected_source['sha256'],'Ledger/source fingerprint mismatch')
    require(source.get('dimensions')==expected_source['dimensions'],'Ledger/source dimensions mismatch')
    if 'source_url' in source:require(source['source_url']==expected_source['source_url'],'Ledger/source URL mismatch')
    if 'bytes' in source:require(source['bytes']==expected_source['bytes'],'Ledger/source byte count mismatch')
    require(metadata['orientation']==orientation,'Raw orientation differs from independently approved source frame')
    dims=frame_dimensions(orientation,expected_source['dimensions'])
    require(metadata['oriented_dimensions']==dims,'Oriented source dimensions mismatch')
    validate_declared_windows(document,dims)
    overlay_map={}  # Mandatory exact-ID review exclusions are applied afterward to derived tokens.
    rows=document.get('rows')
    require(isinstance(rows,list) and rows,'Ledger requires nonempty rows list')
    seen_rows=set();seen_groups=set();seen_units=set();seen_marks=set()
    records=[];line_outputs=[];groups_summary=[];punctuation_records=[]
    counts=Counter({'representation_slots':0,'provisionally_mapped_slots':0,'masked_representation_slots':0,
                    'emitted_known_letters':0,'capped_ch_slots':0,'recorded_punctuation_marks':0,
                    'uncertain_punctuation_masks':0})
    distinct=set()
    for ri,row in enumerate(rows,1):
        require(isinstance(row,dict),'Row must be an object')
        rid=unique_id(row,seen_rows,'row')
        if 'row_index' in row:require(row['row_index']==ri and type(row['row_index']) is int,f'{rid}: row_index/order mismatch')
        if 'bbox_xyxy' in row:box(row['bbox_xyxy'],dims,rid)
        groups=row.get('groups')
        require(isinstance(groups,list) and groups,f'{rid}: nonempty groups list required')
        row_outputs=[]
        for gi,group in enumerate(groups,1):
            require(isinstance(group,dict),f'{rid}: group must be an object')
            gid=unique_id(group,seen_groups,'group')
            group_box=box(group.get('bbox_xyxy'),dims,gid)
            if 'group_index' in group:require(group['group_index']==gi and type(group['group_index']) is int,f'{gid}: group_index/order mismatch')
            units=group.get('units')
            require(isinstance(units,list) and units,f'{gid}: nonempty units list required')
            outputs=[];unit_ids=[];group_counts=Counter()
            for ui,unit in enumerate(units,1):
                require(isinstance(unit,dict),f'{gid}: unit must be an object')
                uid=unique_id(unit,seen_units,'unit')
                unit_ids.append(uid)
                unit_box=box(unit.get('bbox_xyxy'),dims,uid)
                if 'unit_index' in unit:require(unit['unit_index']==ui and type(unit['unit_index']) is int,f'{uid}: unit_index/order mismatch')
                status=unit.get('status')
                require(isinstance(status,str) and status in KNOWN_STATUSES|UNKNOWN_STATUSES,f'{uid}: unknown status {status!r}')
                alternatives=unit.get('alternatives',[])
                validate_alternatives(alternatives,key,uid)
                cid=unit.get('class_id')
                require(cid is None or (isinstance(cid,str) and cid in key),f'{uid}: unsupported class_id {cid!r}')
                review_masked=uid in overlay_map
                masked=status in UNKNOWN_STATUSES or bool(alternatives) or cid is None or review_masked
                if masked:
                    for field in ('accepted_body_count','mapped_body_count'):
                        require(unit.get(field) is None or unit.get(field)==0,f'{uid}: uncertain span cannot have accepted/physical body count')
                    if status=='unresolved_shape' or review_masked or (status in KNOWN_STATUSES and bool(alternatives)):
                        require(unit.get('physical_body_count') is None or unit.get('physical_body_count')==1,f'{uid}: unresolved shape reader count must be null or1, not an accepted mapping')
                    elif status=='unresolved_span':
                        require(unit.get('physical_body_count') is None,f'{uid}: unresolved span physical_body_count must be null')
                    else:
                        require(unit.get('physical_body_count') is None or unit.get('physical_body_count')==0,f'{uid}: uncertain span cannot have accepted/physical body count')
                    emitted=f'[U:{uid}]'
                else:
                    emitted=key[cid]
                    distinct.add(cid)
                outputs.append(emitted)
                group_counts['representation_slots']+=1
                group_counts['masked_representation_slots' if masked else 'provisionally_mapped_slots']+=1
                if not masked:
                    group_counts['emitted_known_letters']+=len(emitted)
                    group_counts['capped_ch_slots']+=int(cid=='G10_CAP')
                record={'record_type':'unit','row_id':rid,'row_index':ri,'group_id':gid,'group_index':gi,
                    'unit_id':uid,'unit_index':ui,'unit_bbox_xyxy':unit_box,'group_bbox_xyxy':group_box,
                    'row_bbox_xyxy':row.get('bbox_xyxy'),'orientation':orientation,'card_id':card,'face':face,
                    'class_id_recorded':cid,'alternatives_recorded':alternatives,'status_recorded':status,
                    'shape_notes_recorded':unit.get('shape_notes'),'raw_unit_recorded':unit,'emitted':emitted,
                    'representation_slots':1,'provisionally_mapped_slots':0 if masked else 1,
                    'masked_representation_slots':1 if masked else 0,
                    'emitted_known_letters':0 if masked else len(emitted),'physical_body_count':None,
                    'reader_physical_body_count_recorded':unit.get('physical_body_count'),
                    'masked_by_source_review_overlay':review_masked,
                    'source_review_mask_reason':overlay_map[uid]['reason'] if review_masked else None}
                records.append(record)
            # Punctuation is placed only at exact recorded unit boundaries.
            marks=group.get('punctuation',[])
            require(isinstance(marks,list),f'{gid}: punctuation must be a list')
            before={};after={}
            for mark in marks:
                require(isinstance(mark,dict),f'{gid}: malformed punctuation record; no prose inferred')
                mid=unique_id(mark,seen_marks,'punctuation')
                mark_box=box(mark.get('bbox_xyxy'),dims,mid)
                sides=[k for k in ('before_unit_id','after_unit_id') if k in mark]
                require(len(sides)==1,f'{mid}: exactly one recorded unit boundary required')
                side=sides[0]
                target=mark[side]
                require(target in unit_ids,f'{mid}: punctuation target not in group')
                require(mark.get('status') in {'recorded','known','uncertain','unresolved'},f'{mid}: unknown punctuation status')
                literal=mark.get('literal')
                require(literal is None or (isinstance(literal,str) and literal in PUNCTUATION_LITERALS),f'{mid}: unsupported punctuation literal')
                uncertain=mark['status'] in {'uncertain','unresolved'} or literal is None
                rendered=f'[P:{mid}]' if uncertain else literal
                destination=before if side=='before_unit_id' else after
                require(target not in destination,f'{mid}: duplicate punctuation boundary; explicit ordering required')
                destination[target]=rendered
                group_counts['recorded_punctuation_marks']+=1
                group_counts['uncertain_punctuation_masks']+=int(uncertain)
                punctuation_records.append({'row_id':rid,'group_id':gid,'id':mid,'bbox_xyxy':mark_box,
                    'recorded':mark,'emitted':rendered})
            group_text=''.join(before.get(uid,'')+text+after.get(uid,'') for uid,text in zip(unit_ids,outputs))
            row_outputs.append(group_text)
            if group_counts['masked_representation_slots']:
                require(group.get('physical_body_count') is None,f'{gid}: uncertain group physical_body_count must be null')
            groups_summary.append({'row_id':rid,'group_id':gid,'bbox_xyxy':group_box,
                'counts':{k:group_counts[k] for k in counts},'physical_body_count':None})
            counts.update(group_counts)
        line_outputs.append(' '.join(row_outputs))
    if counts['masked_representation_slots']:
        require(document.get('physical_body_count') is None,'Uncertain ledger physical_body_count must be null')
    counts['observed_known_classes']=len(distinct)
    counts['additional_source_review_masks']=len(overlay_map)
    windows=[r['bbox_xyxy'] for r in rows if 'bbox_xyxy' in r]+[g['bbox_xyxy'] for r in rows for g in r['groups']]+[u['bbox_xyxy'] for r in rows for g in r['groups'] for u in g['units']]
    envelope=[min(b[0] for b in windows),min(b[1] for b in windows),max(b[2] for b in windows),max(b[3] for b in windows)]
    original= document.get('full_observed_cipher_block_bbox_xyxy') or document.get('metadata',{}).get('full_observed_cipherblock_bbox_xyxy')
    warnings=[]
    if original and not (original[0]<=envelope[0] and original[1]<=envelope[1] and original[2]>=envelope[2] and original[3]>=envelope[3]):
        warnings.append('Raw outer cipher locator does not enclose every recorded row/group/unit window. Derived union is a recorded-window envelope, not an exact source-ink boundary; raw coordinates are preserved.')
    return {'literal_lines':'\n'.join(line_outputs)+'\n','tokens':records,'counts':dict(counts),
        'groups':groups_summary,'punctuation':punctuation_records,'row_count':len(rows),
        'row_source_metadata_recorded':[{k:v for k,v in row.items() if k!='groups'} for row in rows],'orientation':orientation,'oriented_dimensions':dims,'card_id':card,'face':face,'group_count':len(groups_summary),'physical_body_count':None,'schema_notes':metadata['schema_notes'],
        'raw_outer_cipher_locator_xyxy':original,'recorded_cipher_window_union_xyxy':envelope,'outer_locator_warnings':warnings}


def package_bytes(replay,hashes,source):
    fields=['record_type','card_id','face','region_id','row_id','row_index','group_id','group_index','unit_id','unit_index',
            'unit_bbox_xyxy','group_bbox_xyxy','row_bbox_xyxy','orientation','class_id_recorded',
            'alternatives_recorded','status_recorded','shape_notes_recorded','raw_unit_recorded','emitted',
            'representation_slots','provisionally_mapped_slots','masked_representation_slots',
            'emitted_known_letters','physical_body_count','reader_physical_body_count_recorded','masked_by_source_review_overlay','source_review_mask_reason']
    fh=io.StringIO(newline='')
    writer=csv.DictWriter(fh,fieldnames=fields,lineterminator='\n')
    writer.writeheader()
    for token in replay['tokens']:
        writer.writerow({k:json.dumps(v,ensure_ascii=False,sort_keys=True,separators=(',',':')) if isinstance(v,(list,dict)) else '' if v is None else v for k,v in token.items()})
    csv_bytes=fh.getvalue().encode('utf-8')
    literal_bytes=replay['literal_lines'].encode('utf-8')
    receipt={'status':'replayed_saved_proposal','input_hashes':hashes,'source':source,
      'orientation':replay['orientation'],'card_id':replay['card_id'],'face':replay['face'],'oriented_dimensions':replay['oriented_dimensions'],
      'counts':replay['counts'],'row_count':replay['row_count'],'group_count':replay['group_count'],
      'groups':replay['groups'],'recorded_punctuation':replay['punctuation'],'physical_body_count':None,
      'raw_schema_adaptation':replay['schema_notes'],
      'raw_outer_cipher_locator_xyxy':replay['raw_outer_cipher_locator_xyxy'],
      'recorded_cipher_window_union_xyxy':replay['recorded_cipher_window_union_xyxy'],
      'outer_locator_warnings':replay['outer_locator_warnings'],
      'raw_baseline_counts':replay.get('raw_baseline_counts',replay['counts']),
      'raw_baseline_limit':'Mechanical projection of frozen raw labels only; source review masks supersede affected mapping eligibility. No source-validity certification.',
      'outputs_sha256':{'tokens.csv':sha_bytes(csv_bytes),'literal-lines.txt':sha_bytes(literal_bytes)},
      'coordinate_units':'Native pixels in the declared oriented image, integer xyxy half-open. Boxes are saved inspection windows, not measured physical outlines.',
      'ordering':'Preserved frozen rows, groups and units in list order; group whitespace is an explicit display convention, not inferred source word segmentation.',
      'key_scope':'Unchanged 24-class primary mapping only. No secondary mark transformations or language-driven repairs.',
      'mask_policy':'Any uncertainty status, any retained class alternatives, or missing class ID yields [U:unitID]. One span is one representation slot; no physical glyph count is assigned. Candidate classes remain recorded without preference.',
      'source_face_scope':'Only this explicitly supplied frozen face ledger is replayed; complete both-face survey is validated by the manifest runner. No diplomatic-to-ledger reconstruction.',
      'limits':['Outputs reproduce proposed source coding, not visual truth, calibrated accuracy or a complete decipherment.',
        'Source hash and native dimensions establish byte/bounds consistency only. Uncertain source coding, shapes and segmentation remain.',
        'No complete physical-body count, key upgrade, mask resolution, postal-date upgrade or historical certification is claimed.']}
    return {'tokens.csv':csv_bytes,'literal-lines.txt':literal_bytes,'replay-receipt.json':json_bytes(receipt)}

