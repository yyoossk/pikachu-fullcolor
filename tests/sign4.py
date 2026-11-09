import sys; sys.path.insert(0,'.')
from lib import *
k=sys.argv[1]; st=sys.argv[2]
r,s=rom(k); S,BK=loadsym(s)
g=GR(r,state=st)
for i in range(6): g.press('B',4,30)
g.poke(S['wDestinationMap'],6)
f=g.peek(S['wStatusFlags6'])[0]; g.poke(S['wStatusFlags6'], f|0x0c)
g.down('R'); g.wait(18); g.up('R')
for i in range(900):
    g.wait(1)
    if g.peek(0xffb0)[0]==0x70 and g.peek(S['wCurMap'])[0]==6: break
g.wait(300)
def pos(): return g.peek(S['wCurMap'])[0], g.peek(S['wXCoord'])[0], g.peek(S['wYCoord'])[0]
g.down('R'); 
for i in range(200):
    g.wait(2)
    if pos()[0]!=6: break
print(pos())
n=0
for i in range(60):
    g.wait(3)
    if i%5==0: g.shot(f'/tmp/claude-0/s4_{n}.png'); n+=1
g.up('R'); print(pos(), hex(g.peek(0xff4a)[0]))
