#!/usr/bin/env python3
"""Build a dated, one-card-per-row submission inventory from a pinned Git snapshot."""
import csv, hashlib, io, json, re, subprocess
from collections import Counter
from functools import lru_cache
from pathlib import Path

HERE = Path(__file__).resolve().parent
REPO = HERE.parents[1]
PACKAGE = 'research-updates/2026-10-20-confirmed-key-continuation'
BASE = 'f1b9c746afbe589ecc68dbca7bf213fce9e92d70'
URL = 'https://github.com/Cipher-Atelier/anna-ticha-cipher-postcards/blob/' + BASE + '/'
@lru_cache(maxsize=None)
def original(path):
    return subprocess.check_output(['git', 'show', BASE + ':' + path], cwd=REPO)
def read_json(path):
    return json.loads(original(path))
def url(path):
    return URL + path
def digest(data):
    return hashlib.sha256(data).hexdigest()
def dump(name, value):
    (HERE / name).write_text(json.dumps(value, ensure_ascii=False, indent=2) + '\n')
def leaves(value, prefix=''):
    if isinstance(value, dict):
        for key, child in value.items():
            yield from leaves(child, prefix + '/' + key.replace('~', '~0').replace('/', '~1'))
    elif isinstance(value, list):
        for i, child in enumerate(value):
            yield from leaves(child, prefix + '/' + str(i))
    else:
        yield prefix, value
def proof(path, pointer, value):
    return dict(path=path, json_pointer=pointer, value=value,
                snapshot_sha256=digest(original(path)), url=url(path))

queue_path = PACKAGE + '/queue.json'
queue = read_json(queue_path)
catalogue = {int(x['card_id']): (i, x) for i, x in enumerate(queue['cards'])}
names = subprocess.check_output(['git', 'ls-tree', '-r', '--name-only', BASE], cwd=REPO).decode().splitlines()
candidates = {int(Path(x).stem): x for x in names if re.fullmatch(PACKAGE + r'/cards/\d+\.json', x)}
legacy = {int(Path(x).stem.split('-')[-1]): x for x in names if re.fullmatch(r'anna-ticha/card-\d+\.md', x)}
ids = sorted(set(candidates) | set(legacy))
assert len(candidates) == 137 and len(legacy) == 38 and len(ids) == 154
roots = {'reader', 'independent_readings', 'raw_preservation', 'original_readings',
         'original_reads', 'frozen_readings', 'reading_preservation', 'frozen_raw',
         'raw_freeze', 'raw_frozen_at_utc', 'provenance', 'reconciliation',
         'original_phase1_records', 'scientific_originals', 'first_computational_decode_record',
         'record_created_date', 'prepared_utc', 'raw_freeze_record', 'initial_reconciliation', 'original_objects'}
date_keys = {'date', 'record_created_date', 'raw_frozen_at_utc', 'frozen_at_utc',
             'raw_frozen_at_utc', 'decoded_at_utc', 'at_utc', 'utc_freeze',
             'actual_selected_snapshot_captured_at_utc', 'prepared_utc', 'date_utc', 'utc',
             'first_frozen_at_utc', 'blind_frozen_at_utc'}
explicit_legacy_dates = {201:'2026-10-05', 202:'2026-10-05', 203:'2026-10-05',
                         204:'2026-10-08', 205:'2026-10-05', 223:'2026-10-05',
                         247:'2026-10-06', 248:'2026-10-06', 447:'2026-10-05'}
records = []
for n in ids:
    qi, q = catalogue[n]
    path = candidates.get(n, legacy.get(n))
    md_path = path[:-5] + '.md' if n in candidates else path
    text = original(md_path).decode()
    first_commit = subprocess.check_output(['git', 'log', '--diff-filter=A', '--reverse', '--format=%H %aI', BASE, '--', path], cwd=REPO).decode().splitlines()[0]
    publication_commit, publication_time = first_commit.split(' ', 1)
    models = []; date_proofs = []; model_proofs = []
    if n in candidates:
        d = read_json(path)
        metadata = {k:d[k] for k in roots if k in d}
        for pointer, value in sorted(leaves(metadata)):
            key = pointer.rsplit('/', 1)[-1]
            if any(x in pointer for x in ['/context_attestation/', '/group_barrier/', '/phase1_originals/']):
                continue
            if isinstance(value, str) and key in {'model','actual_model_deployment','family','model_deployment'} and re.search(r'gpt|codex|claude|gemini|openai', value, re.I):
                if value not in models: models.append(value)
                model_proofs.append(proof(path, pointer, value))
            if isinstance(value, str) and key in date_keys and re.match(r'2026-10-(20|21|22)(T|$)', value) and not any(x in pointer.lower() for x in ['group_barrier','own_input','source_metadata','source/','rows/','prior_context','started_record']):
                date_proofs.append(proof(path, pointer, value))
        initial = PACKAGE + f'/revisions/{n}-initial-reconciliation.json'
        if initial in names:
            init = read_json(initial)
            for key in ['date','frozen_at_utc','actual_selected_snapshot_captured_at_utc']:
                if isinstance(init.get(key), str) and re.match(r'2026-10-(20|21|22)', init[key]):
                    date_proofs = [proof(initial, '/' + key, init[key])]
                    break
        selected_date = min((x['value'][:10] for x in date_proofs), default=None)
        if date_proofs:
            date_proofs = [x for x in date_proofs if x['value'][:10] == selected_date][:2]
        if selected_date is None and n in [253,254,255]:
            batch_path = PACKAGE + '/validation-batch2.json'
            batch = read_json(batch_path)
            assert n in batch['public_card_ids']
            selected_date = batch['date']
            date_proofs = [proof(batch_path, '/date', selected_date)]
        basis = 'Recorded date of the selected canonical-key candidate or its frozen source/reconciliation stage; not a complete-solve date.' if selected_date else 'Exact reading date not recorded in the located public metadata; first file-addition commit is supplied separately.'
        ai_role = 'Key-visible source transcription and comparison, provisional Czech restoration, English interpretation and nonblind curation. Fixed-key literal replay is deterministic Python, not independent AI validation.'
        workflow = 'paired_related_AI_readers' if n <= 370 else 'single_root_AI_reader'
        agents = 'Yes: separately assigned related AI source-reader tasks; later coordinator review is nonblind.' if n <= 370 else 'Single root AI workflow; no second source reader recorded. Additional source agents are not claimed.'
        status = 'Provisional canonical-key candidate; not externally confirmed or declared solved.'
        root_status = d.get('status')
        coverage = 'Deeper working coverage of selected entries' if n >= 320 else 'Existing candidate awaiting current descending source-completion pass'
        review_file = PACKAGE + f'/revisions/{n}-source-completion.json'
        if review_file in names:
            review = read_json(review_file); latest_review = review.get('date')
        elif n in [384,385]:
            review_file = PACKAGE + '/validation-completion-384-385.json'
            review = read_json(review_file); latest_review = review.get('date')
        else:
            latest_review = None; review_file = None
        # A deep pass can leave earlier note-only addenda separate from this date.
        model_label = '; '.join(models) if models else 'Not recorded in the located public metadata'
        model_notes = 'Labels/families reproduced as recorded. Exact release/build and later curator deployment are not established by these labels; no public product version is inferred.'
        heading = re.search(r'^## Complete working reading.*$', text, re.M)
        anchor = '#complete-working-reading--28-october-2026' if heading and '28 October 2026' in heading.group() else ''
        if heading and not anchor:
            anchor = '#' + re.sub(r'[^\w\- ]', '', heading.group()[3:].lower()).replace(' ', '-')
        reading_url = url(md_path) + anchor
        model_status = 'recorded_label_or_family' if models else 'not_recorded'
        agent_proof = proof(queue_path, f'/cards/{qi}/independent_ai_source_check', q['independent_ai_source_check'])
    else:
        selected_date = explicit_legacy_dates.get(n)
        basis = 'Research/first replay date explicitly stated in the preserved report.' if selected_date else 'Exact decipherment/research date not stated. Original report publication is recorded on 2026-10-05 and is not substituted for the research date.'
        if n == 204: basis = 'Contribution packet preparation date explicitly stated in the preserved report; external check reported separately on 2026-10-20.'
        if selected_date:
            matches = [line for line in text.splitlines() if re.search(r'(Research result|Research recorded|First replay recorded|recorded 6 October|packet, prepared on)', line)]
            assert matches, n
            date_proofs = [dict(path=path, exact_text=matches[0], snapshot_sha256=digest(original(path)), url=url(path), value=selected_date)]
        model_label = 'Not recorded in the preserved public report'
        model_notes = 'Do not infer a model/version from neighbouring cards or from the model used to prepare this inventory.'
        model_status = 'not_recorded'
        ai_role = 'AI-assisted source/language research and preparation of the preserved partial report; deterministic replay where documented. Exact division of labour is not fully recorded.'
        agents = 'Not recorded in the preserved public report; separate reviews alone do not establish an orchestration count.'
        workflow = 'historical_workflow_not_fully_recorded'
        agent_proof = None
        status = 'Partial historical reading under the staged legacy model; not a fresh canonical-key solve.'
        if n == 204: status = 'Partial contribution reading; external validity/key-consistency confirmation received on 2026-10-20. Original alternatives remain.'
        root_status = None; coverage = 'Preserved partial report'; latest_review = None; review_file = None; reading_url = url(md_path)
    prior_report = legacy.get(n)
    r = dict(card_id=n, record_name=f'pc_hcp_{n}', catalogue_record_id=q['catalogue_ids'][0], catalogue_url=q['catalogue_url'],
             date_of_decipherment=selected_date, date_basis=basis, date_evidence=date_proofs,
             ai_model_and_version=model_label, ai_model_evidence=model_proofs, model_metadata_status=model_status, model_version_notes=model_notes,
             role_of_AI=ai_role, AI_agents_used=agents, workflow_category=workflow, agent_evidence=agent_proof,
             decipherment_record_url=reading_url, reading_path=md_path, reading_sha256=digest(original(md_path)),
             evidence_url=url(path), evidence_path=path, evidence_sha256=digest(original(path)),
             result_status=status, current_record_status=root_status, working_coverage_stage=coverage,
             first_repository_commit=publication_commit, first_repository_commit_author_at=publication_time,
             first_repository_commit_url='https://github.com/Cipher-Atelier/anna-ticha-cipher-postcards/commit/'+publication_commit,
             latest_dated_source_completion=latest_review, latest_source_completion_url=url(review_file) if review_file else None,
             earlier_or_preserved_report_url=url(prior_report) if prior_report else None)
    records.append(r)

coord = json.loads((HERE/'coordination.json').read_text())
remaining = set(catalogue)-set(ids)
assert set(coord['planned_team_card_ids']) == remaining-{460}
summary = dict(published_readings_including_partial=154, current_canonical_candidates=137, legacy_only_reports=17,
               catalogue_cards=263, without_our_separate_reading=109, planned_team_cards=108,
               current_pass_working_coverage=67, current_pass_remaining=70, next_existing_card=319,
               recorded_reading_dates=sum(r['date_of_decipherment'] is not None for r in records),
               missing_exact_reading_dates=sum(r['date_of_decipherment'] is None for r in records),
               model_labels_or_families_recorded=sum(r['model_metadata_status']!='not_recorded' for r in records),
               no_recorded_model_label=sum(r['model_metadata_status']=='not_recorded' for r in records),
               workflow_categories=dict(Counter(r['workflow_category']for r in records)))
payload=dict(schema='hcportal-ai-decipherment-submission-v1',prepared_date='2026-10-28',snapshot_commit=BASE,
             purpose='One row per published card reading, including partial proposals, for curator review before register classification.',
             field_definitions=dict(date_of_decipherment='Date of recorded working reading/freeze/reconciliation or contribution packet where documented. Null means unavailable. This never certifies a complete decipherment. See date_basis and separate commit author timestamp.',
                                    AI_agents_used='Source-reading workflow only. Paired means separately assigned related AI source-reader tasks, not human/external independence or a total count of all agents over the project.',
                                    ai_model_and_version='Exact retained label/family, with evidence pointers. Internal model labels are not converted into guessed public release names. Exact deployment/build and some later curator models are unavailable.',
                                    result_status='137 provisional canonical candidates plus 17 legacy-only partial records. Only 204 has the separate external confirmation; 460 is excluded as another team result.'),
             summary=summary,records=records)
dump('register.json',payload)
columns=['record_name','date_of_decipherment','date_basis','ai_model_and_version','model_version_notes','role_of_AI','AI_agents_used','decipherment_record_url','result_status','catalogue_record_id','catalogue_url','first_repository_commit_author_at','latest_dated_source_completion','evidence_url']
stream=io.StringIO(newline='');writer=csv.DictWriter(stream,fieldnames=columns,lineterminator='\n');writer.writeheader()
for r in records:writer.writerow({k:r[k] if r[k] is not None else 'Not recorded' for k in columns})
(HERE/'register.csv').write_text(stream.getvalue())
md='# Anna Tichá: individual reading records\n\nPrepared 28 October 2026 from snapshot [`'+BASE[:12]+'`](https://github.com/Cipher-Atelier/anna-ticha-cipher-postcards/commit/'+BASE+'). One row per card. Dates refer to recorded working readings; unknown research dates stay unknown. [Field definitions and scope](README.md) · [CSV](register.csv) · [Complete JSON with metadata evidence](register.json)\n\n**154 readings including partial: 137 canonical-key candidates and 17 legacy-only reports. Only card 204 has the separate external confirmation.** A direct text link opens each individual report. The machine-readable files contain all six requested fields and their qualifications.\n\n| Record / catalogue ID | Reading date | Recorded AI model or family | Source-reader workflow | Status | Text |\n| --- | --- | --- | --- | --- | --- |\n'
for r in records:
    def esc(s):return str(s).replace('|','\\|').replace('\n',' ')
    status='External check; partial' if r['card_id']==204 else 'Provisional canonical' if r['card_id']in candidates else 'Historical partial'
    date=r['date_of_decipherment']or 'Not recorded (publication 5 Oct)'
    md+='| [`'+r['record_name']+'`]('+r['catalogue_url']+') / '+str(r['catalogue_record_id'])+' | '+date+' | '+esc(r['ai_model_and_version'])+' | '+{'paired_related_AI_readers':'Paired related AI readers','single_root_AI_reader':'Single root AI reader','historical_workflow_not_fully_recorded':'Not fully recorded'}[r['workflow_category']]+' | '+status+' | [Read text]('+r['decipherment_record_url']+') · [Evidence]('+r['evidence_url']+') |\n'
(HERE/'register.md').write_text(md)
rows=['# Planned work by Eugen Antal and team','', 'Announcement: 28 October 2026. These 108 cards have no separate reading in this repository snapshot. Planned work does not imply a completed decipherment or external validation. Card 460 remains the team’s separate comparison result. [Machine-readable coordination](coordination.json) · [Submission overview](README.md)','', '| Record | Catalogue ID | HCPortal |','| --- | --- | --- |']
for n in coord['planned_team_card_ids']:
    q=catalogue[n][1];rows.append(f"| pc_hcp_{n} | {q['catalogue_ids'][0]} | [Record]({q['catalogue_url']}) |")
(HERE/'coordination.md').write_text('\n'.join(rows)+'\n')
print(json.dumps(summary))
