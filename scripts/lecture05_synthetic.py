#!/usr/bin/env python3
"""Reproduce Lecture 5's scalar AR/subspace comparison; no parameter tuning.

Run from the repository root:
    python3 scripts/lecture05_synthetic.py

Both fits see the same single trajectory. The true rank and fixed lag
length are supplied. Calibration/test are later blocks, not independent
replicates. All 50 seeds, including unstable fits, enter reported summaries.
The two-sided 95% interval is a paired Monte Carlo standard-error interval;
it measures variation over training trajectories, not a general theorem.
"""
import argparse
import hashlib
import json
import platform
from pathlib import Path
import numpy as np
from lecture05_synthetic_plots import write_plots

def trajectory(rng, length):
    innovations = rng.normal(size=length)
    observations = np.empty(length)
    means = np.empty(length)
    state = 0.0
    for t, noise in enumerate(innovations):
        means[t] = state
        observations[t] = state + noise
        state = 0.98 * state + 0.18 * noise
    return observations, means

def fit(z, p=32, q=16):
    x = np.lib.stride_tricks.sliding_window_view(z[:-1], p)[:, ::-1]
    b = np.linalg.lstsq(x, z[p:], rcond=None)[0]
    index = np.add.outer(np.arange(q), np.arange(q))
    h0, h1 = b[index], b[index + 1]
    u, singular, vh = np.linalg.svd(h0, full_matrices=False)
    o = u[:, :1] * np.sqrt(singular[0])
    r = np.sqrt(singular[0]) * vh[:1, :]
    f = (np.linalg.pinv(o) @ h1 @ np.linalg.pinv(r)).item()
    c, ell = o[0, 0], r[0, 0]
    companion = np.zeros((p, p))
    companion[0] = b
    companion[1:, :-1] = np.eye(p - 1)
    radius_ar = float(np.max(np.abs(np.linalg.eigvals(companion))))
    return b, f, c, ell, radius_ar

def prediction_traces(z, b, f, c, ell):
    p = len(b)
    ar = np.zeros(len(z))
    ar[p:] = np.lib.stride_tricks.sliding_window_view(z[:-1], p)[:, ::-1] @ b
    sub = np.empty(len(z))
    state = 0.0
    for t, observation in enumerate(z):
        sub[t] = c * state
        state = f * state + ell * observation
    return ar, sub

def evaluate(z, true_mean, b, f, c, ell, train_stop, cal_len):
    ar, sub = prediction_traces(z, b, f, c, ell)
    calibration = slice(train_stop, train_stop + cal_len)
    test = slice(train_stop + cal_len, len(z))
    metrics = []
    for pred in (ar, sub):
        omega = max(float(np.mean((z[calibration] - pred[calibration]) ** 2)), 1e-8)
        error = float(np.mean((true_mean[test] - pred[test]) ** 2))
        kl = 0.5 * ((1.0 + error) / omega - 1.0 + np.log(omega))
        metrics.append(dict(excess_mse=error, conditional_kl=float(kl), omega=omega))
    return metrics

def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--output-dir", type=Path,
                        default=Path(__file__).resolve().parents[1] / "documents/figures")
    args = parser.parse_args()
    args.output_dir.mkdir(parents=True, exist_ok=True)
    rows, raw = [], []
    example = None
    for n in (256, 1024, 4096):
        trials = []
        for seed in range(50):
            rng = np.random.default_rng(seed)
            z, mu = trajectory(rng, 2000 + n + 2000 + 10000)
            start, stop = 2000, 2000 + n
            b, f, c, ell, radius_ar = fit(z[start:stop])
            ar, sub = evaluate(z, mu, b, f, c, ell, stop, 2000)
            assert all(np.isfinite(x) for result in (ar, sub) for x in result.values())
            trial = dict(n=n, seed=seed, ar=ar, subspace=sub,
                         radius_ar=radius_ar, radius_subspace=abs(f + ell*c),
                         radius_filter=abs(f), coefficients=b.tolist(),
                         f=float(f), c=float(c), ell=float(ell))
            trials.append(trial)
            # Predeclared illustration: first seed, middle training size,
            # first test segment. Do not select a visually favorable run.
            if n == 1024 and seed == 0:
                ar_trace, sub_trace = prediction_traces(z, b, f, c, ell)
                window = slice(stop + 2000, stop + 2000 + 160)
                example = dict(n=n, seed=seed, time=list(range(1, 161)),
                               absolute_start=window.start,
                               observations=z[window].tolist(),
                               true_mean=mu[window].tolist(),
                               ar_mean=ar_trace[window].tolist(),
                               subspace_mean=sub_trace[window].tolist())
        for method in ("ar", "subspace"):
            rows.append(dict(n=n, method=method,
                excess_mse=float(np.mean([t[method]["excess_mse"] for t in trials])),
                conditional_kl=float(np.mean([t[method]["conditional_kl"] for t in trials])),
                omega=float(np.mean([t[method]["omega"] for t in trials])),
                unstable=int(sum(t["radius_ar" if method=="ar" else "radius_subspace"] >= 1 for t in trials)),
                unstable_filter=None if method=="ar" else int(sum(t["radius_filter"] >= 1 for t in trials))))
        differences = np.array([t["subspace"]["excess_mse"]-t["ar"]["excess_mse"] for t in trials])
        print(n, rows[-2:], "paired difference:",
              float(differences.mean()), "+/-", float(1.96*differences.std(ddof=1)/np.sqrt(50)))
        raw.extend(trials)
    output = dict(config=dict(seeds=list(range(50)), p=32, q=16, rank=1,
                      burnin=2000, calibration=2000, test=10000, a=.98, ell=.18,
                      c=1., omega=1., train_sizes=[256, 1024, 4096],
                      example_seed=0, example_n=1024, example_length=160),
                  schema_version=3,
                  environment=dict(python=platform.python_version(), numpy=np.__version__,
                                   platform=platform.platform()),
                  source_sha256={p.name: hashlib.sha256(p.read_bytes()).hexdigest()
                                 for p in (Path(__file__),
                                           Path(__file__).with_name("lecture05_synthetic_plots.py"))},
                  summary=rows, trials=raw, example=example)
    (args.output_dir/"lecture05-synthetic.json").write_text(json.dumps(output, indent=2)+"\n")
    lines = [r"\begin{table}[htbp]", r"\centering\small",
             r"\begin{tabular}{rlrrrr}\toprule",
             r"Training \(T\) & Model & Excess MSE & KL/step & \(\widehat\Omega\) & Unstable / 50\\\midrule"]
    for row in rows:
        name = "AR(32)" if row["method"]=="ar" else "Rank-one state"
        lines.append(f'{row["n"]} & {name} & {row["excess_mse"]:.4f} & '
                     f'{row["conditional_kl"]:.4f} & {row["omega"]:.4f} & {row["unstable"]}' + r"\\")
    lines += [r"\bottomrule\end{tabular}",
              r"\caption{Means over 50 trajectories. Excess MSE compares the fitted",
              r"conditional mean with the true mean; irreducible variance is one.",
              r"Both models estimate \(\widehat\Omega\) on the calibration block; the true",
              r"innovation variance is one. KL uses each fitted variance. Unstable means generative",
              r"spectral radius at least one; such fits are not discarded.}",
              r"\label{tab:l5-synthetic}", r"\end{table}"]
    (args.output_dir/"lecture05-synthetic-results.tex").write_text("\n".join(lines)+"\n")
    write_plots(output, args.output_dir)

if __name__ == "__main__":
    main()
