import sys; sys.path.insert(0,'/home/claude/pk/fc/tests')
from lib import *
from PIL import Image
k=sys.argv[1]; st=sys.argv[2]; r,s=rom(k); S,BK=loadsym(s)
g=GR(r,state=st); g.wait(2)
out=[]
for seq in ['UUU','LLL','RRR','DDD']:
    for d in seq:
        g.down(d); g.wait(17); g.up(d); g.wait(4)
    g.wait(20); g.shot('/tmp/claude-0/t.png')
    out.append(Image.open('/tmp/claude-0/t.png').convert('RGB').crop((40,40,120,104)).resize((240,192),Image.NEAREST))
W=Image.new('RGB',(240*4,192))
for i,im in enumerate(out): W.paste(im,(i*240,0))
W.save('/tmp/claude-0/dir2.png')
