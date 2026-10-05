#!/usr/bin/env python3
"""Representation experiments for Lecture 9.

The statistical problem is fixed: X is uniform on [-1,1] and
Y=f*(X)+N(0,sigma^2).  ReLU networks compare redundant, frozen spline,
trainable spline, and polynomial representations.  A development phase tunes
the learning rate from validation loss under a fixed budget.  Confirmatory
runs use fresh datasets.  NumPy is the only dependency.
"""

from __future__ import annotations

import argparse
import csv
import json
import math
import time
from dataclasses import dataclass
from pathlib import Path

import numpy as np


ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / "instructor-materials" / "lecture-plans" / "lecture09-representation-experiment"
SIGMA = 0.28
N_TRAIN = 20
N_VALIDATION = 256
P = 164
M = 4
D = P - M
TOLERANCE = 1e-3
CHECK_EVERY = 50


def target(x: np.ndarray) -> np.ndarray:
    return 0.55 + 0.55 * np.sin(np.pi * x / 2.0) - 0.15 * np.cos(np.pi * x)


def make_dataset(dataset: int) -> dict[str, np.ndarray]:
    rng = np.random.default_rng(910_000 + dataset)
    x_train = np.sort(rng.uniform(-1.0, 1.0, N_TRAIN))[:, None]
    y_train = target(x_train) + rng.normal(0.0, SIGMA, size=(N_TRAIN, 1))
    x_validation = rng.uniform(-1.0, 1.0, N_VALIDATION)[:, None]
    y_validation = target(x_validation) + rng.normal(0.0, SIGMA, size=(N_VALIDATION, 1))
    x_test = np.linspace(-1.0, 1.0, 2001)[:, None]
    return {
        "x_train": x_train,
        "y_train": y_train,
        "x_validation": x_validation,
        "y_validation": y_validation,
        "x_test": x_test,
        "y_test": target(x_test),
    }


def legendre(x: np.ndarray, count: int) -> np.ndarray:
    values = [np.ones_like(x)]
    if count > 1:
        p_prev = np.ones_like(x)
        p_now = x
        values.append(math.sqrt(3.0) * p_now)
        for degree in range(1, count - 1):
            p_next = ((2 * degree + 1) * x * p_now - degree * p_prev) / (degree + 1)
            values.append(math.sqrt(2 * degree + 3) * p_next)
            p_prev, p_now = p_now, p_next
    return np.concatenate(values, axis=1)


def chebyshev(x: np.ndarray, count: int) -> np.ndarray:
    values = [np.ones_like(x)]
    if count > 1:
        t_prev = np.ones_like(x)
        t_now = x
        values.append(math.sqrt(2.0) * t_now)
        for _ in range(1, count - 1):
            t_next = 2.0 * x * t_now - t_prev
            values.append(math.sqrt(2.0) * t_next)
            t_prev, t_now = t_now, t_next
    return np.concatenate(values, axis=1)


def polynomial_features(x: np.ndarray, basis: str) -> np.ndarray:
    if basis == "mixed":
        head = legendre(x, M)
        tail = chebyshev(x, P)[:, M:] / math.sqrt(D)
    elif basis == "legendre":
        all_features = legendre(x, P)
        head, tail = all_features[:, :M], all_features[:, M:] / math.sqrt(D)
    elif basis == "chebyshev":
        all_features = chebyshev(x, P)
        head, tail = all_features[:, :M], all_features[:, M:] / math.sqrt(D)
    else:
        raise ValueError(basis)
    return np.concatenate([head, tail], axis=1)


def fit_standardizer(features: np.ndarray) -> tuple[np.ndarray, np.ndarray]:
    means = np.mean(features, axis=0, keepdims=True)
    scales = np.std(features, axis=0, keepdims=True)
    constant = scales < 1e-12
    means[constant] = 0.0
    scales[constant] = 1.0
    return means, scales


def scalar_standardizer(x: np.ndarray) -> tuple[np.ndarray, np.ndarray]:
    return np.mean(x, axis=0, keepdims=True), np.std(x, axis=0, keepdims=True)


def fixed_features(
    condition: str, data: dict[str, np.ndarray]
) -> tuple[np.ndarray, np.ndarray, np.ndarray]:
    train, validation, test = data["x_train"], data["x_validation"], data["x_test"]
    if condition == "redundant":
        mean, scale = scalar_standardizer(train)
        return tuple(
            np.repeat((array - mean) / scale, P, axis=1) / math.sqrt(P)
            for array in (train, validation, test)
        )
    if condition == "frozen_relu":
        mean, scale = scalar_standardizer(train)
        knots = np.linspace(-1.75, 1.75, P)[None, :]
        signs = np.where(np.arange(P) % 2 == 0, 1.0, -1.0)[None, :]
        return tuple(
            math.sqrt(2.0 / P)
            * np.maximum(signs * ((array - mean) / scale - knots), 0.0)
            for array in (train, validation, test)
        )
    if condition.startswith("poly_"):
        _, basis, preprocessing = condition.split("_")
        arrays = [polynomial_features(array, basis) for array in (train, validation, test)]
        if preprocessing == "standard":
            mean, scale = fit_standardizer(arrays[0])
            arrays = [(array - mean) / scale for array in arrays]
        return tuple(arrays)
    raise ValueError(condition)


@dataclass(frozen=True)
class NetworkConfig:
    condition: str
    learning_rate: float
    seed: int
    width: int = 64


class Network:
    def __init__(self, config: NetworkConfig, data: dict[str, np.ndarray]) -> None:
        self.config = config
        self.trainable_extractor = config.condition == "trainable_relu"
        self.scalar_mean, self.scalar_scale = scalar_standardizer(data["x_train"])
        rng = np.random.default_rng(70_000 + config.seed)
        self.weights: list[np.ndarray] = []
        self.biases: list[np.ndarray] = []
        self.scales: list[float] = []
        self.trainable: list[bool] = []
        if self.trainable_extractor:
            knots = np.linspace(-1.75, 1.75, P)[None, :]
            signs = np.where(np.arange(P) % 2 == 0, 1.0, -1.0)[None, :]
            self.weights.append(signs.copy())
            self.biases.append((-signs * knots).copy())
            self.scales.append(math.sqrt(2.0 / P))
            self.trainable.append(True)
        input_dimension = P
        for fan_in, fan_out in [(input_dimension, config.width), (config.width, config.width), (config.width, 1)]:
            self.weights.append(rng.normal(0.0, math.sqrt(2.0 / fan_in), size=(fan_in, fan_out)))
            self.biases.append(np.zeros((1, fan_out)))
            self.scales.append(1.0)
            self.trainable.append(True)

    def prepare_scalar(self, x: np.ndarray) -> np.ndarray:
        return (x - self.scalar_mean) / self.scalar_scale

    def forward(self, x: np.ndarray) -> tuple[np.ndarray, list[np.ndarray], list[np.ndarray]]:
        values = self.prepare_scalar(x) if self.trainable_extractor else x
        activations = [values]
        preactivations: list[np.ndarray] = []
        for index, (weight, bias, scale) in enumerate(zip(self.weights, self.biases, self.scales)):
            pre = values @ weight + bias
            preactivations.append(pre)
            if index + 1 < len(self.weights):
                values = scale * np.maximum(pre, 0.0)
            else:
                values = pre
            activations.append(values)
        return values, activations, preactivations

    def gradients(self, x: np.ndarray, y: np.ndarray) -> tuple[list[np.ndarray], list[np.ndarray]]:
        prediction, activations, preactivations = self.forward(x)
        delta = (prediction - y) / len(x)
        grad_w = [np.zeros_like(weight) for weight in self.weights]
        grad_b = [np.zeros_like(bias) for bias in self.biases]
        for layer in reversed(range(len(self.weights))):
            grad_w[layer] = activations[layer].T @ delta
            grad_b[layer] = np.sum(delta, axis=0, keepdims=True)
            if layer > 0:
                delta = (delta @ self.weights[layer].T) * self.scales[layer - 1]
                delta *= preactivations[layer - 1] > 0.0
        return grad_w, grad_b

    def state(self) -> tuple[list[np.ndarray], list[np.ndarray]]:
        return [x.copy() for x in self.weights], [x.copy() for x in self.biases]

    def load_state(self, state: tuple[list[np.ndarray], list[np.ndarray]]) -> None:
        self.weights = [x.copy() for x in state[0]]
        self.biases = [x.copy() for x in state[1]]


class Adam:
    def __init__(self, model: Network, learning_rate: float) -> None:
        self.learning_rate = learning_rate
        self.step_number = 0
        self.mw = [np.zeros_like(x) for x in model.weights]
        self.vw = [np.zeros_like(x) for x in model.weights]
        self.mb = [np.zeros_like(x) for x in model.biases]
        self.vb = [np.zeros_like(x) for x in model.biases]

    def reduce_learning_rate(self) -> None:
        self.learning_rate = max(1e-6, 0.3 * self.learning_rate)

    def step(self, model: Network, grad_w: list[np.ndarray], grad_b: list[np.ndarray]) -> None:
        self.step_number += 1
        c1 = 1.0 - 0.9**self.step_number
        c2 = 1.0 - 0.999**self.step_number
        for index, (parameter, gradient) in enumerate(zip(model.weights, grad_w)):
            if not model.trainable[index]:
                continue
            self.mw[index] = 0.9 * self.mw[index] + 0.1 * gradient
            self.vw[index] = 0.999 * self.vw[index] + 0.001 * gradient**2
            parameter -= self.learning_rate * self.mw[index] / c1 / (np.sqrt(self.vw[index] / c2) + 1e-8)
        for index, (parameter, gradient) in enumerate(zip(model.biases, grad_b)):
            if not model.trainable[index]:
                continue
            self.mb[index] = 0.9 * self.mb[index] + 0.1 * gradient
            self.vb[index] = 0.999 * self.vb[index] + 0.001 * gradient**2
            parameter -= self.learning_rate * self.mb[index] / c1 / (np.sqrt(self.vb[index] / c2) + 1e-8)


def mse(prediction: np.ndarray, truth: np.ndarray) -> float:
    return float(np.mean((prediction - truth) ** 2))


def train_network(
    condition: str,
    dataset: int,
    seed: int,
    learning_rate: float,
    max_steps: int,
    width: int,
) -> dict[str, object]:
    data = make_dataset(dataset)
    if condition == "trainable_relu":
        train_x, validation_x, test_x = data["x_train"], data["x_validation"], data["x_test"]
    else:
        train_x, validation_x, test_x = fixed_features(condition, data)
    config = NetworkConfig(condition, learning_rate, seed, width)
    model = Network(config, data)
    optimizer = Adam(model, learning_rate)
    best_validation = math.inf
    best_state = model.state()
    best_step = 0
    best_training = math.inf
    plateau_checks = 0
    stable_checks = 0
    first_interpolation_step: int | None = None
    first_interpolation_state = None
    start = time.perf_counter()
    for step in range(1, max_steps + 1):
        grad_w, grad_b = model.gradients(train_x, data["y_train"])
        optimizer.step(model, grad_w, grad_b)
        if step % CHECK_EVERY:
            continue
        train_prediction, _, _ = model.forward(train_x)
        validation_prediction, _, _ = model.forward(validation_x)
        train_loss = mse(train_prediction, data["y_train"])
        validation_loss = mse(validation_prediction, data["y_validation"])
        maximum_residual = float(np.max(np.abs(train_prediction - data["y_train"])))
        if validation_loss < best_validation:
            best_validation = validation_loss
            best_state = model.state()
            best_step = step
        if train_loss < best_training * (1.0 - 1e-4):
            best_training = train_loss
            plateau_checks = 0
        else:
            plateau_checks += 1
        if plateau_checks >= 20:
            optimizer.reduce_learning_rate()
            plateau_checks = 0
        if maximum_residual <= TOLERANCE:
            stable_checks += 1
            if first_interpolation_step is None:
                first_interpolation_step = step
                first_interpolation_state = model.state()
        else:
            stable_checks = 0
        if stable_checks >= 3:
            break
    final_state = model.state()
    final_step = step

    def evaluate(state: tuple[list[np.ndarray], list[np.ndarray]]) -> tuple[float, float, float]:
        model.load_state(state)
        train_prediction, _, _ = model.forward(train_x)
        test_prediction, _, _ = model.forward(test_x)
        return (
            float(np.max(np.abs(train_prediction - data["y_train"]))),
            mse(test_prediction, data["y_test"]),
            mse(train_prediction, data["y_train"]),
        )

    final_residual, final_l2, final_train_mse = evaluate(final_state)
    validation_residual, validation_l2, _ = evaluate(best_state)
    if first_interpolation_state is not None:
        _, first_l2, _ = evaluate(first_interpolation_state)
    else:
        first_l2 = math.nan
    return {
        "kind": "network",
        "condition": condition,
        "dataset": dataset,
        "seed": seed,
        "width": width,
        "learning_rate": learning_rate,
        "steps": final_step,
        "interpolated": first_interpolation_step is not None,
        "stable_interpolation": stable_checks >= 3,
        "first_interpolation_step": first_interpolation_step,
        "first_interpolation_l2": first_l2,
        "final_maximum_residual": final_residual,
        "final_training_mse": final_train_mse,
        "final_l2": final_l2,
        "validation_selected_step": best_step,
        "validation_selected_maximum_residual": validation_residual,
        "validation_selected_l2": validation_l2,
        "validation_loss": best_validation,
        "elapsed_seconds": time.perf_counter() - start,
    }


def linear_interpolant(condition: str, dataset: int) -> dict[str, object]:
    data = make_dataset(dataset)
    train_x, _, test_x = fixed_features(condition, data)
    coefficients, _, _, singular_values = np.linalg.lstsq(train_x, data["y_train"], rcond=None)
    train_prediction = train_x @ coefficients
    test_prediction = test_x @ coefficients
    return {
        "kind": "linear",
        "condition": condition.replace("poly_", "linear_"),
        "dataset": dataset,
        "seed": -1,
        "width": 0,
        "learning_rate": 0.0,
        "steps": 0,
        "interpolated": bool(np.max(np.abs(train_prediction - data["y_train"])) <= TOLERANCE),
        "stable_interpolation": True,
        "first_interpolation_step": 0,
        "first_interpolation_l2": mse(test_prediction, data["y_test"]),
        "final_maximum_residual": float(np.max(np.abs(train_prediction - data["y_train"]))),
        "final_training_mse": mse(train_prediction, data["y_train"]),
        "final_l2": mse(test_prediction, data["y_test"]),
        "validation_selected_step": 0,
        "validation_selected_maximum_residual": float(np.max(np.abs(train_prediction - data["y_train"]))),
        "validation_selected_l2": mse(test_prediction, data["y_test"]),
        "validation_loss": math.nan,
        "elapsed_seconds": 0.0,
        "minimum_singular_value": float(np.min(singular_values)),
    }


NETWORK_CONDITIONS = [
    "redundant",
    "frozen_relu",
    "trainable_relu",
    "poly_mixed_raw",
    "poly_mixed_standard",
    "poly_legendre_raw",
    "poly_legendre_standard",
    "poly_chebyshev_raw",
    "poly_chebyshev_standard",
]
POLYNOMIAL_CONDITIONS = [condition for condition in NETWORK_CONDITIONS if condition.startswith("poly_")]


def write_csv(path: Path, rows: list[dict[str, object]]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    fieldnames = list(rows[0])
    for row in rows[1:]:
        fieldnames.extend(key for key in row if key not in fieldnames)
    with path.open("w", newline="") as stream:
        writer = csv.DictWriter(stream, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(rows)


def tune(args: argparse.Namespace) -> dict[str, float]:
    rows = []
    selected: dict[str, float] = {}
    for condition in NETWORK_CONDITIONS:
        condition_rows = []
        for learning_rate in args.learning_rates:
            for dataset in range(args.development_datasets):
                result = train_network(condition, -100 - dataset, 0, learning_rate, args.max_steps, args.width)
                rows.append(result)
                condition_rows.append(result)
                print("tune", condition, learning_rate, dataset, result["stable_interpolation"], result["validation_loss"])
        candidates = []
        for learning_rate in args.learning_rates:
            subset = [row for row in condition_rows if row["learning_rate"] == learning_rate]
            stable = sum(bool(row["stable_interpolation"]) for row in subset)
            validation = float(np.median([float(row["validation_loss"]) for row in subset]))
            candidates.append((-stable, validation, learning_rate))
        selected[condition] = min(candidates)[2]
    write_csv(OUT / "development-results.csv", rows)
    (OUT / "selected-learning-rates.json").write_text(json.dumps(selected, indent=2) + "\n")
    return selected


def confirm(args: argparse.Namespace, selected: dict[str, float]) -> list[dict[str, object]]:
    rows = []
    for condition in NETWORK_CONDITIONS:
        for dataset in range(args.datasets):
            for seed in range(args.seeds):
                result = train_network(
                    condition, dataset, seed, selected[condition], args.max_steps, args.width
                )
                rows.append(result)
                print("confirm", condition, dataset, seed, result["stable_interpolation"], result["final_l2"])
    for condition in POLYNOMIAL_CONDITIONS:
        for dataset in range(args.datasets):
            rows.append(linear_interpolant(condition, dataset))
    write_csv(OUT / "confirmatory-results.csv", rows)
    metadata = {
        "sigma": SIGMA,
        "n_train": N_TRAIN,
        "n_validation": N_VALIDATION,
        "feature_dimension": P,
        "head_dimension": M,
        "tail_dimension": D,
        "interpolation_tolerance": TOLERANCE,
        "datasets": args.datasets,
        "seeds": args.seeds,
        "width": args.width,
        "max_steps": args.max_steps,
        "selected_learning_rates": selected,
    }
    (OUT / "metadata.json").write_text(json.dumps(metadata, indent=2) + "\n")
    return rows


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser()
    parser.add_argument("--phase", choices=["pilot", "confirm", "all"], default="all")
    parser.add_argument("--datasets", type=int, default=10)
    parser.add_argument("--seeds", type=int, default=2)
    parser.add_argument("--development-datasets", type=int, default=2)
    parser.add_argument("--width", type=int, default=64)
    parser.add_argument("--max-steps", type=int, default=15000)
    parser.add_argument("--learning-rates", type=float, nargs="+", default=[3e-4, 1e-3, 3e-3])
    return parser.parse_args()


def main() -> None:
    args = parse_args()
    OUT.mkdir(parents=True, exist_ok=True)
    if args.phase == "pilot":
        start = time.perf_counter()
        result = train_network("frozen_relu", -999, 0, 1e-3, args.max_steps, args.width)
        print(json.dumps(result, indent=2))
        print("wall", time.perf_counter() - start)
        return
    if args.phase == "confirm":
        selected = json.loads((OUT / "selected-learning-rates.json").read_text())
        confirm(args, selected)
        return
    selected = tune(args)
    confirm(args, selected)


if __name__ == "__main__":
    main()
