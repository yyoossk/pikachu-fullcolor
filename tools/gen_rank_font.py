#!/usr/bin/env python3
"""はじめの画面のランキング用の文字（0〜9・ー・ハイスコア）を、ゲームの文字（04:4a19 の 1bpp）から 2bpp（色3）にして beach/rank_font.inc に書く。
  python3 tools/gen_rank_font.py build/xf.gbc"""
import sys, os
ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
rom = open(sys.argv[1], 'rb').read()
FONT = 4 * 0x4000 + 0x4a19 - 0x4000          # 文字 $80〜$ff の絵（1文字 8 バイト）
chars = list(range(0xf6, 0x100)) + [0xe3, 0x99, 0x81, 0x8c, 0x89, 0x80]   # ０〜９ ー ハ イ ス コ ア
out = ['; tools/gen_rank_font.py で作る。VRAM タイル $20〜$2f（0〜9・ー・ハ・イ・ス・コ・ア）']
for c in chars:
    g = rom[FONT + (c - 0x80) * 8: FONT + (c - 0x80) * 8 + 8]
    out.append('\tdb ' + ', '.join('$%02x, $%02x' % (b, b) for b in g))
open(os.path.join(ROOT, 'beach', 'rank_font.inc'), 'w').write('\n'.join(out) + '\n')
print(len(chars), 'tiles')
