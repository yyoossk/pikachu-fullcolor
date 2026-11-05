"""syms/<k>.sym から、そのラベルを「大きさ0のSECTION」として決まった場所に置く asm を作る。
これをアセンブルしてパッチといっしょにリンクすると、パッチのソースから元のラベル名と BANK() が使える。
  使い方: python3 tools/symobj.py syms/v.sym build/v/syms.asm"""
import sys, re
src, out = sys.argv[1:3]
lines = []
seen = set()
for l in open(src):
    m = re.match(r'([0-9a-f]+):([0-9a-f]+) (\S+)', l)
    if not m: continue
    b, a, n = int(m.group(1), 16), int(m.group(2), 16), m.group(3)
    if n in seen: continue
    seen.add(n)
    if a < 0x4000: t = f'ROM0[${a:04x}]'
    elif a < 0x8000: t = f'ROMX[${a:04x}], BANK[${b:02x}]'
    elif a < 0xa000: t = f'VRAM[${a:04x}], BANK[{b if b < 2 else 0}]'
    elif a < 0xc000: t = f'SRAM[${a:04x}], BANK[{b}]'
    elif a < 0xd000: t = f'WRAM0[${a:04x}]'
    elif a < 0xe000: t = f'WRAMX[${a:04x}], BANK[{max(b,1)}]'
    elif a >= 0xff80: t = f'HRAM[${a:04x}]'
    else: continue
    lines.append(f'SECTION "s{len(lines)}", {t}\n{n}::\n')
open(out, 'w').write(''.join(lines))
print(out, len(lines))
