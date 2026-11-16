# 30 回続けて遊ぶ（ふつうに遊ぶ・ゲームオーバー・ボタン連打をまぜる）。2 つの ROM で同じになるか
import os, sys; sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), '../../sameboy-harness/python'))
from gr import GR
from cmp import sync, script, R
rom=sys.argv[1]; out=[]
g=GR(R+rom); g.wait(60)
def play(seed, frames):
    t=0
    for (s,k,d) in script(seed, frames):
        if s>t: g.wait(s-t); t=s
        if k: g.down(k)
        g.wait(d); t+=d
        if k: g.up(k)
for r in range(30):
    sync(g)
    if r%3==1: g.wait(40); g.pokes(0xc5d6,[0x10,0]); g.wait(300)
    else:
        if r%3==2:
            for i in range(15): g.press('sSB'[i%3],4,20)
        play(1000+r, 3000); sync(g,11,30000)
    g.wait(40); g.press('A',4,10)
    g.wait(20); out.append((r, g.peek(0xd414,2), g.pc().split()[2]))
g.bsave(f'/tmp/cmp/end_{rom}.sav'); g.shot(f'/tmp/cmp/end_{rom}.png'); g.cmd('minsp'); out.append(g.line())
print(out); g.close()
