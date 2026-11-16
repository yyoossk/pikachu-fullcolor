#!/usr/bin/env python3
"""サマービーチだけのゲームの色直しを、データ（beach/colors.asm）として作る。
  python3 tools/gen_beach_colors.py VRAM0.bin VRAM8800.bin VRAM_INTRO.bin
  VRAM_INTRO.bin … はじめの画面のときの VRAM $8000-$8FFF（泳ぐピカチュウの絵）
  VRAM0.bin      … 遊んでいる最中の VRAM $8000-$8FFF（スプライトの絵）
  VRAM8800.bin   … 遊んでいる最中の VRAM $8800-$97FF（背景・ウィンドウの絵）
直すもの（どれもデータだけ。毎フレームの処理の時間は変えない＝波の並びは同じ）:
  ・雲：輪郭を黒（色3）、中を白（すき間＝空の白）
  ・ピカチュウのほっぺ：赤（スプライトのパレット1 = 白・黄・赤・こげ茶）。ほっぺのない所の水色の点は輪郭の色に
  ・サーフボード：正面のポーズの、ボードの中の黄色をなくす
  ・島とヤシの木：葉は緑、幹は茶、島は砂の色（背景のパレット2・3）
"""
import os, sys
ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
rom = open(os.path.join(ROOT, 'build', 'xf.gbc'), 'rb').read()
v0 = open(sys.argv[1], 'rb').read(); v8 = open(sys.argv[2], 'rb').read()
out = []
def emit(bank, addr, data, note):
    out.append(f'SECTION "beachcol_{bank:02x}_{addr:04x}", ROM{"0" if bank == 0 else "X"}[${addr:04x}]{"" if bank == 0 else f", BANK[${bank:02x}]"} ; {note}')
    for i in range(0, len(data), 16):
        out.append('\tdb ' + ', '.join(f'${b:02x}' for b in data[i:i + 16]))
    out.append('')
def where(tilebytes, hint=None):
    hits = []; i = rom.find(tilebytes)
    while i >= 0: hits.append(i); i = rom.find(tilebytes, i + 1)
    return hits
def dec(d): return [[((d[2 * y] >> (7 - x)) & 1) | (((d[2 * y + 1] >> (7 - x)) & 1) << 1) for x in range(8)] for y in range(8)]
def enc(p):
    b = bytearray()
    for y in range(8):
        lo = hi = 0
        for x in range(8):
            lo |= (p[y][x] & 1) << (7 - x); hi |= (p[y][x] >> 1) << (7 - x)
        b += bytes([lo, hi])
    return bytes(b)
done = {}
OBJ_SRC = 0x20 * 0x4000 + 0x4411 - 0x4000   # スプライトの絵は 20:4411 から $1000 バイト（3e:4142 の FarCopyData）
def edit_tile(src, t, fn, note):
    d = src(t)
    p = dec(d); q = [r[:] for r in p]; fn(q)
    if q == p: return
    if src is obj:
        hits = [OBJ_SRC + t * 16]
    else:
        hits = [h for h in where(d) if (h - 1) % 16 == 0 or h % 16 == 0]
        assert len(hits) == 1, f'bg tile {t:02x}: {hits}'
    for h in hits: assert rom[h:h + 16] == d, f'tile {t:02x} mismatch'
    for o in hits:
        if o in done: continue
        done[o] = True
        b = o // 0x4000; a = o if b == 0 else 0x4000 + o % 0x4000
        emit(b, a, enc(q), f'{note} (VRAM タイル ${t:02x})')
obj = lambda t: v0[t * 16:t * 16 + 16]
def bg(t):
    o = 0x1000 + (t if t < 128 else t - 256) * 16 - 0x800
    return v8[o:o + 16]

# 雲（スプライト $EC-$EF）
def cloud(q):
    for r in q:
        for x in range(8):
            r[x] = {0: 0, 1: 0, 2: 3, 3: 3}[r[x]]
for t in (0xec, 0xed, 0xee, 0xef): edit_tile(obj, t, cloud, '雲：輪郭を黒・中を白')

# ピカチュウ：OAM のフレーム表（3e:54ce, 36 個 × [base, ptr]）と 9 枚の組（3e:553f）
O = lambda x: 0x3e * 0x4000 + x - 0x4000
TABLE, BLK = 0x54ce, 0x553f
blk = [list(rom[O(BLK) + 1 + k * 4:O(BLK) + 5 + k * 4]) for k in range(9)]
# 水色（色2）のままにする＝ボードの入っている部品（パレット0）
BOARD = {}
for f in range(1, 19):
    BOARD[f] = {0x10, 0x20, 0x21, 0x22} if f <= 4 else {0x02, 0x12, 0x22} if f >= 17 else {0x12, 0x20, 0x21, 0x22} if 11 <= f <= 14 else {0x20, 0x21, 0x22}
# 口を開いたときの舌（1 点）。ポーズごとの位置（24×24 の中の 行, 列）
MOUTH = {1: {(13, 11)}, 2: {(13, 11)}, 3: {(12, 11)}, 4: {(12, 11)}, 5: {(11, 11)}, 6: {(11, 11)}, 7: {(11, 8)}, 8: {(11, 8)},
         9: {(12, 6)}, 10: {(12, 6)}, 15: {(12, 12)}, 17: {(13, 10)}, 18: {(12, 10)}}
# しっぽの付け根：右下の部品 $22（f7・f8 は $21 にも 1 点）の、小さな水色のかたまり
#   f1〜f6 … パレット2（白・黄・茶・黒）。部品に入るボードの先（f3〜f6）はすき間にする（下の海はボードと同じ水色）
#   f7・f8 … ボードの大部分が同じ部品なので、パレット3（白・茶・水色・黒）。付け根を色1（茶）に。部品の黄色 2 点も茶になる
TAILPAL = {1: 2, 2: 2, 3: 2, 4: 2, 5: 2, 6: 2, 7: 3, 8: 3}
# ほっぺの部品：ポーズ全体（24×24）で見て、まわり 4 方向がどれもすき間（色0）でない水色の点＝ほっぺ。
# すき間に接する水色の点（背中の輪郭のふち取り）は輪郭の色（色3）に。
def frame_pixels(base):
    img = [[0] * 24 for _ in range(24)]
    for (y, x, t, at) in blk:
        p = dec(obj((base + t) & 0xff)); oy = ((y ^ 0x80) - 0x80) + 12; ox = ((x ^ 0x80) - 0x80) + 12
        for yy in range(8):
            for xx in range(8): img[oy + yy][ox + xx] = p[yy][xx]
    return img
def cheek_mask(img, board_cells):
    # すき間に接しない水色の点の、つながったかたまりで 3 点以上のもの＝ほっぺ
    ok = [[img[Y][X] == 2 and (Y // 8, X // 8) not in board_cells and all(
        (img[Y + dy][X + dx] if 0 <= Y + dy < 24 and 0 <= X + dx < 24 else 0) != 0 for dy, dx in ((-1, 0), (1, 0), (0, -1), (0, 1)))
        for X in range(24)] for Y in range(24)]
    seen = set(); keep = set()
    for Y in range(24):
        for X in range(24):
            if not ok[Y][X] or (Y, X) in seen: continue
            st = [(Y, X)]; comp = []; seen.add((Y, X))
            while st:
                y, x = st.pop(); comp.append((y, x))
                for dy, dx in ((-1, 0), (1, 0), (0, -1), (0, 1)):
                    n = (y + dy, x + dx)
                    if 0 <= n[0] < 24 and 0 <= n[1] < 24 and ok[n[0]][n[1]] and n not in seen: seen.add(n); st.append(n)
            if len(comp) >= 3: keep |= set(comp)
    return keep
cheek_tiles = {}
for f in range(1, 19):
    base = rom[O(TABLE) + f * 3]; img = frame_pixels(base)
    bc = {((((y ^ 0x80) - 0x80) + 12) // 8, (((x ^ 0x80) - 0x80) + 12) // 8) for (y, x, t, at) in blk if t in BOARD[f]}
    keep = cheek_mask(img, bc)
    if f in (13, 14):   # 横向き：部品 $11 の右はし（ボードのふち）はほっぺではない
        keep = {(Y, X) for (Y, X) in keep if not (8 <= Y < 16 and X >= 13)}
    keep |= MOUTH.get(f, set())   # 口を開いたときの舌＝赤
    for (y, x, t, at) in blk:
        if t in BOARD[f]: continue
        tt = (base + t) & 0xff; oy = ((y ^ 0x80) - 0x80) + 12; ox = ((x ^ 0x80) - 0x80) + 12
        def fix(q, oy=oy, ox=ox, keep=keep):
            for yy in range(8):
                for xx in range(8):
                    if q[yy][xx] == 2 and (oy + yy, ox + xx) not in keep: q[yy][xx] = 3
        cheek_tiles[tt] = (f, fix)
for tt, (f, fix) in sorted(cheek_tiles.items()):
    edit_tile(obj, tt, fix, f'ピカチュウ f{f}：ほっぺ以外の水色を輪郭の色に')
def tail_root(img):
    seen = set(); out = set()
    for Y in range(24):
        for X in range(24):
            if img[Y][X] != 2 or (Y, X) in seen: continue
            st = [(Y, X)]; comp = []; seen.add((Y, X))
            while st:
                y, x = st.pop(); comp.append((y, x))
                for dy, dx in ((-1, 0), (1, 0), (0, -1), (0, 1)):
                    n = (y + dy, x + dx)
                    if 0 <= n[0] < 24 and 0 <= n[1] < 24 and img[n[0]][n[1]] == 2 and n not in seen: seen.add(n); st.append(n)
            if len(comp) <= 5 and all(y >= 16 and x >= 15 for y, x in comp): out |= set(comp)
    return out
for f, pal in TAILPAL.items():
    base = rom[O(TABLE) + f * 3]; img = frame_pixels(base); tr = tail_root(img)
    for off_, oy, ox in ((0x22, 16, 16), (0x21, 16, 8)):
        tt = (base + off_) & 0xff
        if off_ == 0x22:
            def fix(q, oy=oy, ox=ox, tr=tr, pal=pal):
                for yy in range(8):
                    for xx in range(8):
                        if q[yy][xx] != 2: continue
                        if (oy + yy, ox + xx) in tr:
                            if pal == 3: q[yy][xx] = 1   # 茶（パレット3 の色1）
                        elif pal == 2: q[yy][xx] = 0     # ボードの水色 → すき間（下の海の水色が見える。海とボードは同じ水色）
            edit_tile(obj, tt, fix, f'ピカチュウ f{f}：しっぽの付け根（パレット{pal}）')
        else:
            def fix21(q, oy=oy, ox=ox, tr=tr):
                for yy in range(8):
                    for xx in range(8):
                        if q[yy][xx] == 2 and (oy + yy, ox + xx) in tr: q[yy][xx] = 1   # ボードと同じ部品なので黄に
            edit_tile(obj, tt, fix21, f'ピカチュウ f{f}：しっぽの付け根（部品 $21 の点は黄に）')
# 正面のポーズ（f15 base $6c・f16 base $9c）のボードの中の黄色 → 水色
def board_fill(q):
    for y in range(8):
        for x in range(8):
            if q[y][x] == 1 and y >= 4: q[y][x] = 2
for base in (0x6c, 0x9c): edit_tile(obj, (base + 0x21) & 0xff, board_fill, 'サーフボード：中の黄色をなくす')

# フレームの組：B（ほとんど）は今の組を書きかえ、A・C・E は新しい組（3e:4000〜 の使わない SurfingPikachuMinigame の所）
def block(board, tailpal=None):
    b = bytearray([9])
    for (y, x, t, at) in blk:
        pal = (tailpal if (t == 0x22 and tailpal) else 0) if t in board else 1
        b += bytes([y, x, t, (at & ~7) | pal])
    return bytes(b)
emit(0x3e, BLK, block(BOARD[9]), 'ピカチュウ 9 枚の組：ほっぺの部品をパレット1に（f9・f10・f15・f16）')
groups = [('A', [1, 2, 3, 4], 0x4000), ('E', [11, 12, 13, 14], 0x4025), ('C', [17, 18], 0x404a),
          ('B5', [5, 6], 0x7fa0), ('B7', [7, 8], 0x7fc5)]   # 3e:4000〜 は使わない SurfingPikachuMinigame、3e:7fa0〜 は空き
assert all(b == 0 for b in rom[O(0x7fa0):O(0x8000)])
for name, fs, NEW in groups:
    emit(0x3e, NEW, block(BOARD[fs[0]], TAILPAL.get(fs[0])), f'ピカチュウ 9 枚の組 {name}（f{fs[0]}〜f{fs[-1]}）')
    for f in fs:
        emit(0x3e, TABLE + f * 3 + 1, bytes([NEW & 0xff, NEW >> 8]), f'フレーム f{f} → 組 {name}')

# 水しぶき（f25 3e:5595・f19 3e:55a2・f20 3e:55bb。絵は色1 だけ）→ パレット4（白）
for ptr, n in ((0x5595, 3), (0x55a2, 6), (0x55bb, 12)):
    b = bytearray(rom[O(ptr):O(ptr) + 1 + 4 * n]); assert b[0] == n
    for k in range(n): b[4 + 4 * k] = (b[4 + 4 * k] & ~7) | 4
    emit(0x3e, ptr, bytes(b), '水しぶき → パレット4（ビーチの色を OBP1 で：色1＝白。元のゲームボーイ版と同じ白）')
# はじめの画面で泳ぐピカチュウ（f32〜f35, 3e:565b, 4×3 枚。左右反転）：まん中の段をパレット1（ほっぺ）に。
# まん中の段の絵は、2×2 の水色のかたまり（ほっぺ）以外の水色を輪郭の色に
SWIM = 0x565b
b = bytearray(rom[O(SWIM):O(SWIM) + 49]); assert b[0] == 12
for k in range(4, 8): b[4 + 4 * k] = (b[4 + 4 * k] & ~7) | 1
emit(0x3e, SWIM, bytes(b), '泳ぐピカチュウ：まん中の段をパレット1に')
def cluster_only(q):
    keep = set()
    for y in range(7):
        for x in range(7):
            if q[y][x] == q[y][x + 1] == q[y + 1][x] == q[y + 1][x + 1] == 2: keep |= {(y, x), (y, x + 1), (y + 1, x), (y + 1, x + 1)}
    for y in range(8):
        for x in range(8):
            if q[y][x] == 2 and (y, x) not in keep: q[y][x] = 3
# はじめの画面の絵は、遊んでいるときとは別の 20:4c11 から読み込まれる（VRAM $8000〜）
vi = open(sys.argv[3], 'rb').read()   # はじめの画面のときの VRAM $8000-$8FFF
INTRO_SRC = 0x20 * 0x4000 + 0x4c11 - 0x4000
for base in (0x80, 0x84, 0x88, 0x8c):
    for k in range(4):
        t = base + 0x10 + k; d = vi[t * 16:t * 16 + 16]; h = INTRO_SRC + t * 16
        assert rom[h:h + 16] == d, hex(t)
        p_ = dec(d); q = [r[:] for r in p_]; cluster_only(q)
        if q != p_ and h not in done:
            done[h] = True; emit(0x20, 0x4000 + h % 0x4000, enc(q), f'泳ぐピカチュウ：ほっぺ以外の水色を輪郭の色に (はじめの画面のタイル ${t:02x})')

# 絵の部品の色：3e:7c52 の and $e0（反転・優先だけ残す）を and $e7 に（パレット 0〜7 も残す）。命令の長さ・時間は同じ。
# もとのデータはどれも下 3 ビットが 0 なので、ほかの部品は変わらない
assert rom[O(0x7c52):O(0x7c54)] == b'\xe6\xe0'
emit(0x3e, 0x7c53, bytes([0xe7]), 'SetCurrentAnimatedObjectOAMAttributes：パレットの番号も残す')

# 島とヤシの木（背景 $15-$18）
def palm(q):
    for r in q:
        for x in range(8):
            if r[x] == 3: r[x] = 2   # 葉＝緑（背景パレット4 の色2）
edit_tile(bg, 0x15, palm, 'ヤシの葉')
edit_tile(bg, 0x16, palm, 'ヤシの葉')
def isl17(q):
    for y in range(3, 8):
        for x in range(8):
            if q[y][x] == 3: q[y][x] = 1   # 島＝砂（色1）。幹（上の 3 行）は色3＝茶
def isl18(q):
    for y in range(8):
        for x in range(8):
            if q[y][x] == 3: q[y][x] = 2 if y < 3 else 1   # 上の葉＝緑（色2）、島＝砂（色1）
edit_tile(bg, 0x17, isl17, '島と幹')
edit_tile(bg, 0x18, isl18, '島と葉のはし')

# ウィンドウ（$9C00）の色分け：フルカラー化の処理が 09:5d50 の見出しから HDMA で 1KB 写す（背景 $9800 と同じ 09:5d60 を使っていた）。
# ウィンドウの分だけ、使っていない 09:6510（見える 3 行分の 96 バイトが全部 0。HDMA の元は 16 バイトそろえ）を指すようにする（写す量は同じ＝時間も同じ）。葉 2 枚＝パレット2、島 2 枚＝パレット3
WIN = 0x6510
assert WIN % 16 == 0 and all(b == 0 for b in rom[9 * 0x4000 + WIN - 0x4000:9 * 0x4000 + WIN - 0x4000 + 0x60])
emit(0x09, 0x5d51, bytes([(WIN - 0x5d53) & 0xff, (WIN - 0x5d53) >> 8]), 'ウィンドウの色分けの場所 → 09:6510')
emit(0x09, WIN + 0x01, bytes([4, 4]), 'ウィンドウ 1 行目：ヤシの葉 → パレット4')
emit(0x09, WIN + 0x21, bytes([4, 4]), 'ウィンドウ 2 行目：島と幹 → パレット4')

# 色の表（バンク09 の 6ef9 + 番号×8）：使わない 14・15・16 番を書きかえる
def rgb(r, g, b): v = r | g << 5 | b << 10; return bytes([v & 0xff, v >> 8])
PAL = 0x6ef9
emit(0x09, PAL + 0x14 * 8, rgb(31, 31, 31) + rgb(31, 31, 0) + rgb(31, 4, 4) + rgb(3, 3, 3), '色14：ほっぺ（白・黄・赤・こげ茶）')
emit(0x09, PAL + 0x15 * 8, rgb(31, 31, 31) + rgb(31, 31, 0) + rgb(17, 9, 3) + rgb(3, 3, 3), '色15：しっぽの付け根（白・黄・茶・こげ茶）')
emit(0x09, PAL + 0x16 * 8, rgb(31, 31, 31) + rgb(17, 9, 3) + rgb(11, 23, 31) + rgb(3, 3, 3), '色16：しっぽの付け根とボード（白・茶・水色・こげ茶）')
# 背景パレット4 は色の表の 0F 番から（1c:67d0）。サマービーチでは画面に使われていないので、島とヤシの木に
emit(0x09, PAL + 0x0f * 8, rgb(31, 31, 31) + rgb(30, 25, 13) + rgb(3, 17, 5) + rgb(15, 8, 3), '色0F（背景パレット4）：島とヤシの木（白・砂・緑・茶）')
# PAL_SET：4 つの枠を ビーチ・14・15・16 に
emit(0x1c, 0x6bb4, bytes([0x51, 0x25, 0x00, 0x14, 0x00, 0x15, 0x00, 0x16, 0x00]), 'サマービーチの PAL_SET')

open(os.path.join(ROOT, 'beach', 'colors.asm'), 'w').write('; tools/gen_beach_colors.py で作ったもの（手で直さない）\n\n' + '\n'.join(out))
print(len(out), 'lines;', len(done), 'tiles')
