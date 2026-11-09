import sys; sys.path.insert(0,'.')
from lib import *
r,s=rom('v'); S,BK=loadsym(s)
g=GR(r,state='/tmp/claude-0/pallet_v.st')
def pos(): return g.peek(S['wCurMap'])[0], g.peek(S['wXCoord'])[0], g.peek(S['wYCoord'])[0], g.peek(S['wStatusFlags6'])[0], g.pc()
print(pos()); g.wait(30); print(pos())
g.down('R'); g.wait(18); g.up('R'); g.wait(30); print(pos())
