import sys; sys.path.insert(0, '.')
from lib import *
k = sys.argv[1]; out = sys.argv[2]
g, S = boot(k)
set_party(g, S, [mon(const('PIKACHU'), 30, 100, 100, [const('THUNDERSHOCK', 'constants/move_constants.asm')], [30], stats=(100, 100, 100, 100))])
wild_battle(g, S, const('RATTATA'), 30)
print('battle', g.peek(S['wIsInBattle'])[0], 'menu', menu_up(g, S))
# enemy HP: 55/100 (green); the player's: 55/100
g.pokes(S['wEnemyMonHP'], [0, 1]); g.pokes(S['wEnemyMonMaxHP'], [0, 100])
g.pokes(S['wBattleMonHP'], [0, 55])
g.wait(5); g.shot(out + '_0.png'); print('pals0', g.pals()[:70])
g.press('A', 4, 60)   # たたかう
g.shot(out + '_f.png')
g.press('A', 4, 60)   # でんきショック
g.shot(out + '_g.png')
for i in range(40):
    g.wait(15); g.shot(f'{out}_s{i:02d}.png')
g.close()
