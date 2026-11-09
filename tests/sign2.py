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
g.wait(20); g.shot('/tmp/claude-0/s2_a.png')
g.press('START',4,40); g.shot('/tmp/claude-0/s2_b.png'); print('menu', g.pals()[115:131], hex(g.peek(0xffb0)[0]))
g.press('B',4,60); g.shot('/tmp/claude-0/s2_c.png'); print('after', g.pals()[115:131], hex(g.peek(0xffb0)[0]), bytes(g.wpeek(7,0xd000,4)).hex())
g.wait(60); g.shot('/tmp/claude-0/s2_d.png'); print('later', g.pals()[115:131])
# walk a bit
g.down('L'); g.wait(60); g.up('L'); g.wait(20); g.shot('/tmp/claude-0/s2_e.png'); print('walk', g.pals()[115:131], hex(g.peek(0xffb0)[0]))
