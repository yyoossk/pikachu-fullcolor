# ドア: ポケモンセンターに入って、1歩歩く。回復してもらう。外に出る
import sys; sys.path.insert(0,'.')
from fol_lib import *
k=sys.argv[1]; slot=int(sys.argv[2])
g,S=start(k,f'/tmp/claude-0/fol_{k}.st',slot)
fs=[]
def shot(n):
    fn=f'/tmp/claude-0/door_{n}.png'; g.shot(fn); fs.append(fn); print(n, pos(g,S), fpos(g,S), [x[1:4] for x in follower_oam(g)][:1])
step(g,'U',1); shot('a')
g.down('U'); 
for i in range(80):
    g.wait(1)
    if pos(g,S)[2]!=1: break
g.up('U'); g.wait(60); shot('b_inside')
step(g,'U',1); g.wait(10); shot('c_step1')
step(g,'U',3); g.wait(10); shot('d_step4')
# ジョーイさんに話しかける（カウンターの前まで）
for i in range(6):
    step(g,'U',1)
g.wait(10); shot('e_counter')
g.press('A',4,40)
for i in range(30):
    g.press('A',4,20)
    if i in (3,6,9,12,15): shot(f'f_heal{i}')
g.wait(60); shot('g_after')
step(g,'D',8); g.wait(60); shot('h_out')
step(g,'D',1); g.wait(20); shot('i_out1')
strip(fs,'/tmp/claude-0/door_strip.png',scale=1,cols=6)
g.save_state(f'/tmp/claude-0/door_{k}.st')
