# 小さくした ROM（summer_beach_small.gbc）と 1MB の summer_beach.gbc を、同じ操作で動かして比べる
import os, sys; sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), '../../sameboy-harness/python'))
import numpy as np
from gr import GR
from cmp import sync, play, align, R
seed=int(sys.argv[1]); frames=int(sys.argv[2]); out=sys.argv[3]
gs=[]
for rom in (sys.argv[4], sys.argv[5]) if len(sys.argv) > 5 else ('summer_beach_small.gbc','summer_beach.gbc'):
    g=GR(R+rom); g.wait(60); sync(g); align(g); gs.append(g)
play(gs[0], out+'_a', seed, frames); play(gs[1], out+'_b', seed, frames)
for g in gs: print(g.peek(0xc5d1), g.peek(0xc5d6,2), g.peek(0xc5dc,2), g.peek(0xd414,2), g.pc()); g.close()
a=np.fromfile(out+'_a.rgb',np.uint8).reshape(-1,144,160,3); b=np.fromfile(out+'_b.rgb',np.uint8).reshape(-1,144,160,3)
n=min(len(a),len(b)); d=[i for i in range(n) if (a[i]!=b[i]).any()]
pa=np.fromfile(out+'_a.pcm',np.int16); pb=np.fromfile(out+'_b.pcm',np.int16); m=min(len(pa),len(pb))
print('frames',n,'diff frames',len(d),'first',d[:1], 'audio same' if (pa[:m]==pb[:m]).all() else 'audio diff at %d' % np.argmax(pa[:m]!=pb[:m]))
