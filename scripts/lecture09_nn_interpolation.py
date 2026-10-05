#!/usr/bin/env python3
"""Neural-network interpolation experiment for Lecture 9.

The experiment uses the data and target from Figure 1 of Lecture 9.  It trains
one- and two-hidden-layer tanh or ReLU networks by full-batch Adam, records
when each run first interpolates, and evaluates population L2 error on a dense
grid.  Only NumPy is required.
"""

from __future__ import annotations

import argparse
import csv
import json
import math
import random
import time
from dataclasses import asdict, dataclass
from pathlib import Path

import numpy as np


ROOT = Path(__file__).resolve().parents[1]
OUT_DIR = ROOT / "instructor-materials" / "lecture-plans" / "lecture09-nn-experiment"

DATA_SEED = 9
N = 20
SIGMA = 0.28
GRID_SIZE = 4001
INTERPOLATION_TOLERANCE = 1e-3


def target(x: np.ndarray) -> np.ndarray:
    return 0.55 + 0.55 * np.sin(np.pi * x / 2.0) - 0.15 * np.cos(np.pi * x)


def make_data() -> tuple[np.ndarray, np.ndarray, np.ndarray, np.ndarray]:
    """Reproduce the sample used by scripts/lecture09_interpolants.py."""
    rng = random.Random(DATA_SEED)
    x = np.array(sorted(rng.uniform(-0.96, 0.96) for _ in range(N)), dtype=np.float64)
    y = np.array([float(target(np.array(value))) + rng.gauss(0.0, SIGMA) for value in x])
    grid = np.linspace(-1.0, 1.0, GRID_SIZE, dtype=np.float64)
    return x[:, None], y[:, None], grid[:, None], target(grid)[:, None]


@dataclass(frozen=True)
class Configuration:
    depth: int
    width: int
    learning_rate: float
    init_scale: float
    seed: int
    activation: str = "tanh"

    @property
    def parameter_count(self) -> int:
        sizes = [1] + [self.width] * self.depth + [1]
        return sum(sizes[i] * sizes[i + 1] + sizes[i + 1] for i in range(len(sizes) - 1))

    @property
    def name(self) -> str:
        lr = f"{self.learning_rate:g}".replace(".", "p")
        scale = f"{self.init_scale:g}".replace(".", "p")
        prefix = "" if self.activation == "tanh" else f"{self.activation}_"
        return f"{prefix}d{self.depth}_w{self.width}_lr{lr}_s{scale}_seed{self.seed}"


class MLP:
    def __init__(self, config: Configuration) -> None:
        self.config = config
        rng = np.random.default_rng(config.seed)
        sizes = [1] + [config.width] * config.depth + [1]
        self.weights: list[np.ndarray] = []
        self.biases: list[np.ndarray] = []
        for fan_in, fan_out in zip(sizes[:-1], sizes[1:]):
            bound = config.init_scale / math.sqrt(fan_in)
            self.weights.append(rng.uniform(-bound, bound, size=(fan_in, fan_out)))
            self.biases.append(rng.uniform(-bound, bound, size=(1, fan_out)))

    def forward(self, x: np.ndarray) -> tuple[np.ndarray, list[np.ndarray]]:
        activations = [x]
        value = x
        for layer, (weight, bias) in enumerate(zip(self.weights, self.biases)):
            value = value @ weight + bias
            if layer + 1 < len(self.weights):
                if self.config.activation == "tanh":
                    value = np.tanh(value)
                elif self.config.activation == "relu":
                    value = np.maximum(value, 0.0)
                else:
                    raise ValueError(f"unsupported activation: {self.config.activation}")
            activations.append(value)
        return value, activations

    def gradients(
        self, x: np.ndarray, y: np.ndarray
    ) -> tuple[float, list[np.ndarray], list[np.ndarray]]:
        prediction, activations = self.forward(x)
        residual = prediction - y
        loss = 0.5 * float(np.mean(residual**2))
        delta = residual / len(x)
        grad_weights: list[np.ndarray] = [np.empty_like(weight) for weight in self.weights]
        grad_biases: list[np.ndarray] = [np.empty_like(bias) for bias in self.biases]
        for layer in reversed(range(len(self.weights))):
            grad_weights[layer] = activations[layer].T @ delta
            grad_biases[layer] = np.sum(delta, axis=0, keepdims=True)
            if layer > 0:
                if self.config.activation == "tanh":
                    derivative = 1.0 - activations[layer] ** 2
                else:
                    derivative = activations[layer] > 0.0
                delta = (delta @ self.weights[layer].T) * derivative
        return loss, grad_weights, grad_biases


# Preserve the name used by the existing tanh report-asset generator.
TanhMLP = MLP


class Adam:
    def __init__(
        self,
        model: MLP,
        learning_rate: float,
        beta1: float = 0.9,
        beta2: float = 0.999,
        epsilon: float = 1e-8,
    ) -> None:
        self.learning_rate = learning_rate
        self.beta1 = beta1
        self.beta2 = beta2
        self.epsilon = epsilon
        self.step_number = 0
        self.mw = [np.zeros_like(weight) for weight in model.weights]
        self.vw = [np.zeros_like(weight) for weight in model.weights]
        self.mb = [np.zeros_like(bias) for bias in model.biases]
        self.vb = [np.zeros_like(bias) for bias in model.biases]

    def step(
        self,
        model: MLP,
        grad_weights: list[np.ndarray],
        grad_biases: list[np.ndarray],
    ) -> None:
        self.step_number += 1
        correction1 = 1.0 - self.beta1**self.step_number
        correction2 = 1.0 - self.beta2**self.step_number
        for index, (parameter, gradient) in enumerate(zip(model.weights, grad_weights)):
            self.mw[index] = self.beta1 * self.mw[index] + (1.0 - self.beta1) * gradient
            self.vw[index] = self.beta2 * self.vw[index] + (1.0 - self.beta2) * gradient**2
            parameter -= self.learning_rate * (self.mw[index] / correction1) / (
                np.sqrt(self.vw[index] / correction2) + self.epsilon
            )
        for index, (parameter, gradient) in enumerate(zip(model.biases, grad_biases)):
            self.mb[index] = self.beta1 * self.mb[index] + (1.0 - self.beta1) * gradient
            self.vb[index] = self.beta2 * self.vb[index] + (1.0 - self.beta2) * gradient**2
            parameter -= self.learning_rate * (self.mb[index] / correction1) / (
                np.sqrt(self.vb[index] / correction2) + self.epsilon
            )


def metrics(
    model: MLP,
    x: np.ndarray,
    y: np.ndarray,
    grid: np.ndarray,
    truth: np.ndarray,
) -> dict[str, float]:
    train_prediction, _ = model.forward(x)
    grid_prediction, _ = model.forward(grid)
    residual = train_prediction - y
    return {
        "training_mse": float(np.mean(residual**2)),
        "maximum_training_residual": float(np.max(np.abs(residual))),
        "l2_error": float(np.mean((grid_prediction - truth) ** 2)),
        "prediction_minimum": float(np.min(grid_prediction)),
        "prediction_maximum": float(np.max(grid_prediction)),
    }


def train(
    config: Configuration,
    max_steps: int,
    post_interpolation_steps: int,
    checkpoint_steps: set[int],
) -> tuple[dict[str, object], list[dict[str, float]], np.ndarray]:
    x, y, grid, truth = make_data()
    model = MLP(config)
    optimizer = Adam(model, config.learning_rate)
    history: list[dict[str, float]] = []
    first_interpolation_step: int | None = None
    first_interpolation_values: dict[str, float] | None = None
    stop_step = max_steps

    def record(step: int) -> dict[str, float]:
        values = metrics(model, x, y, grid, truth)
        row = {"step": float(step), **values}
        history.append(row)
        return values

    initial = record(0)
    if initial["maximum_training_residual"] <= INTERPOLATION_TOLERANCE:
        first_interpolation_step = 0
        first_interpolation_values = initial
        stop_step = min(stop_step, post_interpolation_steps)

    start = time.perf_counter()
    for step in range(1, max_steps + 1):
        _, grad_weights, grad_biases = model.gradients(x, y)
        optimizer.step(model, grad_weights, grad_biases)

        should_check = step in checkpoint_steps or step % 100 == 0 or step == stop_step
        if should_check:
            values = metrics(model, x, y, grid, truth)
            if first_interpolation_step is None and values["maximum_training_residual"] <= INTERPOLATION_TOLERANCE:
                first_interpolation_step = step
                first_interpolation_values = values
                stop_step = min(max_steps, step + post_interpolation_steps)
                if not history or int(history[-1]["step"]) != step:
                    history.append({"step": float(step), **values})
            if step in checkpoint_steps or step == stop_step:
                if not history or int(history[-1]["step"]) != step:
                    history.append({"step": float(step), **values})
        if step >= stop_step:
            break

    final_values = metrics(model, x, y, grid, truth)
    if not history or int(history[-1]["step"]) != step:
        history.append({"step": float(step), **final_values})
    grid_prediction, _ = model.forward(grid)
    result: dict[str, object] = {
        **asdict(config),
        "name": config.name,
        "parameter_count": config.parameter_count,
        "steps": step,
        "first_interpolation_step": first_interpolation_step,
        "interpolated": first_interpolation_step is not None,
        "final_interpolates": final_values["maximum_training_residual"] <= INTERPOLATION_TOLERANCE,
        "first_interpolation_l2_error": (
            first_interpolation_values["l2_error"] if first_interpolation_values is not None else None
        ),
        "first_interpolation_training_mse": (
            first_interpolation_values["training_mse"] if first_interpolation_values is not None else None
        ),
        "elapsed_seconds": time.perf_counter() - start,
        **final_values,
    }
    best_record = min(history, key=lambda row: row["l2_error"])
    result["minimum_recorded_l2_error"] = best_record["l2_error"]
    result["minimum_recorded_l2_step"] = int(best_record["step"])
    return result, history, grid_prediction[:, 0]


def write_rows(path: Path, rows: list[dict[str, object]]) -> None:
    if not rows:
        return
    fieldnames = list(rows[0].keys())
    with path.open("w", newline="") as stream:
        writer = csv.DictWriter(stream, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(rows)


def run_pilot(args: argparse.Namespace) -> None:
    out_dir = output_directory(args.activation)
    config = Configuration(
        depth=args.depth,
        width=args.width,
        learning_rate=args.learning_rate,
        init_scale=args.init_scale,
        seed=args.seed,
        activation=args.activation,
    )
    checkpoints = {0, 10, 30, 100, 300, 1000, 3000, 10000, 30000, args.max_steps}
    result, history, prediction = train(
        config,
        max_steps=args.max_steps,
        post_interpolation_steps=args.post_interpolation_steps,
        checkpoint_steps=checkpoints,
    )
    out_dir.mkdir(parents=True, exist_ok=True)
    write_rows(out_dir / "pilot-history.csv", history)
    x, y, grid, truth = make_data()
    write_rows(
        out_dir / "pilot-fit.csv",
        [
            {
                "x": float(grid[index, 0]),
                "truth": float(truth[index, 0]),
                "prediction": float(prediction[index]),
            }
            for index in range(len(grid))
        ],
    )
    write_rows(
        out_dir / "training-data.csv",
        [{"x": float(xi), "y": float(yi)} for xi, yi in zip(x[:, 0], y[:, 0])],
    )
    (out_dir / "pilot-result.json").write_text(json.dumps(result, indent=2) + "\n")
    print(json.dumps(result, indent=2))


def hyperparameter_key(result: dict[str, object]) -> tuple[int, int, float, float]:
    return (
        int(result["depth"]),
        int(result["width"]),
        float(result["learning_rate"]),
        float(result["init_scale"]),
    )


def output_directory(activation: str) -> Path:
    if activation == "tanh":
        return OUT_DIR
    return ROOT / "instructor-materials" / "lecture-plans" / f"lecture09-{activation}-experiment"


def run_grid(args: argparse.Namespace) -> None:
    out_dir = output_directory(args.activation)
    out_dir.mkdir(parents=True, exist_ok=True)
    checkpoint_steps = {0, 10, 30, 100, 300, 1000, 3000, 10000, 30000, args.max_steps}
    widths = {1: [16, 32, 64, 128, 256], 2: [8, 16, 32, 64, 128]}
    learning_rates = [1e-3, 3e-3, 1e-2]
    init_scales = [0.5, 1.0, 2.0]

    coarse_results: list[dict[str, object]] = []
    total = sum(len(values) for values in widths.values()) * len(learning_rates) * len(init_scales)
    completed = 0
    for depth, depth_widths in widths.items():
        for width in depth_widths:
            for learning_rate in learning_rates:
                for init_scale in init_scales:
                    config = Configuration(
                        depth, width, learning_rate, init_scale, 0, args.activation
                    )
                    result, _, _ = train(
                        config,
                        max_steps=args.max_steps,
                        post_interpolation_steps=args.post_interpolation_steps,
                        checkpoint_steps=checkpoint_steps,
                    )
                    coarse_results.append(result)
                    completed += 1
                    print(
                        f"coarse {completed:3d}/{total}: {config.name} "
                        f"interp={result['final_interpolates']} L2={float(result['l2_error']):.5f}",
                        flush=True,
                    )
    write_rows(out_dir / "coarse-results.csv", coarse_results)

    eligible = [result for result in coarse_results if bool(result["final_interpolates"])]
    if not eligible:
        raise RuntimeError("No coarse configuration interpolated at the final iterate")
    eligible.sort(key=lambda result: float(result["l2_error"]))
    selected_keys = [hyperparameter_key(result) for result in eligible[: args.top_configurations]]

    replicated_results: list[dict[str, object]] = []
    saved_runs: dict[str, tuple[list[dict[str, float]], np.ndarray]] = {}
    for depth, width, learning_rate, init_scale in selected_keys:
        for seed in range(args.replicates):
            config = Configuration(
                depth, width, learning_rate, init_scale, seed, args.activation
            )
            result, history, prediction = train(
                config,
                max_steps=args.max_steps,
                post_interpolation_steps=args.post_interpolation_steps,
                checkpoint_steps=checkpoint_steps,
            )
            replicated_results.append(result)
            saved_runs[config.name] = (history, prediction)
            print(
                f"replicate {config.name}: interp={result['final_interpolates']} "
                f"L2={float(result['l2_error']):.5f}",
                flush=True,
            )
    write_rows(out_dir / "replicated-results.csv", replicated_results)

    grouped: dict[tuple[int, int, float, float], list[dict[str, object]]] = {}
    for result in replicated_results:
        grouped.setdefault(hyperparameter_key(result), []).append(result)
    summaries: list[dict[str, object]] = []
    for key, results in grouped.items():
        final_errors = [float(result["l2_error"]) for result in results if bool(result["final_interpolates"])]
        first_errors = [
            float(result["first_interpolation_l2_error"])
            for result in results
            if result["first_interpolation_l2_error"] is not None
        ]
        summaries.append(
            {
                "depth": key[0],
                "width": key[1],
                "learning_rate": key[2],
                "init_scale": key[3],
                "parameter_count": results[0]["parameter_count"],
                "replicates": len(results),
                "final_interpolation_fraction": len(final_errors) / len(results),
                "median_final_l2_error": float(np.median(final_errors)) if final_errors else None,
                "minimum_final_l2_error": min(final_errors) if final_errors else None,
                "maximum_final_l2_error": max(final_errors) if final_errors else None,
                "median_first_interpolation_l2_error": float(np.median(first_errors)) if first_errors else None,
            }
        )
    summaries.sort(
        key=lambda row: (
            -float(row["final_interpolation_fraction"]),
            float(row["median_final_l2_error"]) if row["median_final_l2_error"] is not None else math.inf,
        )
    )
    write_rows(out_dir / "configuration-summaries.csv", summaries)

    successful_runs = [result for result in replicated_results if bool(result["final_interpolates"])]
    successful_runs.sort(key=lambda result: float(result["l2_error"]))
    if not successful_runs:
        raise RuntimeError("No replicated run interpolated at the final iterate")
    best_result = successful_runs[0]
    best_history, best_prediction = saved_runs[str(best_result["name"])]
    write_rows(out_dir / "best-history.csv", best_history)
    x, y, grid, truth = make_data()
    write_rows(
        out_dir / "best-fit.csv",
        [
            {
                "x": float(grid[index, 0]),
                "truth": float(truth[index, 0]),
                "prediction": float(best_prediction[index]),
            }
            for index in range(len(grid))
        ],
    )
    write_rows(
        out_dir / "training-data.csv",
        [{"x": float(xi), "y": float(yi)} for xi, yi in zip(x[:, 0], y[:, 0])],
    )
    metadata = {
        "activation": args.activation,
        "data_seed": DATA_SEED,
        "sample_size": N,
        "noise_standard_deviation": SIGMA,
        "grid_size": GRID_SIZE,
        "interpolation_tolerance": INTERPOLATION_TOLERANCE,
        "max_steps": args.max_steps,
        "post_interpolation_steps": args.post_interpolation_steps,
        "coarse_seed": 0,
        "coarse_configurations": len(coarse_results),
        "selected_configurations": len(selected_keys),
        "replicates": args.replicates,
        "best_run": best_result,
        "best_configuration_by_median": summaries[0],
    }
    (out_dir / "search-metadata.json").write_text(json.dumps(metadata, indent=2) + "\n")
    print(json.dumps(metadata, indent=2))


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser()
    parser.add_argument("--pilot", action="store_true")
    parser.add_argument("--grid", action="store_true")
    parser.add_argument("--depth", type=int, default=2)
    parser.add_argument("--width", type=int, default=64)
    parser.add_argument("--learning-rate", type=float, default=3e-3)
    parser.add_argument("--init-scale", type=float, default=1.0)
    parser.add_argument("--seed", type=int, default=0)
    parser.add_argument("--max-steps", type=int, default=60000)
    parser.add_argument("--post-interpolation-steps", type=int, default=10000)
    parser.add_argument("--top-configurations", type=int, default=8)
    parser.add_argument("--replicates", type=int, default=5)
    parser.add_argument("--activation", choices=("tanh", "relu"), default="tanh")
    return parser.parse_args()


def main() -> None:
    args = parse_args()
    if args.pilot:
        run_pilot(args)
        return
    if args.grid:
        run_grid(args)
        return
    raise SystemExit("Choose --pilot or --grid.")


if __name__ == "__main__":
    main()
