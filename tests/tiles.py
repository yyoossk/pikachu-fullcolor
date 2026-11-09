import sys; sys.path.insert(0,'.')
from lib import *
k=sys.argv[1]
r,s=rom(k); S,BK=loadsym(s)
g=GR(r,state=f'/tmp/claude-0/battle_{k}.st')
lcdc=g.peek(0xff40)[0]; print('lcdc',hex(lcdc))
for t in [int(x,16) for x in sys.argv[2:]]:
    a = 0x8000+t*16 if (lcdc&0x10) or t>=0x80 else 0x9000+t*16
    d=g.vpeek(0,a,16); print(hex(t))
    for y in range(8):
        lo,hi=d[2*y],d[2*y+1]
        print(''.join('.123'[((lo>>(7-x))&1)|(((hi>>(7-x))&1)<<1)] for x in range(8)))
