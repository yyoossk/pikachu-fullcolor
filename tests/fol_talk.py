import sys; sys.path.insert(0,'/home/claude/pk/fc/tests')
from lib import *
k=sys.argv[1]; st=sys.argv[2]; d=sys.argv[3]; r,s=rom(k); S,BK=loadsym(s)
g=GR(r,state=st); g.wait(2)
for dd in (sys.argv[4] if len(sys.argv)>4 else ''):
    g.down(dd); g.wait(17); g.up(dd); g.wait(8)
g.wait(20)
g.press(d,2,10)
g.press('A',4,1)
for i in range(12):
    g.wait(10); g.shot(f'/tmp/claude-0/tk{i:02d}.png')
for i in range(3):
    g.press('A',4,30); g.shot(f'/tmp/claude-0/tkz{i}.png')
g.wait(30); g.shot('/tmp/claude-0/tkend.png'); print(g.pc())
