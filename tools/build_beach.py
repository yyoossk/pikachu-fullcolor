#!/usr/bin/env python3
"""サマービーチだけのゲームを作る。
  python3 tools/build_beach.py          … build/xf.gbc（151匹そろう版・60fps版）に beach/*.asm を当てて build/summer_beach.gbc
  python3 tools/mkips.py build/summer_beach.gbc ピカチュウのサマービーチ.ips   … v1.0〜v1.3 のどれに当てても同じになるパッチ
先に python3 tools/build.py xf で build/xf.gbc を作っておく。"""
import os, sys, glob, subprocess, zlib
ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DIS = os.environ.get('PKJP', os.path.join(os.path.dirname(ROOT), 'pokeyellow-jp'))
RGB = os.environ.get('RGBDS', os.path.join(os.path.dirname(ROOT), 'rgbds'))
K = 'xf'
def run(cmd):
    r = subprocess.run(cmd, capture_output=True, text=True)
    if r.returncode: sys.exit(' '.join(cmd) + '\n' + r.stdout + r.stderr)
out = os.path.join(ROOT, 'build', 'beach'); os.makedirs(out, exist_ok=True)
base = os.path.join(ROOT, 'build', K + '.gbc'); rom = os.path.join(ROOT, 'build', 'summer_beach.gbc')
symo = os.path.join(out, 'syms.o')
run([sys.executable, os.path.join(ROOT, 'tools', 'symobj.py'), os.path.join(ROOT, 'build', K + '.sym'), os.path.join(out, 'syms.asm')])
defs = ['-D', 'V_XF', '-D', 'V_60FPS', '-D', 'V_151']
asm = lambda *a: run([os.path.join(RGB, 'rgbasm'), '-I', DIS, '-I', os.path.join(ROOT, 'beach'), '-P', 'includes.asm'] + defs + list(a))
asm('-o', symo, os.path.join(out, 'syms.asm'))
objs = []
for p in sorted(glob.glob(os.path.join(ROOT, 'beach', '*.asm'))):
    o = os.path.join(out, os.path.basename(p)[:-4] + '.o'); asm('-o', o, p); objs.append(o)
run([os.path.join(RGB, 'rgblink'), '-O', base, '-m', os.path.join(out, 'beach.map'), '-n', os.path.join(ROOT, 'build', 'summer_beach.sym'), '-o', rom, symo] + objs)
run([os.path.join(RGB, 'rgbfix'), '-v', rom])
print('summer_beach %08X' % zlib.crc32(open(rom, 'rb').read()))
