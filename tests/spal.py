import sys; sys.path.insert(0,'.')
from lib import *
r,s=rom('v'); S,BK=loadsym(s)
g=GR(r,state='/tmp/claude-0/room2_v.st')
for i in range(6): g.press('B',4,30)
g.poke(S['wDestinationMap'],6)
f=g.peek(S['wStatusFlags6'])[0]; g.poke(S['wStatusFlags6'], f|0x0c)
g.down('R'); g.wait(18); g.up('R')
for i in range(900):
    g.wait(1)
    if g.peek(0xffb0)[0]==0x70 and g.peek(S['wCurMap'])[0]==6: break
for j in range(6):
    print(j, g.pals()[115:131], bytes(g.wpeek(2,0xd038,8)).hex(), bytes(g.wpeek(2,0xd078,8)).hex(), bytes(g.wpeek(7,0xd000,8)).hex(), bytes(g.wpeek(2,0xd438,8)).hex(), hex(g.wpeek(2,0xd094,1)[0]))
    g.wait(3)
