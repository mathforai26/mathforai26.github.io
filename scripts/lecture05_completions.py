#!/usr/bin/env python3
"""Reproduce Lecture 5's fitted-model and constant-state completions.

Reads the saved AR/subspace fits; does not refit or select trials.
All bands are exact pointwise Gaussian prediction intervals conditional on
the original prompt. Three paths use shared standard normals across models.
"""
import argparse
import hashlib
import json
import platform
from pathlib import Path
import numpy as np
from lecture05_synthetic import trajectory
from lecture05_completion_plots import write_plots

NORMAL_975 = 1.959963984540054


def scalar_window_variance(a, c, ell, omega, p):
    """Population residual variance given p observations of a stationary model.

    For M_next=a*M+ell*E, Z=c*M+E, E~N(0,omega), start with
    Var(M)=ell**2*omega/(1-a**2) and condition on p successive observations.
    Gaussian conditioning gives P_next=(a-ell*c)**2*P*omega/(c*c*P+omega).
    Assumes abs(a)<1, omega>0, and integer p>=0.
    """
    if not (abs(a) < 1 and omega > 0 and p >= 0 and int(p) == p):
        raise ValueError("Need a stationary model, positive variance, and integer p>=0")
    variance = ell * ell * omega / (1 - a * a)
    f = a - ell * c
    for _ in range(p):
        variance = f * f * variance * omega / (c * c * variance + omega)
    return c * c * variance + omega


def predictor_state(prefix, f, ell):
    state = 0.0
    for z in prefix:
        state = f * state + ell * z
    return state


def scalar_moments(state, a, c, ell, omega, horizon):
    """Future observation means/variances, with current predictive state fixed."""
    mean = np.empty(horizon)
    variance = np.empty(horizon)
    state_variance = 0.0
    for h in range(horizon):
        mean[h] = c * state
        variance[h] = c * c * state_variance + omega
        state = a * state
        state_variance = a * a * state_variance + ell * ell * omega
    return mean, variance


def scalar_paths(state, a, c, ell, omega, normals):
    states = np.full(normals.shape[0], state, dtype=float)
    out = np.empty_like(normals)
    for h in range(normals.shape[1]):
        noise = np.sqrt(omega) * normals[:, h]
        out[:, h] = c * states + noise
        states = a * states + ell * noise
    return out


def ar_moments(prefix, b, omega, horizon):
    b = np.asarray(b)
    history = np.array(prefix[-len(b):][::-1], dtype=float)
    mean = np.empty(horizon)
    impulse = np.zeros(horizon)
    impulse[0] = 1.0
    for h in range(horizon):
        mean[h] = b @ history
        history[1:] = history[:-1].copy()
        history[0] = mean[h]
        if h:
            count = min(h, len(b))
            impulse[h] = b[:count] @ impulse[h-count:h][::-1]
    return mean, omega * np.cumsum(impulse**2)


def ar_paths(prefix, b, omega, normals):
    b = np.asarray(b)
    history = np.tile(np.asarray(prefix[-len(b):][::-1]), (normals.shape[0], 1))
    out = np.empty_like(normals)
    for h in range(normals.shape[1]):
        out[:, h] = history @ b + np.sqrt(omega) * normals[:, h]
        history[:, 1:] = history[:, :-1].copy()
        history[:, 0] = out[:, h]
    return out


def constant_posterior(prefix, tau2=1.0, sigma2=1.0):
    variance = 1.0 / (1.0 / tau2 + len(prefix) / sigma2)
    return variance * float(np.sum(prefix)) / sigma2, variance


def constant_paths(mean, variance, sigma2, normals):
    means = np.full(normals.shape[0], mean, dtype=float)
    out = np.empty_like(normals)
    for h in range(normals.shape[1]):
        total_variance = sigma2 + variance
        residual = np.sqrt(total_variance) * normals[:, h]
        out[:, h] = means + residual
        means += variance / total_variance * residual
        variance *= sigma2 / total_variance
    return out


def record(mean, variance, paths, **parameters):
    sd = np.sqrt(variance)
    return dict(parameters=parameters, mean=mean.tolist(), variance=variance.tolist(),
                lower=(mean-NORMAL_975*sd).tolist(),
                upper=(mean+NORMAL_975*sd).tolist(), paths=paths.tolist())


def fitted_completion(saved):
    cfg = saved["config"]
    n, seed = cfg["example_n"], cfg["example_seed"]
    trial = next(t for t in saved["trials"] if t["n"] == n and t["seed"] == seed)
    stop = cfg["burnin"] + n + cfg["calibration"]
    z, true_mean = trajectory(np.random.default_rng(seed), stop + cfg["test"])
    prefix = z[:stop]
    horizon, paths, future_seed = 300, 3, 20260916
    normals = np.random.default_rng(future_seed).normal(size=(paths, horizon))
    truth = dict(a=cfg["a"], c=cfg["c"], ell=cfg["ell"], omega=cfg["omega"])
    truth_state = predictor_state(prefix, truth["a"]-truth["ell"]*truth["c"],
                                  truth["ell"])
    np.testing.assert_allclose(truth_state * truth["c"], true_mean[stop], atol=1e-12)
    np.testing.assert_allclose(z[stop:stop+160], saved["example"]["observations"])
    fitted = dict(a=trial["f"]+trial["ell"]*trial["c"], c=trial["c"],
                  ell=trial["ell"], omega=trial["subspace"]["omega"])
    fitted_state = predictor_state(prefix, trial["f"], trial["ell"])
    models = {}
    for name, state, params in (("true", truth_state, truth),
                                ("subspace", fitted_state, fitted)):
        mean, variance = scalar_moments(state, horizon=horizon, **params)
        sims = scalar_paths(state, normals=normals, **params)
        models[name] = record(mean, variance, sims, state=state, **params)
    b, omega = trial["coefficients"], trial["ar"]["omega"]
    mean, variance = ar_moments(prefix, b, omega, horizon)
    models["ar"] = record(mean, variance, ar_paths(prefix, b, omega, normals),
                           coefficients=b, omega=omega,
                           spectral_radius=trial["radius_ar"])
    return dict(config=dict(train_size=n, training_seed=seed, prefix_length=stop,
                            horizon=horizon, paths=paths, future_seed=future_seed),
                prefix=prefix.tolist(), standard_normals=normals.tolist(),
                population_reference=dict(full_history_omega=truth["omega"],
                    ar_order=len(b),
                    ar_omega=scalar_window_variance(p=len(b), **truth)),
                models=models)


def memory_completion():
    n, p, horizon = 1000, 10, 400
    prefix_seed, future_seed = 0, 20260917
    # A prescribed prompt, centered at 2; future laws use the N(0,1) prior.
    prefix = 2.0 + np.random.default_rng(prefix_seed).normal(size=n)
    normals = np.random.default_rng(future_seed).normal(size=(3, horizon))
    mean, variance = constant_posterior(prefix)
    state = record(np.full(horizon, mean), np.full(horizon, 1.0+variance),
                   constant_paths(mean, variance, 1.0, normals),
                   posterior_mean=mean, posterior_variance=variance)
    window_variance = 1.0 / (1.0+p)
    b = np.full(p, window_variance)
    omega = 1.0 + window_variance
    ar_mean, ar_variance = ar_moments(prefix, b, omega, horizon)
    ar = record(ar_mean, ar_variance, ar_paths(prefix, b, omega, normals),
                coefficients=b.tolist(), omega=omega)
    return dict(config=dict(prefix_length=n, p=p, horizon=horizon, paths=3,
                            prefix_center=2.0, prefix_seed=prefix_seed,
                            future_seed=future_seed, tau2=1.0, sigma2=1.0),
                prefix=prefix.tolist(), standard_normals=normals.tolist(),
                models=dict(true=state, state=state, ar=ar))


def main():
    root = Path(__file__).resolve().parents[1]
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--results", type=Path,
                        default=root / "documents/figures/lecture05-synthetic.json")
    parser.add_argument("--output-dir", type=Path, default=root / "documents/figures")
    args = parser.parse_args()
    saved = json.loads(args.results.read_text())
    sources = ["lecture05_completions.py", "lecture05_completion_plots.py",
               "lecture05_synthetic.py", "lecture05_synthetic_plots.py"]
    result = dict(schema_version=2, normal_975=NORMAL_975,
                  input_sha256=hashlib.sha256(args.results.read_bytes()).hexdigest(),
                  source_sha256={name: hashlib.sha256(
                      (Path(__file__).parent/name).read_bytes()).hexdigest()
                      for name in sources},
                  environment=dict(python=platform.python_version(), numpy=np.__version__,
                                   platform=platform.platform()),
                  fitted=fitted_completion(saved), memory=memory_completion())
    args.output_dir.mkdir(parents=True, exist_ok=True)
    (args.output_dir / "lecture05-completions.json").write_text(
        json.dumps(result, indent=2, allow_nan=False)+"\n")
    write_plots(result, args.output_dir)
    for case in ("fitted", "memory"):
        for name, model in result[case]["models"].items():
            print(case, name, "first/last mean:", model["mean"][0], model["mean"][-1],
                  "first/last variance:", model["variance"][0], model["variance"][-1])


if __name__ == "__main__":
    main()
