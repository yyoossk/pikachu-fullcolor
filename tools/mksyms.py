"""元のピカチュウ（pokeyellow-jp）のラベルが、Ver.3.50 の ROM のどこにあるかを、中身の一致で探す。
  使い方: python3 tools/mksyms.py ORIG.gb ORIG.sym BASE.gbc OUT.sym
  ・RAM のラベル（WRAM/HRAM/SRAM）は元のまま書く。改造で足した変数のあとのラベルはずれていることがあるので、
    使う前にエミュレーターで確かめる（README）。
  ・ROM のラベル：そのラベルから次のラベルまで（最大24バイト）が1か所だけ見つかれば、その場所。
    見つからなければ、命令の 16ビットの値（call/jp の行き先、ld hl,nn など）を比べないで探しなおす。
    同じバンクを先に探す。1か所に決まらないラベルはのせない。
  ・それでも見つからないラベルは、すぐ前の見つかったラベルから元と同じ距離の所で、中身（8バイト）が合えばその場所。
"""
import sys, re, bisect
orig, osym, base, out = sys.argv[1:5]
O = open(orig, 'rb').read(); B = open(base, 'rb').read()
syms = []
for l in open(osym):
    m = re.match(r'([0-9a-f]+):([0-9a-f]+) (\S+)', l)
    if m: syms.append((int(m.group(1), 16), int(m.group(2), 16), m.group(3)))
def off(bk, ad): return ad if ad < 0x4000 else bk * 0x4000 + ad - 0x4000
# the length of each instruction, and whether bytes 1-2 are a 16-bit value
L2 = {0x06,0x0e,0x16,0x1e,0x26,0x2e,0x36,0x3e,0x18,0x20,0x28,0x30,0x38,0xc6,0xce,0xd6,0xde,0xe6,0xee,0xf6,0xfe,0xe0,0xf0,0xe8,0xf8,0xcb}
W16 = {0x01,0x11,0x21,0x31,0x08,0xc2,0xc3,0xca,0xd2,0xda,0xc4,0xcc,0xcd,0xd4,0xdc,0xea,0xfa}
def mask(data):
    """bytes → a pattern with None where a 16-bit value is"""
    p = []; i = 0
    while i < len(data):
        op = data[i]
        if op in W16: p += [op, None, None]; i += 3
        elif op in L2: p += [op] + list(data[i + 1:i + 2]); i += 2
        else: p.append(op); i += 1
    return p[:len(data)]
def find_masked(pat, lo, hi, limit=2):
    hits = []; first = next(j for j, v in enumerate(pat) if v is not None)
    p = B.find(bytes([pat[first]]), lo + first, hi)
    while p >= 0 and len(hits) < limit:
        s = p - first
        if s + len(pat) <= hi and all(v is None or B[s + j] == v for j, v in enumerate(pat)): hits.append(s)
        p = B.find(bytes([pat[first]]), p + 1, hi)
    return hits
rom = sorted((off(b, a), n, b, a) for b, a, n in syms if a < 0x8000)
offs = [r[0] for r in rom]
lost = []
res = []; stat = {'ram': 0, 'same': 0, 'moved': 0, 'masked': 0, 'lost': 0}
for b, a, n in syms:
    if a >= 0x8000:
        res.append((b, a, n)); stat['ram'] += 1; continue
    o = off(b, a)
    i = bisect.bisect_right(offs, o)
    nxt = offs[i] if i < len(offs) else len(O)
    ln = min(24, nxt - o)
    if ln < 8: ln = 16
    pat = O[o:o + ln]
    if B[o:o + ln] == pat:
        res.append((b, a, n)); stat['same'] += 1; continue
    lo, hi = (0, 0x4000) if a < 0x4000 else (b * 0x4000, b * 0x4000 + 0x4000)
    def exact(lo, hi):
        h = []; p = B.find(pat, lo, hi)
        while p >= 0 and len(h) < 2: h.append(p); p = B.find(pat, p + 1, hi)
        return h
    hits = exact(lo, hi)
    if len(hits) != 1: hits = exact(0, len(B))
    kind = 'moved'
    if len(hits) != 1:
        mp = mask(O[o:o + 24])
        if sum(v is not None for v in mp) >= 12:
            hits = find_masked(mp, lo, hi)
            if len(hits) != 1 and a >= 0x4000: hits = find_masked(mp, 0x4000, len(B))
            kind = 'masked'
    if len(hits) == 1:
        h = hits[0]; nb = 0 if h < 0x4000 else h // 0x4000; na = h if h < 0x4000 else 0x4000 + h % 0x4000
        res.append((nb, na, n)); stat[kind] += 1
    else:
        stat['lost'] += 1; lost.append((b, a, n, o))
# 2nd pass: a lost label right after a found one (the same distance as in the original) if its bytes match there
found = {}
for nb, na, n in res:
    if na < 0x8000: found[n] = off(nb, na)
byoff = {}
for b, a, n in syms:
    if a < 0x8000: byoff.setdefault(off(b, a), []).append(n)
for b, a, n, o in lost:
    i = bisect.bisect_left(offs, o) - 1
    done = False
    while i >= 0 and o - offs[i] < 0x400 and not done:
        po = offs[i]
        for pn in byoff.get(po, []):
            if pn in found:
                cand = found[pn] + (o - po)
                mp = mask(O[o:o + 8])
                if cand + 8 <= len(B) and (cand < 0x4000) == (o < 0x4000) and all(v is None or B[cand + j] == v for j, v in enumerate(mp)):
                    nb = 0 if cand < 0x4000 else cand // 0x4000; na = cand if cand < 0x4000 else 0x4000 + cand % 0x4000
                    res.append((nb, na, n)); found[n] = cand; stat['near'] = stat.get('near', 0) + 1; stat['lost'] -= 1
                done = True; break
        i -= 1
with open(out, 'w') as f:
    f.write('; Ver.3.50 の ROM でのラベルの場所（tools/mksyms.py で作ったもの。見つからなかったラベルはのせていない）\n')
    for b, a, n in sorted(res): f.write('%02x:%04x %s\n' % (b, a, n))
print(base, stat)
