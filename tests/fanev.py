import sys; sys.path.insert(0,'.')
from lib import *
k=sys.argv[1]; st=sys.argv[2]; tag=sys.argv[3]
r,s=rom(k); S,BK=loadsym(s)
g=GR(r,state=st)
def pos(): return g.peek(S['wCurMap'])[0], g.peek(S['wXCoord'])[0], g.peek(S['wYCoord'])[0]
g.down('U'); g.wait(30); g.up('U')
trail=[]
for i in range(60):
    g.wait(8)
    py,px=g.peek(0xc200+0xf0+4,2)
    t=(px-4,py-4)
    if not trail or trail[-1]!=t: trail.append(t)
    if i%3==0: g.shot(f'/tmp/claude-0/{tag}_{i:02d}.png')
print(pos(), 'pikachu', trail)
g.save_state('/tmp/claude-0/fe_end_'+k+'.st')
