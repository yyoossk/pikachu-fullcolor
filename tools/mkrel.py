#!/usr/bin/env python3
"""リリース用 zip を作る。種類ごとにパッチ1つ（v1.0〜v1.3 のどれに当てても同じ ROM）。
  python3 tools/mkrel.py 3.83 前の版のzip 出力先フォルダ
  フォルダ分けと名前は前の版の zip にならう（ファイル名の _v1.x用 は取る）。"""
import zipfile, os, subprocess, sys, re, zlib
ROOT=os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0,os.path.join(ROOT,'tools'))
from applyips import apply
VER=sys.argv[1]; FC=ROOT
old=zipfile.ZipFile(sys.argv[2])
folder={'1_完全版':'', '2_カラー化のみ':'co', '3_完全版_60fps版':'f', '4_カラー化のみ_60fps版':'cf', '5_151匹そろう版':'x', '6_151匹そろう版_60fps版':'xf'}
bases=[open(f'{FC}/orig/v1{i}.gb','rb').read() for i in range(4)]
out=os.path.join(sys.argv[3],f'ポケットモンスターピカチュウフルカラー_Ver.{VER}.zip')
import tempfile; tmp=tempfile.mkdtemp(); os.makedirs(tmp,exist_ok=True)
z=zipfile.ZipFile(out,'w',zipfile.ZIP_DEFLATED); done=set()
for info in old.infolist():
    n=info.filename
    if n.endswith('/'):
        zi=zipfile.ZipInfo(n); zi.flag_bits|=0x800; z.writestr(zi,b''); continue
    p=n.split('/'); k=(('s' if p[2].startswith('初代') else '')+folder[p[1]]) or 'v'
    n2=re.sub(r'_v1\.[0-3]用\.ips$','.ips',n)
    if n2 in done: continue
    done.add(n2)
    ip=f'{tmp}/{k}.ips'
    r=subprocess.run([sys.executable,f'{FC}/tools/mkips.py',f'{FC}/build/{k}.gbc',ip],capture_output=True,text=True); assert r.returncode==0,r.stderr
    data=open(ip,'rb').read(); tgt=open(f'{FC}/build/{k}.gbc','rb').read()
    for b in bases: assert apply(b,data)==tgt
    zi=zipfile.ZipInfo(n2, date_time=(2026,11,19,13,0,0)); zi.flag_bits|=0x800; zi.compress_type=zipfile.ZIP_DEFLATED
    z.writestr(zi,data); print(k,'%08X'%zlib.crc32(tgt),n2.split('/')[-1])
z.close(); print(out, os.path.getsize(out), len(done))
