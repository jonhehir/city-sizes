# Blatant copy-and-paste job from simulate_powerlaw.py.

import argparse
import hashlib
import itertools
import multiprocessing
import numpy as np
import powerlaw

np.seterr(all="ignore") # https://github.com/jeffalstott/powerlaw/issues/25

def simulate_packed(args):
    return simulate(*args)

def simulate(dist, x_min, n, discrete):
    np.random.seed()
    
    # generate random data from dist
    simdata = np.array([])
    while len(simdata) < n:
        simdata = np.append(simdata, dist.generate_random(min(1000, n-len(simdata))))
    if discrete:
        simdata = np.round(simdata).astype(int)
    simdata = simdata[simdata > 0] # remove zeros
    
    # fit a truncated powerlaw on simulated data
    fitted = powerlaw.Lognormal(data=simdata, xmin=x_min)
    ks = fitted.KS(simdata)
    
    # return fitted params and KS
    return fitted.mu, fitted.sigma, ks

def bootstrap_p(batchid, mu, sigma, x_min, n, discrete, trials):
    dist = powerlaw.Lognormal(parameters=[mu, sigma], xmin=x_min, discrete=False) # discrete=True is too slow
    args = (dist, x_min, n, discrete)
    
    pool = multiprocessing.Pool()
    results = pool.map(simulate_packed, itertools.repeat(args, trials))
    pool.close()
    for result in results:
        params = [batchid, mu, sigma, x_min, n]
        cols = params + list(result)
        print("\t".join(map(str, cols)))

parser = argparse.ArgumentParser()
parser.add_argument("mu", type=float)
parser.add_argument("sigma", type=float)
parser.add_argument("x_min", type=float)
parser.add_argument("n", type=int)
parser.add_argument("batchid", type=str)
parser.add_argument("--trials", default=100, type=int)
parser.add_argument("--discrete", default=False, action="store_true")

args = parser.parse_args()

bootstrap_p(args.batchid, args.mu, args.sigma, args.x_min, args.n, args.discrete, args.trials)
