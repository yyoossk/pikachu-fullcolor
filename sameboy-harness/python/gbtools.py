"""ハーネスのまわりの道具：.sym の読み込み、録画のコマ一覧、動画への変換"""
import re, subprocess
FS = 160 * 144 * 3

def loadsym(path):
    """rgblink の .sym -> {名前: アドレス}（bank は bank_of に）"""
    d = {}; bank_of = {}
    for l in open(path):
        m = re.match(r'([0-9a-fA-F]+):([0-9a-fA-F]+) (\S+)', l)
        if m: d[m.group(3)] = int(m.group(2), 16); bank_of[m.group(3)] = int(m.group(1), 16)
    return d, bank_of

def charmap(path):
    """pokered 系の constants/charmap.asm -> {文字: コード}（文字列をRAMに書くとき用）"""
    cm = {}
    for l in open(path, encoding='utf-8'):
        m = re.match(r'\s*charmap "(.+?)",\s*\$([0-9a-fA-F]+)', l)
        if m and m.group(1) not in cm: cm[m.group(1)] = int(m.group(2), 16)
    return cm

def frames(rgb):
    import numpy as np
    data = open(rgb, 'rb').read()
    return [np.frombuffer(data[i * FS:(i + 1) * FS], np.uint8).reshape(144, 160, 3) for i in range(len(data) // FS)]

def unique_sheet(rgb, out_png, cols=10):
    """録画から、前のコマと違うコマだけを番号つきで並べた一覧画像を作る"""
    import numpy as np
    from PIL import Image, ImageDraw
    fr = frames(rgb); uniq = []
    for i, f in enumerate(fr):
        if not uniq or not np.array_equal(f, fr[uniq[-1]]): uniq.append(i)
    rows = max(1, (len(uniq) + cols - 1) // cols)
    im = Image.new('RGB', (cols * 164, rows * 158), 'white'); d = ImageDraw.Draw(im)
    for k, i in enumerate(uniq):
        x, y = (k % cols) * 164, (k // cols) * 158
        im.paste(Image.fromarray(fr[i]), (x + 2, y + 12)); d.text((x + 2, y), str(i), fill='black')
    im.save(out_png); return uniq

def to_mp4(name, out, scale=4):
    """name.rgb / name.pcm -> mp4（ffmpeg が要る）。59.7275fps"""
    subprocess.run(['ffmpeg', '-y', '-loglevel', 'error',
                    '-f', 'rawvideo', '-pix_fmt', 'rgb24', '-s', '160x144', '-r', '59.7275', '-i', name + '.rgb',
                    '-f', 's16le', '-ar', '48000', '-ac', '2', '-i', name + '.pcm',
                    '-vf', f'scale={160 * scale}:{144 * scale}:flags=neighbor', '-pix_fmt', 'yuv420p',
                    '-c:v', 'libx264', '-crf', '18', '-c:a', 'aac', '-shortest', out], check=True)
