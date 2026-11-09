import sys; sys.path.insert(0,'.')
from lib import *
k=sys.argv[1]
r,s=rom(k); S,BK=loadsym(s)
g=GR(r,state=f'/tmp/claude-0/cel2_{k}.st')
g.wait(400); g.shot(f'/tmp/claude-0/after_{k}.png'); print(hex(g.peek(0xffb0)[0]), g.peek(0xd6a4)[0])
