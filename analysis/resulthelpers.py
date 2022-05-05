import glob
import hashlib
import io
import pandas


def load_basic_results(pattern):
    files = glob.glob(pattern)
    dfs = [ pandas.read_table(file) for file in files ]
    return pandas.concat(dfs)

def load_simulation_results(filename):
    return pandas.read_table(filename, header=None,
                            names=["batchid", "alpha", "x_min", "n", "n_tail",
                                  "fit_xmin", "fit_alpha", "fit_ks"])

def load_lognormal_simulation_results(filename):
    return pandas.read_table(filename, header=None,
                            names=["batchid", "mu", "sigma", "x_min", "n",
                                  "fit_mu", "fit_sigma", "fit_ks"])

def join_results(basic_results, sim_results, ks_col="ks"):
    results = basic_results.set_index("batchid")
    
    joined_df = results.merge(sim_results, left_index=True, right_on="batchid", how="inner")
    results["bootstrap_n"] = joined_df.groupby("batchid").size()
    results["bootstrap_n"] = results["bootstrap_n"].fillna(0).astype(int)
    results["bootstrap_gt"] = joined_df[joined_df["fit_ks"] > joined_df[ks_col]].groupby("batchid").size()
    results["bootstrap_gt"] = results["bootstrap_gt"].fillna(0).astype(int)
    results["bootstrap_p"] = results["bootstrap_gt"] / results["bootstrap_n"]
    
    return results

def batch_id(**args):    
    # We changed names at one point, but we want to keep the hashes the same.
    # It's much faster to write this than to rerun the bootstrapping.
    # Oops.
    original_names = {
        "CCA Tract, 1990/2000": "CCA Original",
        "CCA Tract": "CCA Original, 2010 Data",
        "Census CBSA": "Census MSAs",
        "Census CBSA, 1990": "Census MSAs, 1990 Data",
        "Census CBSA, 2000": "Census MSAs, 2000 Data",
        "Census UA/UC": "Census Urban Areas",
        "Census Place": "Census Places",
        "CCA Street Network": "Natural Cities"
    }
    
    if args["name"] in original_names:
        name = original_names[args["name"]]
    else:
        name = args["name"]
    
    # It seems when reading CSV from pandas, we lose precision slightly or something.
    # See, for example: https://github.com/pandas-dev/pandas/issues/2697
    # This is unbelievably ugly, but we must go through the same ugly process here that we used in the past
    # in order to make our hashes line up.
    fake_csv = "alpha\tx_min\tn\tn_tail\n"
    fake_csv += "\t".join(map(str, [args["alpha"], args["x_min"], args["n"], args["n_tail"]]))
    df = pandas.read_table(io.StringIO(fake_csv))
    
    items = [str(a) for a in [name, args["col"], df["alpha"].item(), df["x_min"].item(), df["n"].item(), df["n_tail"].item()]]
    return hashlib.md5("\n".join(items).encode("utf-8")).hexdigest()

def lognormal_batch_id(**args):
    # By the time we did lognormal stuff, we wisened up and no longer need all the hacks we used on the powerlaw IDs.
    items = [str(a) for a in [args["name"], args["col"], args["mu"], args["sigma"], args["x_min"], args["n"]]]
    return hashlib.md5("\n".join(items).encode("utf-8")).hexdigest()
