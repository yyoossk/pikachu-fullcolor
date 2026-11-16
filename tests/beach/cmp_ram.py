# 色だけ変えた ROM と前の ROM で、ゲームの動き（スプライトの位置・ポーズ、サマービーチの変数、乱数、ハイスコア）が毎フレーム同じかを見る
import os, sys; sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), '../../sameboy-harness/python'))
from gr import GR
from cmp import script
seed=int(sys.argv[1]); N=int(sys.argv[2]); roms=sys.argv[3:5]
logs=[]
for rom in roms:
    g=GR(rom); g.wait(300); t=0; log=[]; ev={}
    for (s,k,d) in script(seed, N):
        if k: ev.setdefault(s,[]).append(('down',k)); ev.setdefault(s+d,[]).append(('up',k))
    for f in range(N):
        for act,k in ev.get(f,[]): getattr(g,act)(k)
        g.wait(1)
        if f%3==0:
            oam=g.peek(0xc300,160); oam=[v for i,v in enumerate(oam) if i%4!=3]
            log.append((f, tuple(oam), tuple(g.peek(0xc5d0,0x70)), tuple(g.peek(0xffd3,3)), tuple(g.peek(0xd414,2))))
    g.bsave(f'/tmp/cmp/ram_{seed}_{len(logs)}.sav'); g.close(); logs.append(log)
d=[a[0] for a,b in zip(*logs) if a!=b]
s0=open(f'/tmp/cmp/ram_{seed}_0.sav','rb').read(); s1=open(f'/tmp/cmp/ram_{seed}_1.sav','rb').read()
print('seed',seed,'比べたコマ',len(logs[0]),'ちがうコマ',len(d),d[:3],'セーブ',s0==s1)
