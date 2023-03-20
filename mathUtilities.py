from math import *
import random, sys

def sample_event(evnt_lst,uniform_val=None):
    '''
    Samples a random index according to the given weights.
    @param evnt_lst: a list of weights.
    @param uniform_val (optional): a uniform value chosen from (0,1) which is used for the sampling. If none is given
           a freshly generated uniform value is used while sampling.
    @returns {int} a random index (starts at 1) chosen according to its weight.
    '''
    total=sum(evnt_lst)
    coin=uniform_val*total if uniform_val else random.uniform(0,total)
    cur_sum=0
    N = len(evnt_lst)
    for i in range(N):
        if cur_sum < coin <= cur_sum+evnt_lst[i]: return i+1
        cur_sum+=evnt_lst[i]
    return random.randint(1,N) # if the coin toss was inconclusive, return a uniformly chosen index.  
    
def neighbour(i,R=1,max_dist=False):
    '''
    Returns a list containing the points with integer coordinates in the R-neighbourhood of i (excludes i)
    @param i: a point in R^n (array of length n = len(i))
    @param R (positive integer): range of the neighbourhood points outside which are discarded.
    @param max_dist (bool): should it use maxium-distance or euclidean-distance while computing the neighbourhood of the point i?
    '''
    dimn=len(i)
    nbd=[]
    code=""
    for k in range(1,dimn+1):
        code+="for e_%d in range(-R,R+1):\n"%k+k*"\t"
    code+="point="+"("+",".join(["i[%d]+e_%d"%(k-1,k) for k in range(1,dimn+1)])+")\n"+dimn*"\t"
    code+="dist=sup_dist(point,i) if max_dist else euclid_dist(point,i)\n"+dimn*"\t"
    code+="if dist==0: continue\n"+dimn*"\t"
    code+="elif dist>R: continue\n"+dimn*"\t"
    code+="else: nbd.append(point)"
    exec(code,globals(),locals())
    return nbd
    
def migrate(i,j,nbd_lst=None,mig_range=1,max_dist=False):
    '''
    Returns the probability a(i,j) of the point j (!=i) being present in the R-neighbourhood (discrete) of i
    @param i: a point in R^n (array of length n = len(i))
    @param j: a point in R^n (array of length n = len(j))
    @param nbd_lst (optional): the (discrete) neighbourhood of i against which the probability is being computed.
    @param mig_range (optional): if nbd_lst is not set, this is used to compute the range of the neighbourhood of i.
    @param max_dist (optional): if nbd_lst is not set, this is used to determine if max-distance should be used or not while computing the neighbourhood.
    '''
    if nbd_lst: nbd=nbd_lst
    else: nbd=neighbour(i,mig_range,max_dist)
    if j in nbd: return 1/len(nbd)
    else: return 0

def torus_nbd(grid_x, grid_y):
    '''
    Returns the number of distinct neighbours of a point in an (grid_x, grid_y) discrete torus.
    '''
    if grid_x>2 and grid_y>2: return 4
    elif (grid_x>2 and grid_y==2) or (grid_y>2 and grid_x==2): return 3
    elif grid_x==grid_y:
        if grid_x==1: return 0
        else: return 2
    else: return 1
    
def finite_migrate(i,j, grid_x, grid_y):
    '''
    Returns the i,j the entry in the one-step probability kernel of a simple random walk on grid_x by grid_y discrete torus. 
    '''
    valid=False
    if i[0]==j[0]:
        if abs(i[1]-j[1])!=0 and abs(i[1]-j[1]) in [1,grid_y-1] and grid_y>1: valid=True
    elif i[1]==j[1]:
        if abs(i[0]-j[0])!=0 and abs(i[0]-j[0]) in [1,grid_x-1] and grid_x>1: valid=True
    else: return 0
    nbd=torus_nbd(grid_x, grid_y)
    if nbd>0 and valid: return 1/nbd
    else: return 0

def sup_dist(i,j):
    '''Computes the max-distance between the two points i and j'''
    assert len(i)==len(j)
    max_val=0
    for k in range(len(i)):
        val=abs(i[k]-j[k])
        if val > max_val: max_val=val
    return max_val

def euclid_dist(i,j):
    '''Computes the euclidean-distance between the two points i and j'''
    assert len(i)==len(j)
    s=0
    for k in range(len(i)): s+=(i[k]-j[k])**2
    return sqrt(s)
    
def setSeed(seed=None):
    if seed: seedValue=seed
    else: seedValue = random.randrange(sys.maxsize)
    print("Current seed: ",seedValue)
    random.seed(seedValue)
    return seedValue