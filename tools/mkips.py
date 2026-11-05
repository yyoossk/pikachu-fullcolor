#!/usr/bin/env python3
"""リリース用の IPS を作る。元のピカチュウ v1.0〜v1.3 のどれに当てても、同じ ROM になるパッチ。
  python3 tools/mkips.py build/v.gbc out.ips   （orig/v10.gb〜v13.gb を使う）
  作ったあと、4つの版に当てて同じになるか確かめる。"""
import sys, os, zlib
ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, os.path.join(ROOT, 'tools'))
from applyips import apply
tgt = open(sys.argv[1], 'rb').read(); out = sys.argv[2]
bases = [open(os.path.join(ROOT, 'orig', f'v1{i}.gb'), 'rb').read() for i in range(4)]
diff = [any(b[i] != tgt[i] for b in bases) for i in range(len(tgt))]
recs = []; i = 0; n = len(tgt)
while i < n:
    if not diff[i]: i += 1; continue
    j = i
    while j < n and (diff[j] or (j + 1 < n and diff[j + 1]) or (j + 2 < n and diff[j + 2])) and j - i < 0xffff: j += 1
    recs.append((i, tgt[i:j])); i = j
ips = bytearray(b'PATCH')
for off, data in recs:
    if off == 0x454f46:  # 'EOF'
        off -= 1; data = tgt[off:off + len(data) + 1]
    ips += off.to_bytes(3, 'big') + len(data).to_bytes(2, 'big') + data
ips += b'EOF'
open(out, 'wb').write(ips)
for i, b in enumerate(bases):
    assert apply(b, bytes(ips)) == tgt, f'v1.{i}'
print(out, len(ips), 'bytes, OK for v1.0-v1.3, CRC32 %08X' % zlib.crc32(tgt))
