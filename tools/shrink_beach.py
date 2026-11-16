#!/usr/bin/env python3
"""サマービーチだけの ROM（build/summer_beach.gbc, 1MB）から、要らない部分を消して小さい ROM に詰め直す。
  python3 tools/shrink_beach.py COVERAGE.npy        → build/summer_beach_small.gbc（と .map.txt）
COVERAGE.npy は tests/beach/cov.py で遊んで記録した「読まれた場所」（1=読まれた, 3=命令として実行）。
残すもの:
  ・実際に読まれた所（前後に少し余白）
  ・実行された命令から、飛び先（call/jp/jr/rst・farcall・predef）を静的にたどって届くプログラム
  ・ヘッダーと割り込みの入口
残したものをバンクごとの区間にして、アドレスが重ならないバンクどうしを 1 つのバンクにまとめる。
バンクの切り替え（ld [$2000], a）は、すべて「論理バンク → 実際のバンク」の表を引くルーチン経由にする。
消した所は $FF。"""
import os, sys, re, zlib
sys.path = [p for p in sys.path if os.path.abspath(p or ".") != os.path.dirname(os.path.abspath(__file__))]
import numpy as np
ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
import importlib.util
_sp = importlib.util.spec_from_file_location('gbdis', os.path.join(ROOT, 'tools', 'dis.py')); _gd = importlib.util.module_from_spec(_sp); _sp.loader.exec_module(_gd)
one = _gd.one

SRC = os.path.join(ROOT, 'build', 'summer_beach.gbc')
OUT = os.path.join(ROOT, 'build', 'summer_beach_small.gbc')
rom = open(SRC, 'rb').read()
cov = np.load(sys.argv[1])
NB = len(rom) // 0x4000
BANKSWITCH, BANKSWITCH_COMMON, PREDEF = 0x3e83, 0x3e7d, 0x3eb3
PREDEF_TABLE = (0x3d, 0x5d70)
PAD = 16

def off(b, a): return a if a < 0x4000 else b * 0x4000 + a - 0x4000
def m_for(b): return lambda x: rom[off(b, x & 0xffff)] if (x & 0xffff) < 0x8000 else 0

keep = np.zeros(len(rom), bool)
# 1) 読まれた所（余白つき）
idx = np.where(cov > 0)[0]
for i in idx:
    b = i // 0x4000; lo = b * 0x4000
    keep[max(lo, i - PAD):min(lo + 0x4000, i + PAD + 1)] = True
keep[0:0x4000] = True   # バンク0 はまるごと残す（いつも見えているバンク。大きさは変わらない）

# 2) 実行された命令からの静的なたどり
code = np.zeros(len(rom), bool)
warn = []
work = []
ex = (cov == 3)
# 実行された連続区間の先頭を入口にする
starts = np.where(ex & ~np.concatenate([[False], ex[:-1]]))[0]
for i in starts:
    if i < 0x4000: continue
    b = i // 0x4000; a = i if b == 0 else 0x4000 + (i - b * 0x4000)
    work.append((b, a, (b if b else None), {}))   # (この命令のあるバンク, アドレス, ROMX に今出ているバンク, レジスタの定数)
seen = set()
sites = set()   # ld [$2000-$3fff], a のある場所（ROM 上の位置）
while work:
    b, a, cur, st = work.pop()
    key = (b if a >= 0x4000 else 0, a, cur if a < 0x4000 else b)
    if key in seen: continue
    seen.add(key)
    st = dict(st)
    for _ in range(4000):
        if a >= 0x8000: break
        bb = b if a >= 0x4000 else 0
        if a >= 0x4000 and bb is None: break
        m = m_for(bb if a >= 0x4000 else 0)
        t, n = one(m, a)
        o = off(bb, a)
        if t.startswith('db '):
            warn.append(f'{bb:02x}:{a:04x} 不明な命令 {t}'); break
        code[o:o + n] = True; keep[o:o + n] = True
        op = rom[o]
        # 定数のレジスタを追う
        mm = re.match(r'ld (a|b|c|d|e|h|l), \$([0-9a-f]{2})$', t)
        m16 = re.match(r'ld (bc|de|hl), \$([0-9a-f]{4})$', t)
        if mm: st[mm[1]] = int(mm[2], 16); [st.pop(x, None) for x in ('bc', 'de', 'hl') if mm[1] in x]
        elif m16:
            mm = m16
            v = int(mm[2], 16); st[mm[1]] = v; st[mm[1][0]] = v >> 8; st[mm[1][1]] = v & 0xff
        elif re.match(r'(ldh|ld|inc|dec|pop|add|adc|sub|sbc|and|xor|or|cpl|rl|rr|sl|sr|swap|daa|res|set) ', t) or t in ('cpl', 'rla', 'rra', 'rlca', 'rrca', 'daa', 'scf', 'ccf'):
            for r in ('a', 'b', 'c', 'd', 'e', 'h', 'l', 'bc', 'de', 'hl'):
                dst = re.match(r'(?:ld|inc|dec|pop|res \d,|set \d,|rl|rr|rlc|rrc|sla|sra|srl|swap) (\[?\w+\]?)', t)
            dst = re.match(r'(?:ldh|ld|inc|dec|pop) (\w+)', t)
            if dst and dst[1] in ('a', 'b', 'c', 'd', 'e', 'h', 'l', 'bc', 'de', 'hl', 'af'):
                for r in (dst[1],) + ((dst[1][0], dst[1][1]) if len(dst[1]) == 2 else ('hl', 'bc', 'de')):
                    st.pop(r, None)
                if dst[1] == 'af': st.pop('a', None)
            if re.match(r'(add|adc|sub|sbc|and|xor|or|cp|cpl|rla|rra|rlca|rrca|daa)', t): st.pop('a', None)
            if t.startswith('add hl'): st.pop('hl', None); st.pop('h', None); st.pop('l', None)
        # ld [$2000-$3fff], a
        if op == 0xea and 0x20 <= rom[o + 2] < 0x40:
            sites.add(o)
            cur = st.get('a')
        if op == 0xcd and (m(a + 1) | m(a + 2) << 8) == BANKSWITCH_COMMON:
            cur = st.get('a')
        tgt = None
        mm = re.search(r'\$([0-9a-f]{4})$', t)
        if mm and re.match(r'(call|jp|jr)', t): tgt = int(mm[1], 16)
        if t.startswith('rst'): tgt = int(t[5:], 16)
        if tgt is not None:
            # 遠くへの呼び出し
            if tgt == BANKSWITCH and 'b' in st and 'hl' in st:
                work.append((st['b'], st['hl'], st['b'], {}))
            if tgt == PREDEF and 'a' in st:
                pb, pa = PREDEF_TABLE; po = off(pb, pa) + st['a'] * 3
                keep[po:po + 3] = True
                work.append((rom[po], rom[po + 1] | rom[po + 2] << 8, rom[po], {}))
            if tgt < 0x4000:
                pass   # バンク0 はまるごと残すので、たどらない
            elif tgt < 0x8000:
                tb = b if a >= 0x4000 else cur
                if tb is None:
                    # バンクが分からない：実際にそこを実行したバンクをたどる
                    hit = [x for x in range(1, NB) if cov[off(x, tgt)] == 3]
                    if not hit: warn.append(f'{bb:02x}:{a:04x} バンク不明の飛び先 {tgt:04x}')
                    for x in hit: work.append((x, tgt, x, st))
                else:
                    work.append((tb, tgt, tb, st))
        if t in ('ret', 'reti', 'jp hl') or t.startswith('jp $') or t.startswith('jr $'):
            break
        if t.startswith('call') or t.startswith('rst'):
            st = {}   # 呼んだ先でレジスタが変わる
        a += n

# バンク0 の ld [$2000-$3fff], a を、関数の頭から順に読んで探す
labels0 = sorted({int(l[3:7], 16) for l in open(SRC[:-4] + '.sym') if l.startswith('00:') and int(l[3:7], 16) < 0x4000})
for i, st0 in enumerate(labels0):
    en = labels0[i + 1] if i + 1 < len(labels0) else 0x4000
    a = st0; m0 = m_for(0)
    while a < en:
        t, n = one(m0, a)
        if rom[a] == 0xea and 0x20 <= rom[a + 2] < 0x40 and a + 3 <= en: sites.add(a)
        a += n
# 3) 区間にまとめる（バンクごと、$4000-$7fff の中のアドレスで）
def intervals(b):
    seg = keep[b * 0x4000:(b + 1) * 0x4000]
    if not seg.any(): return []
    iv = []; i = 0; L = len(seg)
    while i < L:
        if seg[i]:
            j = i
            while j < L and seg[j]: j += 1
            iv.append([i, j]); i = j
        else: i += 1
    out = []
    for s, e in iv:
        if out and s - out[-1][1] < 32: out[-1][1] = e
        else: out.append([s, e])
    return out
IV = {b: intervals(b) for b in range(1, NB)}
IV = {b: v for b, v in IV.items() if v}
for b, v in IV.items():
    for s, e in v: keep[b * 0x4000 + s:b * 0x4000 + e] = True

# 4) 詰める（大きいものから、アドレスが重ならない実バンクへ）
phys = {}   # 実バンク -> [区間]
place = {}  # 論理バンク -> 実バンク
def fits(p, v):
    for s, e in v:
        for s2, e2 in phys.get(p, []):
            if s < e2 and s2 < e: return False
    return True
order = sorted(IV, key=lambda b: -sum(e - s for s, e in IV[b]))
for b in order:
    p = 1
    while not fits(p, IV[b]): p += 1
    phys.setdefault(p, []).extend(IV[b]); place[b] = p
used = max(phys) + 1
size = 2
while size < used: size *= 2
print('使うバンク', len(IV) + 1, '→ 実バンク', used, '→ ROM', size * 16, 'KB')

# 5) 新しい ROM を作る
new = bytearray(b'\xff' * (size * 0x4000))
k0 = keep[:0x4000]
new[:0x4000] = bytes(rom[i] if k0[i] else 0xff for i in range(0x4000))
for b, p in place.items():
    for s, e in IV[b]:
        new[p * 0x4000 + s:p * 0x4000 + e] = rom[b * 0x4000 + s:b * 0x4000 + e]

# 6) バンクの表と切り替えルーチンを、バンク0 の消した所に置く
refs = set()
for o in np.where(code)[0]:
    if o >= 0x4000 and rom[o] in (0xcd, 0xc3, 0xc4, 0xcc, 0xd4, 0xdc, 0xc2, 0xca, 0xd2, 0xda, 0x21, 0x11, 0x01):
        refs.add(rom[o + 1] | rom[o + 2] << 8)
names0 = {}
for l in open(SRC[:-4] + '.sym'):
    if l.startswith('00:') and '.' not in l and int(l[3:7], 16) < 0x4000: names0.setdefault(int(l[3:7], 16), l.split()[1].strip())
def free0(n):
    L = sorted(names0) + [0x4000]
    for i in range(len(L) - 1):
        a, e = L[i], L[i + 1]
        if a < 0x150 or e - a < n: continue
        if (cov[a:e] > 0).any(): continue
        if any(a <= r < e for r in refs): continue
        if any(a <= x < e or x <= a < x + 3 for x in sites): continue
        if not names0[a][0].isupper() or names0[a] in KEEP0: continue
        return a, names0[a]
    raise SystemExit('バンク0 に置き場がない')
KEEP0 = set()
T, TNAME = free0(0x58)
table = [place.get(b, 0) for b in range(0x40)]
table[0] = table[1] = place.get(1, 1)
new[T:T + 0x40] = bytes(table)
R = T + 0x40
remap = bytes([0xe5,                 # push hl
               0xf5,                 # push af
               0xc6, T & 0xff,       # add LOW(table)
               0x6f,                 # ld l, a
               0x3e, T >> 8,         # ld a, HIGH(table)
               0xce, 0x00,           # adc 0
               0x67,                 # ld h, a
               0x7e,                 # ld a, [hl]
               0xea, 0x00, 0x20,     # ld [$2000], a
               0xf1,                 # pop af
               0xe1,                 # pop hl
               0xc9])                # ret
new[R:R + len(remap)] = remap
for o in sorted(sites):
    if o >= 0x4000:
        b = o // 0x4000; p = place[b]; o2 = p * 0x4000 + (o - b * 0x4000)
    else: o2 = o
    if new[o2] != 0xea: print("NG site", hex(o), place.get(o // 0x4000), [iv for iv in IV.get(o // 0x4000, []) if iv[0] <= (o % 0x4000) < iv[1]]); continue
    new[o2:o2 + 3] = bytes([0xcd, R & 0xff, R >> 8])
# ヘッダー：ROM の大きさ、チェックサム
new[0x148] = {2: 0, 4: 1, 8: 2, 16: 3, 32: 4, 64: 5}[size]
c = 0
for i in range(0x134, 0x14d): c = (c - new[i] - 1) & 0xff
new[0x14d] = c
s = (sum(new) - new[0x14e] - new[0x14f]) & 0xffff
new[0x14e] = s >> 8; new[0x14f] = s & 0xff
open(OUT, 'wb').write(new)
with open(OUT[:-4] + '.map.txt', 'w') as f:
    f.write(f'place {TNAME} table {T:04x} remap {R:04x} sites ' + ' '.join(f'{o:x}' for o in sorted(sites)) + '\n')
    for b in sorted(place): f.write(f'{b:02x} -> {place[b]:02x} ' + ' '.join(f'{s + 0x4000:04x}-{e + 0x3fff:04x}' for s, e in IV[b]) + '\n')
    for w in sorted(set(warn)): f.write('WARN ' + w + '\n')
print('残した', int(keep.sum()), 'バイト  切り替え場所', len(sites), ' 注意', len(set(warn)))
print('summer_beach_small %08X' % zlib.crc32(new))
# 残した場所（新しい ROM の上で）。試験で「消した所を読んでいないか」を見るのに使う
pk = np.zeros(len(new), bool); pk[:0x4000] = True
for b, p in place.items():
    for s_, e_ in IV[b]: pk[p * 0x4000 + s_:p * 0x4000 + e_] = True
np.save(OUT[:-4] + '.keep.npy', pk)
