#!/usr/bin/env python3
"""Ver.3.50 の ROM（base/<版>.gbc）に、src/ の asm を当てて build/<版>.gbc を作る。

  python3 tools/build.py            … 12種類ぜんぶ
  python3 tools/build.py v f        … 指定した版だけ

・src/*.asm の1行目に「; variants: v f x xf s sf sx sxf」のように入れる版を書く（ない時は「完全版・151匹そろう版の8種類」）。
  版の名前：v 完全版 / f 完全版60fps / x 151匹 / xf 151匹60fps / co カラー化のみ / cf カラー化のみ60fps、
  それぞれの初代グラフィック版は s をつける（s, sf, sx, sxf, sco, scf）。
・asm には pokeyellow-jp の includes.asm が先に読みこまれる。元のピカチュウのラベル名（syms/<版>.sym にあるもの）と、pokeyellow-jp の includes.asm の定数・マクロが使える。
  BANK() も使える（farcall など）。版ごとの分けかたは IF DEF(V_60FPS) など（下の DEFINES）。
・場所を決めた SECTION（ROMX[$xxxx], BANK[$xx]）は、その場所に上書き（元の命令を書きかえるフック）。
  場所を決めない SECTION は、あき（tools/freespace.py）に置く。BANK[$xx] だけ決めたものはそのバンクのあきに。
・できた ROM のチェックサムは rgbfix で直す。src/ に何もないと、base と同じ ROM になる。
"""
import os, sys, re, subprocess, glob, zlib
ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DIS = os.environ.get('PKJP', os.path.join(os.path.dirname(ROOT), 'pokeyellow-jp'))
RGB = os.environ.get('RGBDS', os.path.join(os.path.dirname(ROOT), 'rgbds'))
sys.path.insert(0, os.path.join(ROOT, 'tools'))
from freespace import free
ALL = ['v', 's', 'f', 'sf', 'x', 'sx', 'xf', 'sxf', 'co', 'sco', 'cf', 'scf']
DEFAULT = ['v', 's', 'f', 'sf', 'x', 'sx', 'xf', 'sxf']
def defines(k):
    d = ['V_' + k.upper()]
    if 'f' in k[1:] or k in ('f', 'cf'): d.append('V_60FPS')
    if k.startswith('s'): d.append('V_SHODAI')
    if 'x' in k: d.append('V_151')
    if 'c' in k: d.append('V_COLORONLY')
    return d
def run(cmd, **kw):
    r = subprocess.run(cmd, capture_output=True, text=True, **kw)
    if r.returncode: sys.exit(' '.join(cmd) + '\n' + r.stdout + r.stderr)
    return r
def variants_of(path):
    first = open(path, encoding='utf-8').readline()
    m = re.match(r'\s*;\s*variants:\s*(.*)', first)
    return m.group(1).split() if m else DEFAULT
def build(k):
    out = os.path.join(ROOT, 'build', k); os.makedirs(out, exist_ok=True)
    srcs = [p for p in sorted(glob.glob(os.path.join(ROOT, 'src', '*.asm'))) if k in variants_of(p)]
    base = os.path.join(ROOT, 'base', k + '.gbc'); rom = os.path.join(ROOT, 'build', k + '.gbc')
    asm = lambda *a: run([os.path.join(RGB, 'rgbasm'), '-I', DIS, '-I', os.path.join(ROOT, 'src'), '-P', 'includes.asm'] + [x for d in defines(k) for x in ('-D', d)] + list(a))
    symo = os.path.join(out, 'syms.o')
    if not os.path.exists(symo) or os.path.getmtime(symo) < os.path.getmtime(os.path.join(ROOT, 'syms', k + '.sym')):
        run([sys.executable, os.path.join(ROOT, 'tools', 'symobj.py'), os.path.join(ROOT, 'syms', k + '.sym'), os.path.join(out, 'syms.asm')])
        asm('-o', symo, os.path.join(out, 'syms.asm'))
    objs = []
    for p in srcs:
        o = os.path.join(out, os.path.basename(p)[:-4] + '.o'); asm('-o', o, p); objs.append(o)
    link = os.path.join(RGB, 'rgblink')
    if not objs:
        data = open(base, 'rb').read()
    else:
        # 1) a link without the base ROM: the floating sections' sizes and banks
        run([link, '-m', os.path.join(out, 'trial.map'), '-o', os.path.join(out, 'trial.gb'), symo] + objs)
        secs = []
        for l in open(os.path.join(out, 'trial.map'), encoding='utf-8'):
            m = re.match(r'\s*SECTION: \$([0-9a-f]+)(?:-\$([0-9a-f]+))? \(\$([0-9a-f]+) bytes?\) \["(.+)"\]', l)
            if m: secs.append((m.group(4), int(m.group(3), 16)))
        fixed, banked = set(), {}
        for p in srcs:
            for l in open(p, encoding='utf-8'):
                m = re.match(r'\s*SECTION\s+"([^"]+)"\s*,\s*(\w+)\s*(\[[^\]]*\])?\s*(?:,\s*BANK\[([^\]]+)\])?', l)
                if not m: continue
                if m.group(3): fixed.add(m.group(1))
                elif m.group(4): banked[m.group(1)] = m.group(4)
        # 2) the free space of this version, and where each floating section goes
        bd = open(base, 'rb').read()
        fr = {b: [st, en] for b, st, en, n in free(bd, 16) if b > 0}
        script = {}
        for name, size in sorted(secs, key=lambda s: -s[1]):
            if name in fixed or name.startswith('s') and name[1:].isdigit() or size == 0: continue
            want = banked.get(name)
            cands = [int(want.strip().lstrip('$'), 16)] if want else sorted(fr, key=lambda b: -(fr[b][1] - fr[b][0]))
            for b in cands:
                if b in fr and fr[b][1] - fr[b][0] >= size:
                    script.setdefault(b, []).append((fr[b][0], name)); fr[b][0] += size; break
            else: sys.exit(f'{k}: no room for "{name}" ({size} bytes)')
        ls = os.path.join(out, 'patch.link')
        with open(ls, 'w') as f:
            for b in sorted(script):
                f.write(f'ROMX ${b:02x}\n')
                for addr, name in sorted(script[b]): f.write(f'\tORG ${addr:04x}\n\t"{name}"\n')
        run([link, '-O', base, '-l', ls, '-m', os.path.join(out, 'patch.map'), '-n', os.path.join(ROOT, 'build', k + '.sym'), '-o', rom, symo] + objs)
        run([os.path.join(RGB, 'rgbfix'), '-v', rom])
        data = open(rom, 'rb').read()
    open(rom, 'wb').write(data)
    return '%08X' % zlib.crc32(data)
if __name__ == '__main__':
    for k in (sys.argv[1:] or ALL):
        print(k, build(k), flush=True)
