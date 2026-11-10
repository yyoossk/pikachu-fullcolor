#!/usr/bin/env python3
"""かんたんな逆アセンブラ（SM83）。
  python3 tools/dis.py base/v.gbc 3a:7600 [行数] [syms/v.sym]
"""
import sys, signal
signal.signal(signal.SIGPIPE, signal.SIG_DFL)
R = ['b', 'c', 'd', 'e', 'h', 'l', '[hl]', 'a']
RP = ['bc', 'de', 'hl', 'sp']; RP2 = ['bc', 'de', 'hl', 'af']
CC = ['nz', 'z', 'nc', 'c']
ALU = ['add a,', 'adc a,', 'sub', 'sbc a,', 'and', 'xor', 'or', 'cp']
CB = ['rlc', 'rrc', 'rl', 'rr', 'sla', 'sra', 'swap', 'srl']
def one(m, pc):
    """m(addr) -> byte. returns (text, length)"""
    o = m(pc); n8 = lambda: m(pc + 1); n16 = lambda: m(pc + 1) | m(pc + 2) << 8
    x, y, z = o >> 6, o >> 3 & 7, o & 7
    if o == 0xcb:
        b = m(pc + 1); bx, by, bz = b >> 6, b >> 3 & 7, b & 7
        if bx == 0: return f'{CB[by]} {R[bz]}', 2
        return f"{['', 'bit', 'res', 'set'][bx]} {by}, {R[bz]}", 2
    if x == 1:
        return ('halt', 1) if o == 0x76 else (f'ld {R[y]}, {R[z]}', 1)
    if x == 2: return f'{ALU[y]} {R[z]}', 1
    T = {0x00: ('nop', 1), 0x08: (f'ld [${n16():04x}], sp', 3), 0x10: ('stop', 2), 0x18: (f'jr ${(pc + 2 + ((n8() ^ 0x80) - 0x80)) & 0xffff:04x}', 2),
         0x07: ('rlca', 1), 0x0f: ('rrca', 1), 0x17: ('rla', 1), 0x1f: ('rra', 1), 0x27: ('daa', 1), 0x2f: ('cpl', 1), 0x37: ('scf', 1), 0x3f: ('ccf', 1),
         0x02: ('ld [bc], a', 1), 0x12: ('ld [de], a', 1), 0x22: ('ld [hli], a', 1), 0x32: ('ld [hld], a', 1),
         0x0a: ('ld a, [bc]', 1), 0x1a: ('ld a, [de]', 1), 0x2a: ('ld a, [hli]', 1), 0x3a: ('ld a, [hld]', 1),
         0xc9: ('ret', 1), 0xd9: ('reti', 1), 0xe9: ('jp hl', 1), 0xf9: ('ld sp, hl', 1), 0xc3: (f'jp ${n16():04x}', 3), 0xcd: (f'call ${n16():04x}', 3),
         0xe0: (f'ldh [${0xff00 | n8():04x}], a', 2), 0xf0: (f'ldh a, [${0xff00 | n8():04x}]', 2), 0xe2: ('ld [c], a', 1), 0xf2: ('ld a, [c]', 1),
         0xea: (f'ld [${n16():04x}], a', 3), 0xfa: (f'ld a, [${n16():04x}]', 3), 0xe8: (f'add sp, {n8()}', 2), 0xf8: (f'ld hl, sp+{n8()}', 2),
         0xf3: ('di', 1), 0xfb: ('ei', 1)}
    if o in T: return T[o]
    if x == 0:
        if z == 0 and y >= 4: return f'jr {CC[y - 4]}, ${(pc + 2 + ((n8() ^ 0x80) - 0x80)) & 0xffff:04x}', 2
        if z == 1: return (f'ld {RP[y >> 1]}, ${n16():04x}', 3) if y % 2 == 0 else (f'add hl, {RP[y >> 1]}', 1)
        if z == 3: return f"{'inc' if y % 2 == 0 else 'dec'} {RP[y >> 1]}", 1
        if z == 4: return f'inc {R[y]}', 1
        if z == 5: return f'dec {R[y]}', 1
        if z == 6: return f'ld {R[y]}, ${n8():02x}', 2
    if x == 3:
        if z == 0 and y < 4: return f'ret {CC[y]}', 1
        if z == 2 and y < 4: return f'jp {CC[y]}, ${n16():04x}', 3
        if z == 4 and y < 4: return f'call {CC[y]}, ${n16():04x}', 3
        if z == 1 and y % 2 == 0: return f'pop {RP2[y >> 1]}', 1
        if z == 5 and y % 2 == 0: return f'push {RP2[y >> 1]}', 1
        if z == 6: return f'{ALU[y]} ${n8():02x}', 2
        if z == 7: return f'rst ${y * 8:02x}', 1
    return f'db ${o:02x}', 1
def main():
    rom = open(sys.argv[1], 'rb').read()
    b, a = sys.argv[2].split(':'); b = int(b, 16); a = int(a, 16)
    n = int(sys.argv[3]) if len(sys.argv) > 3 else 40
    names = {}
    if len(sys.argv) > 4:
        for l in open(sys.argv[4]):
            p = l.split()
            if len(p) == 2 and ':' in p[0]:
                bb, aa = p[0].split(':'); names.setdefault((int(bb, 16), int(aa, 16)), p[1])
    def m(x):
        x &= 0xffff
        return rom[x] if x < 0x4000 else rom[b * 0x4000 + x - 0x4000]
    for _ in range(n):
        t, l = one(m, a)
        for key in ((b if a >= 0x4000 else 0, a),):
            if key in names: print(f'{names[key]}:')
        import re
        def lab(mm):
            v = int(mm.group(1), 16); k2 = (0 if v < 0x4000 else b, v)
            return mm.group(0) + (f' ; {names[k2]}' if k2 in names else '')
        t2 = re.sub(r'\$([0-9a-f]{4})$', lab, t)
        print(f'{b:02x}:{a:04x}  {" ".join(f"{m(a + i):02x}" for i in range(l)):<9} {t2}')
        a += l
if __name__ == '__main__': main()
