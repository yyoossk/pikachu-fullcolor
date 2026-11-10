import sys; sys.path.insert(0,'/home/claude/pk/fc/tests')
from fol_lib import *
k=sys.argv[1]; slot=None if sys.argv[2]=='p' else int(sys.argv[2])
g,S=start(k,f'/tmp/claude-0/vir_{k}.st',slot)
g.pokes(S['wWarpEntries'],[25,23,0,0x87])
g.down('U')
for i in range(80):
    g.wait(1)
    if pos(g,S)[2]==0x87: break
g.up('U'); g.wait(90)
res=[]; fs=[]; maxo=0; misses=0; frames=0; folmiss=0
for t,d in enumerate('UUUULLLLLLUUUUDDDDRRRRRRRRRRUUUULLLL'):
    p0=pos(g,S); n=0
    g.down(d)
    while pos(g,S)==p0 and n<40:
        g.wait(1); n+=1; frames+=1
        o=g.oam(); used=sum(1 for i in range(40) if 0<o[i*4]<160); maxo=max(maxo,used)
        fol=[i for i in range(40) if 0<o[i*4]<160 and (o[i*4+2]&0x7f)-0x0c in range(12) and not o[i*4+3]&8]
        und=[i for i in range(40) if 0<o[i*4]<160 and o[i*4+3]&8]
        if slot is not None and fol and not und: misses+=1
        if not fol: folmiss+=1
    g.up(d); res.append(n); g.wait(4)
    if t%5==4:
        fn=f'/tmp/claude-0/gc_{t}.png'; g.shot(fn); fs.append(fn)
print(k, sys.argv[2], 'sum', sum(res), 'max OAM', maxo, 'underlay missing', misses, 'follower missing', folmiss, '/', frames, pos(g,S), g.pc())
strip(fs,f'/tmp/claude-0/gc_{k}_{sys.argv[2]}.png',scale=1,cols=4)
