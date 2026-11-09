import sys; sys.path.insert(0,'.')
from lib import *
k=sys.argv[1]; st=sys.argv[2]; dexno=int(sys.argv[3]) if len(sys.argv)>3 else 1
r,s=rom(k); S,BK=loadsym(s)
g=GR(r,state=st)
ev=const('EVENT_GOT_POKEDEX','constants/event_constants.asm')
a=S['wEventFlags']+ev//8; g.poke(a, g.peek(a)[0]|(1<<(ev%8)))
for base in (S['wPokedexOwned'],S['wPokedexSeen']):
    g.pokes(base,[0xff]*19)
g.press('START',4,40)
g.press('A',4,90)   # ずかん
for i in range(dexno-1): g.press('D',4,12)
g.wait(30)
g.press('A',4,40)   # menu
g.press('A',4,240)  # じょうほう
g.shot(f'/tmp/claude-0/dex_{k}_1.png')
g.press('A',4,60)
g.shot(f'/tmp/claude-0/dex_{k}_2.png')
t=g.peek(S['wTileMap'],360)
for r_ in range(18): print(r_, ' '.join(f'{x:02x}' for x in t[r_*20:r_*20+20]))
g.save_state(f'/tmp/claude-0/dex_{k}.st')
