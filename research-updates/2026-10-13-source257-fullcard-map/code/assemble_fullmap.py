#!/usr/bin/env python3
"""Assemble source-inspected manual decisions; no shape matching or decoding.

CLI: assemble_fullmap.py RESULTS_DIRECTORY FROZEN_FILE
Inputs are pinned immutable annotations. Numeric intersection below retrieves
context only, never establishes physical identity, ownership, or similarity.
The explicit decision tables are the adjudicator's native visual ledger.
"""
import argparse
import copy
import hashlib
import json
from collections import Counter
from pathlib import Path

WHOLE = 'VISUALLY_BOUNDED_WHOLE_PHYSICAL_CONSTRUCTION'
UNRESOLVED = 'UNRESOLVED_SPAN'
PINS = {
    'right-A-v2.json': '51aebbb7b0f9f9f5032d5934acb9628736efd698eac88b22a421a76231b61481',
    'right-B-v1.json': '8fd0a16cded0e0b12b539bb1c7f675bdcf08e815c509fc95feb89a19ec82b3eb',
    'bottom-A-v1.json': 'aacf3ab359fad1b1e8f83710ebd3ccdafd43a7cf684eb82fc318002b42e75b47',
    'bottom-B-v1.json': '1a2ff9d5320dd8329e405ac8f4f31c063b41bb8f9283442a5920d91a00fb49ee',
}
SOURCE_SHA = '7407bb54bcfbf69af61d801fb04a0b4de8fce9d8c24976ba1a3f4c3f2120aae4'
FROZEN_SHA = 'bdb98089160dea39306bdce159c0d9bed88fc6eab7f75aaf7bc6a25ed2cd9c91'

# A range, B range, decision. S=bounded unresolved span. B ranges are an
# explicit visual correspondence ledger, not nearest-box identity matching.
RIGHT = [
 (1,5,1,5,'parallel'), (6,6,6,6,'S'), (7,11,7,11,'parallel'),
 (12,14,12,14,'S'), (15,18,15,18,'parallel'), (19,22,19,21,'S'),
 (23,24,22,23,'parallel'), (25,25,24,25,'S'), (26,26,26,26,'S'),
 (27,35,27,35,'parallel'), (36,36,36,36,'S'), (37,40,37,39,'S'),
 (41,45,40,44,'parallel'), (46,46,45,46,'S'), (47,48,47,48,'parallel'),
 (49,49,49,49,'S'), (50,54,50,54,'parallel'), (55,56,55,55,'S'),
 (57,60,56,59,'parallel'), (61,61,60,60,'S'), (62,64,61,62,'S'),
 (65,71,63,69,'parallel'), (72,74,70,70,'S'), (75,78,71,74,'parallel'),
 (79,83,75,79,'parallel'), (84,84,80,81,'S'), (85,85,82,82,'S'),
 (86,87,83,84,'S'), (88,96,85,93,'parallel'), (97,97,0,0,'S'),
 (98,100,94,95,'S'), (101,106,96,101,'parallel'), (107,107,102,102,'S'),
 (108,112,103,107,'parallel'), (113,113,108,108,'S'),
 (114,121,109,116,'parallel'), (122,122,117,117,'S'),
 (123,126,118,121,'parallel'), (127,130,122,126,'S'), (131,131,127,128,'S'),
 (132,132,129,130,'S'), (133,136,131,134,'parallel'), (137,137,135,135,'S'),
 (138,148,136,146,'parallel'), (149,152,147,151,'S'),
 (153,156,152,154,'S'), (157,160,155,158,'S'), (161,161,0,0,'S'),
 (162,163,159,160,'S'), (164,164,161,161,'S'), (165,165,162,162,'S'),
 (166,166,163,163,'S'), (167,169,165,167,'parallel'),
 (170,170,168,168,'S'), (171,171,169,169,'S'),
]

# Bottom decisions preserve granular A as alternative partitions. Whole runs
# were individually reinspected in the native tiles. Remaining ranges are
# explicitly bounded envelopes with unresolved internal count/joins; they
# are not assertions that a whole coarse B interval is a single glyph.
BOTTOM = [
 (1,7,'whole'), (8,15,'S'), (16,16,'whole'), (17,21,'S'),
 (22,22,'whole'), (23,29,'S'), (30,34,'S'), (35,39,'S'),
 (40,40,'whole'), (41,46,'S'), (47,52,'S'),
 (53,60,'whole'), (61,62,'S'), (63,65,'S'), (66,66,'whole'),
 (67,68,'S'), (69,76,'S'), (77,78,'S'), (79,83,'S'),
 (84,90,'S'), (91,96,'S'), (97,102,'S'),
 (103,104,'whole'), (105,106,'S'), (107,108,'whole'), (109,117,'S'),
 (118,127,'S'), (128,133,'S'), (134,144,'S'), (145,151,'S'), (152,156,'S'),
 (157,165,'whole'), (166,167,'S'), (168,173,'S'), (174,175,'S'),
 (176,181,'S'), (182,187,'S'), (188,190,'S'), (191,196,'S'),
 (197,201,'S'), (202,208,'S'),
 (209,215,'whole'), (216,223,'S'), (224,230,'S'), (231,239,'S'),
 (240,248,'S'), (249,258,'S'), (259,265,'S'), (266,266,'S'),
]

def digest(p):
    return hashlib.sha256(p.read_bytes()).hexdigest()

def union(boxes):
    return [min(b[0] for b in boxes), min(b[1] for b in boxes),
            max(b[2] for b in boxes), max(b[3] for b in boxes)]

def intersects(a,b):
    return max(a[0],b[0]) < min(a[2],b[2]) and max(a[1],b[1]) < min(a[3],b[3])

def dump(path,obj):
    path.write_text(json.dumps(obj,ensure_ascii=False,indent=2)+'\n')

def main():
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument('results_directory',type=Path)
    parser.add_argument('frozen_file',type=Path)
    args=parser.parse_args(); d=args.results_directory
    raw={}
    for name,pin in PINS.items():
        assert digest(d/name)==pin, name
        raw[name]=json.loads((d/name).read_text())
    assert digest(args.frozen_file)==FROZEN_SHA
    frozen=json.loads(args.frozen_file.read_text())
    ra={i+1:u for i,u in enumerate(raw['right-A-v2.json']['units'])}
    rb={i+1:u for i,u in enumerate(raw['right-B-v1.json']['units'])}
    ba={i+1:u for i,u in enumerate(raw['bottom-A-v1.json']['units'])}
    bb=raw['bottom-B-v1.json']['units']
    units=[]; ledger=[]; rawlinks=[]

    def add(box,status,features,amb,views,region,refs,decision):
        uid=f'FC{len(units)+1:03d}'
        overlap=[u['id'] for u in frozen['units'] if intersects(box,u['native_bbox_xyxy_halfopen'])]
        if overlap:
            status=UNRESOLVED
            amb=list(amb)+['Frozen-band box intersection is a same-instance/cross-row ownership candidate; no distinct repeat occurrence is certified.']
        record={'id':uid,'native_bbox_xyxy_halfopen':box,'physical_extent_status':status,
            'cipher_role':'UNKNOWN','geometric_features':features,'ambiguities':amb,
            'evidence_views':sorted(set(views)), 'region':region,'order':len(units)+1,
            'overlap_with_frozen_ids':overlap,'raw_refs':refs,
            'bbox_precision_native_pixels':{'approximate_plus_minus':4,'exact_ink_mask':False},
            'inspection_decision':decision,'source_file_sha256':SOURCE_SHA}
        units.append(record)
        ledger.append({'canonical_id':uid,'decision':decision,'raw_refs':refs,
                       'status':status,'native_bbox_xyxy_halfopen':box})
        for ref in refs:rawlinks.append({'raw_ref':ref,'canonical_id':uid,'relation':'DECISION_SCOPE; see ledger. Context intersections do not assert identity.'})
        return record

    covered_ra=[]
    for a0,a1,b0,b1,decision in RIGHT:
        aa=list(range(a0,a1+1)); bs=list(range(b0,b1+1)) if b0 else []
        covered_ra+=aa
        pairs=list(zip(aa,bs)) if decision=='parallel' else [(aa,bs)]
        if decision=='parallel': assert len(aa)==len(bs)
        for ais,bis in pairs:
            ais=[ais] if isinstance(ais,int) else ais
            bis=[bis] if isinstance(bis,int) else bis
            au=[ra[i] for i in ais]; bu=[rb[i] for i in bis]
            boxes=[u['native_bbox_half_open'] for u in au]+[u['bbox_native'] for u in bu]
            features=' / '.join(u['structural_features']['description_in_cw_orientation'] for u in au)
            amb=[v for u in au for v in u['partition_or_mark_owner_alternatives']]
            amb += [v for u in bu for v in u['partition_uncertainty']]
            refs=[f'right-A-v2.json:{u["unit_id"]}' for u in au]+[f'right-B-v1.json:{u["id"]}' for u in bu]
            views=[v for u in au for v in u['evidence_view_ids']]+[v for u in bu for v in u['evidence_view_ids']]
            status=WHOLE if decision=='parallel' else UNRESOLVED
            if status==UNRESOLVED:
                amb.append('A/B joins, partitions, isolated-mark ownership, or body boundary remain unresolved on native reinspection; no fixed internal construction count.')
            if 113 in ais:
                boxes.append(rb[170]['bbox_native']);refs.append('right-B-v1.json:RB170')
                amb.append('Detached low dot/dash near curled descent retained in the same unresolved scope; ownership not assigned.')
            add(union(boxes),status,features,amb,views,'right-'+au[0]['row_id'],refs,
                'Native full/three overlapping 90CW tiles reinspected. '+('Both partitions identify a visibly separable body; envelope union is tolerance/context, not similarity evidence.' if status==WHOLE else 'Manual crowded/mark envelope; finer alternative partitions retained.'))
    assert sorted(covered_ra)==list(range(1,172))
    add(rb[164]['bbox_native'],UNRESOLVED,rb[164]['geometric_features'],
        ['Small dot after crossed date-like cluster omitted as a standalone A record; owner/function unknown.'],
        rb[164]['evidence_view_ids'],'right-R7-date-like',['right-B-v1.json:RB164'],
        'Own native view confirms a bounded detached low dot; no numeral, punctuation, or cipher role assigned.')

    # Reuse an existing unresolved scope for RAM inventory marks whenever the
    # original A author already included that same ink in the described span.
    ram_targets={'RAM01':'RA046','RAM02':'RA061','RAM03':'RA097','RAM04':'RA122',
                 'RAM05':'RA131','RAM06':'RA137','RAM07':'RA107'}
    for mark in raw['right-A-v2.json']['unallocated_or_alternative_owner_marks']:
        target=next(u for u in units if f'right-A-v2.json:{ram_targets[mark["mark_id"]]}' in u['raw_refs'])
        target['native_bbox_xyxy_halfopen']=union([target['native_bbox_xyxy_halfopen'],mark['native_bbox_half_open']])
        target['ambiguities'].append({'retained_mark':mark['mark_id'],'owner_alternatives':mark['owner_alternatives']})
        target['raw_refs'].append('right-A-v2.json:'+mark['mark_id'])

    covered_ba=[]
    for a0,a1,decision in BOTTOM:
        covered_ba+=list(range(a0,a1+1))
        chunks=[[i] for i in range(a0,a1+1)] if decision=='whole' else [list(range(a0,a1+1))]
        for chunk in chunks:
            au=[ba[i] for i in chunk]; box=union([u['native_bbox_xyxy_halfopen'] for u in au])
            row=au[0]['physical_row_or_region']; assert all(u['physical_row_or_region']==row for u in au)
            # Mechanical context lookup only. All raw B records are also
            # retained in full in the evidence artifact for audit.
            ctx=[u for u in bb if u['physical_row']==row.replace('B','R') and intersects(box,u['native_bbox_xyxy_halfopen'])]
            refs=[f'bottom-A-v1.json:{u["id"]}' for u in au]+[f'bottom-B-v1.json:{u["id"]}' for u in ctx]
            amb=[]
            if decision!='whole':
                amb=['Internal body count, joins, faint closures, and/or detached return ownership unresolved; A finer partition and B broader partition remain alternatives.']
                amb += [{'raw_id':u['id'],'partition_alternatives':u['partition_alternatives']} for u in au if u['physical_extent_status']=='UNRESOLVED_SPAN']
            else:
                amb=['Cipher function and alphabet identity unknown. Detached flecks excluded from body description and not allocated by proximity.']
            views=[v+'.png' if not v.endswith('.png') else v for u in au for v in u['evidence_view_ids']]
            add(box,WHOLE if decision=='whole' else UNRESOLVED,
                ' / '.join(u['geometric_features'] for u in au),amb,views,'bottom-'+row,refs,
                'Native original/context and relevant exact column tiles reinspected. '+('Visible body and continuous return bounded individually; B contextual coarse spans do not determine count.' if decision=='whole' else 'Explicit conservative envelope for remaining A/B partition disagreements; no automatic equivalence or fixed glyph count.'))
    assert sorted(covered_ba)==list(range(1,267))
    add([903,887,1011,944],UNRESOLVED,
        'Low pale/short strokes followed by raised stem, lower curls, and a descending return in the B2 interval absent from finer A unit list.',
        ['A has no unit between BA029 and BA030. B maps only part as BB015/BB016; full interval includes ambiguous weak strokes/background. Internal partition and exact ink ownership unestablished.'],
        ['pc_hcp_257_pic.JPG','bottom-context-native.png','bottom-r1-c3-native.png','bottom-r1-c4-native.png','bottom-r2-c3-native.png','bottom-r2-c4-native.png'],
        'bottom-B2',['bottom-B-v1.json:BB015','bottom-B-v1.json:BB016'],
        'Own large-gap reinspection adds unresolved ink-bearing interval; no expectation-based filling.')

    # Additional short intervals exposed by comparing physical path coverage,
    # not by requiring an expected glyph inventory. They were rechecked in
    # the already verified native tiles: weak stroke endpoints/body division
    # cannot be settled consistently between A and B. These residual scopes
    # are not established extra constructions or repeated instances.
    residuals=[
      ('B2',[225,882,246,917],['BB002']),
      ('B2',[1478,910,1500,950],['BB024']),
      ('B4',[1345,996,1365,1042],['BB083']),
      ('B5',[881,1049,907,1095],['BB108']),
      ('B5',[1066,1025,1095,1098],['BB111']),
      ('B5',[1180,1049,1201,1110],['BB113']),
      ('B5',[1380,1040,1392,1113],['BB117']),
      ('B6',[515,1090,542,1128],['BB132']),
      ('B6',[733,1080,749,1133],['BB136']),
      ('B6',[978,1095,995,1134],['BB141']),
      ('B6',[1220,1097,1238,1134],['BB145']),
    ]
    for row,box,brefs in residuals:
        add(box,UNRESOLVED,'Weak/local stroke residue or neighboring-body endpoint in an A inter-envelope interval; B proposes ink-bearing extent here.',
            ['Native reinspection does not certify a separate whole body. Endpoint ownership, pale stroke/background distinction, and count remain unresolved.',
             'Cross-reference to neighboring mapped row spans; this is a residual overlay, not an independent repeat occurrence.'],
            ['pc_hcp_257_pic.JPG','bottom-context-native.png']+
            [f'bottom-r{r}-c{c}-native.png' for r in range(1,5) for c in range(1,7)
             if intersects(box,([65,345,625,905,1185,1380][c-1],[810,850,935,1020][r-1],
                               [395,675,955,1235,1515,1710][c-1],[930,970,1060,1140][r-1]))],
            'bottom-'+row,['bottom-B-v1.json:'+b for b in brefs],
            'Explicit native path-gap reinspection; preserve uncertain residue rather than infer a missing glyph.')

    # Conspicuous unallocated marks are bounded separately and explicitly
    # excluded from independent-repeat counts. An envelope touching a body
    # does not claim a distinct occurrence; possible owners remain raw refs.
    for m in raw['bottom-A-v1.json']['unallocated_marks']:
        add(m['native_bbox_xyxy_halfopen'],UNRESOLVED,m['physical_features'],
            [m['ownership_alternatives'],{'possible_body_owners':m['possible_body_owners'],'frozen_overlap_refs':m['frozen_overlap_refs']},
             'Same-ink/owner overlay, not an established additional construction or repeat occurrence.'],
            [v+'.png' for v in m['evidence_view_ids']],'bottom-unallocated-marks',['bottom-A-v1.json:'+m['id']],
            'Own native reinspection retains conspicuous mark without assigning owner or function.')

    # B's detached inventory sometimes describes already bounded body ink,
    # sometimes a separate uncertain residue. This explicit ledger records
    # the adjudication without treating intersecting boxes as identity.
    bmark_policy={
      'BB155':('scope','BA008','Within unresolved crossing/slash scope; no extra occurrence.'),
      'BB156':('scope','BA010','Within unresolved upper-loop and low-return scope; no extra occurrence.'),
      'BB157':('scope','BA012','Falling-stroke fragment in frozen/lower-row crossing scope; no extra occurrence.'),
      'BB158':('new',None,'Upper forked mark may belong to frozen U017 or lower bowl; owner unresolved.'),
      'BB159':('scope','BA029','Low flecks fall within unresolved B2 end/gap scope; no extra occurrence.'),
      'BB160':('scope','BA039','Lower curled fragment in unresolved local upper-cap/return scope; no extra occurrence.'),
      'BB161':('scope','BA062','Same visible detached falling stem retained within unresolved B3 scope; no extra occurrence.'),
      'BB162':('mark','BAM005','Same visible low dot; A/B envelopes differ within local extent.'),
      'BB163':('scope','BA077','Terminal darkening inside long returned stem scope; distinct mark not certified.'),
      'BB164':('scope','BA139','Small low darkening at neighboring curved return; no independent owner certified.'),
      'BB165':('mark','BAM006','Same isolated terminal point; union retains differing approximate envelopes.'),
      'BB166':('mark','BAM007','Low point before tall stem: envelope disagreement retained, no double count.'),
      'BB167':('new',None,'A and B place low points at materially different x positions; this local dark residue may be preceding-body endpoint. No same-mark identity forced.'),
      'BB168':('scope','BA208','Fine right terminal already included in unresolved last-body envelope; no extra occurrence.'),
      'BB169':('scope','BA237','Low endpoint/short trail inside unresolved final-row scope; no distinct mark certified.'),
      'BB170':('new',None,'Two fine terminal strokes beside final-row gap; body endpoint versus detached mark unresolved.'),
      'BB171':('frozen','U008','Fine extension beside frozen U008: possible same occurrence, terminal/adjacent falling-slash ownership unresolved; preserve frozen bytes.'),
    }
    frozen_links=[]
    for m in bb[154:]:
        action,target,detail=bmark_policy[m['id']]
        if action=='frozen':
            frozen_links.append({'raw_ref':'bottom-B-v1.json:'+m['id'],'frozen_ids':[target],
                'native_bbox_xyxy_halfopen':m['native_bbox_xyxy_halfopen'],'relation':detail})
            continue
        if action in ('scope','mark'):
            ref=('bottom-A-v1.json:'+target)
            dest=next(u for u in units if ref in u['raw_refs'])
            # This is an explicit manually selected same-scope ledger entry.
            dest['native_bbox_xyxy_halfopen']=union([dest['native_bbox_xyxy_halfopen'],m['native_bbox_xyxy_halfopen']])
            dest['physical_extent_status']=UNRESOLVED
            dest['raw_refs'].append('bottom-B-v1.json:'+m['id']);dest['ambiguities'].append(detail)
        else:
            add(m['native_bbox_xyxy_halfopen'],UNRESOLVED,m['visual_structure'],[detail,
                'Unresolved mark overlay; not an additional established physical construction.'],m['native_views_inspected'],
                'bottom-unallocated-marks',['bottom-B-v1.json:'+m['id']],detail)

    add([565,25,577,52],UNRESOLVED,'Thin oblique red trace in external upper white margin, ending near card edge.',
        ['Manual ink versus other trace unknown; textual status and cipher role unknown. No additional coherent writing is visible in adjoining reserve.'],
        ['pc_hcp_257_pic.JPG','right-A-toptrace-native.png'],'outer-top-red-trace',[],
        'Original and exact native upper-margin cut reinspected; preserved as unresolved trace.')

    for region in dict.fromkeys(u['region'] for u in units):
        local=sorted([u for u in units if u['region']==region],key=lambda u:
            (855-u['native_bbox_xyxy_halfopen'][3]) if region.startswith('right-') else u['native_bbox_xyxy_halfopen'][0])
        for order,u in enumerate(local,1):u['order']=order

    # Recompute conservative frozen intersections after explicit envelope
    # extensions; these remain candidates, not identity assignments.
    conflicts=[]
    for u in units:
        u['overlap_with_frozen_ids']=[f['id'] for f in frozen['units'] if intersects(u['native_bbox_xyxy_halfopen'],f['native_bbox_xyxy_halfopen'])]
        if u['overlap_with_frozen_ids']:
            u['physical_extent_status']=UNRESOLVED
            conflicts.append({'frozen_ids':u['overlap_with_frozen_ids'],
                'native_bbox_xyxy_halfopen':u['native_bbox_xyxy_halfopen'],
                'detail':f'{u["id"]}: frozen/lower-row ink ownership or same-instance relation unresolved; envelope intersection alone is not a contradiction or identity. Exclude affected frozen records from later grouping until adjudicated.'})
    conflicts += [{'frozen_ids':l['frozen_ids'],'native_bbox_xyxy_halfopen':l['native_bbox_xyxy_halfopen'],
                   'detail':l['relation']} for l in frozen_links]

    coverage=[
      {'id':'full-original-context','bbox':[0,0,1785,1175],'state':'INSPECTED_NATIVE_ORIGINAL','detail':'Whole original viewed at original detail after byte/RGB verification; supports reserve inventory, not pixel-exhaustive ink segmentation.'},
      {'id':'frozen-first-band','bbox':[180,825,1650,920],'state':'FROZEN_UNCHANGED_WITH_OVERLAY_CONFLICTS','detail':'All 56 original records and uncertainties exact deep copies; entire original file retained bytewise by reference.'},
      {'id':'right-all-seven-trajectories','bbox':[1330,50,1711,855],'state':'MAPPED_WHOLE_BODIES_AND_UNRESOLVED_SPANS','detail':'Six upright physical trajectories in exact 90CW view plus date-like cluster. Native and three exact overlapping CW tiles inspected.'},
      {'id':'bottom-all-five-new-trajectories','bbox':[65,810,1710,1140],'state':'MAPPED_WHOLE_BODIES_AND_UNRESOLVED_SPANS','detail':'All 24 exact native tiles inspected. Large disagreements retained as conservative local spans with complete finer A alternatives and B context in evidence.'},
      {'id':'right-bottom-junction','bbox':[1330,810,1705,855],'state':'INSPECTED_CROSS_SECTOR_DUPLICATE_AUDIT','detail':'Right row starts enter this context. Bottom A/B new physical rows begin below y869. No duplicate new lower-row occurrence established in this junction; incidental right ink in bottom context is referenced to right units, not counted anew.'},
      {'id':'date-edge','bbox':[1615,560,1730,635],'state':'EXACT_EXTRA_NATIVE_REINSPECTION','detail':'Extra exact native pixels recover original ROI clip. Separator shaft reaches card edge near x1705–1707; no dark continuation in external white; intended endpoint versus physical truncation remains unresolved.'},
      {'id':'photo-and-watermark-reserve','bbox':[65,55,1330,810],'state':'INSPECTED_NO_ADDITIONAL_COHERENT_MANUSCRIPT','detail':'Printed photograph, grain, scratches/discoloration and translucent circular watermark inspected in original context; no further coherent manuscript trajectory identified. Printed/watermark forms are not manual signs.'},
      {'id':'left-card-reserve','bbox':[0,55,95,1140],'state':'INSPECTED_NO_ADDITIONAL_COHERENT_MANUSCRIPT','detail':'Card/background edge, photo texture and damage; no additional coherent writing.'},
      {'id':'upper-reserve','bbox':[0,0,1785,55],'state':'INSPECTED_WITH_UNRESOLVED_RED_TRACE','detail':'External pale margin and upper card edge; thin red trace separately mapped; other tiny marks not certified manuscript.'},
      {'id':'right-external-reserve','bbox':[1705,55,1785,1140],'state':'INSPECTED_NO_ADDITIONAL_COHERENT_MANUSCRIPT','detail':'Pale external margin/card boundary, date-edge endpoint locally unresolved; no additional coherent manuscript.'},
      {'id':'lower-external-reserve','bbox':[0,1140,1785,1175],'state':'INSPECTED_NO_ADDITIONAL_COHERENT_MANUSCRIPT','detail':'Lower card/external border and image background; no further coherent manuscript.'},
    ]
    quality=[
      {'region':'whole original','limit':'No global bad-scan declaration: source pixels support many physical observations. Approximate envelopes ±4 pixels are not traced masks or exhaustive ink/background certificates.'},
      {'region':'crowded local joins','limit':'Crossings, long returns, detached marks and A/B positional/partition differences remain local unresolved spans; accepted whole body is a physical observation, never a cipher unit or alphabet identity.'},
      {'region':'printed/watermark crossings','limit':'Faint closure and manual ink/background distinction limited in some lower rows. No rescale, filter, enhancement, OCR, or other-image comparison used.'},
      {'region':'date-like cluster','limit':'Numeral-like arrangement is contextual only; no letters/numerals transcribed and no physical punctuation/date function assigned. Card-edge endpoint ambiguous after initial ROI clipping was fixed.'},
      {'region':'counts','limit':'Record IDs and counts are annotation partitions, not proven physical glyph totals. Mark overlays and frozen overlaps do not establish additional repeat instances. Reproducibility does not establish visual similarity or historical truth.'},
    ]
    full={'schema':'source257-fullcard-physical-map-v1','source':{'file_sha256':SOURCE_SHA,'size':[1785,1175],
          'rgb_sha256':'5861cd6fe98334bc983dda575a6c36bb3222e73a71329865a42e8cc492f2db94'},
          'frozen_first_band':{'file_reference':'research-updates/2026-10-13-native-source257-annotation/data/reconciled-native-annotation-v1.json',
          'file_sha256':FROZEN_SHA,'units':copy.deepcopy(frozen['units']),'preserved_annotation_keys':[k for k in frozen if k!='units']},
          'new_units':units,'frozen_overlay_conflicts':conflicts,'coverage_regions':coverage,'source_quality':quality,
          'raw_input_sha256':PINS,'frozen_raw_reference_links':frozen_links}
    # Source-visible trajectories are tilted; these are whole path envelopes,
    # not rectangular rows inferred from the crop names.
    trajectories=[]; gaps=[]
    for region in dict.fromkeys(u['region'] for u in units if u['region'].startswith(('right-R','bottom-B'))):
        us=[u for u in units if u['region']==region]; boxes=[u['native_bbox_xyxy_halfopen'] for u in us]
        right=region.startswith('right-')
        intervals=sorted([(855-b[3],855-b[1],u['id']) if right else (b[0],b[2],u['id']) for b,u in zip(boxes,us)])
        trajectories.append({'region':region,'native_extent_xyxy_halfopen':union(boxes),
            'first_last_axis_extent':[intervals[0][0],max(t[1] for t in intervals)],
            'axis':'u=855-native_y in exact CW view' if right else 'native x',
            'canonical_ids':[u['id'] for u in us]})
        end=intervals[0][1]; prev=intervals[0][2]
        for start,stop,ident in intervals[1:]:
            if start-end>=30:
                # Cutoff is only an inventory aid; no scoring/count fitting.
                pathbox=union(boxes)
                gapbox=([pathbox[0],855-start,pathbox[2],855-end] if right
                        else [end,pathbox[1],start,pathbox[3]])
                overlay=[u['id'] for u in units if u['region']=='bottom-unallocated-marks' and intersects(gapbox,u['native_bbox_xyxy_halfopen'])]
                gaps.append({'region':region,'axis_interval_halfopen':[end,start],
                    'native_context_bbox_xyxy_halfopen':gapbox,
                    'neighbor_ids':[prev,ident],'state':'INSPECTED_BACKGROUND_OR_WORDSPACE',
                    'unresolved_mark_overlay_ids':overlay,
                    'detail':'Native full context and relevant exact tiles inspected. No additional coherent body certified in this inter-envelope space. Listed detached-mark overlays remain unresolved and are not blank space; other fine background-confounded residue remains covered by source-quality limits. The bbox spans local path context and can include adjacent-row ink. Cutoff 30px is an inventory aid only.'})
                if overlay:gaps[-1]['state']='INSPECTED_WORDSPACE_WITH_UNRESOLVED_MARK_OVERLAY'
            if stop>end:end=stop;prev=ident
    # Rebuild actual links after explicit mark merges and final statuses.
    rawlinks=[{'raw_ref':r,'canonical_id':u['id'],'relation':'EXPLICIT_MANUAL_SCOPE' if r.startswith('right-') else 'PARTITION_OR_CONTEXT; not automatic same-occurrence identity'} for u in units for r in u['raw_refs']]
    counts={'frozen_records':len(frozen['units']),'frozen_whole_records':sum(u['physical_extent_status']==WHOLE for u in frozen['units']),
        'frozen_unresolved_records':sum(u['physical_extent_status']!=WHOLE for u in frozen['units']),
        'new_records':len(units),'new_whole_records':sum(u['physical_extent_status']==WHOLE for u in units),
        'new_unresolved_records':sum(u['physical_extent_status']==UNRESOLVED for u in units),
        'new_records_with_frozen_overlap':sum(bool(u['overlap_with_frozen_ids']) for u in units),
        'frozen_overlay_conflict_entries':len(conflicts),'raw_right_records_A_B':[171,170],
        'raw_bottom_records_A_B':[266,171],
        'deduplication':'Right A/B alternatives collapsed by explicit ledger; seven RAM and 13 B bottom mark entries mapped to existing scopes; one B mark linked to frozen U008; junction inspection establishes no additional lower/right duplicate. Counts do not prove glyph totals.'}
    evidence={'schema':'fullcard-adjudication-evidence-v1','raw_input_sha256':PINS,
      'source_file_sha256':SOURCE_SHA,'frozen_file_sha256':FROZEN_SHA,
      'native_manifest_file_sha256':'69745a00a2dca6e8609a306679df9844d706042eed7602d31b68a72ecd39a2ec',
      'pre_view_proof_reference':'adjudicator-pre-view-proof-v1.json',
      'own_actual_inspected_views':['pc_hcp_257_pic.JPG','rightblock-cw90.png','rightblock-cw90-tile1.png','rightblock-cw90-tile2.png','rightblock-cw90-tile3.png','bottom-context-native.png']+
        [f'bottom-r{r}-c{c}-native.png' for r in range(1,5) for c in range(1,7)]+['right-A-toptrace-native.png','right-A-date-edge-native.png'],
      'viewing_operations':'Original detail only; exact native cuts and exact 90CW transpose; hashes and decoded RGB/crop equality checked before views. No other transform, OCR, optimizer, scorer, model or control sessions.',
      'manual_right_decision_table':RIGHT,'manual_bottom_decision_table':BOTTOM,
      'record_decisions':[{k:u[k] for k in ('id','native_bbox_xyxy_halfopen','physical_extent_status','raw_refs','inspection_decision','overlap_with_frozen_ids')} for u in units],
      'raw_reference_links':rawlinks,'frozen_reference_links':frozen_links,
      'retained_raw_bottom_partitions':{'A':raw['bottom-A-v1.json']['units'],'B':bb},
      'retained_raw_right_partitions':{'A':raw['right-A-v2.json']['units'],'B':raw['right-B-v1.json']['units']},
      'body_ownership_differences':'Right crowded/date clusters collapsed by explicit range ledger. Bottom A granular and B coarse/position-shifted spans are retained in full; source-clear runs bounded individually, unresolved remainder kept as envelope ranges, not voted glyph units. Mark owner differences retained in units.',
      'trajectory_coverage':trajectories,'large_gap_inventory_cutoff_native_pixels':30,'large_gap_audit':gaps,
      'newly_recovered_gap':[903,887,1011,944],
      'short_gap_unresolved_residual_inventory':residuals,'counts':counts,
      'limits':quality,'all_cipher_roles':'UNKNOWN'}
    dump(d/'fullcard-map-v1.json',full);dump(d/'fullcard-adjudication-evidence-v1.json',evidence)
    print(json.dumps(counts))

if __name__=='__main__':main()
