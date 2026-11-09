import sys, os; sys.path.insert(0,'.')
from lib import *
k=sys.argv[1]; st=sys.argv[2]
r,s=rom(k); S,BK=loadsym(s)
g=GR(r,state=st)
for i in range(6): g.press('B',4,30)
g.poke(S['wDestinationMap'],6)
f=g.peek(S['wStatusFlags6'])[0]; g.poke(S['wStatusFlags6'], f|0x0c)
g.down('R'); g.wait(18); g.up('R')
for i in range(60):
    g.wait(8)
    print(i, g.peek(S['wCurMap'])[0], 'hwy',hex(g.peek(0xffb0)[0]),'wy',hex(g.peek(0xff4a)[0]),'lcdc',hex(g.peek(0xff40)[0]),'timer',g.peek(0xd6a4)[0],'b7',bytes(g.wpeek(7,0xd000,8)).hex(), g.pc())
    if i==38: g.shot('/tmp/claude-0/sdbg.png')
