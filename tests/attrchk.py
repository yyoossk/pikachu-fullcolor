import sys; sys.path.insert(0,'.')
from lib import *
k=sys.argv[1]
r,s=rom(k); S,BK=loadsym(s)
for st in sys.argv[2:]:
    g=GR(r,state=st); g.wait(2)
    a=g.vpeek(1,0x9800,0x400); t=g.vpeek(0,0x9800,0x400)
    print(st.split('/')[-1], 'pal7 cells', sum(1 for x in a if x&7==7), 'pals', sorted(set(x&7 for x in a)))
    print(g.pals()[:140])
    g.close()
