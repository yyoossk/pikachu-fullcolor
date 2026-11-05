"""各バンクの終わりの、0 が続いている所（あき）を出す。前の 16 バイトは、データの終わりの 0 かもしれないので使わない。
  使い方: python3 tools/freespace.py BASE.gbc [最小バイト数]
  出力: バンク 始まり 終わり(含まない) バイト数"""
import sys
MARGIN = 16
def free(d, mn=64):
    out = []
    for b in range(len(d) // 0x4000):
        s = b * 0x4000; e = s + 0x4000; i = e
        while i > s and d[i - 1] == 0: i -= 1
        st = i + MARGIN if i > s else s
        if e - st >= mn:
            base = 0 if b == 0 else 0x4000
            out.append((b, base + st - s, base + 0x4000, e - st))
    return out
if __name__ == '__main__':
    d = open(sys.argv[1], 'rb').read(); mn = int(sys.argv[2]) if len(sys.argv) > 2 else 64
    tot = 0
    for b, st, en, n in free(d, mn): print('%02x %04x %04x %d' % (b, st, en, n)); tot += n
    print('total', tot)
