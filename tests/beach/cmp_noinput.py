# ボタンを押さずに、結果の画面・ベストスコア・つぎの回のはじめまで流して比べる（乱数は試験用に固定）
import os, sys; sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), '../../sameboy-harness/python'))
import numpy as np
from gr import GR
from cmp import sync, align, R
out=sys.argv[1]; roms=sys.argv[2:4]
gs=[]
for rom in roms:
    g=GR(R+rom); g.wait(60); sync(g); align(g); gs.append(g)
for i,g in enumerate(gs):
    g.rec(f'{out}_{"ab"[i]}'); g.wait(6500)
    g.down('A'); g.wait(30); g.up('A'); g.wait(600); g.stop()
    print(roms[i], g.peek(0xc5d1), g.peek(0xd414,2), g.pc())
    g.bsave(f'{out}_{"ab"[i]}.sav'); g.close()
a=np.fromfile(out+'_a.rgb',np.uint8).reshape(-1,144,160,3); b=np.fromfile(out+'_b.rgb',np.uint8).reshape(-1,144,160,3)
n=min(len(a),len(b)); d=[i for i in range(n) if (a[i]!=b[i]).any()]
print('frames',n,'diff',len(d),d[:5])
sa=open(out+'_a.sav','rb').read(); sb=open(out+'_b.sav','rb').read(); print('sav same', sa==sb, sa[0x3f00:0x3f05].hex())
