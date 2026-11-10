# 自転車: のるとボールにもどり（かくれる）、おりるとまた出てくる。色がピカチュウにもどらない・まちがわないか
import sys; sys.path.insert(0,'.')
from fol_lib import *
k=sys.argv[1]; slot=int(sys.argv[2])
g,S=start(k,f'/tmp/claude-0/pal_{k}.st',slot)
g.poke(S['wNumBagItems'],1); g.pokes(S['wBagItems'],[const('BICYCLE','constants/item_constants.asm'),1,0xff])
g.wait(30)
fs=[]
def shot(n):
    fn=f'/tmp/claude-0/bk_{n}.png'; g.shot(fn); fs.append(fn)
    print(n, 'state', g.peek(S['wWalkBikeSurfState'])[0], pos(g,S), fpos(g,S), 'b7', g.wpeek(7,0xd010,3), 'pal6', g.pals().split('OB:')[1][96:112])
def use_bike():
    g.press('S',4,40); g.press('D',4,20); g.press('A',4,60)   # リュック
    g.press('R',4,30); g.press('R',4,30)                      # たいせつ ポケット
    g.press('A',4,40); g.press('A',4,90)                      # 自転車 → つかう
    for i in range(3): g.press('B',4,30)
shot('0')
use_bike(); g.wait(30); shot('bike')
step(g,'U',2); g.wait(10); shot('bike2')
use_bike(); g.wait(30); shot('off')
step(g,'D',1); g.wait(20); shot('off1')
step(g,'L',1); g.wait(20); shot('off2')
strip(fs,'/tmp/claude-0/bk_strip.png',scale=1,cols=6)
