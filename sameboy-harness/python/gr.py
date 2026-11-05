"""SameBoy ハーネス（gbrec）を Python から動かすクラス。
   g = GR('game.gbc'); g.wait(300); g.press('A'); g.shot('a.png'); g.close()
"""
import os, subprocess
H = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
BIN = os.environ.get('GBREC', os.path.join(H, 'bin', 'gbrec'))
BOOT = {'cgb': 'cgb_boot.bin', 'dmg': 'dmg_boot.bin', 'sgb': 'sgb_boot.bin'}

class GR:
    def __init__(s, rom, state=None, model='cgb', sav=None, binary=None):
        env = dict(os.environ)
        if model == 'dmg': env['GBDMG'] = '1'
        if model == 'sgb': env['GBSGB'] = '1'
        boot = os.path.join(H, 'bin', BOOT[model])
        s.p = subprocess.Popen([binary or BIN, rom, boot], stdin=subprocess.PIPE, stdout=subprocess.PIPE,
                               text=True, bufsize=1, env=env)
        if sav: s.cmd(f'bload {sav}'); s.cmd('reset')
        if state: s.cmd(f'load {state}'); s.wait(2)
    # --- 低レベル
    def cmd(s, c): s.p.stdin.write(c + '\n'); s.p.stdin.flush()
    def line(s): return s.p.stdout.readline().strip()
    def sync(s): s.peek(0); return s   # それまでのコマンドが終わるまで待つ
    # --- 進める・ボタン（R L U D A B S=START s=SELECT）
    def wait(s, n): s.cmd(f'wait {n}')
    def press(s, k, n=4, w=20): s.cmd(f'press {k} {n}'); s.cmd(f'wait {w}')
    def down(s, k): s.cmd(f'down {k}')
    def up(s, k): s.cmd(f'up {k}')
    # --- メモリ
    def peek(s, a, n=1):
        s.cmd(f'peek {a:x} {n}'); l = s.line(); return [int(x, 16) for x in l.split(':')[1].split()]
    def poke(s, a, v): s.cmd(f'poke {a:x} {v}')
    def pokes(s, a, vals):
        for i, v in enumerate(vals): s.poke(a + i, v)
    def vpeek(s, bank, addr, n=16):   # VRAM（bank 0/1, $8000-$9FFF）
        s.cmd(f'vpeek {bank * 0x10000 + addr:x} {n}'); return [int(x, 16) for x in s.line().split(':')[1].split()]
    def wpeek(s, bank, addr, n=16):   # WRAM のバンク（$D000-$DFFF）
        s.cmd(f'wpeek {bank * 0x10000 + addr:x} {n}'); return [int(x, 16) for x in s.line().split(':')[1].split()]
    def pals(s): s.cmd('pals'); return s.line()
    def oam(s): s.cmd('oam'); return bytes.fromhex(s.line()[4:])
    def pc(s): s.cmd('pc'); return s.line()
    # --- 画面・セーブ
    def shot(s, path):
        """path が .ppm ならそのまま、.png なら変換（Pillow が要る）。終わるまで待つ"""
        ppm = path if path.endswith('.ppm') else path + '.ppm'
        s.cmd(f'shot {ppm}'); s.sync()
        if ppm != path:
            from PIL import Image
            Image.open(ppm).save(path); os.remove(ppm)
        return path
    def save_state(s, f): s.cmd(f'save {f}'); s.sync()
    def load_state(s, f): s.cmd(f'load {f}')
    def bsave(s, f): s.cmd(f'bsave {f}'); s.sync()   # 電池バックアップ（.sav）
    def bload(s, f): s.cmd(f'bload {f}')
    def reset(s): s.cmd('reset')
    # --- 録画（name.rgb = 160x144 RGB の連続フレーム, name.pcm = 48kHz 16bit ステレオ）
    def rec(s, name): s.cmd(f'rec {name}')
    def stop(s): s.cmd('stoprec'); s.line()
    def close(s): s.p.stdin.close(); s.p.wait()
