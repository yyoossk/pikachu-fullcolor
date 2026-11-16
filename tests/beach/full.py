# 1回を最後まで（結果の画面 → A）通して、録画と場面ごとの画面を残す
import os, sys; sys.path.insert(0,os.path.join(os.path.dirname(os.path.abspath(__file__)), '../../sameboy-harness/python'))
from gr import GR
from cmp import sync, script, R
which, out, seed = sys.argv[1], sys.argv[2], int(sys.argv[3])
g = GR(R+os.environ.get('BEACH_ROM','summer_beach.gbc'), sav=(sys.argv[4] if len(sys.argv)>4 else None)) if which=='a' else GR(R+'xf.gbc', state='/tmp/cmp/talk.st')
if which=='a': g.wait(60)
sync(g)
g.rec(out); tl=[]; f=0; prev=None; ev=script(seed, 20000); ei=0
while f < 12000:
    r=g.peek(0xc5d1)[0]
    if r!=prev:
        tl.append((f,r)); prev=r; g.shot(f'{out}_r{len(tl):02d}_{r:02x}.png')
    if which=='b' and r>11: break
    if r & 0x80: break
    if r>=8 and f%30==0: g.press('A',4,0)
    elif r<8 and ei<len(ev) and ev[ei][0]<=f:
        k=ev[ei][1]; d=ev[ei][2]; ei+=1
        if k and k!='A':
            g.down(k); g.wait(d); g.up(k); f+=d; continue
    g.wait(1); f+=1
g.wait(400); g.stop()
print(which, tl, 'hi', g.peek(0xd414,2), 'pc', g.pc())
g.shot(out+'_after.png')
if which=='a': g.bsave(out+'.sav')
g.close()
