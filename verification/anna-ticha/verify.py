#!/usr/bin/env python3
"""Offline, read-only verification of the public text/data package."""
from pathlib import Path
import argparse,csv,hashlib,json,sys,struct
P=Path(__file__).resolve().parent
R=lambda s:json.loads((P/s).read_text(encoding='utf-8'))
S=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
def require(ok,what):
 if not ok:raise AssertionError(what)
def main():
 ap=argparse.ArgumentParser(description=__doc__);ap.add_argument('--source-dir',type=Path,help='Also verify originals and all 599 crop pixel arrays; requires Pillow.');args=ap.parse_args()
 inv=R('PUBLIC_INVENTORY_SHA256.json')
 for f in inv['files']:require(S(P/f['path'])==f['sha256'],'Changed public file: '+f['path'])
 expected={'frozen/key.json':'61877fb4366d8712865c7d6557d920a61f5a752d2d7b1a44da6d350439254a56','frozen/rules.json':'2c9ecfbeb3f2898342d00f2b564d9c7f798ea38fda16675398a695ab59db5ddc','frozen/tokens.json':'56e7f5aef953a69a1192aa794db64d9bcef106a6e4d84e6e3bed12377688b7c8','frozen/features.json':'344d9dcff1802714f2d9aaebf1739549bc8fefd18f75420fadbc7c11b3e12262'}
 for f,h in expected.items():require(S(P/f)==h,'Retained research hash: '+f)
 toks=R('frozen/tokens.json');rr=[r for r in toks['positions'] if r['kind']=='body'];key=R('frozen/key.json')['plaintext_mapping'];rules=R('frozen/rules.json');receipt=R('frozen/first_receipt.json')
 require(len(rr)==532 and [r['body_index_in_canonical_listing'] for r in rr]==list(range(1,533)),'532 sequential bodies');require(len(key)==24,'24 fixed entries')
 vals=[key.get(r['fullform_id'],'?') for r in rr];out=[];region=line=group=None
 for r,v in zip(rr,vals):
  if r['region']!=region:
   if out:out.append('')
   out.append('=== SOURCE REGION '+r['region']+' ===');region=r['region'];line=None
  if r['line_id']!=line:out.append('');line=r['line_id'];group=None
  elif r['group']!=group:out[-1]+=' '
  out[-1]+=v;group=r['group']
 literal=('\n'.join(out)+'\n').encode();require(literal==(P/'literal.txt').read_bytes(),'Exact historical literal bytes');require(hashlib.sha256(literal).hexdigest()==receipt['primary_literal_sha256']=='b7aa7b869b73efa7a0907b48a655833cfd9b75128be0db7126b1880bd0798832','Historical literal hash')
 require(sum(v!='?' for v in vals)==522 and sum(len(v) for v in vals if v!='?')==524,'Mapped/character counts');require(len({r['fullform_id'] for r in rr if r['fullform_id'] in key})==23,'23 observed key families')
 feats=R('frozen/features.json')['positions'];require({f['token_id'] for f in feats}=={r['token_id'] for r in rr if r['fullform_id']=='UNKNOWN'},'Every unknown reviewed')
 for f in feats:
  good=(len(f['definite_base_family_candidates'])==1 and len(f['all_base_candidates'])==1 and f['base_confidence']=='high' and f['mark_type_confidence']=='high' and f['mark_ownership_confidence']=='high' and f['mark_type'] in rules['geometry_functions'] and not f['cancelled_or_overwritten_confirmed'] and not f['cancellation_or_overwriting_uncertain'] and not f['unmarked_new_shape_flag'])
  require(good==f['eligible']==False,'Secondary eligibility')
 flat=R('data/card199_positions.json')['positions'];require(len(flat)==532,'Derived table length')
 with (P/'data/card199_positions.csv').open(encoding='utf-8-sig',newline='') as f:csvrows=list(csv.DictReader(f))
 require(len(csvrows)==532,'CSV length')
 for a,b,c,v in zip(rr,flat,csvrows,vals):
  for x,y in [('token_id','token_id'),('body_index_in_canonical_listing','body_index'),('fullform_id','class_id'),('original_bbox_xyxy','original_bbox_xyxy'),('oriented_bbox_xyxy','oriented_bbox_xyxy'),('orientation','orientation')]:require(a[x]==b[y],'Derived table record '+a['token_id'])
  require(b['literal']==c['literal']==v and c['token_id']==a['token_id'],'CSV literal/position')
 atlas=R('data/glyph_atlas.json');require({a['class_id']:a['literal'] for a in atlas}==key,'Atlas unchanged key');byid={r['token_id']:r for r in rr};c440={r['source_position_id']:r for r in R('data/card440_atlas_records.json')}
 for a in atlas:
  require(len(a['examples'])>=1,'Image reference for every class')
  for e in a['examples']:
   r=byid[e['token_id']] if e['card']==199 else c440[e['token_id']];cls=r['fullform_id'] if e['card']==199 else r['token_id'];bb=r['original_bbox_xyxy'] if e['card']==199 else r['source_context_bbox_xyxy'];require(cls==a['class_id'] and bb==e['original_bbox_xyxy'],'Atlas provenance '+e['token_id'])
 # Embedded viewer data must be the same public data, not a stale preview.
 import re
 match=re.search(r'<script id="data" type="application/json">(.*?)</script>',(P/'viewer.html').read_text(),re.S);require(match is not None,'Viewer data block');vd=json.loads(match.group(1).replace('<\\/','</'))
 for k,path in [('sources','data/sources.json'),('atlas','data/glyph_atlas.json'),('lines','data/line_coordinates.json'),('marks','data/mark_examples.json')]:require(vd[k]==R(path),'Viewer data '+k)
 require(vd['positions']==flat and vd['literal'].encode()==literal,'Viewer positions/literal')
 print('PASS: public inventory; exact retained key/rules/tokens; all 532 CSV/JSON rows; 24 atlas classes; unchanged viewer data')
 print('PASS: 522 mapped, 10 unknown, 524 emitted characters, 23 observed classes, no secondary transformation')
 print('PASS: exact historical literal SHA-256 '+hashlib.sha256(literal).hexdigest())
 if args.source_dir:
  from PIL import Image
  ims={}
  for s in R('data/sources.json'):
   p=args.source_dir/Path(s['file']).name;require(S(p)==s['sha256'],'Source JPEG '+p.name);ims[s['card']]=Image.open(p).convert('RGB');require(list(ims[s['card']].size)==s['size_pixels'],'Source dimensions')
  turns={'CCW90':Image.Transpose.ROTATE_90,'CW90':Image.Transpose.ROTATE_270};checks=R('data/crop_pixel_checksums.json')['crops']
  for x in checks:
   im=ims[x['card']].crop(tuple(x['original_bbox_xyxy']))
   if x['orientation'] in turns:im=im.transpose(turns[x['orientation']])
   require(hashlib.sha256(struct.pack('>II',*im.size)+im.tobytes()).hexdigest()==x['rgb_pixel_sha256'],'Crop pixels '+x['id'])
  print('PASS: 3 original source hashes and '+str(len(checks))+' exact crop pixel arrays')
 print('LIMIT: deterministic replay is not proof of correct source classification, historical truth, authorship or priority.')
if __name__=='__main__':
 try:main()
 except Exception as e:print('FAIL:',e,file=sys.stderr);sys.exit(1)
