import sys; sys.path.insert(0,'.')
from lib import *
k=sys.argv[1]
r,s=rom(k); S,BK=loadsym(s)
g=GR(r,state='/tmp/claude-0/pallet_'+k+'.st')
def pos(): return g.peek(S['wCurMap'])[0], g.peek(S['wXCoord'])[0], g.peek(S['wYCoord'])[0]
def step(d,n=1):
    for _ in range(n): g.down(d); g.wait(18); g.up(d); g.wait(6)
step('R',5); print(pos())
for i in range(8):
    step('U',1); print(pos())
    if pos()[0]!=0: break
for i in range(10):
    g.wait(8); g.shot(f'/tmp/claude-0/r1_{i}.png')
