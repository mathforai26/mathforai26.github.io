# Reproducing the Lecture 5 experiment

From the course repository root:

```sh
python3 scripts/lecture05_synthetic.py
python3 scripts/lecture05_completions.py
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

Both predictors also have a separately calibrated Gaussian residual variance.
The summary table now includes its mean over the 50 runs. The AR coefficient
fit itself remains ordinary least squares; this extra estimate supplies the
probability model for log-loss evaluation and generation.
The exact state predictor's population residual variance is 1. Under the
stationary law, the optimal AR(32) value is 1.000000156927612. This is
computed and saved by the completion script, with an independent
autocovariance-regression check in its tests. For a fitted mean, calibration
targets noise variance plus mean-prediction MSE.

## Completion experiments

The completion script reads the saved seed-0, T=1024 fit; it does not refit.
Its common prompt comprises observations 0 through 5023 (warmup, training,
and calibration). The true and fitted state predictors run through this
prefix from zero initial states; AR starts with the last 32 observations.
For three 300-step continuations, use standard normals from
`default_rng(20260916)`, shaped `(3, 300)`, shared across all models.
A corresponding path receives the same fresh standard normal at every
future step, scaled by its model's residual standard deviation. Similar
responses to this shared forcing explain the similar paths throughout
the continuation, including after prompt influence has decayed.

The separate memory comparison uses the known model U~N(0,1), Z=U+W,
W~N(0,1). Supply the prescribed prompt `2 + default_rng(0).normal(size=1000)`.
The center 2 is chosen as an experimental input, not a selected fitted run.
The full-history model uses its exact posterior; the fixed-window comparator
uses the exact ten-observation conditional law, recursively: every AR
coefficient is 1/11, and innovation variance is 12/11. Three 400-step
continuations share a `(3, 400)` normal array from `default_rng(20260917)`.
The full-history path simulation uses sequential Gaussian posterior updates,
equivalent in law to drawing U once from its posterior and holding it fixed.
The true and full-history state laws therefore coincide. Both figures use
the same panel order: (a) conditional means, (b) true continuations,
(c) AR continuations, (d) state-model continuations. In the constant-state
figure, the true and state curves, bands, and coupled paths are identical.
Its ideal next-observation variances after the prompt are 1+1/1001 for the
full-history predictor and 12/11 for the ten-observation predictor.

The fitted comparison exhibits different one-step and long-horizon errors
for one prespecified fitted pair. The known-parameter comparison exhibits
a fixed-window restriction that remains with unlimited training data.

All means and pointwise 95% prediction bands are computed analytically
conditional on the original supplied prompt. They are not Monte Carlo
confidence bands; the three paths are illustrations, not estimates of them.
The script saves `lecture05-completions.json` with full prompts, Gaussian
draws, paths, analytic moments, bands, configuration, versions, source hashes,
and the input JSON hash. It also writes `lecture05-completion-fit.tex` and
`lecture05-completion-memory.tex`.

To redraw the completion figures from saved JSON:

```sh
python3 scripts/lecture05_completion_plots.py
```

Both completion commands accept `--results` and `--output-dir`.
The lecture's Appendix 5.B derives the formulas and specifies both protocols.

Tests:

```sh
python3 scripts/test_lecture05_synthetic.py
python3 scripts/test_lecture05_completions.py
```
