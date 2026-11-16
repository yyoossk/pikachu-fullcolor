import os, sys; sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), '../../sameboy-harness/python'))
from gr import GR
from cmp import sync, align, script, R
seed=int(sys.argv[1]); upto=int(sys.argv[2]); roms=sys.argv[3:5]
gs=[]
for rom in roms:
    g=GR(R+rom); g.wait(60); sync(g); align(g); gs.append(g)
ev={}
for (s,k,d) in script(seed, upto+100):
    if k: ev.setdefault(s,[]).append(('down',k)); ev.setdefault(s+d,[]).append(('up',k))
def snap(g):
    return g.peek(0xc000,0x1000)+g.peek(0xd000,0x1000)+g.peek(0xff80,0x7f)
for f in range(upto):
    for g in gs:
        for act,k in ev.get(f,[]): getattr(g,act)(k)
        g.wait(1)
    if f>upto-120 or f%20==0:
        x,y=snap(gs[0]),snap(gs[1])
        d=[i for i in range(len(x)) if x[i]!=y[i]]
        ad=lambda i: 0xc000+i if i<0x2000 else 0xff80+i-0x2000
        d=[i for i in d if not (0xdf00<=ad(i)<0xe000) and ad(i)!=0xd0ff]
        if d:
            print('frame',f,[(hex(ad(i)),x[i],y[i]) for i in d[:16]]); break
for g in gs: g.close()
