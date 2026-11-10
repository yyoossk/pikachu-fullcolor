import sys; sys.path.insert(0,'/home/claude/pk/fc/tests')
from lib import *
k=sys.argv[1]; slot=int(sys.argv[2]); r,s=rom(k); S,BK=loadsym(s)
g=GR(r,state=f'/tmp/claude-0/fol_{k}.st'); g.wait(2)
for i in range(6): g.pokes(S['wPartyMon1']+44*i+27,[0x10+i,0x20+i])
base=S['wPartyMon1']+44*slot
otid=g.peek(base+12,2); dv=g.peek(base+27,2)
g.poke(0xd3f5,1); g.pokes(0xd3f6,[otid[0],otid[1],dv[0]]); g.poke(0xd3f3,dv[1])
g.wait(30)
print('d471',hex(g.peek(S['wd471'])[0]), 'b7', g.wpeek(7,0xd010,3))
g.shot('/tmp/claude-0/sw0.png')
for d in 'LLUURRDD':
    g.down(d); g.wait(17); g.up(d); g.wait(6)
g.wait(20); g.shot('/tmp/claude-0/sw1.png')
o=g.oam(); print([(i,o[i*4],o[i*4+1],hex(o[i*4+2]),hex(o[i*4+3])) for i in range(40) if 0<o[i*4]<160])
print(g.pals()[-80:])
g.save_state(f'/tmp/claude-0/sw_{k}.st')
