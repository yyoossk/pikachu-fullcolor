# 新しい ROM と前の ROM を同じ操作で動かして録画（起動が終わってから操作する）
import sys, numpy as np; sys.path.insert(0,'../../sameboy-harness/python')
from gr import GR
from cmp import script
N=int(sys.argv[3]) if len(sys.argv)>3 else 6000
for rom,tag in ((sys.argv[1],'new'),(sys.argv[2],'old')):
    g=GR(rom); g.wait(300); g.rec(f'/tmp/cmp/vis_{tag}'); t=0
    for (s,k,d) in script(7, N):
        if s>t: g.wait(s-t); t=s
        if k: g.down(k)
        g.wait(d); t+=d
        if k: g.up(k)
    g.wait(max(0,N-t)); g.stop(); g.close()
