#!/usr/bin/env python3
"""Explicit optional source download and local-only crop preview. Never uploads anything."""
from pathlib import Path
import argparse,hashlib,json,sys,html,struct,urllib.request,urllib.parse
P=Path(__file__).resolve().parent
R=lambda n:json.loads((P/n).read_text(encoding='utf-8'))
def sha(b):return hashlib.sha256(b).hexdigest()
class SameHostRedirect(urllib.request.HTTPRedirectHandler):
 def redirect_request(self,req,fp,code,msg,headers,newurl):
  if urllib.parse.urlparse(newurl).scheme!='https' or urllib.parse.urlparse(newurl).hostname!='api.hcportal.eu':raise RuntimeError('Unexpected redirect; stopped. Open the official source manually.')
  return super().redirect_request(req,fp,code,msg,headers,newurl)
def main():
 ap=argparse.ArgumentParser(description=__doc__)
 ap.add_argument('--source-dir',type=Path,default=P/'private_sources')
 ap.add_argument('--fetch',action='store_true',help='Explicitly fetch the three listed originals; no fetch otherwise.')
 ap.add_argument('--accept-source-terms',action='store_true',help='Confirm you reviewed https://hcportal.eu/terms.html and may obtain these sources for your intended use.')
 ap.add_argument('--render',action='store_true',help='Generate a local image atlas and complete source transcript; requires Pillow.')
 ap.add_argument('--output',type=Path,default=P/'local_preview')
 args=ap.parse_args();sources=R('data/sources.json')
 if args.fetch and not args.accept_source_terms:raise RuntimeError('Read https://hcportal.eu/terms.html; use --accept-source-terms only if you may download the listed sources for your intended use.')
 if args.fetch:
  args.source_dir.mkdir(parents=True,exist_ok=True);opener=urllib.request.build_opener(SameHostRedirect())
  for s in sources:
   dest=args.source_dir/Path(s['file']).name
   if dest.exists():
    if sha(dest.read_bytes())!=s['sha256']:raise RuntimeError('Existing file differs; it will not be overwritten: '+dest.name)
    continue
   url=s['source_url'];parsed=urllib.parse.urlparse(url)
   if parsed.scheme!='https' or parsed.hostname!='api.hcportal.eu':raise RuntimeError('Unapproved source host')
   req=urllib.request.Request(url,headers={'User-Agent':'AnnaTicha-research-verifier/1.0 (three-source personal verification)'})
   with opener.open(req,timeout=30) as response:data=response.read(12_000_001)
   if len(data)>12_000_000:raise RuntimeError('Unexpected source size; stopped')
   if sha(data)!=s['sha256']:raise RuntimeError('Downloaded source has changed; stopped without saving '+dest.name)
   dest.write_bytes(data);print('Downloaded and hash-checked',dest.name)
 # Hash checks apply equally to manually supplied and script-fetched originals.
 paths={}
 for s in sources:
  p=args.source_dir/Path(s['file']).name
  if not p.is_file():raise RuntimeError('Missing '+p.name+'. Obtain it from '+s['source_url']+' subject to the provider terms.')
  if sha(p.read_bytes())!=s['sha256']:raise RuntimeError('Source hash mismatch: '+p.name)
  paths[s['card']]=p
 print('PASS: all three original source SHA-256 values')
 if not args.render:return
 from PIL import Image
 ims={k:Image.open(p).convert('RGB') for k,p in paths.items()};checks=R('data/crop_pixel_checksums.json')['crops'];turns={'CCW90':Image.Transpose.ROTATE_90,'CW90':Image.Transpose.ROTATE_270}
 if args.output.exists():raise RuntimeError('Output already exists; choose a new --output folder. No files overwritten.')
 args.output.mkdir(parents=True);(args.output/'images').mkdir();refs={}
 for x in checks:
  im=ims[x['card']].crop(tuple(x['original_bbox_xyxy']))
  if x['orientation'] in turns:im=im.transpose(turns[x['orientation']])
  if sha(struct.pack('>II',*im.size)+im.tobytes())!=x['rgb_pixel_sha256']:raise RuntimeError('Pixel comparison failed: '+x['id'])
  filename=x['id'].replace('/','_')+'.png';im.save(args.output/'images'/filename);refs[x['id']]='images/'+filename
 esc=html.escape
 def image(id,caption,cls='crop'):
  return '<figure><img loading="lazy" class="'+cls+'" src="'+refs[id]+'" alt="'+esc(caption)+'"><figcaption>'+esc(caption)+'</figcaption></figure>'
 chunks=['<!doctype html><html lang="en"><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1"><title>Anna Tichá: local source review</title><style>body{font:16px/1.5 system-ui,sans-serif;color:#193343;background:#f4f7f8;margin:0;padding:28px;max-width:1200px;margin:auto}h1,h2,h3{line-height:1.2}.grid{display:grid;grid-template-columns:repeat(auto-fit,minmax(310px,1fr));gap:18px}article,details{background:white;border:1px solid #d4dfe5;border-radius:8px;padding:18px;margin:14px 0}.examples{display:flex;gap:20px;flex-wrap:wrap}figure{margin:8px 0}.crop{height:160px;max-width:240px;object-fit:contain;object-position:left}.line{width:100%;height:auto}.body{height:85px;max-width:140px;object-fit:contain;object-position:left}figcaption{font:11px/1.4 monospace;max-width:300px}table{border-collapse:collapse;width:100%;font-size:13px}td,th{border-bottom:1px solid #ddd;padding:7px;text-align:left}pre{white-space:pre-wrap;background:white;padding:20px}summary{cursor:pointer;color:#175f88;font-weight:bold}.scroll{overflow:auto}.unknown{color:#9c482a}@media(max-width:700px){body{padding:14px}.grid{display:block}}</style><h1>Anna Tichá: local source verification</h1><p>This local-only preview was generated from three originals whose hashes match the retained sources. All 599 crop pixel arrays passed comparison. Images are not part of the public repository and are not licensed here for redistribution.</p><p><b>Scope:</b> complete replay for card199 only: 532 bodies, 522 mapped, 10 unknown, 524 emitted nonunknown characters. Card440 supplies two unbarred-t atlas examples; card453 supplies four training-mark examples. AI-generated readings; no external human expert review. Context crops can include neighboring strokes; use the original boxes and retained anchors.</p><h2>Source credits</h2><ul>']
 for s in sources:chunks.append('<li>HCPortal: <a href="'+s['source_url']+'">'+Path(s['file']).name+'</a> · <a href="'+s['record_url']+'">catalogue</a></li>')
 chunks+=['</ul><h2>24-class glyph atlas</h2><div class="grid">']
 for a in R('data/glyph_atlas.json'):
  chunks.append('<article><h3>'+esc(a['class_id'])+' → '+esc(a['literal'])+'</h3><p>'+esc(a['description'])+'</p><div class="examples">')
  for e in a['examples']:chunks.append(image('atlas/'+a['class_id']+'/'+e['token_id'],str(e['card'])+'/'+e['token_id']+' '+e['orientation']+' box '+str(e['original_bbox_xyxy'])+' local horizontal anchors '+str(e['local_anchor_x'])))
  chunks.append('</div><p>Card199 count: '+str(a['count_in_card199'])+'</p></article>')
 chunks+=['</div><h2>All 532 card199 bodies</h2><p>Expand a line to inspect each source body. The two opposite-orientation panels have no established cross-panel order. Continuous body indices exclude punctuation; T item numbers can have gaps.</p>']
 rows=R('data/card199_positions.json')['positions']
 for line in R('data/line_coordinates.json'):
  rr=[r for r in rows if r['line_id']==line['line_id']];chunks.append('<details><summary>'+line['line_id']+' / '+line['orientation']+' / '+str(len(rr))+' bodies</summary>');chunks.append(image('line/'+line['line_id'],line['line_id']+' source context','line'));chunks.append('<div class="scroll"><table><tr><th>Body</th><th>Position / box</th><th>Source crop</th><th>Class</th><th>Literal</th></tr>')
  for r in rr:chunks.append('<tr'+(' class="unknown"' if r['unknown'] else '')+'><td>'+str(r['body_index'])+'</td><td>'+r['token_id']+'<br>'+str(r['original_bbox_xyxy'])+'</td><td>'+image('body/'+r['token_id'],r['token_id'],'body')+'</td><td>'+r['class_id']+'</td><td>'+r['literal']+'</td></tr>')
  chunks.append('</table></div></details>')
 chunks+=['<h2>Separate card453 training mark examples</h2><div class="grid">']
 for m in R('data/mark_examples.json'):
  chunks.append('<article><h3>Card453 / P'+str(m['position'])+'</h3>'+image('mark/453/P'+str(m['position']),m['mark_type']+' / '+str(m['original_bbox_xyxy']))+'<p>'+esc(m['description'])+'</p><p>Base confidence '+m['base_confidence']+'; mark confidence '+m['mark_confidence']+'; ownership '+m['ownership_confidence']+'. These are training examples, not card199 mark-rule successes.</p></article>')
 chunks+=['</div><h2>Exact historical literal</h2><pre>'+esc((P/'literal.txt').read_text())+'</pre><p>Read the repository RIGHTS.md and README.md before reusing these materials. No file has been uploaded or published by this script.</p></html>']
 (args.output/'index.html').write_text('\n'.join(chunks),encoding='utf-8');print('PASS: 599 exact source crops generated locally. Open',args.output/'index.html')
if __name__=='__main__':
 try:main()
 except Exception as e:print('STOP:',e,file=sys.stderr);sys.exit(1)
