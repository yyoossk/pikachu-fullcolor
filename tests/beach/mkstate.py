# ピカチュウフルカラー（xf）で、海の家のサーフィンおじさんに話しかけて サマービーチが始まったところの状態を作る（/tmp/cmp/talk.st）
# 新しいゲーム → 自分の部屋で、手持ちを「なみのりを覚えた最初のピカチュウ」にして、部屋の出口のワープ先を海の家にする（くらべる試験のためだけ）
import os, sys, os; sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), '../../sameboy-harness/python'))
from gr import GR
os.makedirs('/tmp/cmp', exist_ok=True)
g = GR(os.path.join(os.path.dirname(os.path.abspath(__file__)), '../../build/xf.gbc'))
g.wait(600)
for i in range(12): g.press('S', 4, 60)
for i in range(36): g.press('A', 4, 50)      # オーキド博士の話・自分の名前
g.press('D', 4, 30); g.press('A', 4, 60)     # ライバルの名前（ブルー）
for i in range(24): g.press('A', 4, 50)
for i in range(3): g.press('B', 4, 40)
g.wait(30)
pid = g.peek(0xd2d8, 2); name = g.peek(0xd11d, 11)
st = [0x54, 0,50, 30, 0, 0x17,0x17, 0xa3, 0x54,0x39,0,0, pid[0],pid[1], 0,0x40,0] + [0]*10 + [0xaa,0xaa] + [30,15,0,0] + [30, 0,50, 0,40, 0,30, 0,60, 0,40]
g.pokes(0xd12b, st); g.poke(0xd123, 1); g.pokes(0xd124, [0x54, 0xff])
g.pokes(0xd233, name[:6]); g.pokes(0xd257, name[:6])
g.poke(0xd3f1, g.peek(0xd3f1)[0] | 0x40)   # ピカチュウが なみのりを覚えた
g.pokes(0xd32e, [7, 3, 0, 0xf8])           # 足もとのワープ → 海の家
g.down('D'); g.wait(24); g.up('D'); g.wait(150)
for k in range(3): g.down('U'); g.wait(24); g.up('U'); g.wait(30)
assert g.peek(0xd2dd)[0] == 0xf8 and g.peek(0xd2e0, 2) == [4, 2], 'not in front of the surf dude'
for i in range(12): g.press('A', 4, 50)
assert 'bank=3e' in g.pc(), 'minigame did not start'
g.save_state('/tmp/cmp/talk.st'); g.close(); print('OK /tmp/cmp/talk.st')
