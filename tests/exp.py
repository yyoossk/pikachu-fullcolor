import sys; sys.path.insert(0,'.')
from lib import *
import lib
r,s=rom('v'); S,BK=loadsym(s)
g=GR('/tmp/claude-0/exp.gbc')
g.wait(600)
for i in range(400):
    g.press('A',4,20)
    if i%10==9:
        y=g.peek(S['wYCoord'])[0]; g.down('D'); g.wait(20); g.up('D'); g.wait(30)
        if g.peek(S['wYCoord'])[0]!=y: g.down('U'); g.wait(20); g.up('U'); g.wait(30); break
set_party(g,S,[mon(const('ABRA'),11,27,27,[const('TELEPORT','constants/move_constants.asm')],[20])])
import sys as _s
if len(_s.argv)>1: g.poke(S['wTrainerNo'],1); wild_battle(g,S,int(_s.argv[1]),12)
else: wild_battle(g,S,const('DROWZEE'),12)
g.wait(30)
for row in range(5): print(row,' '.join(f'{x:02x}' for x in g.vpeek(1,0x9c00+row*32,12)))
