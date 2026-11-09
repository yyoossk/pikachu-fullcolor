import sys; sys.path.insert(0,'.')
from lib import *
k=sys.argv[1]
r,s=rom(k); S,BK=loadsym(s)
g=GR(r,state=sys.argv[2])
g.wait(int(sys.argv[3]) if len(sys.argv)>3 else 1)
p=g.pals(); print(p)
for row in range(14,18): print(row,' '.join(f'{x:02x}' for x in g.vpeek(0,0x9c00+(row-14)*32,20)),'|',' '.join(f'{x:02x}' for x in g.vpeek(1,0x9c00+(row-14)*32,20)))
print('lcdc',hex(g.peek(0xff40)[0]),'wy',hex(g.peek(0xff4a)[0]))
