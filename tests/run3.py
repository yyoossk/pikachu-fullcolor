import sys; sys.path.insert(0,'.')
from lib import *
k=sys.argv[1]
r,s=rom(k); S,BK=loadsym(s)
g=GR(r,state=f'/tmp/claude-0/verm_{k}.st')
def pos(): return g.peek(S['wXCoord'])[0], g.peek(S['wYCoord'])[0]
def pika():
    py,px=g.peek(0xc2f4,2); return px-4,py-4,g.peek(0xc1f2)[0]
g.down('B')
for d,fr in [('R',30),('D',24),('L',20),('U',12)]:
    g.down(d); 
    for i in range(fr//2):
        g.wait(2)
    g.up(d)
    print(d, pos(), pika())
g.shot(f'/tmp/claude-0/r3a_{k}.png')
g.up('B'); g.wait(60); print('stop', pos(), pika()); g.shot(f'/tmp/claude-0/r3b_{k}.png')
g.down('L'); g.wait(40); g.up('L'); g.wait(30); print('walk', pos(), pika()); g.shot(f'/tmp/claude-0/r3c_{k}.png')
