# サマービーチだけの ROM で、実際に読まれる ROM の場所を記録する（いろいろな遊び方を通す）
import os, sys, random; sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), '../../sameboy-harness/python'))
from gr import GR
from cmp import sync, script
rom=sys.argv[1]; out=sys.argv[2]; seed=int(sys.argv[3])
g=GR(rom); g.cmd('cov 1')
if len(sys.argv)>4: g.cmd('watch 2000 8192')
g.wait(60)
def play(seed, frames):
    t=0
    for (s,k,d) in script(seed, frames):
        if s>t: g.wait(s-t); t=s
        if k: g.down(k)
        g.wait(d); t+=d
        if k: g.up(k)
# 1回目：遊んで結果まで（ベストスコア・声・セーブ）
sync(g); play(seed, 3000); sync(g,11,20000); g.wait(60); g.press('A',4,10)
# 2回目：ゲームオーバー
sync(g); g.wait(50); g.pokes(0xc5d6,[0x10,0]); g.wait(300); g.press('A',4,10)
# 3回目：SELECT・START・B を押しながら遊ぶ、ベストでない結果
sync(g)
for i in range(20): g.press('sSB'[i%3],4,30)
play(seed+1, 2000); sync(g,11,20000); g.wait(60); g.press('A',4,10)
# ソフトリセット
sync(g); g.wait(100)
g.down('ABSs'); g.wait(10); g.up('ABSs'); g.wait(600); sync(g); play(seed+2, 6000)
g.cmd(f'covsave {out}'); g.line(); g.close()
