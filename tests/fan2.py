import sys; sys.path.insert(0,'.')
from lib import *
k=sys.argv[1]; tag=sys.argv[2] if len(sys.argv)>2 else 'fan'
r,s=rom(k); S,BK=loadsym(s)
g=GR(r,state='/tmp/claude-0/verm_'+k+'.st')
def pos(): return g.peek(S['wCurMap'])[0], g.peek(S['wXCoord'])[0], g.peek(S['wYCoord'])[0]
def step(d,n=1):
    for _ in range(n): g.down(d); g.wait(18); g.up(d); g.wait(6)
for d,n in eval(sys.argv[3]):
    step(d,n); print(d,pos())
g.wait(30); print(pos())
for i in range(30):
    g.wait(10); g.shot(f'/tmp/claude-0/{tag}_{i:02d}.png')
    print(i, [ (g.peek(0xc104+16*j)[0], g.peek(0xc106+16*j)[0]) for j in range(1,9)][:0])
g.save_state(f'/tmp/claude-0/fanin_{k}.st')
