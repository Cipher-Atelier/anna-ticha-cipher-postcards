#!/usr/bin/env python3
"""Check the curator submission against exact pinned public evidence, offline."""
import csv, hashlib, io, json, re, subprocess, sys, unicodedata
from collections import Counter
from functools import lru_cache
from pathlib import Path
from urllib.parse import unquote, urlsplit

HERE = Path(__file__).resolve().parent
REPO = HERE.parents[1]
BASE = 'f1b9c746afbe589ecc68dbca7bf213fce9e92d70'
PACKAGE = 'research-updates/2026-10-20-confirmed-key-continuation'
PREFIX = 'https://github.com/Cipher-Atelier/anna-ticha-cipher-postcards/blob/' + BASE + '/'
@lru_cache(maxsize=None)
def original(path):
    return subprocess.check_output(['git','show',BASE+':'+path],cwd=REPO)
@lru_cache(maxsize=None)
def old_json(path):
    return json.loads(original(path))
def sha(data):
    return hashlib.sha256(data).hexdigest()
def pointer(data, path):
    for part in path.split('/')[1:]:
        part=part.replace('~1','/').replace('~0','~')
        data=data[int(part)] if isinstance(data,list) else data[part]
    return data
def anchors(text):
    result=set();seen=Counter()
    for title in re.findall(r'^#{1,6}\s+(.+)$',text,re.M):
        title=re.sub(r'\[([^\]]+)\]\([^)]*\)',r'\1',title)
        title=title.replace('`','').lower()
        slug=''.join(c for c in title if c.isalnum() or c in '-_ ' or unicodedata.category(c).startswith('M')).replace(' ','-')
        count=seen[slug];seen[slug]+=1
        result.add(slug if count==0 else slug+'-'+str(count))
    result.update(re.findall(r'<a\s+id="([^"]+)"',text))
    return result
def check_proof(item):
    data=original(item['path'])
    assert sha(data)==item['snapshot_sha256']
    assert item['url']==PREFIX+item['path']
    if 'json_pointer' in item:
        assert pointer(old_json(item['path']),item['json_pointer'])==item['value']
    else:
        assert item['exact_text'] in data.decode().splitlines()
        # These dated historical report quotations explicitly spell out their dates.
        day=int(item['value'][-2:])
        assert re.search(r'\b'+str(day)+r' October 2026\b',item['exact_text'])
    return 1
def check():
    if not __debug__:
        raise SystemExit('Assertions required; do not use optimized Python.')
    reg=json.loads((HERE/'register.json').read_text())
    coord=json.loads((HERE/'coordination.json').read_text())
    assert reg['snapshot_commit']==coord['repository_snapshot']==BASE
    names=subprocess.check_output(['git','ls-tree','-r','--name-only',BASE],cwd=REPO).decode().splitlines()
    canonical={int(Path(x).stem) for x in names if re.fullmatch(PACKAGE+r'/cards/\d+\.json',x)}
    legacy={int(Path(x).stem.split('-')[-1]) for x in names if re.fullmatch(r'anna-ticha/card-\d+\.md',x)}
    rows=reg['records']; ids=[x['card_id'] for x in rows]
    assert ids==sorted(set(ids))==sorted(canonical|legacy) and len(ids)==154 and 460 not in ids
    assert (len(canonical),len(legacy),len(canonical&legacy))==(137,38,21)
    queue=old_json(PACKAGE+'/queue.json');by={int(x['card_id']):x for x in queue['cards']}
    proof_count=0;targets=0
    for r in rows:
        n=r['card_id'];q=by[n]
        assert r['record_name']==f'pc_hcp_{n}' and r['catalogue_record_id']==q['catalogue_ids'][0] and r['catalogue_url']==q['catalogue_url']
        for key in ['ai_model_and_version','model_version_notes','role_of_AI','AI_agents_used','decipherment_record_url','result_status','date_basis']:
            assert isinstance(r[key],str) and r[key].strip()
        for prefix in ['reading','evidence']:
            assert r[prefix+'_path'] in names and sha(original(r[prefix+'_path']))==r[prefix+'_sha256']
        assert r['evidence_url']==PREFIX+r['evidence_path']
        assert r['decipherment_record_url'].split('#')[0]==PREFIX+r['reading_path']
        text=original(r['reading_path']).decode();fragment=urlsplit(r['decipherment_record_url']).fragment
        if fragment:assert unquote(fragment) in anchors(text),(n,fragment)
        assert len(text.strip())>300 and re.search(r'literal|Czech|English|reading',text,re.I),n
        targets+=1
        for item in r['date_evidence']+r['ai_model_evidence']:
            proof_count+=check_proof(item)
        if n in canonical:
            assert r['date_evidence'] and r['date_of_decipherment'] in {'2026-10-20','2026-10-21','2026-10-22'}
            assert all(x['value'][:10]==r['date_of_decipherment'] for x in r['date_evidence'])
            assert r['ai_model_evidence'] and r['model_metadata_status']=='recorded_label_or_family'
            assert r['ai_model_and_version']=='; '.join(dict.fromkeys(x['value']for x in r['ai_model_evidence']))
            assert r['agent_evidence']
            proof_count+=check_proof(r['agent_evidence'])
            assert r['workflow_category']==('paired_related_AI_readers'if n<=370 else'single_root_AI_reader')
            assert 'not externally confirmed' in r['result_status']
        else:
            assert r['model_metadata_status']=='not_recorded' and r['ai_model_evidence']==[] and r['agent_evidence']is None
            assert r['workflow_category']=='historical_workflow_not_fully_recorded'
            assert r['date_of_decipherment'] is None or r['date_evidence']
        if r['date_of_decipherment']is None:assert 'not ' in r['date_basis'].lower() and not r['date_evidence']
        pub=subprocess.check_output(['git','show','-s','--format=%aI',r['first_repository_commit']],cwd=REPO).decode().strip()
        assert pub==r['first_repository_commit_author_at']
    summary=reg['summary']
    assert summary==dict(published_readings_including_partial=154,current_canonical_candidates=137,legacy_only_reports=17,catalogue_cards=263,without_our_separate_reading=109,planned_team_cards=108,current_pass_working_coverage=67,current_pass_remaining=70,next_existing_card=319,recorded_reading_dates=146,missing_exact_reading_dates=8,model_labels_or_families_recorded=137,no_recorded_model_label=17,workflow_categories=dict(Counter(r['workflow_category']for r in rows)))
    assert {r['card_id']for r in rows if r['date_of_decipherment']is None}=={198,199,200,250,440,441,453,458}
    team=coord['planned_team_card_ids'];missing=set(by)-set(ids)
    assert len(team)==len(set(team))==108 and set(team)==missing-{460} and not set(team)&set(ids)
    assert missing-set(team)=={460} and 'planned' in coord['status'] and coord['separate_team_comparison_card_id']==460
    assert queue['active_completion_priority']['progress']['remaining_in_descending_pass']==70
    csv_rows=list(csv.DictReader(io.StringIO((HERE/'register.csv').read_text())))
    assert len(csv_rows)==154
    assert set(csv_rows[0])=={'record_name','date_of_decipherment','date_basis','ai_model_and_version','model_version_notes','role_of_AI','AI_agents_used','decipherment_record_url','result_status','catalogue_record_id','catalogue_url','first_repository_commit_author_at','latest_dated_source_completion','evidence_url'}
    for flat,r in zip(csv_rows,rows):
        assert all(flat[k]==str(r[k] if r[k]is not None else'Not recorded') for k in flat)
    table=(HERE/'register.md').read_text()
    assert len(re.findall(r'^\| \[`pc_hcp_',table,re.M))==154
    for r in rows:assert r['decipherment_record_url'] in table and r['catalogue_url'] in table
    coordination=(HERE/'coordination.md').read_text()
    assert [int(x)for x in re.findall(r'^\| pc_hcp_(\d+) \|',coordination,re.M)]==team
    for n in team:assert by[n]['catalogue_url'] in coordination
    review=(HERE/'review-request.md').read_text()
    # Validate the exact three questions, offsets and row pointers independently.
    for n,rid,source_offset,symbol,lit_offset,literal in [(321,'321-R03',31,'v',28,'DOUvATI'),(320,'320-R03',7,'9',5,'RO9HILA'),(320,'320-R10',13,'n',11,'LIMA')]:
        d=old_json(PACKAGE+f'/cards/{n}.json');line=next(x for x in d['lines']if x['line_id']==rid)
        assert line['ciphertext'][source_offset]==symbol and line['literal'][lit_offset:lit_offset+len(literal)]==literal
        assert line['ciphertext'] in review and line['literal'] in review
    # Every pinned reading link in the review request must resolve to an exact snapshot heading.
    for target in re.findall(r'\]\((https://github.com/[^)]+)\)',review):
        assert target.startswith(PREFIX)
        path,_,fragment=target[len(PREFIX):].partition('#')
        assert path in names and (not fragment or fragment in anchors(original(path).decode()))
    return dict(status='passed',snapshot_commit=BASE,unique_reading_records=154,canonical_candidates=137,legacy_only_reports=17,
                exact_metadata_evidence_checked=proof_count,direct_text_targets_checked=targets,csv_rows=154,index_rows=154,
                review_cards=2,review_questions=3,review_literal_spans_checked=3,planned_team_cards=108,
                no_overlap_with_our_readings=True,sole_extra_card_without_our_reading=460,
                recorded_reading_dates=146,unrecorded_exact_reading_dates=8,recorded_model_labels_or_families=137,
                reports_without_recorded_model_label=17,complete_solve_dates_or_missing_model_versions_invented=False,
                deeper_pass_remaining=70,next_card=319,without_our_separate_published_reading=109)
if __name__=='__main__':
    print(json.dumps(check(),ensure_ascii=False,indent=2))
