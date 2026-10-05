#!/usr/bin/env python3
"""Paired long-training, ordinary Legendre ridge, and Gram diagnostics.

Reuses the original data, initialization, Adam updates, and validation rule.
All generated outputs have distinct names from the original experiment.
"""
from __future__ import annotations

import argparse
from concurrent.futures import ProcessPoolExecutor
import csv
import json
import math
import os
from pathlib import Path

# Small dense arrays run efficiently with one BLAS thread per worker.
os.environ.setdefault("OPENBLAS_NUM_THREADS", "1")
os.environ.setdefault("OMP_NUM_THREADS", "1")
os.environ.setdefault("VECLIB_MAXIMUM_THREADS", "1")
import numpy as np

import lecture09_representation_experiment as base

OUT = base.OUT
CONDITIONS = ["redundant", "frozen_relu", "trainable_relu", "poly_mixed_raw"]


def gram_statistics(features: np.ndarray) -> dict[str, float]:
    gram = features @ features.T
    diagonal = np.diag(gram)
    cosine = gram / np.sqrt(np.maximum(diagonal[:, None] * diagonal[None, :], 1e-300))
    off = cosine[~np.eye(len(features), dtype=bool)]
    eigenvalues = np.linalg.eigvalsh(gram)
    cosine_eigenvalues = np.linalg.eigvalsh(cosine)
    return {
        "mean_abs_cosine": float(np.mean(np.abs(off))),
        "max_abs_cosine": float(np.max(np.abs(off))),
        "participation_rank": float(np.trace(gram)**2 / np.sum(gram**2)),
        "cosine_participation_rank": float(np.trace(cosine)**2 / np.sum(cosine**2)),
        "cosine_min_eigenvalue": float(cosine_eigenvalues[0]),
        "cosine_max_eigenvalue": float(cosine_eigenvalues[-1]),
        "gram_min_eigenvalue": float(eigenvalues[0]),
        "gram_max_eigenvalue": float(eigenvalues[-1]),
    }


def linear_paths() -> None:
    paths, selections, grams = [], [], []
    lambdas = np.r_[0.0, np.logspace(-12, 4, 129)]
    specs = [("legendre_equal", p) for p in [4, 8, 12, 20, 40, 80, 164]]
    specs += [("mixed_weighted", 164)]
    for dataset in range(10):
        data = base.make_dataset(dataset)
        for basis, p in specs:
            features = [base.legendre(data[key], p) if basis == "legendre_equal"
                        else base.polynomial_features(data[key], "mixed")
                        for key in ["x_train", "x_validation", "x_test"]]
            train, validation, test = features
            u, s, vt = np.linalg.svd(train, full_matrices=False)
            cutoff = s[0] * max(train.shape) * np.finfo(float).eps
            inverse = np.divide(1.0, s, out=np.zeros_like(s), where=s > cutoff)
            factors = s[:, None] / (s[:, None]**2 + base.N_TRAIN * lambdas[None, :])
            factors[:, 0] = inverse
            coefficients = vt.T @ (factors * (u.T @ data["y_train"]))
            prediction = test @ coefficients
            validation_prediction = validation @ coefficients
            training_prediction = train @ coefficients
            risks = np.mean((prediction - data["y_test"])**2, axis=0)
            validation_losses = np.mean((validation_prediction - data["y_validation"])**2, axis=0)
            train_losses = np.mean((training_prediction - data["y_train"])**2, axis=0)
            residuals = np.max(np.abs(training_prediction - data["y_train"]), axis=0)
            # Exact conditional decomposition, up to the common test-grid integral.
            test_v = test @ vt.T
            noise_cost = base.SIGMA**2 * np.mean(test_v**2, axis=0) @ factors**2
            noiseless = test_v @ (factors * (u.T @ base.target(data["x_train"])))
            bias = np.mean((noiseless - data["y_test"])**2, axis=0)
            local = []
            for j, lam in enumerate(lambdas):
                row = dict(dataset=dataset, basis=basis, p=p, ridge_lambda=float(lam),
                           l2=float(risks[j]), validation_loss=float(validation_losses[j]),
                           training_mse=float(train_losses[j]), maximum_residual=float(residuals[j]),
                           conditional_noise_cost=float(noise_cost[j]), conditional_bias=float(bias[j]))
                paths.append(row)
                local.append(row)
            chosen = dict(local[int(np.argmin(validation_losses))])
            chosen["selection"] = "lambda_with_fixed_p"
            selections.append(chosen)
            gram = dict(dataset=dataset, representation=f"{basis}_{p}", **gram_statistics(train))
            gram["conditional_noise_cost"] = float(noise_cost[0])
            gram["conditional_bias"] = float(bias[0])
            grams.append(gram)
        local = [r for r in selections if r["dataset"] == dataset and r["basis"] == "legendre_equal"]
        chosen = dict(min(local, key=lambda r: r["validation_loss"]))
        chosen["selection"] = "p_and_lambda"
        selections.append(chosen)
        for condition in base.NETWORK_CONDITIONS:
            if condition == "trainable_relu":
                continue
            train, _, _ = base.fixed_features(condition, data)
            grams.append(dict(dataset=dataset, representation=condition, **gram_statistics(train)))
        mixed = base.polynomial_features(data["x_train"], "mixed")
        for name, features in [("mixed_head", mixed[:, :base.M]), ("mixed_tail", mixed[:, base.M:])]:
            grams.append(dict(dataset=dataset, representation=name, **gram_statistics(features)))
    base.write_csv(OUT / "followup-ridge-paths.csv", paths)
    base.write_csv(OUT / "followup-ridge-selected.csv", selections)
    base.write_csv(OUT / "followup-fixed-gram.csv", grams)
    print("Saved ridge paths and fixed-feature Gram diagnostics", flush=True)


def long_run(job: tuple[str, int, int, float, int]) -> dict[str, object]:
    condition, dataset, seed, learning_rate, max_steps = job
    data = base.make_dataset(dataset)
    if condition == "trainable_relu":
        train_x, validation_x, test_x = [data[k] for k in ["x_train", "x_validation", "x_test"]]
    else:
        train_x, validation_x, test_x = base.fixed_features(condition, data)
    model = base.Network(base.NetworkConfig(condition, learning_rate, seed), data)
    optimizer = base.Adam(model, learning_rate)
    best_validation, best_training = math.inf, math.inf
    best_state, best_step = model.state(), 0
    best_late_validation, best_late_state, best_late_step = math.inf, None, None
    plateau_checks = stable_checks = 0
    original_step, original_state, original_best_state, original_best_step = None, None, None, None
    first_stable_step = None
    history, grams = [], []

    def evaluation(state):
        model.load_state(state)
        prediction, _, _ = model.forward(test_x)
        train_prediction, _, _ = model.forward(train_x)
        return dict(l2=base.mse(prediction, data["y_test"]),
                    maximum_residual=float(np.max(np.abs(train_prediction-data["y_train"]))),
                    training_mse=base.mse(train_prediction, data["y_train"]))

    for step in range(1, max_steps+1):
        optimizer.step(model, *model.gradients(train_x, data["y_train"]))
        if step % base.CHECK_EVERY:
            continue
        train_prediction, _, _ = model.forward(train_x)
        validation_prediction, _, _ = model.forward(validation_x)
        train_loss = base.mse(train_prediction, data["y_train"])
        val_loss = base.mse(validation_prediction, data["y_validation"])
        residual = float(np.max(np.abs(train_prediction-data["y_train"])))
        if val_loss < best_validation:
            best_validation, best_state, best_step = val_loss, model.state(), step
        if original_step is not None and val_loss < best_late_validation:
            best_late_validation, best_late_state, best_late_step = val_loss, model.state(), step
        if train_loss < best_training*(1.0-1e-4):
            best_training, plateau_checks = train_loss, 0
        else:
            plateau_checks += 1
        if plateau_checks >= 20:
            optimizer.reduce_learning_rate()
            plateau_checks = 0
        stable_checks = stable_checks+1 if residual <= base.TOLERANCE else 0
        if stable_checks >= 3 and first_stable_step is None:
            first_stable_step = step
        if original_step is None and (stable_checks >= 3 or step == 30000):
            original_step, original_state = step, model.state()
            original_best_state, original_best_step = best_state, best_step
        if step <= 1000 or step % 1000 == 0 or step == original_step or step == first_stable_step:
            pred, _, _ = model.forward(test_x)
            history.append(dict(condition=condition, dataset=dataset, seed=seed, step=step,
                                l2=base.mse(pred, data["y_test"]), validation_loss=val_loss,
                                training_mse=train_loss, maximum_residual=residual,
                                learning_rate=optimizer.learning_rate))
    final_state = model.state()
    row = dict(condition=condition, dataset=dataset, seed=seed, steps=max_steps,
               original_step=original_step, first_stable_step=first_stable_step,
               original_selected_step=original_best_step,
               extended_selected_step=best_step, late_selected_step=best_late_step,
               final_learning_rate=optimizer.learning_rate)
    states = dict(original=original_state, original_selected=original_best_state,
                  final=final_state, extended_selected=best_state, late_selected=best_late_state)
    for name, state in states.items():
        row.update({f"{name}_{key}": value for key, value in evaluation(state).items()})
        if name in ["original", "original_selected", "final"]:
            _, activations, _ = model.forward(train_x)
            features = activations[1] if condition == "trainable_relu" else activations[-2]
            grams.append(dict(condition=condition, dataset=dataset, seed=seed, checkpoint=name,
                              features="extractor" if condition == "trainable_relu" else "penultimate",
                              **gram_statistics(features)))
    return dict(summary=row, history=history, grams=grams)


def extended_training(workers: int, steps: int, rerun: bool = False) -> None:
    rates = json.loads((OUT / "selected-learning-rates.json").read_text())
    jobs = [(c,d,s,rates[c],steps) for c in CONDITIONS for d in range(10) for s in range(2)]
    checkpoint_dir = OUT / "followup-runs"
    checkpoint_dir.mkdir(exist_ok=True)
    results, pending = [], []
    for job in jobs:
        c,d,s,_,_ = job
        path = checkpoint_dir / f"{c}-{d}-{s}-{steps}.json"
        if path.exists() and not rerun:
            results.append(json.loads(path.read_text()))
        else:
            pending.append(job)
    with ProcessPoolExecutor(max_workers=workers) as pool:
        for job, result in zip(pending, pool.map(long_run, pending)):
            c,d,s,_,_ = job
            (checkpoint_dir / f"{c}-{d}-{s}-{steps}.json").write_text(json.dumps(result)+"\n")
            results.append(result)
            row = result["summary"]
            print(c,d,s,"stable",row["first_stable_step"],"original",round(row["original_l2"],5),
                  "final",round(row["final_l2"],5),flush=True)
    base.write_csv(OUT / "followup-long-training.csv", [r["summary"] for r in results])
    base.write_csv(OUT / "followup-long-history.csv", [h for r in results for h in r["history"]])
    base.write_csv(OUT / "followup-learned-gram.csv", [g for r in results for g in r["grams"]])
    (OUT / "followup-metadata.json").write_text(json.dumps(dict(steps=steps,workers=workers,
        conditions=CONDITIONS,datasets=10,seeds=2,description="Continue original Adam trajectory; stop at fixed budget"),indent=2)+"\n")


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--phase", choices=["linear","long","all"], default="all")
    parser.add_argument("--workers", type=int, default=4)
    parser.add_argument("--steps", type=int, default=100000)
    parser.add_argument("--rerun", action="store_true",
                        help="recompute long runs instead of reusing saved per-run results")
    args = parser.parse_args()
    if args.phase in ["linear","all"]:
        linear_paths()
    if args.phase in ["long","all"]:
        extended_training(args.workers,args.steps,args.rerun)
