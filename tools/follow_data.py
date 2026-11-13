#!/usr/bin/env python3
"""連れ歩き（全ポケモン）の絵・下じき・色・番号の表を作る（src/gfx/follow/ に書く）。
  元: reference/follow_kit/（赤緑青ピカチュウ連れ歩きキットの絵と色）
  python3 tools/follow_data.py
・絵: 1匹 24タイル（止まり 下・上・横、歩き 下・上・横 の順）。
  正面（下向き）は、この版の手持ちのアイコン（ポケモンごとの絵、2コマ）と同じ絵にする（止まり＝1コマめ、歩き＝2コマめ）。
  後ろ・横はキットの絵のまま（横は左向き。右へ行くときはゲームが左右反転して出す）。色はキットのまま（キットの「歩き」の色で描いてある）。
・下じき: 1匹 192バイト（下のビットだけ。上のビットはいつも 0）。
  正面はアイコンの絵から作る（まわりとつながっていない すき間＝目・顔の白 を白に）。後ろ・横はキットの下じき。
・色: 1匹 4バイト（色1・色2）。pals.bin は正面の色（この版の手持ちのアイコンの色）、
  palsback.bin は後ろ・横の色（キットの「歩き」の色）。連れ歩きの向きで OBJ パレット6 を入れかえる。
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
rom = open(os.path.join(ROOT, 'base', 'v.gbc'), 'rb').read()
def icon_off(d):  # この版の手持ちのアイコン（バンク$30 の読みこみの処理と同じ分けかた）。1匹 128バイト（2コマ）
    if d < 0x54: return 0x28 * 0x4000 + 0x15f9 + d * 128
    if d < 0x54 + 0x35: return 0x34 * 0x4000 + 0x2576 + (d - 0x54) * 128
    return 0x30 * 0x4000 + 0x319e + (d - 0x89) * 128
ICONPAL = 0x30 * 0x4000 + 0x0fe8  # 1匹 8バイト（色1・色2・黒・白）
def dist(a, b): return sum(((a >> k & 31) - (b >> k & 31)) ** 2 for k in (0, 5, 10))
def front_mask(frame):  # 4タイル（左上・右上・左下・右下）→ まわりとつながっていない色0 の所を 1 に
    px = [[0] * 16 for _ in range(16)]
    for t in range(4):
        for r in range(8):
            lo, hi = frame[t * 16 + r * 2], frame[t * 16 + r * 2 + 1]
            for c in range(8):
                px[(t // 2) * 8 + r][(t % 2) * 8 + c] = (lo >> (7 - c) & 1) | (hi >> (7 - c) & 1) << 1
    out = [[0] * 16 for _ in range(16)]
    seen = set(); st = [(y, x) for y in range(16) for x in range(16) if (y in (0, 15) or x in (0, 15)) and px[y][x] == 0]
    while st:
        y, x = st.pop()
        if (y, x) in seen: continue
        seen.add((y, x))
        for dy, dx in ((1, 0), (-1, 0), (0, 1), (0, -1)):
            yy, xx = y + dy, x + dx
            if 0 <= yy < 16 and 0 <= xx < 16 and px[yy][xx] == 0: st.append((yy, xx))
    m = bytearray()
    for t in range(4):
        for r in range(8):
            b = 0
            for c in range(8):
                y, x = (t // 2) * 8 + r, (t % 2) * 8 + c
                if px[y][x] == 0 and (y, x) not in seen: b |= 1 << (7 - c)
            m.append(b)
    return m
gfx = bytearray(); mask = bytearray(); pals = bytearray(); palsback = bytearray()
m = open(os.path.join(KIT, 'follow_icon', 'mask.bin'), 'rb').read()
for d in range(151):
    g = bytearray(open(os.path.join(KIT, 'follow_icon', '%03d.2bpp' % d), 'rb').read())
    assert len(g) == 384
    ic = rom[icon_off(d):icon_off(d) + 128]
    g[0:64] = ic[0:64]; g[12 * 16:16 * 16] = ic[64:128]
    i1 = rom[ICONPAL + d * 8] | rom[ICONPAL + d * 8 + 1] << 8
    i2 = rom[ICONPAL + d * 8 + 2] | rom[ICONPAL + d * 8 + 3] << 8
    w1, w2 = walk[d + 1][:2]
    mm = m[d * 384:(d + 1) * 384]
    assert all(mm[i] == 0 for i in range(1, 384, 2))
    mk = bytearray(mm[i] for i in range(0, 384, 2))
    gfx += g
    mk[0:32] = front_mask(ic[0:64]); mk[12 * 8:16 * 8] = front_mask(ic[64:128])
    mask += mk
    for c in (i1, i2): pals += bytes([c & 255, c >> 8])
    for c in (w1, w2): palsback += bytes([c & 255, c >> 8])
open(os.path.join(OUT, 'gfx.bin'), 'wb').write(gfx)
open(os.path.join(OUT, 'mask1bpp.bin'), 'wb').write(mask)
open(os.path.join(OUT, 'pals.bin'), 'wb').write(pals)
open(os.path.join(OUT, 'palsback.bin'), 'wb').write(palsback)

# 内部の番号 → ずかん番号（元の ROM の PokedexOrder）
syms = {}
for l in open(os.path.join(ROOT, 'syms', 'v.sym')):
    p = l.split()
    if len(p) == 2 and ':' in p[0]: syms[p[1]] = p[0]
b, a = syms['PokedexOrder'].split(':'); off = int(b, 16) * 0x4000 + int(a, 16) - 0x4000
order = rom[off:off + 190]
dex = bytes((x - 1) if 1 <= x <= 151 else 0xff for x in order)
open(os.path.join(OUT, 'dex.bin'), 'wb').write(dex)
print('gfx', len(gfx), 'mask', len(mask), 'pals', len(pals), 'dex', len(dex))
