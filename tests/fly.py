import sys, os; sys.path.insert(0,'.')
from lib import *
k=sys.argv[1]; dest=int(sys.argv[2]); tag=sys.argv[3]
r,s=rom(k); S,BK=loadsym(s)
g=GR(r,state=(sys.argv[4] if len(sys.argv)>4 else '/tmp/claude-0/pallet_'+k+'.st'))
def pos(): return g.peek(S['wCurMap'])[0], g.peek(S['wXCoord'])[0], g.peek(S['wYCoord'])[0]
for i in range(6): g.press('B',4,30)
g.poke(S['wDestinationMap'],dest)
f=g.peek(S['wStatusFlags6'])[0]; g.poke(S['wStatusFlags6'], f|0x0c)
g.down('R'); g.wait(18); g.up('R')
for i in range(40):
    g.wait(10); g.shot(f'/tmp/claude-0/{tag}_{i}.png')
    if g.peek(0xffb0)[0]==0x70 and not os.path.exists(f'/tmp/claude-0/sign_{tag}.st'): g.save_state(f'/tmp/claude-0/sign_{tag}.st')
print(pos())
g.save_state(f'/tmp/claude-0/{tag}_{k}.st')
