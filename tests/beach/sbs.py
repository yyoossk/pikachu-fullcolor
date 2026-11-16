import os, sys, numpy as np
from PIL import Image
p=sys.argv[1]; fr=[int(x) for x in sys.argv[3].split(',')]
a=np.fromfile(p+'_a.rgb',np.uint8).reshape(-1,144,160,3)
b=np.fromfile(p+'_b.rgb',np.uint8).reshape(-1,144,160,3)
W=Image.new('RGB',(330*len(fr)//2+330*(len(fr)%2), 150*2) if False else (330, 150*len(fr)),'white')
for i,f in enumerate(fr):
    W.paste(Image.fromarray(a[f]),(0,i*150)); W.paste(Image.fromarray(b[f]),(165,i*150))
W.save(sys.argv[2])
