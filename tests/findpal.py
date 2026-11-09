import sys; sys.path.insert(0,'.')
from lib import *
k=sys.argv[1]
r,s=rom(k); S,BK=loadsym(s)
g=GR(r,state=sys.argv[2]); g.wait(2)
pat=bytes.fromhex(sys.argv[3])
m=bytes(g.peek(0xc000,0x1000))
i=m.find(pat)
while i>=0: print('c000+', hex(0xc000+i)); i=m.find(pat,i+1)
for b in range(1,8):
    m=bytes(g.wpeek(b,0xd000,0x1000)); i=m.find(pat)
    while i>=0: print('bank',b,hex(0xd000+i)); i=m.find(pat,i+1)
print('svbk',g.peek(0xff70)[0]&7)
