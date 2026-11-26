# 状態異常のまま トレーナーに 勝って、絵が 出て フィールドに もどるか（赤キット「状態異常で勝つと止まる」の確かめ）
#   python3 tests/status_win.py v par|brn|psn|all 出力の頭 [トレーナーの番号 $C8+クラス] [何人め]
import sys; sys.path.insert(0, sys.path[0])
from lib import *
k, mode, out = sys.argv[1], sys.argv[2], sys.argv[3]
opp = int(sys.argv[4], 0) if len(sys.argv) > 4 else 0xC9
no = int(sys.argv[5]) if len(sys.argv) > 5 else 1
g, S = boot(k)
for i in range(8): g.press('B', 4, 30)   # 60fps 版：はじめの 文が のこって いる
mv = const('THUNDERSHOCK', 'constants/move_constants.asm')
set_party(g, S, [mon(const('PIKACHU'), 50, 300, 300, [mv], [30], stats=(200, 200, 200, 200))])
g.poke(S['wTrainerNo'], no); g.poke(S['wCurOpponent'], opp)
for i in range(200):
    if g.peek(S['wIsInBattle'])[0]: break
    g.wait(10)
assert g.peek(S['wIsInBattle'])[0] == 2, 'no trainer battle'
seen_pic = False; n = 0
for t in range(1500):
    ib = g.peek(S['wIsInBattle'])[0]
    if ib == 0 and t > 5: break
    if ib:
        if mode in ('par', 'all'): g.poke(S['wBattleMonStatus'], 0x40); g.poke(S['wPartyMon1Status'], 0x40)
        if mode == 'brn': g.poke(S['wBattleMonStatus'], 0x10); g.poke(S['wPartyMon1Status'], 0x10)
        if mode in ('psn', 'all'): g.poke(S['wEnemyMonStatus'], 0x08)
        if menu_up(g, S): g.pokes(S['wEnemyMonHP'], [0, 1]); g.pokes(S['wBattleMonHP'], [1, 44])
    g.press('A', 4, 16)
    if t % 10 == 0: g.shot(f'{out}_{n:03d}.png'); n += 1
# フィールドで 歩けるか
g.wait(120)
y = g.peek(S['wYCoord'])[0]; x = g.peek(S['wXCoord'])[0]
for d in 'DURL':
    g.down(d); g.wait(24); g.up(d); g.wait(30)
moved = (g.peek(S['wYCoord'])[0], g.peek(S['wXCoord'])[0]) != (y, x)
pc = g.pc()
g.shot(f'{out}_end.png')
print(k, mode, 'inbattle', g.peek(S['wIsInBattle'])[0], 'loops', t, 'moved', moved, pc)
g.close()
