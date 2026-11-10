import sys; sys.path.insert(0,'.')
from lib import *
k=sys.argv[1]; model=sys.argv[2]
r,s=rom(k); S,BK=loadsym(s)
g=GR(r,model=model)
g.wait(700); g.shot(f'/tmp/claude-0/{model}_{k}_title.png')
for i in range(120): g.press('A',4,25)
g.shot(f'/tmp/claude-0/{model}_{k}_game.png'); print(k, model, g.peek(S['wCurMap'])[0], g.pc())
