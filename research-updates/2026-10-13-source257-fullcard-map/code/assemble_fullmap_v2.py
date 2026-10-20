#!/usr/bin/env python3
"""Apply explicit source-reinspection decisions to immutable private v1.

CLI: assemble_fullmap_v2.py INPUT_DIRECTORY FROZEN_FILE OUTPUT_DIRECTORY
INPUT_DIRECTORY contains v1 map/evidence, four raw annotations and two v2
native-view provenance files. No image transforms, classification, OCR,
similarity scores or expected inventory counts are performed by this helper.
Source decisions below are manual observations; byte reproducibility is not
independent confirmation of those observations.
"""
import argparse
import copy
import hashlib
import json
from collections import Counter
from pathlib import Path

WHOLE='VISUALLY_BOUNDED_WHOLE_PHYSICAL_CONSTRUCTION'
UNRESOLVED='UNRESOLVED_SPAN'
PINS={
 'fullcard-map-v1.json':'dda78c5aad9d92e85c3804af53bdcdffde125595b0f72dca507d3176a6f8df50',
 'fullcard-adjudication-evidence-v1.json':'e61ec74db3733112f363a9fcf78ba5b4a68396baeaef50f3c9c0a6fd867d76ac',
 'right-A-v2.json':'51aebbb7b0f9f9f5032d5934acb9628736efd698eac88b22a421a76231b61481',
 'right-B-v1.json':'8fd0a16cded0e0b12b539bb1c7f675bdcf08e815c509fc95feb89a19ec82b3eb',
 'bottom-A-v1.json':'aacf3ab359fad1b1e8f83710ebd3ccdafd43a7cf684eb82fc318002b42e75b47',
 'bottom-B-v1.json':'1a2ff9d5320dd8329e405ac8f4f31c063b41bb8f9283442a5920d91a00fb49ee',
 'adjudicator-bottom-reinspection-proof-v2.json':'9d46599e19b5edb88dc4c09003c695548a1696b2dea07f74331557c4e5eb9fd7',
 'adjudicator-bottom-candidate-tight-proof-v2.json':'6c55eaa5bde50ca06611e9df4a0419c79fb26d2a7c6dcbee31874033c7895902',
}
FROZEN_SHA='bdb98089160dea39306bdce159c0d9bed88fc6eab7f75aaf7bc6a25ed2cd9c91'

# Source-clear body corrections, each inspected in original RGB context and a
# separately proved candidate envelope. Nearby unrelated ink may enter an
# approximate envelope; no exact ink mask is claimed.
CORRECTIONS={
 'FC149':([246,880,269,916], 'Sloping stem with transverse upper-middle arm and continuous bent low return.', 'V1 extended too far into the adjacent small curved body; narrower right limit follows the continuous crossed stem.'),
 'FC166':([246,941,269,967], 'One low curved arch with short upright ends and small outward lower turn.', 'V1 right margin approached the next arch; exact candidate crop bounds this first continuous low body.'),
 'FC195':([240,1045,264,1081], 'Continuous bowed left contour; open on right, with short upper and lower inward terminals.', 'V1 clipped the left contour and included a substantial portion of the neighboring capped/neck body. Context and tight native crop locate the bowed body to the left.'),
 'FC196':([262,1045,292,1081], 'Upper near-horizontal cap feeds a narrow descending neck and rounded low return; upper cap and lower return remain visibly separated at the left.', 'V1 shifted right relative to the upper cap/neck and retained prior-body ink. Source-clear upper cap, neck and lower return are bounded in the corrected crop; no identity with another occurrence is inferred.'),
 'FC209':([136,1082,156,1122], 'Short oblique upright with a leftward middle arm and wider angular low return.', 'V1 began in the preceding low-arch body. Corrected left limit removes that substantial neighboring portion.'),
 'FC210':([157,1085,181,1123], 'Short slanted/wedge-like body with a narrow rising end and pointed low return.', 'V1 included much of the preceding angled upright and approached the right edge of this body; local context establishes a separable low wedge.'),
 'FC211':([184,1076,206,1123], 'Broad upper curved cap descends into a narrow low rounded bend with short inward terminal.', 'V1 began in the preceding wedge. Corrected envelope follows the next high-cap and low-return body.'),
 'FC212':([222,1089,245,1124], 'Low continuous rounded arch with short upturned ends; interior remains open below.', 'V1 right side entered the neighboring tall loop. Tight source crop bounds the low arch separately.'),
 'FC213':([246,1072,278,1124], 'Tall upper curved loop on a sloping stem feeding a smaller low rounded enclosure.', 'V1 left margin entered the previous low arch. Candidate crop retains the full tall loop and low enclosure while reducing prior-body ink.'),
 'FC214':([278,1092,303,1124], 'Two low joined rounded rises with a short outward right terminal.', 'V1 began in the preceding tall-loop body. Corrected envelope follows the visible pair of low rises.'),
}

DOWNGRADES={
 'FC152':([551,880,583,929], 'Raised angular two-prong mark and faint low curved/angular ink in an area crossed by printed watermark texture.', 'The inherited large upper-loop/low-bowl description is not established by the exact source crop. Detached-mark versus lower-body ownership and ink/background distinction remain unresolved.'),
 'FC154':([708,897,747,933], 'Several low upstrokes and an adjoining compact curved stroke near a tall neighboring return.', 'A finer envelope cuts or mixes adjacent local forms; B gives a shifted broader low-body boundary. One whole construction is not certified; local body count and joins remain alternatives.'),
 'FC167':([268,943,307,970], 'Low curved ends and adjacent joined arch-like rises; the left portion may be a return of the preceding low body.', 'Exact v1 and trial crops retain substantial adjacent arch ink. No stable single-body left/right partition is certified within tolerance.'),
 'FC168':([298,937,333,970], 'Right portion of low arch-like writing beside a higher cap and curved low return.', 'Inherited envelope includes the preceding arch and the next capped body. Preserve a bounded local overlay; intended body boundary and shared/adjacent returns remain unresolved.'),
 'FC171':([532,936,590,978], 'Part of a sloping/crossed stroke at left and adjacent upper-hook/low-return ink to its right.', 'V1 includes substantial neighboring stroke and insufficiently establishes the intended body envelope. Broader native context preserves competing body and return ownership without a whole-body claim.'),
 'FC193':([165,1036,203,1079], 'Short slanted/capped ink, a low curved return, and ink from a neighboring taller looped stroke enter this local envelope.', 'V1 left limit clips the intended capped/neck return while its right limit enters the next tall body. Native reinspection confirms an extent/target discrepancy, not a class difference; body partition and upper-stroke owner remain unresolved.'),
 'FC198':([326,1032,365,1083], 'Tail of a preceding curved body beside a tall looped stem and low rounded return.', 'V1 exact crop includes substantial preceding-body ink; the left return and tall-loop entry cannot be partitioned confidently at the inherited boundary. Preserve the local span without assigning a whole construction.'),
}

# Every remaining bottom whole was inspected as a separate exact v1 envelope
# plus 20px native context. These statements specify visible geometry only.
RETAINED={
 'FC144':'The oblique branched stem and its low continuous foot remain bounded; neighboring tall curve is outside the main body.',
 'FC145':'Tall curved stem and its continuous low hooked return remain visible; minor edge entry does not change body attribution.',
 'FC146':'Compact upper/lower curved bends remain connected within the envelope.',
 'FC147':'Single narrow slanted oval/pocket is bounded as one continuous visible body.',
 'FC148':'Single compact paired-curve body is bounded; no detached mark assigned.',
 'FC150':'Small upper/lower opposing curves form the visibly separable compact body.',
 'FC158':'Angular/rounded upper hook and low bent return remain visibly continuous.',
 'FC161':'Upper rounded/angular loop and long low descending return are continuous.',
 'FC162':'Tall slanted upper return and rounded low pocket remain continuous.',
 'FC163':'Compact paired bends remain continuous and separable from taller neighbors.',
 'FC164':'Tall arching stem and low curved shoulder remain visibly continuous.',
 'FC165':'Short angled upright and its low pointed return remain bounded.',
 'FC179':'Single continuous bowed left contour is open on the right; original envelope contains the complete visible curve.',
 'FC180':'Low joined rounded rises remain connected within the envelope.',
 'FC182':'Short angled upright with middle arm and broad low return remains bounded.',
 'FC183':'Single continuous bowed left contour is open on the right; complete curve visible in its original envelope.',
 'FC190':'Tall crossed upper stroke and long narrow low loop remain continuous and bounded.',
 'FC191':'Compact high curved cap and low hooked return remain bounded.',
 'FC192':'Short slanted upright and its low angular foot remain visibly bounded.',
 'FC194':'Tall upper curved loop and low continuous return remain bounded; adjacent curve is contextual edge ink.',
 'FC197':'Compact opposing upper/lower curved bends remain visibly continuous.',
 'FC208':'Low joined arch-like rises remain bounded within original tolerance; wider trial crop introduced more neighboring angled-stem ink and was rejected.',
}

def digest(p):return hashlib.sha256(p.read_bytes()).hexdigest()
def dump(p,v):p.write_text(json.dumps(v,ensure_ascii=False,indent=2)+'\n')
def intersects(a,b):return max(a[0],b[0])<min(a[2],b[2]) and max(a[1],b[1])<min(a[3],b[3])
def union(bs):return [min(b[0] for b in bs),min(b[1] for b in bs),max(b[2] for b in bs),max(b[3] for b in bs)]

def main():
 p=argparse.ArgumentParser(description=__doc__);p.add_argument('input_directory',type=Path);p.add_argument('frozen_file',type=Path);p.add_argument('output_directory',type=Path);a=p.parse_args();d=a.input_directory;o=a.output_directory;o.mkdir(parents=True,exist_ok=True)
 for n,h in PINS.items():assert digest(d/n)==h,n
 assert digest(a.frozen_file)==FROZEN_SHA
 f=json.loads((d/'fullcard-map-v1.json').read_text());e=json.loads((d/'fullcard-adjudication-evidence-v1.json').read_text())
 old=copy.deepcopy(f);fr=json.loads(a.frozen_file.read_text());assert f['frozen_first_band']['units']==fr['units']
 proof=json.loads((d/'adjudicator-bottom-reinspection-proof-v2.json').read_text())
 tight=json.loads((d/'adjudicator-bottom-candidate-tight-proof-v2.json').read_text())
 source_sha=f['source']['file_sha256'];assert proof['source_file_sha256']==tight['source_file_sha256']==source_sha
 whole={u['id'] for u in f['new_units'] if u['region'].startswith('bottom-') and u['physical_extent_status']==WHOLE}
 assert whole==set(CORRECTIONS)|set(DOWNGRADES)|set(RETAINED)
 assert {v['id'] for v in proof['views']}==whole
 byid={u['id']:u for u in f['new_units']}; audits=[];view_by_id={v['id']:v for v in proof['views']};tight_by_id={v['id']:v for v in tight['views']}
 for uid in sorted(whole):
  u=byid[uid];prior=copy.deepcopy(u);v=view_by_id[uid]
  if uid in CORRECTIONS:
   b,g,why=CORRECTIONS[uid];assert tight_by_id[uid]['source_bbox_xyxy_halfopen']==b
   u['native_bbox_xyxy_halfopen']=b;u['geometric_features']=g
   action='SOURCE_CORRECTED_WHOLE_BODY_ENVELOPE'
   u['evidence_views'].append(tight_by_id[uid]['file_reference'])
  elif uid in DOWNGRADES:
   b,g,why=DOWNGRADES[uid];u['native_bbox_xyxy_halfopen']=b;u['geometric_features']=g;u['physical_extent_status']=UNRESOLVED
   u['ambiguities'].append(why);u['ambiguities'].append('This envelope can include multiple bodies or neighboring-row/return fragments; no independent repeat instance or fixed body count is certified.')
   action='DOWNGRADED_AFTER_EXACT_SOURCE_REINSPECTION'
  else:
   why=RETAINED[uid];action='SOURCE_RECHECKED_WHOLE_RETAINED'
   if uid in ('FC179','FC183'):u['geometric_features']='Continuous bowed left contour; open on right, with short upper and lower inward terminals.'
  u['evidence_views']+= [v['file_reference'],v['exact_v1_unit_view']['file_reference']]
  u['evidence_views']=sorted(set(u['evidence_views']))
  u['inspection_decision']='V2 exact native body/context reinspection: '+why
  u['revision_v2']={'action':action,'prior_bbox_xyxy_halfopen':prior['native_bbox_xyxy_halfopen'],'prior_extent_status':prior['physical_extent_status'],'reason':why,'v1_raw_refs_preserved':True}
  audits.append({'id':uid,'action':action,'prior_bbox_xyxy_halfopen':prior['native_bbox_xyxy_halfopen'],'new_bbox_xyxy_halfopen':u['native_bbox_xyxy_halfopen'],'prior_extent_status':prior['physical_extent_status'],'new_extent_status':u['physical_extent_status'],'source_observation':why,'new_geometric_features':u['geometric_features'],'context_and_exact_v1_view':v,'candidate_tight_view':tight_by_id.get(uid)})
 # Geometry frame is explicit even though all bounding boxes are native.
 for u in f['new_units']:
  u['geometric_feature_coordinate_frame']='EXACT_90CW_RIGHTBLOCK_VIEW' if u['region'].startswith('right-') else 'NATIVE_UNROTATED_SOURCE'
  u['overlap_with_frozen_ids']=[r['id'] for r in fr['units'] if intersects(u['native_bbox_xyxy_halfopen'],r['native_bbox_xyxy_halfopen'])]
  if u['overlap_with_frozen_ids']:u['physical_extent_status']=UNRESOLVED
 # Local unresolved overlays retain crosslinks rather than imply new bodies.
 neighbors={'FC167':['FC166','FC168'],'FC168':['FC167'],'FC171':['FC170','FC172'],'FC193':['FC192','FC194'],'FC198':['FC197','FC199'],'FC152':['FC151','FC153'],'FC154':['FC155']}
 for uid,ns in neighbors.items():byid[uid]['uncertain_neighbor_occurrence_refs']=ns
 f['schema']='source257-fullcard-physical-map-v2'
 f['revision']={'previous_map_file':'fullcard-map-v1.json','previous_map_sha256':PINS['fullcard-map-v1.json'],'reason':'Exact per-body native reinspection identified inherited bottom-envelope/target errors beyond approximate tolerance. Correct source-clear bounds and downgrade uncertain spans; original raw A/B and all frozen data unchanged.','bottom_whole_records_reinspected':len(whole),'corrected_whole_envelopes':len(CORRECTIONS),'whole_to_unresolved':len(DOWNGRADES),'retained_whole_records':len(RETAINED)}
 f['source_quality'].append({'region':'new bottom body envelopes','limit':'V1 context-only endorsements did not certify every per-body boundary. V2 reinspects all39 prior whole bottom envelopes with exact unit crops and 20px context, corrects10 source-clear envelopes, and downgrades7 unresolved extents. A/B descriptors remain immutable alternatives; no general ±4px guarantee is retroactively asserted for erroneous v1 bounds.'})
 for r in f['coverage_regions']:
  if r['id']=='bottom-all-five-new-trajectories':r['detail']+=' V2 adds exact per-body audit of every prior whole bottom record; 10 corrected envelopes and 7 downgraded local spans. See v2 evidence.'
 # Rebuild trajectory extents/orders from final records; no glyph count used.
 trajectories=[]
 for region in dict.fromkeys(u['region'] for u in f['new_units']):
  local=sorted([u for u in f['new_units'] if u['region']==region],key=lambda u:(855-u['native_bbox_xyxy_halfopen'][3]) if region.startswith('right-') else u['native_bbox_xyxy_halfopen'][0])
  for i,u in enumerate(local,1):u['order']=i
  if region.startswith(('right-R','bottom-B')):
   boxes=[u['native_bbox_xyxy_halfopen'] for u in local];iv=[(855-b[3],855-b[1]) if region.startswith('right-') else (b[0],b[2]) for b in boxes]
   trajectories.append({'region':region,'native_extent_xyxy_halfopen':union(boxes),'first_last_axis_extent':[min(t[0] for t in iv),max(t[1] for t in iv)],'axis':'u=855-native_y in exact CW view' if region.startswith('right-') else 'native x','canonical_ids':[u['id'] for u in local]})
 counts={'frozen_records':len(fr['units']),'frozen_whole_records':sum(u['physical_extent_status']==WHOLE for u in fr['units']),'frozen_unresolved_records':sum(u['physical_extent_status']!=WHOLE for u in fr['units']),'new_records':len(f['new_units']),'new_whole_records':sum(u['physical_extent_status']==WHOLE for u in f['new_units']),'new_unresolved_records':sum(u['physical_extent_status']==UNRESOLVED for u in f['new_units']),'new_bottom_whole_records':sum(u['physical_extent_status']==WHOLE and u['region'].startswith('bottom-') for u in f['new_units']),'new_records_with_frozen_overlap':sum(bool(u['overlap_with_frozen_ids']) for u in f['new_units']),'frozen_overlay_conflict_entries':len(f['frozen_overlay_conflicts']),'counts_are_physical_glyph_totals':False}
 e['schema']='fullcard-adjudication-evidence-v2';e['previous_evidence_file_sha256']=PINS['fullcard-adjudication-evidence-v1.json'];e['revision']=f['revision'];e['bottom_whole_reinspection_v2']=audits;e['native_reinspection_proof_file_sha256']=digest(d/'adjudicator-bottom-reinspection-proof-v2.json');e['native_candidate_tight_proof_file_sha256']=digest(d/'adjudicator-bottom-candidate-tight-proof-v2.json');e['own_actual_inspected_views']+= [v['file_reference'] for v in proof['views']]+[v['exact_v1_unit_view']['file_reference'] for v in proof['views']]+[v['file_reference'] for v in tight['views']];e['trajectory_coverage']=trajectories;e['counts']=counts;e['limits']=f['source_quality'];e['record_decisions']=[{k:u[k] for k in ('id','native_bbox_xyxy_halfopen','physical_extent_status','raw_refs','inspection_decision','overlap_with_frozen_ids')} for u in f['new_units']];e['v1_large_gap_audit_note']='V1 numeric large-gap inspection remains source evidence. V2 corrected body envelopes can alter numeric gaps; none of the changed bounds establishes extra writing or new blank-space certification.'
 e['geometry_frame_note']='Every bbox remains native unrotated half-open. Right geometric feature prose is explicitly in exact 90CW orientation; bottom/outer prose is native unrotated. No semantic role or alphabet mapping follows.'
 assert f['frozen_first_band']==old['frozen_first_band']
 dump(o/'fullcard-map-v2.json',f);dump(o/'fullcard-adjudication-evidence-v2.json',e);print(json.dumps(counts))

if __name__=='__main__':main()
