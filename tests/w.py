import sys,os; sys.path.insert(0,'.')
os.environ['GBWATCHLOG']='/tmp/claude-0/wy.log'
from lib import *
r,s=rom('v'); S,BK=loadsym(s)
g=GR(r,state='/tmp/claude-0/pallet_v.st')
g.cmd('watch ffb0 1')
g.poke(S['wDestinationMap'],6)
f=g.peek(S['wStatusFlags6'])[0]; g.poke(S['wStatusFlags6'], f|0x0c)
g.wait(600); g.cmd('wflush'); g.sync(); g.close()
