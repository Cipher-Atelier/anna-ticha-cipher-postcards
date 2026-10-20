"""Exact native crops and non-semantic fixed-threshold component proposals."""
import argparse, hashlib, json
from pathlib import Path
from collections import deque
from PIL import Image

THRESHOLDS = (65, 85, 105, 125)
ROI = (170, 815, 1710, 905)
def sha(b): return hashlib.sha256(b).hexdigest()
def components(gray, threshold, offset=(0, 0)):
    w, h = gray.size
    foreground = {i for i, v in enumerate(gray.tobytes()) if v <= threshold}
    remaining = set(foreground)
    result = []
    while remaining:
        seed = min(remaining); remaining.remove(seed)
        q = deque([seed]); pixels = {seed}
        while q:
            i = q.popleft(); x, y = i % w, i // w
            for dy in (-1, 0, 1):
                for dx in (-1, 0, 1):
                    nx, ny = x+dx, y+dy
                    if 0 <= nx < w and 0 <= ny < h:
                        j = ny*w+nx
                        if j in remaining:
                            remaining.remove(j); pixels.add(j); q.append(j)
        xs = [i % w for i in pixels]; ys = [i // w for i in pixels]
        runs = []
        for y in sorted(set(ys)):
            row = sorted(i % w for i in pixels if i // w == y)
            start = end = row[0]
            for x in row[1:]:
                if x == end+1: end = x
                else: runs.append([y+offset[1], start+offset[0], end+1+offset[0]]); start=end=x
            runs.append([y+offset[1], start+offset[0], end+1+offset[0]])
        result.append({'id':len(result), 'area':len(pixels), 'native_bbox_xyxy_halfopen':[min(xs)+offset[0],min(ys)+offset[1],max(xs)+1+offset[0],max(ys)+1+offset[1]], 'native_pixel_rle_y_xstart_xend_halfopen':runs, 'status':'unknown: connectivity mask, not glyph or semantic assignment', '_pixels':pixels})
    projection = [sum(y*w+x in foreground for y in range(h)) for x in range(w)]
    return result, projection
def relations(a,b):
    edges=[]
    for ca in a:
        for cb in b:
            intersection=ca['_pixels'] & cb['_pixels']
            if intersection:
                edges.append({'from_id':ca['id'],'to_id':cb['id'],'intersection_area':len(intersection),'intersection_roi_linear_indices':sorted(intersection)})
    from_counts={c['id']:sum(e['from_id']==c['id'] for e in edges) for c in a}
    to_counts={c['id']:sum(e['to_id']==c['id'] for e in edges) for c in b}
    for e in edges:
        e['from_degree']=from_counts[e['from_id']];e['to_degree']=to_counts[e['to_id']]
        e['relation']='split_and_merge' if e['from_degree']>1 and e['to_degree']>1 else 'split' if e['from_degree']>1 else 'merge' if e['to_degree']>1 else 'overlap'
    return edges
def main():
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument('input', help='locally supplied verified original JPEG')
    parser.add_argument('output_root', help='local private output directory')
    args=parser.parse_args()
    SOURCE=Path(args.input); BASE=Path(args.output_root)
    (BASE/'private-pixels').mkdir(parents=True, exist_ok=True)
    (BASE/'results').mkdir(parents=True, exist_ok=True)
    raw=SOURCE.read_bytes()
    assert len(raw)==1288265 and sha(raw)=='7407bb54bcfbf69af61d801fb04a0b4de8fce9d8c24976ba1a3f4c3f2120aae4'
    rgb=Image.open(SOURCE).convert('RGB')
    assert rgb.size==(1785,1175) and sha(rgb.tobytes())=='5861cd6fe98334bc983dda575a6c36bb3222e73a71329865a42e8cc492f2db94'
    provenance={'original':{'basename':SOURCE.name,'bytes':len(raw),'sha256':sha(raw),'decoded_RGB_size':rgb.size,'decoded_RGB_sha256':sha(rgb.tobytes())},'crops':[], 'policy':'Internal pixels only; no resize, filtering, enhancement, OCR, retouching, or watermark removal. ROI includes neighboring line ascender residuals; not an isolated line.'}
    for name, box in [('roi',ROI)]+[(f'audit_{n+1}',(x,815,min(x+280,1710),905)) for n,x in enumerate((170,430,690,950,1210,1470))]:
        crop=rgb.crop(box); path=BASE/'private-pixels'/f'{name}.png';crop.save(path)
        reopened=Image.open(path).convert('RGB');assert reopened.tobytes()==crop.tobytes()
        # Explicit independent original row slice verifies crop pixel bytes.
        original=rgb.tobytes(); x0,y0,x1,y1=box
        sliced=b''.join(original[(y*rgb.width+x0)*3:(y*rgb.width+x1)*3] for y in range(y0,y1))
        assert reopened.tobytes()==sliced
        provenance['crops'].append({'basename':path.name,'native_bbox_xyxy_halfopen':box,'offset_xy':box[:2],'RGB_size':crop.size,'RGB_bytes':len(sliced),'RGB_sha256':sha(sliced),'PNG_bytes':path.stat().st_size,'PNG_sha256':sha(path.read_bytes()),'exact_original_slice_verified':True})
    (BASE/'results'/'provenance.json').write_text(json.dumps(provenance,indent=2))
    gray=rgb.crop(ROI).convert('L'); allc={};pack={'roi_native_xyxy_halfopen':ROI,'foreground_rule':'Pillow RGB.convert(L), L <= threshold; thresholds fixed before inspection','scope':'First horizontal manuscript band only; partial full card, not exhaustive. Contains neighbor-line ascender residuals. All masks and detached area-1 marks retained as unknown. Threshold-white is not raw whitespace or a body boundary.','thresholds':{},'cross_threshold_relations':{}}
    for t in THRESHOLDS:
        cs,proj=components(gray,t,ROI[:2]);allc[t]=cs
        pack['thresholds'][str(t)]={'component_count':len(cs),'foreground_pixels':sum(proj),'column_projection':proj,'strict_zero_foreground_native_columns':[x+ROI[0] for x,n in enumerate(proj) if n==0],'components':[{k:v for k,v in c.items() if k!='_pixels'} for c in cs]}
    for n,low in enumerate(THRESHOLDS):
        for high in THRESHOLDS[n+1:]:
            pack['cross_threshold_relations'][f'{low}_to_{high}']=relations(allc[low],allc[high])
    pack['quality_diagnostics']={'description':'Fixed luminance masks describe dark pixels only. Dark ink, overlay/watermark, background speckle, and neighboring residuals have no automatic class or ownership. No preferred threshold selected.','grayscale_min':min(gray.tobytes()),'grayscale_max':max(gray.tobytes()),'luminance_histogram':gray.histogram()}
    output=BASE/'results'/'candidate_pack.json';output.write_text(json.dumps(pack,indent=2))
    summary={'candidate_pack_sha256':sha(output.read_bytes()),'counts':{str(t):len(allc[t]) for t in THRESHOLDS},'provenance_sha256':sha((BASE/'results'/'provenance.json').read_bytes())}
    (BASE/'results'/'summary.json').write_text(json.dumps(summary,indent=2));print(json.dumps(summary))
if __name__=='__main__':main()
