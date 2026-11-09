import sys; sys.path.insert(0,'.')
from lib import *
k=sys.argv[1]
r,s=rom(k); S,BK=loadsym(s)
g=GR(r,state=f'/tmp/claude-0/verm_{k}.st')
def pos(): return g.peek(S['wXCoord'])[0], g.peek(S['wYCoord'])[0]
g.down('B'); g.down('R')
for i in range(int(sys.argv[2]) if len(sys.argv)>2 else 12):
    g.wait(6); g.shot(f'/tmp/claude-0/run_{i:02d}.png')
    print(i, pos(), 'walkbike', g.peek(S['wWalkBikeSurfState'])[0], 'pika', [hex(x) for x in g.peek(0xc1f0,3)], hex(g.peek(S['wd471'])[0]))
g.up('R'); g.wait(30); g.up('B'); g.wait(30); g.shot('/tmp/claude-0/run_end.png')
print(pos(), [hex(x) for x in g.peek(0xc1f0,3)])
