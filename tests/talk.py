import sys; sys.path.insert(0,'.')
from lib import *
k=sys.argv[1]
r,s=rom(k); S,BK=loadsym(s)
g=GR(r,state='/tmp/claude-0/fe_end_'+k+'.st')
def pos(): return g.peek(S['wCurMap'])[0], g.peek(S['wXCoord'])[0], g.peek(S['wYCoord'])[0]
for i in range(8): g.press('B',4,20)
g.wait(60)
for ch in 'RRRRUR':
    p=pos(); g.down(ch)
    for i in range(30):
        g.wait(2)
        if pos()!=p: break
    g.up(ch); g.wait(20)
print(pos())
g.press('A',4,90); g.shot('/tmp/claude-0/talk_'+k+'.png')
