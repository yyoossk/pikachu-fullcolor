# 電源を入れてから同じ操作をして、2つの ROM の画面・音・セーブが 1 コマ・1 サンプルまで同じかを見る（乱数も本物のまま）
import os, sys; sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), '../../sameboy-harness/python'))
import numpy as np
from gr import GR
from cmp import script, R
seed=int(sys.argv[1]); frames=int(sys.argv[2]); out=sys.argv[3]; roms=sys.argv[4:6]
for i,rom in enumerate(roms):
    g=GR(R+rom); g.rec(f'{out}_{"ab"[i]}'); t=0
    for (s,k,d) in script(seed, frames):
        if s>t: g.wait(s-t); t=s
        if k=='A' and (s//500)%3==0: k='A'
        if k: g.down(k)
        g.wait(d); t+=d
        if k: g.up(k)
    g.wait(max(0,frames-t)); g.stop(); g.bsave(f'{out}_{"ab"[i]}.sav')
    print(rom, g.peek(0xc5d1), g.peek(0xc5d6,2), g.peek(0xd414,2), g.pc()); g.close()
a=np.fromfile(out+'_a.rgb',np.uint8).reshape(-1,144,160,3); b=np.fromfile(out+'_b.rgb',np.uint8).reshape(-1,144,160,3)
n=min(len(a),len(b)); d=[i for i in range(n) if (a[i]!=b[i]).any()]
pa=np.fromfile(out+'_a.pcm',np.int16); pb=np.fromfile(out+'_b.pcm',np.int16); m=min(len(pa),len(pb))
sa=open(out+'_a.sav','rb').read(); sb=open(out+'_b.sav','rb').read()
print('frames',n,'diff',len(d),d[:3],'| audio',('same' if (pa[:m]==pb[:m]).all() else 'diff'),len(pa),len(pb),'| sav',sa==sb)
