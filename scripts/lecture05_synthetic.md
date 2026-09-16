# Reproducing the Lecture 5 experiment

From the course repository root:

```sh
python3 scripts/lecture05_synthetic.py
python3 scripts/build_lecture_notes.py documents/scribes/lecture05.tex
```

The experiment needs Python 3.9+ and NumPy. This run used Python 3.9.6 and
NumPy 1.22.0; the JSON records the actual Python/NumPy/platform versions and
SHA-256 hashes of both experiment source files. Rendering uses the existing
LaTeX build and PGFPlots (compatibility level 1.18), not Matplotlib.
On the instructor's Mac, `/usr/bin/python3` is the interpreter with NumPy.
Different NumPy/BLAS versions can change floating-point rounding; the seeds
do not imply byte-identical numerical results across platforms.

The experiment writes three persistent artifacts under `documents/figures/`:

- `lecture05-synthetic.json`: configuration, all 150 fits and metrics,
  fitted coefficients/matrices, one predeclared trajectory segment, and
  environment/source provenance.
- `lecture05-synthetic-results.tex`: the summary table computed from those fits.
- `lecture05-synthetic-plots.tex`: vector plots generated from the saved values.

To regenerate the plots from the saved JSON without rerunning the experiment:

```sh
python3 scripts/lecture05_synthetic_plots.py
```

Both commands accept `--output-dir`; the plotting command also accepts
`--results` to read another saved experiment. No random fitting occurs in
the plotting program. Do not edit generated tables or plot coordinates by hand.

## Design and interpretation

For every training size 256, 1024, and 4096, seeds 0 through 49 generate a
single innovations trajectory. The initial state is zero. A 2000-step warmup
precedes the training block; 2000 calibration steps and 10000 test steps
follow it. Both models see the same observations. Parameter fitting uses
only the training block; predictive states are propagated through the prefix.
The supplied AR order is 32, Hankel block count 16, and retained rank one.
There is no hyperparameter tuning or rejection of unstable fits.

Covariances are estimated on the calibration continuation. Test excess MSE
compares the fitted conditional mean with the known true conditional mean;
it excludes the irreducible innovation variance of one. Conditional KL uses
each fitted calibration variance and the exact scalar Gaussian formula.
Stability of the predictive recursion and of the generative model are
recorded separately. Consecutive blocks of one trajectory are not independent.

The trajectory plot is fixed to seed 0, training size 1024, and the first
160 test steps. It was not selected by its measured error. The figure shows
conditional predictions on a common observed history, not free-running
samples. Its lag-coefficient plot uses the same fitted models. The risk
scatter includes all 150 runs and marks unstable state-space generators.
The table and scatter include the small-sample failures.

Tests:

```sh
python3 scripts/test_lecture05_synthetic.py
```
