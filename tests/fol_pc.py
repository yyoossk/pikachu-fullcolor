import sys; sys.path.insert(0,'/home/claude/pk/fc/tests')
from fol_lib import *
exec(open('fol_crystal2.py').read().split('# 2.')[0].split("k=sys.argv[1]")[1])
k=sys.argv[1]; H=17 if k=='v' else 9
g,S=start(k,f'/tmp/claude-0/vir_{k}.st',2)
walk(g,S,'U',1)
for i in range(80):
    g.wait(1)
    if pos(g,S)[2]==41: break
g.wait(60)
print('in', pos(g,S))
# (13,4) へ
for i in range(30):
    p=pos(g,S)
    if p[1]>4: walk(g,S,'U',1)
    elif p[0]<13: walk(g,S,'R',1)
    elif p[1]<4: walk(g,S,'D',1)
    else: break
    g.wait(20)
print('at', pos(g,S))
g.press('U',2,20)
g.save_state(f'/tmp/claude-0/atpc_{k}.st')
fs=[]
for b in ['A']*4:
    g.press(b,4,60); fn=f'/tmp/claude-0/pd_{len(fs)}.png'; g.shot(fn); fs.append(fn)
strip(fs,'/tmp/claude-0/pd.png',scale=1,cols=4)
