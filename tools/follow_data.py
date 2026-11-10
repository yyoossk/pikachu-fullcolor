#!/usr/bin/env python3
"""連れ歩き（全ポケモン）の絵・下じき・色・番号の表を作る（src/gfx/follow/ に書く）。
  元: reference/follow_kit/（赤緑青ピカチュウ連れ歩きキットの絵と色）
  python3 tools/follow_data.py
・絵: 1匹 24タイル（止まり 下・上・横、歩き 下・上・横 の順）。
  後ろ・横の色（キットの「後ろ・横 用」の表）が、正面の色（手持ちと同じ色）の色1・色2を入れかえたものの
  ポケモンは、後ろ・横のタイルの色1と色2を入れかえておく（2bpp の上下のビットをいれかえる）。
  こうすると、1本のパレット（正面の色）で、どの向きも正しい色になる。
・下じき: 1匹 192バイト（下のビットだけ。上のビットはいつも 0）。
・色: 1匹 4バイト（色1・色2）。
・番号: 内部の番号（1〜190）→ ずかん番号−1（0〜150）。$FF は いない番号。
"""
import os, re
ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
KIT = os.path.join(ROOT, 'reference', 'follow_kit')
OUT = os.path.join(ROOT, 'src', 'gfx', 'follow')
os.makedirs(OUT, exist_ok=True)

L = open(os.path.join(KIT, 'follow_data.inc'), encoding='utf-8').read().split('\n')
def table(name):
    i = [j for j, l in enumerate(L) if l.startswith(name + ':')][0]
    out = []
    for l in L[i + 1:]:
        if not l.strip().startswith('dw'): break
        out.append([int(x.strip().replace('$', '0x'), 16) for x in l.split(';')[0].strip()[2:].split(',')])
    return out
own = table('FollowerOwnPals'); walk = table('FollowerWalkPals')

BACKSIDE = [4, 5, 6, 7, 8, 9, 10, 11, 16, 17, 18, 19, 20, 21, 22, 23]
gfx = bytearray(); mask = bytearray(); pals = bytearray()
m = open(os.path.join(KIT, 'follow_icon', 'mask.bin'), 'rb').read()
nswap = 0
for d in range(151):
    g = bytearray(open(os.path.join(KIT, 'follow_icon', '%03d.2bpp' % d), 'rb').read())
    assert len(g) == 384
    o = own[d + 1][:2]; w = walk[d + 1][:2]
    if o != w:
        assert o == w[::-1], d
        nswap += 1
        for t in BACKSIDE:
            for r in range(8):
                a = t * 16 + r * 2
                g[a], g[a + 1] = g[a + 1], g[a]
    gfx += g
    mm = m[d * 384:(d + 1) * 384]
    assert all(mm[i] == 0 for i in range(1, 384, 2))
    mask += bytes(mm[i] for i in range(0, 384, 2))
    for c in o: pals += bytes([c & 255, c >> 8])
open(os.path.join(OUT, 'gfx.bin'), 'wb').write(gfx)
open(os.path.join(OUT, 'mask1bpp.bin'), 'wb').write(mask)
open(os.path.join(OUT, 'pals.bin'), 'wb').write(pals)

# 内部の番号 → ずかん番号（元の ROM の PokedexOrder）
syms = {}
for l in open(os.path.join(ROOT, 'syms', 'v.sym')):
    p = l.split()
    if len(p) == 2 and ':' in p[0]: syms[p[1]] = p[0]
b, a = syms['PokedexOrder'].split(':'); off = int(b, 16) * 0x4000 + int(a, 16) - 0x4000
rom = open(os.path.join(ROOT, 'base', 'v.gbc'), 'rb').read()
order = rom[off:off + 190]
dex = bytes((x - 1) if 1 <= x <= 151 else 0xff for x in order)
open(os.path.join(OUT, 'dex.bin'), 'wb').write(dex)
print('swap', nswap, 'gfx', len(gfx), 'mask', len(mask), 'pals', len(pals), 'dex', len(dex))
