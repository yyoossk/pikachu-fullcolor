import sys; sys.path.insert(0,'.')
from lib import *
k=sys.argv[1]
if len(sys.argv)>2:
    r,s=rom(k); S,BK=loadsym(s); g=GR(r,state=sys.argv[2])
    for i in range(6): g.press('B',4,30)
    g.down('D'); g.wait(20); g.up('D'); g.wait(30)
    for i in range(4): g.press('B',4,30)
else: g,S=boot(k)
set_party(g,S,[mon(const('ABRA'),11,27,27,[const('TELEPORT','constants/move_constants.asm')],[20])])
wild_battle(g,S,const('DROWZEE'),12)
g.wait(30); g.shot(f'/tmp/claude-0/hud_{k}.png')
t=g.peek(S['wTileMap'],20*12)
for r in range(12): print(r, ' '.join(f'{x:02x}' for x in t[r*20:r*20+20]))
g.save_state(f'/tmp/claude-0/battle_{k}.st')
