"""テスト用の道具（sameboy-harness の GR を使う）。
  g, S = boot('v')        … build/v.gbc（なければ base/v.gbc）を起動して、主人公の部屋まで進める
  set_party(g, S, [mon(...)])
  wild_battle(g, S, species, level)  … 野生のバトルを始め、わざを選ぶメニューまで進める
"""
import sys, os, re
ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, os.path.join(ROOT, 'sameboy-harness', 'python'))
from gr import GR
from gbtools import loadsym
DIS = os.path.join(os.path.dirname(ROOT), 'pokeyellow-jp')
def const(name, path='constants/pokemon_constants.asm'):
    v = 0
    for l in open(os.path.join(DIS, path), encoding='utf-8'):
        l = l.split(';')[0].strip()
        if l.startswith('const_def'):
            p = l.split(); v = int(p[1].replace('$', '0x'), 0) if len(p) > 1 else 0
        elif l.startswith('const '):
            if l.split()[1] == name: return v
            v += 1
        elif l.startswith('const_skip'): v += 1
    raise KeyError(name)
def rom(k):
    b = os.path.join(ROOT, 'build', k + '.gbc')
    return (b, os.path.join(ROOT, 'build', k + '.sym')) if os.path.exists(b) else (os.path.join(ROOT, 'base', k + '.gbc'), os.path.join(ROOT, 'syms', k + '.sym'))
def boot(k, frames=600):
    r, s = rom(k); S, BK = loadsym(s)
    g = GR(r); g.wait(frames)
    # the intro: A until the player can walk (the first name in each list)
    for i in range(400):
        g.press('A', 4, 20)
        if i % 10 == 9:
            y = g.peek(S['wYCoord'])[0]
            g.down('D'); g.wait(20); g.up('D'); g.wait(30)
            if g.peek(S['wYCoord'])[0] != y:
                g.down('U'); g.wait(20); g.up('U'); g.wait(30)
                break
    return g, S
def mon(species, level, hp, maxhp, moves, pps, stats=(50, 50, 50, 50), exp=None, otid=(1, 2)):
    m = [species, hp >> 8, hp & 255, level, 0, 0, 0, 0] + (moves + [0] * 4)[:4] + list(otid)
    e = exp if exp is not None else level ** 3
    m += [e >> 16 & 255, e >> 8 & 255, e & 255] + [0] * 10 + [0xff, 0xff] + (pps + [0] * 4)[:4]
    m += [level, maxhp >> 8, maxhp & 255]
    for st in stats: m += [st >> 8, st & 255]
    assert len(m) == 44
    return m
def set_party(g, S, mons, nick=[0x92, 0x8c, 0x93, 0x50, 0x50, 0x50]):
    pid = g.peek(S['wPlayerID'], 2)
    mons = [m[:12] + pid + m[14:] for m in mons]   # the player's ID: the Pokemon obeys
    nick_ot = g.peek(S['wPlayerName'], 6)
    g.poke(S['wPartyCount'], len(mons))
    g.pokes(S['wPartySpecies'], [m[0] for m in mons] + [0xff])
    for i, m in enumerate(mons):
        g.pokes(S['wPartyMons'] + 44 * i, m)
        g.pokes(S['wPartyMonOT'] + 6 * i, nick_ot); g.pokes(S['wPartyMonNicks'] + 6 * i, nick)
def wild_battle(g, S, species, level):
    g.poke(S['wCurEnemyLevel'], level); g.poke(S['wCurOpponent'], species)
    for d in 'DULR':
        if g.peek(S['wIsInBattle'])[0]: break
        g.down(d); g.wait(20); g.up(d); g.wait(30)
    for i in range(300):
        if g.peek(S['wIsInBattle'])[0]: break
        g.wait(10)
    for i in range(80):
        g.wait(10)
        if g.peek(S['wTileMap'] + 14 * 20 + 9, 1)[0] == 0xed or menu_up(g, S): break
        if i % 4 == 3: g.press('A', 4, 10)
def menu_up(g, S):
    t = g.peek(S['wTileMap'] + 14 * 20, 60)
    return any(t[r * 20 + c] == 0xed for r in (0, 2) for c in range(8, 20))
