import sys; sys.path.insert(0,'.')
from lib import *
k=sys.argv[1]; tag=sys.argv[2] if len(sys.argv)>2 else 'fan'
r,s=rom(k); S,BK=loadsym(s)
g=GR(r,state='/tmp/claude-0/pallet_'+k+'.st')
def pos(): return g.peek(S['wCurMap'])[0], g.peek(S['wXCoord'])[0], g.peek(S['wYCoord'])[0]
def step(d,n=1):
    for _ in range(n): g.down(d); g.wait(18); g.up(d); g.wait(6)
set_party(g,S,[mon(const('PIKACHU'),20,50,50,[const('THUNDERSHOCK','constants/move_constants.asm')],[30])])
g.poke(S['wDestinationMap'],5)
f=g.peek(S['wStatusFlags6'])[0]; g.poke(S['wStatusFlags6'], f|0x0c)
g.wait(500); print(pos(), hex(g.peek(S['wd471'])[0]))
g.shot(f'/tmp/claude-0/{tag}_verm.png')
g.save_state(f'/tmp/claude-0/verm_{k}.st')
