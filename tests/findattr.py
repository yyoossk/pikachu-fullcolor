import sys; sys.path.insert(0,'.')
from lib import *
k=sys.argv[1]
r,s=rom(k); S,BK=loadsym(s)
g=GR(r,state=f'/tmp/claude-0/battle_{k}.st')
pat=bytes([0,9,1,1,1,1,1,1,1,1,1,3])
m=bytes(g.peek(0xc000,0x1000))
i=m.find(pat); print('c000', hex(0xc000+i) if i>=0 else None)
for b in range(1,8):
    m=bytes(g.wpeek(b,0xd000,0x1000)); i=m.find(pat)
    if i>=0: print('wram bank',b,hex(0xd000+i))
m=bytes(g.peek(0xd000,0x1000)); i=m.find(pat); print('d000 cur', hex(0xd000+i) if i>=0 else None, 'svbk', g.peek(0xff70)[0])
