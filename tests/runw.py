import sys,os; sys.path.insert(0,'.')
os.environ['GBWATCHLOG']='/tmp/claude-0/runw.log'
from lib import *
k=sys.argv[1]
r,s=rom(k); S,BK=loadsym(s)
g=GR(r,state=f'/tmp/claude-0/verm_{k}.st')
g.cmd('watch c1f2 1')
g.down('B'); g.down('R'); g.wait(40); g.cmd('wflush'); g.sync(); g.close()
