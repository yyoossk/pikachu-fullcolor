import sys; sys.path.insert(0,'.')
from lib import *
k=sys.argv[1]
r,s=rom(k); S,BK=loadsym(s)
g=GR(r,state='/tmp/claude-0/room_'+k+'.st')
def pos(): return g.peek(S['wCurMap'])[0], g.peek(S['wXCoord'])[0], g.peek(S['wYCoord'])[0]
def step(d,n=1):
    for _ in range(n): g.down(d); g.wait(18); g.up(d); g.wait(6)
step('R',4); step('U',5); step('R',3); g.wait(90); print(pos())
step('D',1); print(pos()); step('L',4); print(pos()); step('D',6); print(pos()); step('D',1); g.wait(30); print(pos())
for i in range(8):
    g.wait(10); g.shot(f'/tmp/claude-0/pal_{i}.png')
g.save_state('/tmp/claude-0/pallet_'+k+'.st')
print(pos())
