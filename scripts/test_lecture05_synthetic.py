"""Small deterministic checks of the experiment's indexing and saved plots."""
import json
from pathlib import Path
import tempfile
import unittest
import numpy as np
from lecture05_synthetic import prediction_traces, trajectory
from lecture05_synthetic_plots import coordinates, write_plots


class SyntheticTests(unittest.TestCase):
    def test_true_predictor_reproduces_generator_mean(self):
        z, mean = trajectory(np.random.default_rng(123), 300)
        _, predicted = prediction_traces(z, np.zeros(32), .8, 1., .18)
        np.testing.assert_allclose(predicted, mean, atol=1e-14, rtol=1e-14)

    def test_ar_indexing(self):
        z = np.arange(1., 8.)
        ar, _ = prediction_traces(z, np.array([2., 3.]), 0., 0., 0.)
        np.testing.assert_array_equal(ar[2:], 2 * z[1:-1] + 3 * z[:-2])

    def test_nonfinite_coordinates_are_not_silently_dropped(self):
        with self.assertRaises(ValueError):
            coordinates([1], [float("nan")])

    def test_saved_trial_counts_and_plot_reproduction(self):
        root = Path(__file__).resolve().parents[1]
        data = root / "documents/figures"
        result = json.loads((data / "lecture05-synthetic.json").read_text())
        self.assertEqual(len(result["trials"]), 150)
        self.assertEqual({(t["n"], t["seed"]) for t in result["trials"]},
                         {(n, s) for n in (256, 1024, 4096) for s in range(50)})
        self.assertEqual(result["example"]["seed"], 0)
        self.assertEqual(result["example"]["n"], 1024)
        for row in result["summary"]:
            trials = [t for t in result["trials"] if t["n"] == row["n"]]
            method = row["method"]
            for metric in ("excess_mse", "conditional_kl", "omega"):
                self.assertAlmostEqual(row[metric],
                                       np.mean([t[method][metric] for t in trials]))
        with tempfile.TemporaryDirectory() as temporary:
            write_plots(result, temporary)
            self.assertEqual((Path(temporary) / "lecture05-synthetic-plots.tex").read_bytes(),
                             (data / "lecture05-synthetic-plots.tex").read_bytes())


if __name__ == "__main__":
    unittest.main()
