#!/usr/bin/env python3
"""Fast numerical and saved-evidence checks for the consolidated Lecture 9 study."""
from __future__ import annotations

import csv
import json
import os
import unittest

for variable in ("OPENBLAS_NUM_THREADS", "OMP_NUM_THREADS", "VECLIB_MAXIMUM_THREADS"):
    os.environ[variable] = "1"

import numpy as np
import lecture09_nn_interpolation as initial
import lecture09_representation_experiment as representation
import lecture09_auxiliary_report_assets as auxiliary


def rows(path):
    with path.open(newline="") as stream:
        return list(csv.DictReader(stream))


class ExperimentChecks(unittest.TestCase):
    def test_auxiliary_coverage(self):
        tables, coverage = auxiliary.make_tables()
        self.assertEqual(coverage, {
            "tanh": {"coarse": 90, "repeated": 40},
            "ReLU": {"coarse": 90, "repeated": 20},
            "development": 54, "confirmatory": 240,
            "fixed_gram": 180, "learned_gram": 240, "long": 80,
            "ridge_paths": 10400, "ridge_selected": 90, "long_history": 9550,
            "table_rows": {"coarse": 20, "repeated": 12, "pilots": 2,
                           "development": 9, "confirmatory": 15,
                           "fixed-gram": 18, "learned-gram": 12, "long": 4},
        })
        for name, expected in tables.items():
            self.assertEqual((representation.OUT / f"auxiliary-{name}-table.tex").read_text(), expected)

    def check_gradients(self, model, gradients, loss):
        step = 1e-6
        for parameters, derivatives in zip((model.weights, model.biases), gradients):
            for parameter, derivative in zip(parameters, derivatives):
                for position in sorted({0, parameter.size // 2, parameter.size - 1}):
                    index = np.unravel_index(position, parameter.shape)
                    original = parameter[index]
                    parameter[index] = original + step
                    upper = loss()
                    parameter[index] = original - step
                    lower = loss()
                    parameter[index] = original
                    self.assertAlmostEqual((upper - lower) / (2 * step), derivative[index], delta=2e-7)

    def test_initial_gradients(self):
        x, y, _, _ = initial.make_data()
        for activation in ("tanh", "relu"):
            model = initial.MLP(initial.Configuration(2, 8, 0.001, 1.0, 3, activation))
            _, weight_gradients, bias_gradients = model.gradients(x, y)
            self.check_gradients(model, (weight_gradients, bias_gradients),
                                 lambda: 0.5 * float(np.mean((model.forward(x)[0] - y) ** 2)))

    def test_representation_gradients(self):
        data = representation.make_dataset(0)
        for condition in ("frozen_relu", "trainable_relu", "poly_mixed_raw"):
            model = representation.Network(representation.NetworkConfig(condition, 0.001, 0, 8), data)
            x = (data["x_train"] if condition == "trainable_relu"
                 else representation.fixed_features(condition, data)[0])
            y = data["y_train"]
            self.check_gradients(model, model.gradients(x, y),
                                 lambda: 0.5 * float(np.mean((model.forward(x)[0] - y) ** 2)))

    def test_initial_data_and_search_counts(self):
        x, y, _, _ = initial.make_data()
        for activation, count in (("tanh", 22), ("relu", 4)):
            folder = initial.output_directory(activation)
            recorded = rows(folder / "training-data.csv")
            np.testing.assert_allclose(x[:, 0], [float(r["x"]) for r in recorded], atol=0, rtol=0)
            np.testing.assert_allclose(y[:, 0], [float(r["y"]) for r in recorded], atol=1e-15, rtol=0)
            coarse = rows(folder / "coarse-results.csv")
            self.assertEqual(len(coarse), 90)
            self.assertEqual(sum(r["final_interpolates"] == "True" for r in coarse if r["depth"] == "1"), 0)
            self.assertEqual(sum(r["final_interpolates"] == "True" for r in coarse if r["depth"] == "2"), count)
            by_name = {r["name"]: r for r in coarse}
            for repeated in rows(folder / "replicated-results.csv"):
                if repeated["seed"] == "0":
                    self.assertEqual(repeated["l2_error"], by_name[repeated["name"]]["l2_error"])
                    self.assertEqual(repeated["final_interpolates"],
                                     by_name[repeated["name"]]["final_interpolates"])
            pilot = json.loads((folder / "pilot-result.json").read_text())
            self.assertEqual(pilot["l2_error"], float(by_name[pilot["name"]]["l2_error"]))

    def test_primary_and_extended_evidence(self):
        primary = rows(representation.OUT / "confirmatory-results.csv")
        counts = {"redundant": 0, "frozen_relu": 8, "trainable_relu": 11, "poly_mixed_raw": 20}
        for condition, count in counts.items():
            selected = [r for r in primary if r["condition"] == condition and r["kind"] == "network"]
            self.assertEqual(len(selected), 20)
            self.assertEqual(sum(r["stable_interpolation"] == "True" for r in selected), count)
        original = {(r["condition"], r["dataset"], r["seed"]): r for r in primary if r["kind"] == "network"}
        extended = rows(representation.OUT / "followup-long-training.csv")
        self.assertEqual(len(extended), 80)
        for record in extended:
            key = (record["condition"], record["dataset"], record["seed"])
            previous = original[key]
            self.assertEqual(int(record["original_step"]), int(previous["steps"]))
            self.assertAlmostEqual(float(record["original_l2"]), float(previous["final_l2"]), delta=1e-12)
            self.assertAlmostEqual(float(record["original_selected_l2"]),
                                   float(previous["validation_selected_l2"]), delta=1e-12)
            if record["condition"] != "poly_mixed_raw":
                self.assertGreater(float(record["final_l2"]), float(record["original_selected_l2"]))
                self.assertGreater(float(record["late_selected_l2"]), float(record["original_selected_l2"]))
            filename = f"{key[0]}-{key[1]}-{key[2]}-100000.json"
            saved = json.loads((representation.OUT / "followup-runs" / filename).read_text())
            self.assertAlmostEqual(saved["summary"]["final_l2"], float(record["final_l2"]), delta=1e-12)

    def test_ridge_results_and_selected_dimensions(self):
        selected = rows(representation.OUT / "followup-ridge-selected.csv")
        joint = [r for r in selected if r["selection"] == "p_and_lambda"]
        self.assertEqual(len(joint), 10)
        self.assertTrue(all(int(r["p"]) == 4 for r in joint))
        self.assertAlmostEqual(float(np.median([float(r["l2"]) for r in joint])), 0.012, delta=0.0005)
        paths = rows(representation.OUT / "followup-ridge-paths.csv")
        data = representation.make_dataset(0)
        for dimension in (4, 164):
            train = representation.legendre(data["x_train"], dimension)
            test = representation.legendre(data["x_test"], dimension)
            coefficients = np.linalg.lstsq(train, data["y_train"], rcond=None)[0]
            error = representation.mse(test @ coefficients, data["y_test"])
            stored = next(r for r in paths if r["basis"] == "legendre_equal"
                          and int(r["p"]) == dimension and int(r["dataset"]) == 0
                          and float(r["ridge_lambda"]) == 0)
            self.assertAlmostEqual(error, float(stored["l2"]), delta=1e-10)


if __name__ == "__main__":
    unittest.main(verbosity=2)
