import sys; sys.path.insert(0,'.')
from lib import *
k=sys.argv[1]
g,S=boot(k)
def pos(): return g.peek(S['wCurMap'])[0], g.peek(S['wXCoord'])[0], g.peek(S['wYCoord'])[0]
def step(d,n=1):
    for _ in range(n): g.down(d); g.wait(16); g.up(d); g.wait(8)
print(pos())
g.save_state('/tmp/claude-0/room_'+k+'.st')
g.close()
