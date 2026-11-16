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
farsrc = set()   # (バンク番号, その番号が書いてある ROM 上の位置)
FAR_A = {0x15a4, 0x15b7, 0x15e0, 0x1618, 0x1650, 0x166b, 0x3e7d}   # a にバンク番号を入れて呼ぶもの
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
        if mm: st[mm[1]] = int(mm[2], 16); st['@' + mm[1]] = o + 1; [st.pop(x, None) for x in ('bc', 'de', 'hl') if mm[1] in x]
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
                farsrc.add((st['b'], st['@b']))
            if tgt in FAR_A and 'a' in st:
                farsrc.add((st['a'], st['@a']))
            if tgt == PREDEF and 'a' in st:
                pb, pa = PREDEF_TABLE; po = off(pb, pa) + st['a'] * 3
                keep[po:po + 3] = True; farsrc.add((rom[po], po))
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
    a = st0; m0 = m_for(0); st0r = {}
    while a < en:
        t, n = one(m0, a)
        if rom[a] == 0xea and 0x20 <= rom[a + 2] < 0x40 and a + 3 <= en: sites.add(a)
        mm = re.match(r'ld (a|b), \$([0-9a-f]{2})$', t)
        if mm: st0r[mm[1]] = (int(mm[2], 16), a + 1)
        elif re.match(r'(ldh|ld|pop|inc|dec) (a|b|af|bc)\b', t) or re.match(r'(add|adc|sub|sbc|and|xor|or|cpl)', t):
            st0r.pop('a' if re.search(r' a|af|^(add|adc|sub|sbc|and|xor|or|cpl)', t) else 'b', None)
        mt = re.match(r'(call|jp) \$([0-9a-f]{4})$', t)
        if mt:
            tg = int(mt[2], 16)
            if tg == BANKSWITCH and 'b' in st0r: farsrc.add(st0r['b'])
            if tg in FAR_A and 'a' in st0r: farsrc.add(st0r['a'])
        if t.startswith('call') or t.startswith('rst') or t in ('ret', 'reti', 'jp hl') or t.startswith('jp $') or t.startswith('jr'):
            st0r = {}
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

# 4) 置き場所：ロムを 16 バンク（256KB）にすると、バンク番号 v は自動で v & 15 のバンクとして読まれる（MBC のミラー）。
#    だから、ほとんどのバンクは番号を変えずに v & 15 に置ける。ゲームのプログラムは 1MB 版とまったく同じ時間で動く。
#    v & 15 == 0 のバンク（10・20・30）はバンク0 と重なるので、空いているバンクに置いて、番号の出どころを書きかえる。
SIZE = 16
phys = {}; place = {}; renum = {}
def fits(p, v):
    if p == 0: return False
    for s_, e_ in v:
        for s2, e2 in phys.get(p, []):
            if s_ < e2 and s2 < e_: return False
    return True
for b in sorted(IV):
    p = b % SIZE
    if not fits(p, IV[b]): continue
    phys.setdefault(p, []).extend(IV[b]); place[b] = p
for b in sorted(IV):
    if b in place: continue
    p = next(p for p in range(1, SIZE) if fits(p, IV[b]))
    phys.setdefault(p, []).extend(IV[b]); place[b] = p; renum[b] = p
size = SIZE
print('使うバンク', len(IV) + 1, '→ ROM', size * 16, 'KB  番号を変えるバンク', {f'{k:02x}': f'{v:02x}' for k, v in renum.items()})
# 番号の出どころ：残すプログラムの中の farcall・predef 表・FarCopyData など
patch_src = sorted({o for v, o in farsrc if v in renum and (o < 0x4000 or keep[o])})
miss = [v for v in renum if not any(v2 == v for v2, o in farsrc if (o < 0x4000 or keep[o]))]
if miss: raise SystemExit('番号の出どころが見つからないバンク: ' + ' '.join(f'{v:02x}' for v in miss))

# 5) 新しい ROM を作る。ひとつの実バンクに論理バンクが 1 つだけなら、そのバンクをまるごと写す
#    （遊んで通らなかった道すじも残る）。いくつかで分け合う実バンクは、隙間を前の区間の持ち主にわたす。
new = bytearray(b'\xff' * (size * 0x4000))
new[:0x4000] = rom[:0x4000]
owner = {}   # 実バンク -> 長さ 0x4000 の持ち主（論理バンク）の並び
for p in range(1, size):
    occ = [b for b in place if place[b] == p]
    if not occ: continue
    if len(occ) == 1:
        own = [occ[0]] * 0x4000
    else:
        ivs = sorted((s_, e_, b) for b in occ for s_, e_ in IV[b])
        own = [None] * 0x4000
        for k, (s_, e_, b) in enumerate(ivs):
            nxt = ivs[k + 1][0] if k + 1 < len(ivs) else 0x4000
            st_ = 0 if k == 0 else s_
            for x in range(st_, nxt): own[x] = b
    owner[p] = own
    for x in range(0x4000):
        new[p * 0x4000 + x] = rom[own[x] * 0x4000 + x]
def newoff(o):
    if o < 0x4000: return o
    b = o // 0x4000; return place[b] * 0x4000 + o % 0x4000
for o in patch_src:
    v = rom[o]; assert v in renum
    new[newoff(o)] = renum[v]
# ヘッダー：ROM の大きさ、チェックサム
new[0x148] = {2: 0, 4: 1, 8: 2, 16: 3, 32: 4, 64: 5}[size]
c = 0
for i in range(0x134, 0x14d): c = (c - new[i] - 1) & 0xff
new[0x14d] = c
s = (sum(new) - new[0x14e] - new[0x14f]) & 0xffff
new[0x14e] = s >> 8; new[0x14f] = s & 0xff
open(OUT, 'wb').write(new)
with open(OUT[:-4] + '.map.txt', 'w') as f:
    f.write('renumber ' + ' '.join(f'{k:02x}->{v:02x}' for k, v in renum.items()) + '  at ' + ' '.join(f'{o:x}({rom[o]:02x})' for o in patch_src) + '\n')
    for p in sorted(owner):
        own = owner[p]; segs = []; x = 0
        while x < 0x4000:
            y = x
            while y < 0x4000 and own[y] == own[x]: y += 1
            segs.append(f'{own[x]:02x}:{x + 0x4000:04x}-{y + 0x3fff:04x}'); x = y
        f.write(f'実バンク {p:02x} ← ' + ' '.join(segs) + '\n')
    for w in sorted(set(warn)): f.write('WARN ' + w + '\n')
print('残した', int(keep.sum()), 'バイト  切り替え場所', len(sites), ' 注意', len(set(warn)))
print('summer_beach_small %08X' % zlib.crc32(new))
# 残した場所（新しい ROM の上で）。試験で「消した所を読んでいないか」を見るのに使う
pk = np.zeros(len(new), bool); pk[:0x4000] = True
for p in owner: pk[p * 0x4000:(p + 1) * 0x4000] = True
np.save(OUT[:-4] + '.keep.npy', pk)
