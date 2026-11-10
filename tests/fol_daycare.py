import sys; sys.path.insert(0,'/home/claude/pk/fc/tests')
from fol_lib import *
exec(open('/home/claude/pk/fc/tests/fol_crystal2.py').read().split('# 2.')[0].split("k=sys.argv[1]")[1])
k=sys.argv[1]; slot=int(sys.argv[2]); pick=int(sys.argv[3])
g,S=start(k,f'/tmp/claude-0/vir_{k}.st',slot)
g.pokes(S['wWarpEntries'],[25,23,0,0x48])
g.down('U')
for i in range(120):
    g.wait(1)
    if pos(g,S)[2]==0x48: break
g.up('U'); g.wait(90)
for i in range(20):
    p=pos(g,S)
    if p[1]>5: walk(g,S,'U',1)
    elif p[0]>2: walk(g,S,'L',1)
    elif p[1]>4: walk(g,S,'U',1)
    else: break
    g.wait(10)
g.press('U',2,20); print('at', pos(g,S))
g.save_state(f'/tmp/claude-0/atdc_{k}.st')
fs=[]
def p(b,w=70):
    g.press(b,4,w); fn=f'/tmp/claude-0/dc_{len(fs)}.png'; g.shot(fn); fs.append(fn)
for b in 'AAAA': p(b)
for i in range(pick): p('D',30)
for b in 'AAAAAA': p(b,80)
print('party', g.peek(S['wPartySpecies'],4), 'mode', g.peek(0xd3f5)[0])
for i in range(4): g.press('B',4,40)
g.wait(60); walk(g,S,'R',1); g.wait(30)
print('after', g.wpeek(7,0xd010,3), g.pals().split('OB:')[1][96:112], fpos(g,S), offs(g))
fn='/tmp/claude-0/dc_end.png'; g.shot(fn); fs.append(fn)
strip(fs,'/tmp/claude-0/dc.png',scale=1,cols=8)
