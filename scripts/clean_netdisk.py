import argparse,hashlib,json,os,pathlib,re,shutil,struct,sys
DEFAULT=os.environ.get('BAIDUNETDISK_PATH',r'C:\Program Files\BaiduNetdisk')
REL='module/BrowserEngine/resources/core.asar'
def sha(p):
 with open(p,'rb') as f:return hashlib.file_digest(f,'sha256').hexdigest()
def read_asar(p):
 with open(p,'rb') as f:
  n=struct.unpack('<4I',f.read(16));return json.loads(f.read(n[3])),8+n[1]
def patch(src,dst):
 h,base=read_asar(src); changes={}
 with open(src,'rb') as f:
  for name in ['renderer.js','45.js']:
   e=h['files'][name];f.seek(base+int(e['offset']));changes[name]=f.read(e['size']).decode('utf-8')
 s=changes['renderer.js']
 for key in ['HeaderAd','TextAd','AsideAd']:
  field=key[0].lower()+key[1:]; old='set'+key+'(e,t){e.'+field+'=t}'
  if s.count(old)!=1:raise ValueError('Unsupported resource: '+old)
  s=s.replace(old,'set'+key+'(e,t){e.'+field+'=[]}')
 selectors=['.wp-header-user__drop-channel','.wp-header-user__create-team-wrapper','.wp-header-user__create-team-title','.auto-renew-guide','.limit-time-guide','.vip-cycle-guide__popper','.suprise-gift']
 for sel in selectors:
  if sel[1:] not in s and sel[1:] not in changes['45.js']:raise ValueError('Missing selector '+sel)
 css=','.join(selectors)+'{display:none!important;pointer-events:none!important}'
 js=';/* LOCAL_CLEAN_UI_V1 */(function(){function run(){if(document.getElementById("local-clean-ui"))return;var s=document.createElement("style");s.id="local-clean-ui";s.textContent='+json.dumps(css)+';(document.head||document.documentElement).appendChild(s);}if(document.readyState==="loading")document.addEventListener("DOMContentLoaded",run,{once:true});else run();})();\n'
 changes['renderer.js']=s+'\n'+js
 old='[{comp:"headerGame",evt:"gameEvt",icon:"icon-game"}]'
 if changes['45.js'].count(old)!=1:raise ValueError('Game entry signature mismatch')
 changes['45.js']=changes['45.js'].replace(old,'[]')
 payload_size=src.stat().st_size-base
 for name,text in changes.items():
  data=text.encode('utf-8');changes[name]=data;e=h['files'][name];e['offset']=str(payload_size);e['size']=len(data);payload_size+=len(data)
  if 'integrity' in e:
   block=e['integrity']['blockSize'];e['integrity']={'algorithm':'SHA256','hash':hashlib.sha256(data).hexdigest(),'blockSize':block,'blocks':[hashlib.sha256(data[i:i+block]).hexdigest() for i in range(0,len(data),block)]}
 header=json.dumps(h,ensure_ascii=False,separators=(',',':')).encode();pad=(-len(header))%4;pickle=struct.pack('<II',4+len(header)+pad,len(header))+header+b'\0'*pad
 with open(src,'rb') as inp,open(dst,'wb') as out:
  out.write(struct.pack('<II',4,len(pickle)));out.write(pickle);inp.seek(base);shutil.copyfileobj(inp,out)
  for data in changes.values():out.write(data)
 # Readback validates member offsets, bytes and integrity.
 hh,bb=read_asar(dst)
 with open(dst,'rb') as f:
  for name,data in changes.items():
   e=hh['files'][name];f.seek(bb+int(e['offset']));assert f.read(e['size'])==data
 return changes

def main():
 ap=argparse.ArgumentParser();ap.add_argument('mode',choices=['apply','restore','build']);ap.add_argument('--path',default=DEFAULT);args=ap.parse_args();root=pathlib.Path(args.path);target=root/REL;backup=root/'LocalCleanBackup-v1'
 if args.mode=='build':
  patch(target,pathlib.Path(__file__).with_name('core.patched.asar'));print('Build and readback OK');return
 if not target.is_file():raise ValueError('Install path not found')
 # Refuse live mutation; users close the app themselves to protect transfers.
 import subprocess
 raw=subprocess.check_output(['powershell','-NoProfile','-Command',"Get-Process | Where-Object {$_.ProcessName -match 'BaiduNetdisk|BaiduNetdiskHost|YunUtilityService|Autoupdate'} | Select-Object -ExpandProperty Path"],text=True,errors='replace')
 if any(str(root).lower() in line.lower() for line in raw.splitlines()):raise ValueError('Exit BaiduNetdisk from the tray and retry (active processes found).')
 manifest=backup/'manifest.json'
 if args.mode=='restore':
  m=json.loads(manifest.read_text('utf-8'))
  for rel,info in m['files'].items():
   dest=root/rel
   if sha(backup/info['backup'])!=info['original']:raise ValueError('Backup hash mismatch')
   if sha(dest)!=info['patched']:raise ValueError('Current file changed; restore refused: '+rel)
  updater=root/'AutoUpdate/Autoupdate.exe';disabled=root/'AutoUpdate/Autoupdate.exe.localclean-disabled'
  if m['renamed_updater'] and (updater.exists() or not disabled.exists()):raise ValueError('Updater state changed; inspect backup manually')
  for rel,info in m['files'].items():shutil.copy2(backup/info['backup'],root/rel)
  if m['renamed_updater']:disabled.rename(updater)
  manifest.rename(backup/'restored-manifest.json');print('Restored. Original backups retained.');return
 if backup.exists():raise ValueError('Backup folder already exists. Do not apply twice; restore first or inspect the backup.')
 expected=json.loads(pathlib.Path(__file__).with_name('target.json').read_text('utf-8'))
 if sha(target)!=expected['core_sha256']:raise ValueError('Resource version differs from analyzed version. No files changed.')
 temp=target.with_name('core.asar.localclean-new');backup.mkdir();m={'files':{},'renamed_updater':False}
 try:
  patch(target,temp)
  for rel in [REL,'AutoUpdate/config.ini']:
   p=root/rel
   if p.exists():
    b=str(len(m['files']))+'.original';shutil.copy2(p,backup/b);m['files'][rel]={'backup':b,'original':sha(p),'patched':sha(p)}
  os.replace(temp,target);m['files'][REL]['patched']=sha(target)
  conf=root/'AutoUpdate/config.ini'
  if conf.exists():
   data=conf.read_bytes();new,count=re.subn(rb'(?m)^(IsAutoUpdate\s*=\s*)1\s*\r?$',rb'\g<1>0\r',data)
   if count!=1:raise ValueError('Updater config signature mismatch')
   conf.write_bytes(new);m['files']['AutoUpdate/config.ini']['patched']=sha(conf)
  updater=root/'AutoUpdate/Autoupdate.exe';disabled=root/'AutoUpdate/Autoupdate.exe.localclean-disabled'
  if updater.exists():
   if disabled.exists():raise ValueError('Updater backup name already exists')
   updater.rename(disabled);m['renamed_updater']=True
  manifest.write_text(json.dumps(m,indent=2),encoding='utf-8');print('Applied. Backups: '+str(backup))
 except BaseException:
  for rel,info in m['files'].items():shutil.copy2(backup/info['backup'],root/rel)
  if m['renamed_updater']:(root/'AutoUpdate/Autoupdate.exe.localclean-disabled').rename(root/'AutoUpdate/Autoupdate.exe')
  if temp.exists():temp.unlink()
  raise
if __name__=='__main__':
 try:main()
 except Exception as e:print('ERROR:',e);sys.exit(1)
