"""Whitelist-only peer context packets; no pixels, key values or primary partitions.
Private provenance is separate: share only peer-packet.json and its peer-freeze.json.
"""
import argparse,copy,hashlib,json,re,struct,datetime
from pathlib import Path
ROOT=Path(__file__).resolve().parent
FRAMES={'NONE','CW90','CCW90','ROTATE_180'}
INSTRUCTIONS='Read only these exact source context windows. Choose and record your own graphical groups, representation records, ownership, classes and abstentions. No primary partitions or target values are supplied. Source-selected windows do not establish global blindness or independent control accuracy.'
def require(ok,message):
 if not ok:raise ValueError(message)
def sha(path):return hashlib.sha256(Path(path).read_bytes()).hexdigest()
def encode(data):return (json.dumps(data,ensure_ascii=False,sort_keys=True,indent=2)+'\n').encode()
def dimensions(frame,source):
 require(frame in FRAMES,'Unsupported declared context frame')
 return source[::-1]if frame in {'CW90','CCW90'}else list(source)
def box(value,dims):
 require(isinstance(value,list)and len(value)==4 and all(type(v)is int for v in value),'Integer source context rectangle required')
 require(0<=value[0]<value[2]<=dims[0]and 0<=value[1]<value[3]<=dims[1],'Source context outside declared frame');return copy.deepcopy(value)
def read_ref(ref):
 p=(ROOT/ref['path']).resolve();require(p.is_relative_to(ROOT)and sha(p)==ref['sha256'],'Frozen input fingerprint mismatch: '+ref['path']);return p,json.loads(p.read_text())
def source_freeze_digest(data):
 values=[data[k]for k in ['source_freeze_sha256','source_main_freeze_sha256','primary_freeze_sha256']if k in data]
 require(values and len(set(values))==1,'Unambiguous primary freeze reference required');return values[0]
def validate_packet(packet):
 require(set(packet)=={'schema','card','instructions','fragments'}and packet['schema']=='anna-window-only-peer-packet-v1'and packet['instructions']==INSTRUCTIONS,'Peer packet top-level whitelist mismatch')
 ids=[]
 for f in packet['fragments']:
  require(set(f)=={'nomination_id','card','face','source','coordinate_frame','glyph_read_orientation','context_windows'},'Peer fragment whitelist mismatch')
  require(f['card']==packet['card']and f['face']in {'picture','address'},'Window identity mismatch');ids.append(f['nomination_id'])
  require(isinstance(f['nomination_id'],str)and bool(f['nomination_id']),'Nomination ID missing')
  require(set(f['source'])=={'sha256','dimensions','source_url'}and isinstance(f['source']['source_url'],str)and bool(f['source']['source_url']),'Source metadata scalar whitelist mismatch')
  require(re.fullmatch('[0-9a-f]{64}',f['source']['sha256'])and isinstance(f['source']['dimensions'],list)and len(f['source']['dimensions'])==2 and all(type(v)is int and v>0 for v in f['source']['dimensions']),'Exact source digest/dimensions required')
  require(f['coordinate_frame']in FRAMES and (f['glyph_read_orientation']is None or f['glyph_read_orientation']in FRAMES),'Explicit frame/optional separately recorded glyph pose required')
  require(isinstance(f['context_windows'],list)and f['context_windows'],'Context windows required')
  for w in f['context_windows']:
   require(set(w)=={'orientation','bbox_xyxy','image'},'Context whitelist mismatch');box(w['bbox_xyxy'],dimensions(w['orientation'],f['source']['dimensions']))
   require(set(w['image'])=={'path','sha256'}and isinstance(w['image']['path'],str)and re.fullmatch('[0-9a-f]{64}',w['image']['sha256']),'Exact context image reference required')
 require(ids and len(set(ids))==len(ids),'Unique nonempty nomination set required')
 return packet

def derive(packet,selection,packet_path,image_check):
 card=packet.get('card');require(type(card)is int and 198<=card<=460 and selection.get('card_id')==card,'Exact source packet/selection card required')
 before=copy.deepcopy(packet);fragments=packet.get('fragments',packet.get('nominations'));require(isinstance(fragments,list)and fragments,'Supported fragment or nomination list required')
 faces=selection.get('faces');require(isinstance(faces,list)and {f.get('face')for f in faces}=={'picture','address'}and len(faces)==2,'Both selected original source faces required')
 flags=[packet[k]for k in ['key_projection_performed','key_seen','literal_seen','new_mapping_created']if k in packet]
 require(flags and all(v is False for v in flags),'Original packet must unambiguously precede key/target values')
 outputs=[]
 for fragment in fragments:
  face=fragment.get('face');require(face in {'picture','address'},'Fragment face missing');selected=next(f for f in faces if f['face']==face);require(fragment.get('card',card)==card,'Fragment card mismatch')
  supplied=fragment.get('source',{});digest=fragment.get('source_sha256',supplied.get('sha256'));require(digest==selected['sha256'],'Fragment original source digest mismatch')
  source={'sha256':selected['sha256'],'dimensions':copy.deepcopy(selected['dimensions']),'source_url':selected['source_url']}
  for recorded,expected,label in [(fragment.get('source_dimensions',supplied.get('dimensions')),source['dimensions'],'dimensions'),(fragment.get('source_url',supplied.get('source_url')),source['source_url'],'URL')]:
   if recorded is not None:require(recorded==expected,'Recorded source '+label+' mismatch')
  frame=fragment.get('raw_coordinate_orientation',fragment.get('orientation'));require(frame in FRAMES,'Explicit original coordinate orientation required')
  if 'coordinate_frame'in fragment:require(fragment['coordinate_frame']==frame,'Conflicting source coordinate frame')
  pose=fragment.get('glyph_read_orientation') # Null means the original packet did not separately declare glyph pose.
  contexts=[]
  if 'context_images'in fragment:
   require(isinstance(fragment['context_images'],list)and fragment['context_images'],'Recorded context images missing')
   for image in fragment['context_images']:
    orientation=image['orientation'];require(orientation in {frame,'NONE'},'Context image frame lacks exact recorded window')
    window=fragment['native_context_bbox_xyxy']if orientation=='NONE'and frame!='NONE'else fragment['source_context_bbox_xyxy']
    contexts.append({'orientation':orientation,'bbox_xyxy':box(window,dimensions(orientation,source['dimensions'])),'image':image_check(packet_path.parent/image['path'],image['sha256'],window)})
  else:
   window=box(fragment['bbox_xyxy'],dimensions(frame,source['dimensions']));image_digest=fragment.get('context_png_sha256',fragment.get('context_sha256'));require(image_digest is not None,'Context fingerprint missing')
   contexts=[{'orientation':frame,'bbox_xyxy':window,'image':image_check(packet_path.parent/fragment['context_png'],image_digest,window)}]
  outputs.append({'nomination_id':fragment['fragment_id'],'card':card,'face':face,'source':source,'coordinate_frame':frame,'glyph_read_orientation':pose,'context_windows':contexts})
 result=validate_packet({'schema':'anna-window-only-peer-packet-v1','card':card,'instructions':INSTRUCTIONS,'fragments':outputs});require(packet==before,'Original packet mutated');return result

def build(refs,output):
 require(set(refs)=={'packet','source_freeze','nomination_freeze','selection'},'Exact four frozen provenance refs required')
 loaded={k:read_ref(v)for k,v in refs.items()};packet_path,packet=loaded['packet'];_,selection=loaded['selection'];_,freeze=loaded['source_freeze'];nom_path,nom=loaded['nomination_freeze']
 require(source_freeze_digest(packet)==refs['source_freeze']['sha256']==source_freeze_digest(nom),'Original source/nomination freeze mismatch')
 require(packet['card']==freeze.get('card')==nom.get('card')==selection['card_id'],'Freeze card identity mismatch')
 files=nom.get('files');require(isinstance(files,list),'Supported nomination freeze files required');frozen={str((nom_path.parent/f['path']).resolve()):f['sha256']for f in files};require(len(frozen)==len(files),'Duplicate nomination freeze file')
 require(frozen.get(str(packet_path))==refs['packet']['sha256'],'Original packet absent from nomination freeze')
 checked=[]
 def image_check(path,digest,window):
  path=path.resolve();require(path.is_relative_to(ROOT)and frozen.get(str(path))==digest and sha(path)==digest,'Frozen context image mismatch')
  header=path.read_bytes()[:24];require(len(header)==24 and header[:8]==b'\x89PNG\r\n\x1a\n'and header[12:16]==b'IHDR','Context PNG header required')
  dims=list(struct.unpack('>II',header[16:24]));require(dims==[window[2]-window[0],window[3]-window[1]],'Context image dimensions differ from recorded unscaled window')
  ref={'path':str(path.relative_to(ROOT)),'sha256':digest};checked.append(ref);return ref
 peer=derive(packet,selection,packet_path,image_check)
 output=output.resolve();require(output.is_relative_to(ROOT)and not output.exists(),'New derived peer packet directory required');output.mkdir(parents=True)
 p=output/'peer-packet.json';p.write_bytes(encode(peer));now=datetime.datetime.now(datetime.timezone.utc).isoformat()
 f=output/'peer-freeze.json';f.write_bytes(encode({'schema':'anna-window-only-peer-freeze-v1','card':peer['card'],'packet_sha256':sha(p),'frozen_utc_before_peer_authorization':now,'primary_partition_metadata_supplied':False}))
 private=output/'provenance-private.json';private.write_bytes(encode({'schema':'anna-window-only-peer-derivation-private-v1','inputs':refs,'derived_peer_packet':{'path':str(p.relative_to(ROOT)),'sha256':sha(p)},'derived_peer_freeze':{'path':str(f.relative_to(ROOT)),'sha256':sha(f)},'checked_context_images':checked,'helper_sha256':sha(__file__),'original_input_sha256_after':{k:sha(v[0])for k,v in loaded.items()},'limits':'Only peer-packet.json and peer-freeze.json are peer-facing. Original packets and this provenance may expose primary partitions; do not provide them to the independent reader. No global blindness, source truth or calibrated accuracy claim; no pixels/key/target literals read.'}))
 require(all(refs[k]['sha256']==sha(loaded[k][0])for k in refs),'Frozen original input changed')
 return {'packet':{'path':str(p.relative_to(ROOT)),'sha256':sha(p)},'freeze':{'path':str(f.relative_to(ROOT)),'sha256':sha(f)},'private_provenance':{'path':str(private.relative_to(ROOT)),'sha256':sha(private)}}
def main():
 p=argparse.ArgumentParser(description=__doc__)
 for name in ['packet','source-freeze','nomination-freeze','selection']:p.add_argument('--'+name,type=Path,required=True);p.add_argument('--'+name+'-sha',required=True)
 p.add_argument('--output-dir',type=Path,required=True);a=p.parse_args();refs={name:{'path':str(getattr(a,name)),'sha256':getattr(a,name+'_sha')}for name in ['packet','source_freeze','nomination_freeze','selection']};print(json.dumps(build(refs,a.output_dir),indent=2))
if __name__=='__main__':main()
