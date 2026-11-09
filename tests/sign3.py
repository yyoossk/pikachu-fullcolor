import sys; sys.path.insert(0,'.')
from lib import *
k=sys.argv[1]; st=sys.argv[2]
r,s=rom(k); S,BK=loadsym(s)
g=GR(r,state=st)
for i in range(6): g.press('B',4,30)
set_party(g,S,[mon(const('PIKACHU'),30,90,90,[const('THUNDERSHOCK','constants/move_constants.asm')],[30],stats=(90,90,200,90))])
g.poke(S['wDestinationMap'],6)
f=g.peek(S['wStatusFlags6'])[0]; g.poke(S['wStatusFlags6'], f|0x0c)
g.down('R'); g.wait(18); g.up('R')
for i in range(900):
    g.wait(1)
    if g.peek(0xffb0)[0]==0x70 and g.peek(S['wCurMap'])[0]==6: break
g.wait(10)
g.poke(S['wCurEnemyLevel'],2); g.poke(S['wCurOpponent'],const('RATTATA'))
g.down('L'); g.wait(20); g.up('L')
for i in range(300):
    g.wait(5)
    if g.peek(S['wIsInBattle'])[0]: break
g.wait(200); g.shot('/tmp/claude-0/s3_a.png'); print('battle', g.peek(S['wIsInBattle'])[0])
for i in range(40):
    g.press('A',4,30)
    if not g.peek(S['wIsInBattle'])[0]: break
g.wait(120); g.shot('/tmp/claude-0/s3_b.png'); print('after', g.peek(S['wIsInBattle'])[0], g.pals()[115:131], hex(g.peek(0xffb0)[0]), bytes(g.wpeek(7,0xd000,4)).hex())
g.down('L'); g.wait(40); g.up('L'); g.wait(20); g.shot('/tmp/claude-0/s3_c.png')
