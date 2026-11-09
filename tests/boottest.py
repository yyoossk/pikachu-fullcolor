import sys; sys.path.insert(0,'.')
from lib import *
k=sys.argv[1]
g,S=boot(k)
print('map', g.peek(S['wCurMap'])[0], hex(g.peek(0xff40)[0]), g.pc())
