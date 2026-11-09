import sys; sys.path.insert(0,'.')
from lib import *
k=sys.argv[1]
r,s=rom(k); S,BK=loadsym(s)
g=GR(r,state=f'/tmp/claude-0/verm_{k}.st')
def pos(): return g.peek(S['wXCoord'])[0], g.peek(S['wYCoord'])[0]
g.down('B'); g.down('R')
out=[]
for i in range(int(sys.argv[2])):
    g.wait(2)
    py,px=g.peek(0xc2f4,2); st=g.peek(0xc1f1)[0]; buf=g.peek(0xd3b6)[0]
    out.append(f'{pos()[0]}/{px-4}:{st}:{buf}')
print(' '.join(out))
