import math,random
import numpy as np
from build_counts import ALPHABET
TOL=1e-9
class Model:
    def __init__(self,path):
        data=np.load(path);self.counts=[data[f'order{i}'] for i in range(1,5)]
        self.logs=[np.log((a+.1)/(a.sum(axis=1,keepdims=True)+2.6)) for a in self.counts]
    def score(self,key,runs):
        total=0.;chars=units=0
        for run in runs:
            if not run:continue
            tokens=np.asarray(key)[run]; a=np.empty(len(run)*2,dtype=np.int64); p=0
            for t in tokens:
                if t==26:a[p:p+2]=[2,7];p+=2
                else:a[p]=t;p+=1
            a=a[:p];chars+=p;units+=len(run)
            total+=self.logs[0][0,a[0]]
            if p>1:total+=self.logs[1][a[0],a[1]]
            if p>2:total+=self.logs[2][a[0]*26+a[1],a[2]]
            if p>3:total+=float(self.logs[3][a[:-3]*676+a[1:-2]*26+a[2:-1],a[3:]].sum())
        return {'score':float(total/chars) if chars else None,'log_sum':float(total),'emitted_characters':chars,'mapped_source_units':units}
    def sample(self,rng,n,maxrun=12):
        runs=[]
        while n:
            run=[]
            for _ in range(min(maxrun,n)):
                ctx=0
                for c in run[-3:]:ctx=ctx*26+c
                w=self.counts[min(3,len(run))][ctx]+.1
                run.append(rng.choices(range(26),weights=w,k=1)[0]);n-=1
            runs.append(run)
        return runs
def validate(packet,held=False):
    ids=[c['id'] for c in packet['classes']]
    if len(ids)!=len(set(ids)) or not 7<=len(ids)<=27:raise ValueError('UNAVAILABLE: classes')
    variants=packet['variants']
    if not 1<=len(variants)<=64:raise ValueError('UNAVAILABLE: variants')
    vids=[v.get('id') for v in variants]
    if any(not isinstance(v,str) or not v for v in vids) or len(vids)!=len(set(vids)):raise ValueError('UNAVAILABLE: variant IDs')
    common=packet['common_identity_stable_occurrences'];minimum=80 if held else 150
    if type(common) is not int or common<minimum:raise ValueError('UNAVAILABLE: common occurrences')
    ix={v:i for i,v in enumerate(ids)};result=[]
    for v in variants:
        runs=v['runs']
        if not isinstance(runs,list) or any(not isinstance(r,list) for r in runs):raise ValueError('UNAVAILABLE: runs')
        if sum(map(len,runs))<max(common,minimum):raise ValueError('UNAVAILABLE: mapped occurrences below certified claim')
        if any(c not in ix for r in runs for c in r):raise ValueError('UNAVAILABLE: unknown class')
        result.append((v['id'],[[ix[c] for c in r] for r in runs]))
    return result
def permutation(rng):
    key=list(range(27));rng.shuffle(key);return tuple(key)
def lex(key):return tuple(ALPHABET[x] for x in key)
def better(s,k,t,l):return s>t+TOL or (abs(s-t)<=TOL and lex(k)<lex(l))
def optimize(model,variants):
    best=[];evaluations=0
    def score(k):
        nonlocal evaluations
        evaluations+=len(variants)
        return min(model.score(k,r)['score'] for _,r in variants)
    for seed in range(16):
        rng=random.Random(seed);key=permutation(rng);s=score(key);bk=key;bs=s
        for step in range(2000):
            i,j=rng.sample(range(27),2);v=list(key);v[i],v[j]=v[j],v[i];v=tuple(v);t=score(v);d=t-s
            if d>0 or rng.random()<math.exp(min(0,d/math.exp(math.log(.01)*step/1999))):key,s=v,t
            if better(t,v,bs,bk):bk,bs=v,t
        best.append({'seed':seed,'key':bk,'worst_score':bs})
    winner=best[0]
    for b in best[1:]:
        if better(b['worst_score'],b['key'],winner['worst_score'],winner['key']):winner=b
    k=winner['key'];keys=[k]+[b['key'] for b in best if b is not winner]
    for i in range(27):
        for j in range(i+1,27):
            v=list(k);v[i],v[j]=v[j],v[i];keys.append(tuple(v))
    keys=list(dict.fromkeys(keys));return k,keys,best,evaluations
def table(model,keys,variants):return [[model.score(k,r) for _,r in variants] for k in keys]
def endpoint(rows):
    if any(x['score'] is None or x['emitted_characters']<50 for row in rows for x in row):return {'status':'UNAVAILABLE'}
    margins=[[a['score']-b['score'] for a,b in zip(rows[0],row)] for row in rows[1:]]
    winners=[i+1 for i,m in enumerate(margins) if max(m)<-TOL]
    return {'status':'ROBUST_SUPPORT' if all(min(m)>TOL for m in margins) else 'ROBUST_COUNTEREXAMPLE' if winners else 'NONUNIQUE','margins':margins,'counterexample_indices':winners}
