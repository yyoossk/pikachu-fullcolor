import sys; sys.path.insert(0,'.')
from lib import *
k=sys.argv[1]; st=sys.argv[2]; out=sys.argv[3]; seq=sys.argv[4]
r,s=rom(k); S,BK=loadsym(s)
g=GR(r,state=st)
def pos(): return g.peek(S['wCurMap'])[0], g.peek(S['wXCoord'])[0], g.peek(S['wYCoord'])[0]
log=[]
for ch in seq:
    p=pos(); g.down(ch)
    for i in range(40):
        g.wait(2)
        if pos()!=p: break
    g.up(ch); g.wait(20); log.append(ch+str(pos()[1:]))
print(' '.join(log), pos())
g.shot(out+'.png'); g.save_state(out+'.st')
