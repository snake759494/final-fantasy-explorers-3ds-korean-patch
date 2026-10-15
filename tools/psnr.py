import sys,os,numpy as np;sys.path.insert(0,os.path.dirname(os.path.abspath(__file__)))
from yuv import load
for i in map(int,sys.argv[3:]):
    a=np.concatenate([x.ravel() for x in load(f'{sys.argv[1]}/{i:05d}.yuv')]).astype(float);b=np.concatenate([x.ravel() for x in load(f'{sys.argv[2]}/{i:05d}.yuv')]).astype(float)
    mse=((a-b)**2).mean();print(i,round(10*np.log10(255**2/max(mse,1e-9)),2),end='  ')
print()
