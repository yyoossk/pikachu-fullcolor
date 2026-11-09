import sys, os; sys.path.insert(0,'.')
from lib import *
k=sys.argv[1]; dest=int(sys.argv[2]); tag=sys.argv[3]; st=sys.argv[4]
r,s=rom(k); S,BK=loadsym(s)
if st=='boot': g,S=boot(k)
else: g=GR(r,state=st)
for i in range(6): g.press('B',4,30)
if st=='boot':
    g.down('D'); g.wait(20); g.up('D'); g.wait(30)
    for i in range(4): g.press('B',4,30)
    g.save_state(f'/tmp/claude-0/room2_{k}.st')
g.poke(S['wDestinationMap'],dest)
f=g.peek(S['wStatusFlags6'])[0]; g.poke(S['wStatusFlags6'], f|0x0c)
g.down('R'); g.wait(18); g.up('R')
n=0; seen=False
for i in range(900):
    g.wait(1)
    wy=g.peek(0xff4a)[0]; hwy=g.peek(0xffb0)[0]
    if wy<0x90 and g.peek(0xff40)[0]&0x20 and g.peek(S['wCurMap'])[0]==dest: seen=True
    if seen and i%3==0 and n<60:
        g.shot(f'/tmp/claude-0/{tag}_{n:02d}.png'); print(n, i, hex(wy), hex(hwy), g.peek(0xd6a4)[0]); n+=1
    if seen and wy>=0x90 and n>5: break
g.wait(30); g.shot(f'/tmp/claude-0/{tag}_end.png'); print('end pal', g.pals()[115:131])
g.save_state(f'/tmp/claude-0/{tag}.st')
for j in range(6):
    g.wait(30); g.shot(f'/tmp/claude-0/{tag}_post{j}.png')
print('post wy', hex(g.peek(0xffb0)[0]), g.pc())
