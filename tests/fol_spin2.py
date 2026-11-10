import sys; sys.path.insert(0,'/home/claude/pk/fc/tests')
from fol_lib import *
k=sys.argv[1]; slot=None if sys.argv[2]=='p' else int(sys.argv[2])
g,S=start(k,f'/tmp/claude-0/vir_{k}.st',slot)
g.pokes(S['wWarpEntries'],[25,23,0,0x2d])
g.down('U')
for i in range(80):
    g.wait(1)
    if pos(g,S)[2]==0x2d: break
g.up('U'); g.wait(80)
for d in 'ULLL': step(g,d,1,hold=17 if k=='v' else 9)
g.down('L'); fs=[]
for i in range(150):
    g.wait(1)
    if i%6==0:
        fn=f'/tmp/claude-0/s2_{i:03d}.png'; g.shot(fn); fs.append(fn)
g.up('L'); g.wait(120)
for d in 'DR': step(g,d,1,hold=17 if k=='v' else 9)
g.wait(20); fn='/tmp/claude-0/s2_end.png'; g.shot(fn); fs.append(fn)
print(pos(g,S), fpos(g,S), g.pc())
strip(fs,f'/tmp/claude-0/s2_{k}_{sys.argv[2]}.png',crop=(16,8,144,120),scale=1,cols=9)
