#!/usr/bin/env python3
"""Bounded checks of the two externally supplied readings and their preserved history."""
import hashlib,json,re,subprocess,sys
from functools import lru_cache
from pathlib import Path
HERE=Path(__file__).resolve().parent;REPO=HERE.parents[1];PACKAGE=REPO/'research-updates/2026-10-20-confirmed-key-continuation';BASE='ca87d1638103590b59fa38cac3ce7dbdc5c68c5a';SNAPSHOT='65013ef45d44a49011c2106355987bdb2973f13e'
sys.path.insert(0,str(PACKAGE))
from decode import decode_text
from check import check_card,check_package
sha=lambda b:hashlib.sha256(b).hexdigest();canon=lambda x:sha(json.dumps(x,ensure_ascii=False,sort_keys=True,separators=(',',':')).encode())
@lru_cache(maxsize=None)
def old(path):return subprocess.check_output(['git','show',BASE+':'+str(path.relative_to(REPO))],cwd=REPO)
@lru_cache(maxsize=None)
def at_review(path):return subprocess.check_output(['git','show',SNAPSHOT+':'+str(path.relative_to(REPO))],cwd=REPO)
@lru_cache(maxsize=None)
def load(path):return json.loads(at_review(path))
def walk(value):
 if isinstance(value,dict):
  yield value
  for x in value.values():yield from walk(x)
 elif isinstance(value,list):
  for x in value:yield from walk(x)
def ptr(obj,path):
 for key in path.split('/')[1:]:
  key=key.replace('~1','/').replace('~0','~');obj=obj[int(key)]if isinstance(obj,list)else obj[key]
 return obj
def apply(text,groups):
 end=0;out=[]
 for e in groups:
  assert end<=e['old_offset']<=e['old_end'] and text[e['old_offset']:e['old_end']]==e['prior']
  out.extend([text[end:e['old_offset']],e['selected']]);end=e['old_end']
 return ''.join(out)+text[end:]
def check():
 assert __debug__,'Do not use optimized Python'
 review=load(HERE/'review.json');assert review['reviewer']=='Eugen Antal' and review['correspondence_date']=='2026-10-28T23:00:14+01:00' and review['integration_date']=='2026-10-29'
 totals={};protected={};groups={};before_counts={};all_edits=[]
 expected={320:dict(rows=10,encoded_bodies=200,expanded_letters=203,ch_occurrences=3,unknowns=0),321:dict(rows=5,encoded_bodies=135,expanded_letters=134,ch_occurrences=0,unknowns=1)}
 for n in [320,321]:
  path=PACKAGE/f'cards/{n}.json';d=load(path);prior=json.loads(old(path));rev=load(PACKAGE/f'revisions/{n}-external-review-20261029.json');text=at_review(path.with_suffix('.md')).decode()
  assert rev['base_commit']==BASE and rev['previous_edition']['sha256']==sha(old(path)) and rev['current_json_sha256']==sha(at_review(path))
  assert set(rev['protected_fields'])|set(rev['changed_prior_fields'])==set(prior) and not set(rev['protected_fields'])&set(rev['changed_prior_fields'])
  for k in rev['protected_fields']:assert d[k]==prior[k],(n,k)
  for k in rev['changed_prior_fields']:assert canon(prior[k])==rev['prior_field_hashes'][k]
  for k in ['source','raw_preservation','independent_readings','initial_reconciliation']:
   assert d[k]==prior[k]
  qa='batch_mechanical_qa'if n==320 else'qa_context';assert d[qa]==prior[qa]
  assert ' '.join(r['ciphertext']for r in d['lines'])==review['cards'][str(n)]['reviewed_transcription']
  assert d['proposed_editorial_czech']==review['cards'][str(n)]['reviewer_czech']if n==320 else d['proposed_editorial_czech']==review['cards'][str(n)]['reviewer_czech'].replace('mohu doufati','mohu [doufati; DOUvATI]')
  assert d['proposed_editorial_czech'] in text and d['proposed_english_translation']in text
  assert d['external_review']['reviewer']=='Eugen Antal' and d['physical_encoded_body_count']is None
  for a,b,r in zip(prior['lines'],d['lines'],rev['rows']):
   assert a['line_id']==b['line_id']==r['line_id'] and a['ciphertext']==r['prior_ciphertext'] and b['ciphertext']==r['reviewed_ciphertext']==apply(a['ciphertext'],r['edit_groups'])
   for k in ['native_bbox_xyxy','reading_bbox_xyxy','reading_dimensions','reading_rotation_degrees_clockwise','physical_encoded_body_count']:assert b[k]==a[k]
   result=decode_text(b['ciphertext'],notation=d['notation'],transcription=b['transcription'])
   assert all(b[k]==v for k,v in result.items()) and b['ciphertext']in text and b['literal']in text
  totals[str(n)]=check_card(d);before_counts[str(n)]=check_card(prior);assert totals[str(n)]==rev['current_totals']==expected[n] and before_counts[str(n)]==rev['prior_totals']
  by={r['line_id']:r for r in d['lines']}
  for field in ['uncertainty_ledger']+(['segmentation_ledger']if n==320 else[]):
   assert len(d[field])==len(prior[field])
   for i,e in enumerate(d[field]):
    assert e['prior_record_sha256']==canon(prior[field][i])
    assert by[e['line_id']]['ciphertext'][e['offset']:e['offset']+len(e['selected'])]==e['selected']
  for r,c in zip(d['lines'],d['editorial_coverage']):
   a='literal_offset'if n==320 else'literal_offset_start';b='literal_end_offset'if n==320 else'literal_offset_end'
   assert c[a]==0 and c[b]==len(r['literal']) and c['literal']==r['literal'] and c['czech_segments']==[r['proposed_czech']] and c['english_segments']==[r['proposed_english']]
  for e in d['editorial_restoration_ledger']+d['editorial_literal_fragment_ledger']:
   a=e.get('literal_offset',e.get('literal_offset_start'));b=e.get('literal_end_offset',e.get('literal_offset_end'));assert by[e['line_id']]['literal'][a:b]==e['literal']
  if n==320:
   assert rev['source_sign_substitutions']==8 and rev['source_slot_insertions']==0 and len(rev['source_edits'])==7
   assert d['unassigned_shapes']==[] and d['editorial_restoration_ledger']==[] and d['editorial_ledger_counts']==dict(restorations=0,literal_fragments=1,covered_rows=10)
   assert '9'not in ''.join(r['ciphertext']for r in d['lines']) and all(not r['unknowns']for r in d['lines'])
   assert by['320-R03']['literal']=='MOJE ROZMILA. PREJI TI' and by['320-R10']['literal']=='TE UPRIMNE LIBA TVUJ PEPOUS.'
  else:
   assert rev['source_sign_substitutions']==0 and rev['source_slot_insertions']==1 and rev['source_edits']==[dict(line_id='321-R01',operation='insert',old_offset=31,old_end=31,prior='',current_offset=31,current_end=32,selected='4')]
   assert 'ANDULIKO'in by['321-R01']['literal'] and by['321-R01']['transcription']==[dict(offset=39,text='!',kind='punctuation')]
   assert [(r['line_id'],u['offset'],u['symbol'])for r in d['lines']for u in r['unknowns']]==[('321-R03',31,'v')]
   assert d['unassigned_form_inventory']==prior['unassigned_form_inventory'] and d['unassigned_form_inventory'][0]['encoded_value']is None
   assert 'DOUvATI'in d['proposed_editorial_czech'] and 'DOUvATI'in d['proposed_english_translation']
  protected[str(n)]=len(rev['protected_fields']);groups[str(n)]=len(rev['source_edits']);all_edits+=rev['source_edits']
 # Exact public key invariance; no v→F or 9→Z assignment has been smuggled in.
 key=load(PACKAGE/'key.json');assert at_review(PACKAGE/'key.json')==old(PACKAGE/'key.json') and 'F'not in key['mapping'].values() and 'v'not in key['mapping']and '9'not in key['mapping']and decode_text('f',notation='pdf204-canonical')['literal']=='V'
 live=check_package(PACKAGE);assert live['status']=='passed'
 snapshot_names=subprocess.check_output(['git','ls-tree','-r','--name-only',SNAPSHOT],cwd=REPO).decode().splitlines();snapshot_set=set(snapshot_names)
 snapshot_cards=[x for x in snapshot_names if re.fullmatch(r'research-updates/2026-10-20-confirmed-key-continuation/cards/\d+\.json',x)];report=dict(cards={Path(x).stem:check_card(load(REPO/x))for x in snapshot_cards});aggregate={k:sum(c[k]for c in report['cards'].values())for k in ['rows','encoded_bodies','expanded_letters','ch_occurrences','unknowns']};assert len(report['cards'])==137 and aggregate==dict(rows=1493,encoded_bodies=44348,expanded_letters=44435,ch_occurrences=363,unknowns=276)
 table=at_review(PACKAGE/'README.md').decode()
 for n in [320,321]:
  t=expected[n];assert f'| [{n}](cards/{n}.md) | '+ ' | '.join(str(t[k])for k in ['rows','encoded_bodies','expanded_letters','ch_occurrences','unknowns'])+' |' in table
 q=load(PACKAGE/'queue.json');oq=json.loads(old(PACKAGE/'queue.json'))
 for a,b in zip(q['cards'],oq['cards']):
  assert a['card_id']==b['card_id'] and all(a[k]==b[k]for k in ['picture_urls','address_urls','catalogue_ids','catalogue_url','official_solution_status_label'])
  if a['card_id']not in [320,321]:assert a==b
  else:assert a['selected_totals']==expected[a['card_id']]
 assert q['active_completion_priority']['progress']==oq['active_completion_priority']['progress'] and q['external_coordination']==oq['external_coordination'] and q['active_completion_priority']['externally_manually_reviewed']==[320,321]
 assert set(q['active_completion_priority']['awaiting_source_peer_review'])==set(oq['active_completion_priority']['awaiting_source_peer_review'])-{320,321}
 # The transmitted register is immutable; a README navigation notice alone is allowed.
 submitted=REPO/'research-updates/2026-10-28-hcportal-register'
 for f in submitted.iterdir():
  if f.is_file()and f.name!='README.md'and str(f.relative_to(REPO))in snapshot_set:assert at_review(f)==old(f)
 for f in(PACKAGE/'cards').glob('*'):
  if f.is_file()and f.stem not in ['320','321']and str(f.relative_to(REPO))in snapshot_set:assert at_review(f)==old(f)
 for f in list((PACKAGE/'revisions').glob('*.json'))+list(PACKAGE.glob('validation*.json')):
  if f.name not in ['320-external-review-20261029.json','321-external-review-20261029.json']and str(f.relative_to(REPO))in snapshot_set:assert at_review(f)==old(f)
 refs=0
 for name in snapshot_cards:
  f=REPO/name
  for x in walk(load(f)):
   target=PACKAGE/x['file']if isinstance(x.get('file'),str)and x['file'].startswith('cards/')else PACKAGE/'cards'/x['card_file']if isinstance(x.get('card_file'),str)else None
   if target is not None and 'json_pointer'in x:
    value=ptr(load(target),x['json_pointer'])
    if 'canonical_whole_object_sha256'in x:assert canon(value)==x['canonical_whole_object_sha256']
    refs+=1
 assert refs==74
 return dict(status='passed',review_date='2026-10-28',integration_date='2026-10-29',review_snapshot=SNAPSHOT,live_package_replay_status=live['status'],review_snapshot_totals=totals,prior_totals=before_counts,protected_field_counts=protected,edit_groups=groups,source_sign_substitutions=8,source_slot_insertions=1,punctuation_tag_offsets_shifted=1,source_key_changes=0,source_v_unassigned=True,other_candidate_files_unchanged_at_review_snapshot=270,public_protocol_references=refs,submitted_register_data_unchanged=True,historical_revisions_and_QA_unchanged=True,aggregate_totals=aggregate,progress_at_review_snapshot=dict(remaining=70,next_card=319,readings_including_partial=154,without_separate_reading=109))
if __name__=='__main__':print(json.dumps(check(),ensure_ascii=False,indent=2))
