import hashlib,json,re,unicodedata
from collections import Counter
from pathlib import Path
import numpy as np
ALPHABET=tuple('abcdefghijklmnopqrstuvwxyz')+('ch',)
def normalized_runs(text):
    s=''.join(c for c in unicodedata.normalize('NFKD',text) if not unicodedata.combining(c)).lower()
    return re.findall('[a-z]+',s)
def build(path,out):
    raw=Path(path).read_bytes(); runs=normalized_runs(raw.decode('utf8')); counts=[Counter() for _ in range(4)]
    for run in runs:
        for i in range(len(run)):
            for n in range(1,min(4,i+1)+1): counts[n-1][run[i-n+1:i+1]]+=1
    tables=[]
    for n,C in enumerate(counts):
        arr=np.zeros((26**n,26),dtype=np.int64)
        for gram,count in C.items():
            ctx=0
            for c in gram[:-1]:ctx=ctx*26+ord(c)-97
            arr[ctx,ord(gram[-1])-97]=count
        tables.append(arr)
    np.savez(out,**{f'order{i+1}':a for i,a in enumerate(tables)})
    return {'text_sha256':hashlib.sha256(raw).hexdigest(),'bytes':len(raw),'runs':len(runs),'characters':sum(map(len,runs)),'ngram_totals':[int(a.sum()) for a in tables],'counttable_sha256':hashlib.sha256(Path(out).read_bytes()).hexdigest(),'normalization':'NFKD; strip combining; lowercase; ASCII a-z; nonletters break runs','smoothing':0.1}
