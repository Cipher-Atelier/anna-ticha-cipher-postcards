import argparse,hashlib,json,platform,random,sys,time
from pathlib import Path
import numpy as np
from build_counts import build,ALPHABET
from finite_model import Model,optimize,table,endpoint,permutation,validate
ROOT=Path(__file__).resolve().parent.parent

def collapse(runs):
    out=[]
    for r in runs:
        v=[];i=0
        while i<len(r):
            if r[i:i+2]==[2,7]:v.append(26);i+=2
            else:v.append(r[i]);i+=1
        out.append(v)
    return out

def packet(runs):return {'classes':[{'id':f'N{i+1:03d}'} for i in range(27)],'variants':[{'id':'V001','runs':[[f'N{i+1:03d}' for i in r] for r in runs]}],'common_identity_stable_occurrences':sum(map(len,runs))}
def execute(model,dev,held,truth=None):
    require_class_order(held,[c['id'] for c in dev['classes']]);dv=validate(dev);hv=validate(held,True);k,keys,bests,ev=optimize(model,dv)
    dt=table(model,keys,dv);ht=table(model,keys,hv)
    baseline=[permutation(random.Random(s)) for s in range(2000,2064)]
    shuffles=[]
    for seed in range(9000,9016):
        rng=random.Random(seed);vs=[]
        for vid,runs in hv:
            rr=[]
            for run in runs:
                a=list(run);rng.shuffle(a);rr.append(a)
            vs.append((vid,rr))
        shuffles.append({'seed':seed,'scores':table(model,[k],vs)[0]})
    result={'Kstar':k,'keys':keys,'restart_bests':bests,'development_evaluations':ev,'development_tables':dt,'held_tables':ht,'endpoint':endpoint(ht),'baseline_keys':baseline,'baseline_development_tables':table(model,baseline,dv),'baseline_held_tables':table(model,baseline,hv),'within_run_held_shuffles':shuffles,'diagnostic_warning':'Baselines and shuffles are descriptive; no p-value, no refit, no endpoint change.'}
    if truth:
        used=set(c for _,runs in dv+hv for r in runs for c in r)
        def emit(key,runs):return ''.join(ALPHABET[key[c]] for r in runs for c in r)
        # Alignment by source unit avoids displacement from differing ch widths.
        exact=sum(k[c]==truth[c] for c in used)
        chars=correct=error=0
        for _,runs in hv:
            for r in runs:
                for c in r:
                    t=ALPHABET[truth[c]];p=ALPHABET[k[c]];chars+=len(t)
                    correct+=sum(i<len(p) and p[i]==x for i,x in enumerate(t));error+=max(len(t),len(p))-sum(i<len(p) and p[i]==x for i,x in enumerate(t))
        result['truth']={'key':truth,'used_class_count':len(used),'correct_used_classes':exact,'used_class_recovery_fraction':exact/len(used),'held_true_emitted_characters':chars,'held_correct_aligned_characters':correct,'held_character_recovery_fraction':correct/chars,'held_character_errors_including_insertions':error,'held_error_per_true_emitted_character':error/chars,'development_scores':table(model,[truth],dv)[0],'held_scores':table(model,[truth],hv)[0],'warning':'Model-backed synthetic sample, not independent corpus validation; character comparison aligned within each source unit.'}
    return result

def main():
    args=argparse.Namespace();out=ROOT/'results';out.mkdir(exist_ok=True)
    count=ROOT/'assets/counts.npz';provenance=build(ROOT/'assets/listy_I.txt',count);model=Model(count)
    manifest={'corpus':provenance,'pdf_sha256':'904b56685abd379dcfa458b3708310c7e369f56d352558c36c2b9070c2c35798','extraction':'pdftotext 26.10.0; full 217 pages UTF-8; supplied provenance','runtime':{'python':sys.version,'numpy':np.__version__,'platform':platform.platform()},'PRNG':'Python random.Random seeded MT19937; random(), sample(), shuffle(), choices()','arguments':vars(args),'budget':{'restarts':16,'proposals_per_restart':2000,'variant_limit':64},'alphabet':ALPHABET,'temperature':'exp(log(.01)*step/1999)','tie_tolerance':1e-9,'code_sha256':{f.name:hashlib.sha256(f.read_bytes()).hexdigest() for f in sorted((ROOT/'code').glob('*.py'))}}
    (out/'input-manifest.json').write_text(json.dumps(manifest,indent=2))
    for kind,seeds in [('markov',[101,102,103]),('iid',[901,902,903])]:
        for seed in seeds:
            rng=random.Random(seed)
            if kind=='markov':
                dr=collapse(model.sample(rng,256));hr=collapse(model.sample(rng,128));truth=permutation(random.Random(seed+10000));inv={t:c for c,t in enumerate(truth)};dr=[[inv[t] for t in r] for r in dr];hr=[[inv[t] for t in r] for r in hr]
            else:
                def iid(n):return [[rng.randrange(27) for _ in range(min(12,n-i))] for i in range(0,n,12)]
                dr=iid(256);hr=iid(128);truth=None
            dev=packet(dr);held=packet(hr);start=time.time();result=execute(model,dev,held,truth);result.update({'kind':kind,'seed':seed,'development_input':dev,'held_input':held,'elapsed_seconds':time.time()-start,'interpretation':'False-positive risk control; no plaintext truth' if kind=='iid' else 'Model-backed generated sample; not independent corpus validation'})
            (out/f'control-{kind}-{seed}.json').write_text(json.dumps(result,indent=2));print(kind,seed,result['endpoint']['status'],result.get('truth',{}).get('used_class_recovery_fraction'),flush=True)

def file_hash(path):
    return hashlib.sha256(Path(path).read_bytes()).hexdigest()

def code_hashes():
    return {f.name:file_hash(f) for f in sorted((ROOT/'code').glob('*.py'))}

def require_class_order(packet, frozen_ids):
    ids=[c['id'] for c in packet['classes']]
    if ids!=frozen_ids:
        raise ValueError('UNAVAILABLE: held class IDs/order differ from frozen development slots')

def learn_development(devpath, freeze_path):
    if Path(freeze_path).exists():raise FileExistsError('Development freeze already exists')
    raw=Path(devpath).read_bytes();dev=json.loads(raw);dv=validate(dev)
    counts=ROOT/'assets/counts.npz'
    if not counts.is_file():raise ValueError('Pinned count table missing; no rebuild permitted')
    model=Model(counts);k,keys,bests,ev=optimize(model,dv)
    baselines=[permutation(random.Random(seed)) for seed in range(2000,2064)]
    frozen={'schema':'development-freeze-v2','development_sha256':hashlib.sha256(raw).hexdigest(),
      'development_input':dev,'class_slot_order':[c['id'] for c in dev['classes']],
      'Kstar':k,'keys':keys,'restart_bests':bests,'development_evaluations':ev,
      'development_tables':table(model,keys,dv),'baseline_keys':baselines,
      'baseline_seeds':list(range(2000,2064)), 'baseline_development_tables':table(model,baselines,dv),
      'counts_sha256':file_hash(counts),'code_sha256':code_hashes(),
      'runtime':{'python':sys.version,'numpy':np.__version__},
      'method_sha256':file_hash(ROOT.parent/'key-foundation-audit-next-20261013/one-practical-rebuild-test-v1.json')}
    # Exclusive creation prevents replacing an existing prospective freeze.
    with Path(freeze_path).open('x') as f:json.dump(frozen,f,indent=2)
    return frozen

def evaluate_held(freeze_path, heldpath, output):
    frozen_raw=Path(freeze_path).read_bytes();frozen=json.loads(frozen_raw)
    if frozen['schema']!='development-freeze-v2':raise ValueError('Unexpected freeze schema')
    if frozen['code_sha256']!=code_hashes():raise ValueError('Frozen code hash mismatch')
    counts=ROOT/'assets/counts.npz'
    if file_hash(counts)!=frozen['counts_sha256']:raise ValueError('Frozen counts hash mismatch')
    if frozen['runtime']!={'python':sys.version,'numpy':np.__version__}:raise ValueError('Frozen runtime mismatch')
    raw=Path(heldpath).read_bytes();held=json.loads(raw)
    require_class_order(held,frozen['class_slot_order']);hv=validate(held,True)
    model=Model(counts);keys=frozen['keys'];rows=table(model,keys,hv)
    baseline_rows=table(model,frozen['baseline_keys'],hv);shuffles=[]
    for seed in range(9000,9016):
        rng=random.Random(seed);vs=[]
        for vid,runs in hv:
            rr=[]
            for run in runs:
                a=list(run);rng.shuffle(a);rr.append(a)
            vs.append((vid,rr))
        shuffles.append({'seed':seed,'scores':table(model,[frozen['Kstar']],vs)[0]})
    result={'schema':'held-evaluation-v2','freeze_sha256':hashlib.sha256(frozen_raw).hexdigest(),
      'held_sha256':hashlib.sha256(raw).hexdigest(),'held_input':held,'held_tables':rows,
      'endpoint':endpoint(rows),'baseline_held_tables':baseline_rows,'within_run_held_shuffles':shuffles,
      'held_ranks_per_variant':[[1+sum(r[v]['score']>a['score']+1e-9 for r in rows) for v,a in enumerate(row)] for row in rows],
      'optimizer_calls':0,'counttable_build_calls':0,'diagnostic_warning':'No p-value; no refit; no historical truth claim.'}
    with Path(output).open('x') as f:json.dump(result,f,indent=2)
    return result

def phase_cli():
    parser=argparse.ArgumentParser()
    mode=parser.add_mutually_exclusive_group(required=True)
    mode.add_argument('--controls',action='store_true')
    mode.add_argument('--learn-development',metavar='PACKET')
    mode.add_argument('--evaluate-held',metavar='PACKET')
    parser.add_argument('--freeze');parser.add_argument('--output')
    args=parser.parse_args()
    if args.controls:
        if args.freeze or args.output:parser.error('controls does not accept freeze/output')
        sys.argv=[sys.argv[0]];main()
    elif args.learn_development:
        if not args.freeze or args.output:parser.error('learning requires --freeze and no --output')
        learn_development(args.learn_development,args.freeze)
    else:
        if not args.freeze or not args.output:parser.error('held evaluation requires --freeze and --output')
        evaluate_held(args.freeze,args.evaluate_held,args.output)
if __name__=='__main__':phase_cli()
