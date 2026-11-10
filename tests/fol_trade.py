import sys; sys.path.insert(0,'/home/claude/pk/fc/tests')
from fol_lib import *
exec(open('/home/claude/pk/fc/tests/fol_crystal2.py').read().split('# 2.')[0].split("k=sys.argv[1]")[1])
k=sys.argv[1]; slot=int(sys.argv[2])
g,S=start(k,f'/tmp/claude-0/vir_{k}.st')
cl=const('CLEFAIRY'); g.poke(S['wPartySpecies']+2,cl); g.poke(S['wPartyMon1']+44*2,cl)
choose(g,S,slot)
g.pokes(S['wWarpEntries'],[25,23,0,0x30])
g.down('U')
for i in range(120):
    g.wait(1)
    if pos(g,S)[2]==0x30: break
g.up('U'); g.wait(90)
for i in range(20):
    p=pos(g,S)
    if p[1]>5: walk(g,S,'U',1)
    elif p[0]<5 and p[1]>2: walk(g,S,'R',1)
    elif p[1]>2: walk(g,S,'U',1)
    elif p[0]>4: walk(g,S,'L',1)
    else: break
    g.wait(10)
g.press('U',2,20); print('at', pos(g,S), 'follower', g.wpeek(7,0xd010,3))
fs=[]
def p(b,w=80):
    g.press(b,4,w); fn=f'/tmp/claude-0/tr_{len(fs)}.png'; g.shot(fn); fs.append(fn)
for b in 'AAAA': p(b)
p('D',30); p('D',30); p('A',80)
for i in range(120):
    g.press('A',4,40)
    if g.peek(S['wPartySpecies']+2)[0]!=cl and i>10 and g.peek(0xff40)[0]&0x80 and g.peek(S['wCurMap'])[0]==0x30 and i%10==0:
        pass
for i in range(10): g.press('B',4,40)
fn='/tmp/claude-0/tr_mid.png'; g.shot(fn); fs.append(fn)
print('party', g.peek(S['wPartySpecies'],4), 'mode', g.peek(0xd3f5)[0], 'map', pos(g,S))
for i in range(6): g.press('B',4,40)
g.wait(60); walk(g,S,'L',1); g.wait(30)
print('after', g.wpeek(7,0xd010,3), g.pals().split('OB:')[1][96:112], fpos(g,S), offs(g))
fn='/tmp/claude-0/tr_end.png'; g.shot(fn); fs.append(fn)
strip(fs,'/tmp/claude-0/tr.png',scale=1,cols=9)
