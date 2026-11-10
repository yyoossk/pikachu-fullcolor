# つり・なみのり（マサラタウンの南の水）
import sys; sys.path.insert(0,'.')
from fol_lib import *
k=sys.argv[1]
g,S=start(k,'/tmp/claude-0/pw.st' if k=='v' else f'/tmp/claude-0/pw_{k}.st')
fs=[]
def shot(n):
    fn=f'/tmp/claude-0/wt_{n}.png'; g.shot(fn); fs.append(fn)
    o=g.oam(); ent=[(i,o[i*4],o[i*4+1],o[i*4+2],o[i*4+3]) for i in range(40) if 0<o[i*4]<160]
    print(n, pos(g,S), fpos(g,S), 'state', g.peek(S['wWalkBikeSurfState'])[0], 'pal6', g.pals().split('OB:')[1][96:112], 'b7', g.wpeek(7,0xd010,3), 'oam', [(e[0],hex(e[3]),hex(e[4])) for e in ent][-8:])
it=lambda n: const(n,'constants/item_constants.asm')
g.poke(S['wNumBagItems'],1); g.pokes(S['wBagItems'],[it('OLD_ROD'),1,0xff])
g.press('R',2,20); shot('face')
if 'fish' in sys.argv[2:]:
    # つり
    g.press('S',4,40); g.press('D',4,20); g.press('A',4,60); g.press('R',4,30); g.press('R',4,30)
    g.press('A',4,40); g.press('A',4,10)
    for i in range(6):
        g.wait(15); shot(f'fish{i}')
    for i in range(8): g.press('B',4,30)
    # たたかいになったら にげる
    if g.peek(S['wIsInBattle'])[0]:
        g.press('D',4,10); g.press('R',4,10); g.press('A',4,60)
        for i in range(8): g.press('B',4,30)
    g.wait(60); shot('afterfish')
    sys.exit(0)
# なみのり: フシギダネに なみのり、ブルーバッジ
base=S['wPartyMon1']+44*1; g.poke(base+8, const('SURF','constants/move_constants.asm'))
g.poke(S['wObtainedBadges'], 0xff)
g.press('R',2,20); g.press('S',4,60); g.press('A',4,90)  # ポケモン
g.press('D',4,20); g.press('A',4,40); g.press('A',4,90)   # フシギダネ → なみのり
for i in range(4): g.press('B',4,20)
g.wait(60); shot('surf')
step(g,'R',2); g.wait(20); shot('surf2')
step(g,'L',3); g.wait(40); shot('land')
step(g,'U',1); g.wait(20); shot('land1'); step(g,'U',1); g.wait(20); shot('land2')
strip(fs,f'/tmp/claude-0/wt_{k}.png',scale=1,cols=6)
