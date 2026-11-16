# 結果の画面のあいだ、ピカチュウの声（バンク 3b の PlayPikachuSoundClip）が鳴るかを見る
import os, sys; sys.path.insert(0,os.path.join(os.path.dirname(os.path.abspath(__file__)), '../../sameboy-harness/python'))
from gr import GR
from cmp import sync, R
which=sys.argv[1]
g = GR(R+os.environ.get('BEACH_ROM','summer_beach.gbc')) if which=='a' else GR(R+'xf.gbc', state='/tmp/cmp/talk.st')
if which=='a': g.wait(60)
sync(g)
# 早く結果まで行くため、なにも押さずに待つ
seen={}; f=0
while f<9000:
    r=g.peek(0xc5d1)[0]
    if r>=8:
        pc=g.pc(); b=pc.split('bank=')[1].split()[0]
        if b==os.environ.get('CRY_BANK','3b'): seen.setdefault(r,0); seen[r]+=1
        if r==11 or r&0x80: break
        g.wait(1); f+=1
    else:
        g.wait(30); f+=30
print(which, 'cry frames by routine', seen, 'hi', g.peek(0xd414,2))
g.close()
