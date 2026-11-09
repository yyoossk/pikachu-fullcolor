import sys; sys.path.insert(0,'.')
from lib import *
k=sys.argv[1]
r,s=rom(k); S,BK=loadsym(s)
g=GR(r,state=f'/tmp/claude-0/battle_{k}.st')
print('scy scx', g.peek(0xff42,2))
for base in (0x9800,0x9c00):
  print(hex(base))
  for row in range(0,5):
    print(row,' '.join(f'{x:02x}' for x in g.vpeek(0,base+row*32,12)),'|',' '.join(f'{x:02x}' for x in g.vpeek(1,base+row*32,12)))
def tile(bank,t):
    a=0x9000+t*16 if t<0x80 else 0x8000+t*16
    d=g.vpeek(bank,a,16)
    return [''.join('.123'[((d[2*y]>>(7-x))&1)|(((d[2*y+1]>>(7-x))&1)<<1)] for x in range(8)) for y in range(8)]
ts=[(1,0x5e),(0,0x5e),(1,0x74),(1,0x73),(1,0x76),(1,0x78)]
rows=[tile(b,t) for b,t in ts]
print('   '.join(f'b{b}:{t:02x}  ' for b,t in ts))
for y in range(8): print('   '.join(r[y] for r in rows))
