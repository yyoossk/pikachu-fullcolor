import sys,os; sys.path.insert(0,'.')
os.environ['GBWATCHLOG']='/tmp/claude-0/hudw.log'
from lib import *
k=sys.argv[1]
g,S=boot(k)
set_party(g,S,[mon(const('ABRA'),11,27,27,[const('TELEPORT','constants/move_constants.asm')],[20])])
g.cmd('watch 9c41 1')
wild_battle(g,S,const('DROWZEE'),12)
g.wait(30); g.cmd('wflush'); g.sync(); g.close()
