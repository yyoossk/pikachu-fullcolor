# ポケモンセンター：回復の あと 主人公が 下を 向くか・「かいふくの アニメ」とばす／みる（src/pokecenter_heal.asm の 確かめ）
#   python3 tests/pokecenter_heal.py 版 0|1（1 = とばす） 出力の頭 [yes|no]
import sys, os; sys.path.insert(0, sys.path[0])
from lib import *
from PIL import Image
k, skip, out = sys.argv[1], int(sys.argv[2]), sys.argv[3]
ans = sys.argv[4] if len(sys.argv) > 4 else 'yes'
g, S = boot(k)
for i in range(8): g.press('B', 4, 30)
mv = const('THUNDERSHOCK', 'constants/move_constants.asm')
set_party(g, S, [mon(const('PIKACHU'), 20, 5, 60, [mv], [3])])
o = g.peek(0xd2d6)[0]
g.poke(0xd2d6, (o | 2) if skip else (o & ~2))
# トキワの ポケモンセンターへ ワープ
g.poke(S['hWarpDestinationMap'], 0x29); g.poke(S['wDestinationWarpID'], 0); g.poke(S['wLastMap'], 1)
g.poke(S['wStatusFlags3'], g.peek(S['wStatusFlags3'])[0] | 8)
g.wait(120)
def P(): return g.peek(S['wXCoord'])[0], g.peek(S['wYCoord'])[0], g.peek(S['wCurMap'])[0]
p0 = P()
# ジョーイさんの 前（x=3, y=3 の 見こみ）まで 上へ
for i in range(8):
    if P()[1] <= 3: break
    g.down('UP'); g.wait(17); g.up('UP'); g.wait(8)
g.down('UP'); g.wait(3); g.up('UP'); g.wait(10)
p1 = P()
ims = []; t = 0; frames = None
for i in range(40):
    if ans == 'no' and i == int(os.environ.get('NOAT', 8)): g.press('DOWN', 4, 10)
    g.press('A', 4, 26); t += 30
    g.shot(out + '.s.png'); ims.append(Image.open(out + '.s.png').copy())
    hp = g.peek(S['wPartyMon1HP'], 2)
    if frames is None and hp[1] == 60: frames = t
print(k, 'skip', skip, ans, 'start', p0, 'nurse', p1, 'facing', g.peek(0xc109)[0], 'hp', g.peek(S['wPartyMon1HP'], 2)[1], 'pp', g.peek(S['wPartyMon1'] + 29)[0], 'healed_at', frames, 'opt', hex(g.peek(0xd2d6)[0]), g.pc())
g.close()
W = Image.new('RGB', (160 * 10, 144 * 4), 'white')
for i, im in enumerate(ims): W.paste(im, ((i % 10) * 160, (i // 10) * 144))
W.save(out)
