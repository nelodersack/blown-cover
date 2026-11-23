import sys,glob,subprocess,os
from PIL import Image
pdf,outp,cols=sys.argv[1],sys.argv[2],int(sys.argv[3]) if len(sys.argv)>3 else 10
subprocess.run(['rm','-rf','/tmp/sh'],check=False);os.makedirs('/tmp/sh')
subprocess.run(['pdftoppm','-r','60','-png',pdf,'/tmp/sh/p'],check=True)
fs=sorted(glob.glob('/tmp/sh/p-*.png'));ims=[Image.open(f) for f in fs];w,h=ims[0].size;rows=(len(ims)+cols-1)//cols
S=Image.new('RGB',(cols*(w+6)+6,rows*(h+6)+6),'#888')
for i,im in enumerate(ims):S.paste(im,(6+(i%cols)*(w+6),6+(i//cols)*(h+6)))
S.save(outp)
