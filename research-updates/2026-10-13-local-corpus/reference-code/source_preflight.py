"""Source structure validation only: no key values, decoding or emitted text."""
import hashlib,json
from pathlib import Path
import shared_replay as core
ATLAS_PATH='card330-local-source/reader-a/atlas-class-only.json'
ATLAS_SHA='4073dedf037195260165a77023948d3d01f62addc11a164a2fe268f1e608c0c3'

def class_identifiers(task):
    data=(Path(task)/ATLAS_PATH).read_bytes()
    if hashlib.sha256(data).hexdigest()!=ATLAS_SHA:raise ValueError('Neutral class-only atlas fingerprint mismatch')
    entries=json.loads(data);ids=[e['class_id'] for e in entries]
    if len(ids)!=24 or len(set(ids))!=24:raise ValueError('Frozen neutral class identifier set mismatch')
    return frozenset(ids)

def validate_document(document,source,engine,card,orientation,classes,global_ids):
    """Mirror retained core guards without looking up a class literal value."""
    require=engine.require;box=engine.box;unique=engine.unique_id
    require(isinstance(document,dict),'Ledger must be an object; raw schema not reinterpreted')
    require(document.get('card')==card and 'schema'not in document and 'schema_version'not in document,'Expected explicit canonical rows/groups/units schema for approved card')
    require(isinstance(document.get('source'),dict),'Required native source metadata missing')
    if 'metadata'in document:require(isinstance(document['metadata'],dict),'Optional ledger metadata must be an object')
    recorded=document['source']
    for field in ('sha256','dimensions'):require(recorded.get(field)==source[field],'Ledger/source '+field+' mismatch')
    for field in ('bytes','source_url'):
        if field in recorded:require(recorded[field]==source[field],'Ledger/source '+field+' mismatch')
    require(document.get('orientation')==orientation,'Raw orientation differs from independently approved source frame')
    dims=core.frame_dimensions(orientation,source['dimensions'])
    require(document.get('oriented_dimensions')==dims,'Oriented source dimensions mismatch')
    engine.validate_declared_windows(document,dims)
    rows=document.get('rows');require(isinstance(rows,list)and rows,'Ledger requires nonempty rows list')
    seen={name:set()for name in ('row','group','unit','punctuation')};units={};masked_document=False
    def ident(record,kind):
        value=unique(record,seen[kind],kind)
        require(value not in global_ids[kind],'Cross-document '+kind+' identity collision: '+value)
        global_ids[kind].add(value);return value
    for ri,row in enumerate(rows,1):
        require(isinstance(row,dict),'Row must be an object');rid=ident(row,'row');box(row.get('bbox_xyxy'),dims,rid)
        if 'row_index'in row:require(type(row['row_index'])is int and row['row_index']==ri,rid+': row_index/order mismatch')
        groups=row.get('groups');require(isinstance(groups,list)and groups,rid+': nonempty groups list required')
        for gi,group in enumerate(groups,1):
            require(isinstance(group,dict),rid+': group must be an object');gid=ident(group,'group');box(group.get('bbox_xyxy'),dims,gid)
            if 'group_index'in group:require(type(group['group_index'])is int and group['group_index']==gi,gid+': group_index/order mismatch')
            entries=group.get('units');require(isinstance(entries,list)and entries,gid+': nonempty units list required');group_ids=[];masked_group=False
            for ui,unit in enumerate(entries,1):
                require(isinstance(unit,dict),gid+': unit must be an object');uid=ident(unit,'unit');units[uid]=unit;group_ids.append(uid);box(unit.get('bbox_xyxy'),dims,uid)
                if 'unit_index'in unit:require(type(unit['unit_index'])is int and unit['unit_index']==ui,uid+': unit_index/order mismatch')
                status=unit.get('status');require(isinstance(status,str)and status in engine.KNOWN_STATUSES|engine.UNKNOWN_STATUSES,uid+': unknown status')
                alternatives=unit.get('alternatives',[]);engine.validate_alternatives(alternatives,classes,uid)
                cid=unit.get('class_id');require(cid is None or isinstance(cid,str)and cid in classes,uid+': unsupported class_id')
                masked=status in engine.UNKNOWN_STATUSES or bool(alternatives)or cid is None
                if masked:
                    for field in ('accepted_body_count','mapped_body_count'):require(unit.get(field)is None or unit.get(field)==0,uid+': uncertain span cannot have accepted/physical body count')
                    if status=='unresolved_shape'or status in engine.KNOWN_STATUSES and bool(alternatives):require(unit.get('physical_body_count')is None or unit.get('physical_body_count')==1,uid+': unresolved shape reader count must be null or1, not an accepted mapping')
                    elif status=='unresolved_span':require(unit.get('physical_body_count')is None,uid+': unresolved span physical_body_count must be null')
                    else:require(unit.get('physical_body_count')is None or unit.get('physical_body_count')==0,uid+': uncertain span cannot have accepted/physical body count')
                masked_group|=masked
            marks=group.get('punctuation',[]);require(isinstance(marks,list),gid+': punctuation must be a list');boundaries=set()
            for mark in marks:
                require(isinstance(mark,dict),gid+': malformed punctuation record; no prose inferred');mid=ident(mark,'punctuation');box(mark.get('bbox_xyxy'),dims,mid)
                sides=[k for k in ('before_unit_id','after_unit_id')if k in mark];require(len(sides)==1,mid+': exactly one recorded unit boundary required')
                side=sides[0];target=mark[side];require(target in group_ids,mid+': punctuation target not in group')
                require(mark.get('status')in {'recorded','known','uncertain','unresolved'},mid+': unknown punctuation status')
                value=mark.get('literal');require(value is None or isinstance(value,str)and value in engine.PUNCTUATION_LITERALS,mid+': unsupported punctuation literal')
                require((side,target)not in boundaries,mid+': duplicate punctuation boundary; explicit ordering required');boundaries.add((side,target))
            if masked_group:require(group.get('physical_body_count')is None,gid+': uncertain group physical_body_count must be null')
            masked_document|=masked_group
    if masked_document:require(document.get('physical_body_count')is None,'Uncertain ledger physical_body_count must be null')
    return units
