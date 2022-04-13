import argparse
import hashlib
import itertools
import multiprocessing
import numpy as np
import powerlaw
import os

np.seterr(all="ignore") # https://github.com/jeffalstott/powerlaw/issues/25

def simulate_packed(args):
    return simulate(*args)

def simulate(lower_data, dist, x_min, n, n_tail, discrete):
    np.random.seed()
    n_simtail = np.random.choice([0, 1], n, p=[1-n_tail/n, n_tail/n]).sum()
    simdata = np.concatenate((
        np.random.choice(lower_data, n-n_simtail, replace=True),
        dist.generate_random(n_simtail)
    ))
    if discrete:
        simdata = np.round(simdata).astype(int)
    simdata = simdata[simdata > 0] # remove zeros
    results = powerlaw.Fit(simdata, discrete=discrete, estimate_discrete=True, verbose=False)
    return results.xmin, results.power_law.alpha, results.power_law.KS()

def bootstrap_p(batchid, alpha, x_min, n, n_tail, discrete, trials):
    dist = powerlaw.Power_Law(parameters=(alpha,), xmin=x_min, discrete=discrete, estimate_discrete=True)
    lower_data = np.load(batchid + ".npy")
    args = (lower_data, dist, x_min, n, n_tail, discrete)
    
    pool = multiprocessing.Pool()
    results = pool.map(simulate_packed, itertools.repeat(args, trials))
    pool.close()
    for result in results:
        params = [batchid, alpha, x_min, n, n_tail]
        cols = params + list(result)
        print("\t".join(map(str, cols)))

parser = argparse.ArgumentParser()
parser.add_argument("alpha", type=float)
parser.add_argument("x_min", type=float)
parser.add_argument("n", type=int)
parser.add_argument("n_tail", type=int)
parser.add_argument("batchid", type=str)
parser.add_argument("--trials", default=100, type=int)
parser.add_argument("--discrete", default=False, action="store_true")

args = parser.parse_args()

bootstrap_p(args.batchid, args.alpha, args.x_min, args.n, args.n_tail, args.discrete, args.trials)
