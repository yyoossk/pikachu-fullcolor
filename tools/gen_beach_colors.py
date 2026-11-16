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

# ピカチュウ：OAM のフレーム表（3e:54ce, 36 個 × [base, ptr]）
O = lambda x: 0x3e * 0x4000 + x - 0x4000
TABLE = 0x54ce
vi = open(sys.argv[3], 'rb').read()   # はじめの画面のときの VRAM $8000-$8FFF（泳ぐピカチュウの絵）
INTRO_SRC = 0x20 * 0x4000 + 0x4c11 - 0x4000   # はじめの画面の絵は 20:4c11 から（遊んでいるときは 20:4411）
intro = lambda t: vi[t * 16:t * 16 + 16]
# もとの水色（色2）の点を、つながったかたまりで 4 つに分ける
#   ボード（または泳ぐときの波）＝大きなかたまり … 水色のまま（パレット0）
#   ほっぺ＝2×2 の 4 点、口を開いたときの舌＝MOUTH の点 … 赤（パレット1）
#   模様（背中の模様・しっぽの付け根など）＝それ以外 … 茶（パレット2＝白・黄・茶・黒）。黄のない部品の小さな水色はボードの一部なので水色のまま
# 8×8 の部品は透明のほかに 3 色まで。部品の中に赤と茶が両方あるときは赤を優先し、その部品の模様は輪郭の色に。
# 茶の部品に入るボードの点は透明（下の海はボードと同じ水色）。
BOARDMODE = os.environ.get('BOARDMODE', 'A')   # A：ボードと付け根が同じ部品なら、ボードを優先（付け根はその部品だけ水色のまま）
MOUTH = {1: {(13, 11)}, 2: {(13, 11)}, 3: {(12, 11)}, 4: {(12, 11)}, 5: {(11, 11)}, 6: {(11, 11)}, 7: {(11, 8)}, 8: {(11, 8)},
         9: {(12, 6)}, 10: {(12, 6)}, 15: {(12, 12)}, 17: {(13, 10)}, 18: {(12, 10)}}
# f8 のボードの左の先（黄 2 点・水色 2 点）は輪郭をはさんでボードからはなれているので、ここで指定（24×24 の 行, 列）
TIP_EXTRA = {8: {(19, 1), (19, 2), (20, 4), (20, 5)}}
FREE = [0x5810 + 0x40 * i for i in range(40)]   # 3e:5804〜7ae9 はゲームボーイ版のオープニング（このロムでは通らない）。新しい組をここに置く
assert all(b == 0 or True for b in rom[O(0x5804):O(0x7ae9)])
def frame(f):
    base = rom[O(TABLE) + f * 3]; ptr = rom[O(TABLE) + f * 3 + 1] | rom[O(TABLE) + f * 3 + 2] << 8
    n = rom[O(ptr)]; ents = [list(rom[O(ptr) + 1 + k * 4:O(ptr) + 5 + k * 4]) for k in range(n)]
    return base, ptr, ents
def compose(base, ents, src):
    img = {}; where_ = {}
    for k, (y, x, t, at) in enumerate(ents):
        p = dec(src((base + t) & 0xff)); oy = (y ^ 0x80) - 0x80; ox = (x ^ 0x80) - 0x80
        for yy in range(8):
            for xx in range(8):
                sx = 7 - xx if at & 0x20 else xx; sy = 7 - yy if at & 0x40 else yy
                img[(oy + yy, ox + xx)] = p[sy][sx]; where_[(oy + yy, ox + xx)] = (k, sy, sx)
    return img, where_
def classify(img, mouth):
    cls = {}; seen = set()
    for pnt, c in img.items():
        if c != 2 or pnt in seen: continue
        st = [pnt]; comp = []; seen.add(pnt)
        while st:
            y, x = st.pop(); comp.append((y, x))
            for dy, dx in ((-1, 0), (1, 0), (0, -1), (0, 1)):
                n = (y + dy, x + dx)
                if img.get(n) == 2 and n not in seen: seen.add(n); st.append(n)
        ys = [a for a, b in comp]; xs = [b for a, b in comp]
        if len(comp) > 8: k = 'board'
        elif len(comp) == 4 and max(ys) - min(ys) == 1 and max(xs) - min(xs) == 1: k = 'cheek'
        elif set(comp) <= mouth: k = 'mouth'
        else: k = 'pattern'
        for q in comp: cls[q] = k
    return cls
plans = []   # (フレーム番号のならび, 組のバイト列)
tile_fix = {}   # ROM の位置 -> 新しい 8×8
def comps_of(img, color):
    seen = set(); out = []
    for pnt, c in img.items():
        if c != color or pnt in seen: continue
        st = [pnt]; comp = []; seen.add(pnt)
        while st:
            y, x = st.pop(); comp.append((y, x))
            for dy, dx in ((-1, 0), (1, 0), (0, -1), (0, 1)):
                n = (y + dy, x + dx)
                if img.get(n) == color and n not in seen: seen.add(n); st.append(n)
        out.append(comp)
    return out
def touches(comp, cls, kind):
    return any(cls.get((y + dy, x + dx)) == kind for y, x in comp for dy in (-1, 0, 1) for dx in (-1, 0, 1))
def do_frame(f, src, src_rom, mouth_off, tips=False):
    base, ptr, ents = frame(f)
    img, where_ = compose(base, ents, src)
    mo = {(y + mouth_off[0], x + mouth_off[1]) for (y, x) in MOUTH.get(f, set())}
    cls = classify(img, mo)
    if tips:
        for comp in comps_of(img, 2):   # ボードにくっつく小さな水色（模様と見えたもの）はボード
            if cls[comp[0]] == 'pattern' and touches(comp, cls, 'board'):
                for q_ in comp: cls[q_] = 'board'
        for comp in comps_of(img, 1):   # ボードにくっつく小さな黄色（3 点まで）＝ボードの先 → 水色
            if len(comp) <= 3 and touches(comp, cls, 'board'):
                for q_ in comp: cls[q_] = 'boardtip'
        for (y, x) in TIP_EXTRA.get(f, ()):   # 輪郭をはさんでボードからはなれているボードの先
            q_ = (y - 12, x - 12)
            cls[q_] = 'boardtip' if img[q_] == 1 else 'board'
    pals = []
    for k, (y, x, t, at) in enumerate(ents):
        tt = (base + t) & 0xff; p = dec(src(tt)); kinds = set()
        for pnt, (kk, sy, sx) in where_.items():
            if kk == k and pnt in cls and cls[pnt] != 'boardtip': kinds.add(cls[pnt])
        tipcells = [(sy, sx) for pnt, (kk, sy, sx) in where_.items() if kk == k and cls.get(pnt) == 'boardtip']
        has_y = any(v == 1 for r in p for v in r)
        if not kinds - {'board'} or not has_y: pal = 0   # 黄のない部品（ボードだけの所）の小さな水色はボードの一部
        elif kinds & {'cheek', 'mouth'}: pal = 1
        elif 'board' in kinds: pal = 0 if BOARDMODE == 'A' else 3   # ボードの中は水色でそろえる
        else: pal = 2
        pals.append(pal)
        q = [r[:] for r in p]
        for sy, sx in tipcells:   # ボードの先の黄色 → ボードの水色（赤・茶の部品ではすき間＝下の海の水色）
            q[sy][sx] = 2 if pal in (0, 3) else 0
        if pal == 0:
            if q != p:
                h = src_rom + tt * 16
                if h in tile_fix: assert tile_fix[h] == q
                tile_fix[h] = q
            continue
        for pnt, (kk, sy, sx) in where_.items():
            if kk != k or q[sy][sx] != 2: continue
            c = cls[pnt]
            if pal == 1: q[sy][sx] = 2 if c in ('cheek', 'mouth') else 3
            elif pal == 2: q[sy][sx] = 2 if c == 'pattern' else 0
            else: q[sy][sx] = 3 if c == 'pattern' else 2   # パレット3（黄・水色・茶）：付け根＝色3（茶）。この部品の輪郭も茶
        h = src_rom + tt * 16
        assert rom[h:h + 16] == src(tt), (f, hex(tt))
        if h in tile_fix: assert tile_fix[h] == q, f'f{f} タイル {tt:02x} がほかのポーズと食いちがう'
        tile_fix[h] = q
    b = bytearray([len(ents)])
    for (y, x, t, at), pal in zip(ents, pals): b += bytes([y, x, t, (at & ~7) | pal])
    return bytes(b)
blocks = {}
for f in list(range(1, 16)) + [17, 18]:
    blocks.setdefault(do_frame(f, obj, OBJ_SRC, (-12, -12), tips=True), []).append(f)
for f in (32, 33, 34, 35):
    blocks.setdefault(do_frame(f, intro, INTRO_SRC, (0, 0)), []).append(f)
for h, q in sorted(tile_fix.items()):
    if enc(q) != rom[h:h + 16]:
        done[h] = True; emit(0x20, 0x4000 + h % 0x4000, enc(q), 'ピカチュウ：ほっぺ・口は赤、模様は茶の色番号に')
for i, (b, fs) in enumerate(blocks.items()):
    a = FREE[i]; assert len(b) <= 0x40
    emit(0x3e, a, b, 'ピカチュウの組（' + '・'.join(f'f{f}' for f in fs) + '）')
    for f in fs:
        emit(0x3e, TABLE + f * 3 + 1, bytes([a & 0xff, a >> 8]), f'フレーム f{f} → 3e:{a:04x}')
print('ピカチュウの組', len(blocks), '部品', len(tile_fix))

# 正面のポーズ（f15 base $6c・f16 base $9c）のボードの中の黄色 → 水色
def board_fill(q):
    for y in range(8):
        for x in range(8):
            if q[y][x] == 1 and y >= 4: q[y][x] = 2
for base in (0x6c, 0x9c): edit_tile(obj, (base + 0x21) & 0xff, board_fill, 'サーフボード：中の黄色をなくす')

# 水しぶき（f25 3e:5595・f19 3e:55a2・f20 3e:55bb。絵は色1 だけ）→ パレット7。
# パレット7 は色の表 16 番を OBP1（$E0：色1→色0）で写したもの。スプライトでは色0 は透明で使わないので、16 番の色0 を白っぽい水色にする
for ptr, n in ((0x5595, 3), (0x55a2, 6), (0x55bb, 12)):
    b = bytearray(rom[O(ptr):O(ptr) + 1 + 4 * n]); assert b[0] == n
    for k in range(n): b[4 + 4 * k] = (b[4 + 4 * k] & ~7) | 7
    emit(0x3e, ptr, bytes(b), '水しぶき → パレット7（白っぽい水色）')

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
emit(0x09, PAL + 0x15 * 8, rgb(31, 31, 31) + rgb(31, 31, 0) + rgb(17, 9, 3) + rgb(3, 3, 3), '色15：模様（白・黄・茶・こげ茶）')
emit(0x09, PAL + 0x16 * 8, rgb(24, 30, 31) + rgb(31, 31, 0) + rgb(11, 23, 31) + rgb(17, 9, 3), '色16：色0＝水しぶきの白っぽい水色（パレット7 の色1）、色1〜3＝黄・水色・茶（ボードと付け根が同じ部品）')
# 背景パレット4 は色の表の 0F 番から（1c:67d0）。サマービーチでは画面に使われていないので、島とヤシの木に
emit(0x09, PAL + 0x0f * 8, rgb(31, 31, 31) + rgb(30, 25, 13) + rgb(3, 17, 5) + rgb(15, 8, 3), '色0F（背景パレット4）：島とヤシの木（白・砂・緑・茶）')
# PAL_SET：4 つの枠を ビーチ・14・15・16 に
emit(0x1c, 0x6bb4, bytes([0x51, 0x25, 0x00, 0x14, 0x00, 0x15, 0x00, 0x16, 0x00]), 'サマービーチの PAL_SET')

open(os.path.join(ROOT, 'beach', 'colors.asm'), 'w').write('; tools/gen_beach_colors.py で作ったもの（手で直さない）\n\n' + '\n'.join(out))
print(len(out), 'lines;', len(done), 'tiles')
