# Bootstrap

## Dependencies

- Python 3
- numpy/scipy
- pandas
- [powerlaw](https://github.com/jeffalstott/powerlaw)

## Environment

This was run on a SLURM cluster using a Python virtualenv and a good number of CPUs.

## Usage

The usage of the power law bootstrap is:

    python simulate_powerlaw.py [-h] [--trials TRIALS] [--discrete]
                                alpha x_min n n_tail batchid

In addition to the command-line parameters required here, the power law bootstrap requires a copy of the observed lower tail values as a numpy array in the file `BATCHID.npy` (where *BATCHID* is replaced with the actual batch ID, of course).

For lognormal, nothing is required other than:

    python simulate_lognormal.py [-h] [--trials TRIALS] [--discrete]
                                 mu sigma x_min n batchid

Scripts to run these in SLURM (and to generate the lower tail arrays required for the power law) can be generated in the Jupyter notebooks found in the `analysis` directory.

## Output

The output of both scripts is in TSV format. For power law, the columns are:

    batchid, input_alpha, input_x_min, input_n, input_n_tail, result_x_min, result_alpha, result_ks

For lognormal, the columns are:

    batchid, input_mu, input_sigma, x_min, n, result_mu, result_sigma, result_ks

## Notes

The power law bootstrap is slow, as it attempts to fit a power law for every possible truncation point. Lognormal fitting is faster although not as fast as you might hope, since the lognormal random number generation is a bit slower. The scripts will automatically parallelize over as many CPUs as are available.
