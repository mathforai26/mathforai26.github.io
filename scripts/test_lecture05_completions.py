"""Analytic, recurrence, simulation, and saved-plot checks for Lecture 5."""
import hashlib
import json
from pathlib import Path
import tempfile
import unittest
import numpy as np
from lecture05_completions import (ar_moments, ar_paths, constant_posterior,
    constant_paths, fitted_completion, memory_completion, predictor_state,
    scalar_moments, scalar_paths, scalar_window_variance)
from lecture05_completion_plots import write_plots


class CompletionTests(unittest.TestCase):
    def test_population_window_variance(self):
        # Independent Toeplitz/Yule--Walker calculation of the same variance.
        for a, c, ell, omega in ((.98, 1., .18, 1.), (.6, 1.3, .2, .7)):
            state_var = ell**2 * omega / (1-a*a)
            gamma0 = c*c*state_var + omega
            gamma1 = c*c*a*state_var + c*ell*omega
            self.assertAlmostEqual(scalar_window_variance(a,c,ell,omega,0), gamma0)
            for p in (1, 10, 32):
                k = np.arange(p)
                lag = np.abs(k[:, None] - k[None, :])
                gram = np.where(lag == 0, gamma0, gamma1*a**(lag-1))
                cross = gamma1*a**k
                expected = gamma0-cross @ np.linalg.solve(gram, cross)
                self.assertAlmostEqual(scalar_window_variance(a,c,ell,omega,p), expected)
        self.assertAlmostEqual(scalar_window_variance(.98,1.,.18,1.,32),
                               1.0000001569276118, places=14)

    def test_true_and_full_history_memory_laws_coincide(self):
        case = memory_completion()
        self.assertEqual(case["models"]["true"], case["models"]["state"])

    def test_ar1_matches_scalar_state(self):
        horizon = 20
        mean, variance = ar_moments([2.0], [.7], .4, horizon)
        exact_mean, exact_var = scalar_moments(1.4, .7, 1., .7, .4, horizon)
        np.testing.assert_allclose(mean, exact_mean)
        np.testing.assert_allclose(variance, exact_var)
        normals = np.random.default_rng(3).normal(size=(4, horizon))
        np.testing.assert_allclose(ar_paths([2.], [.7], .4, normals),
                                   scalar_paths(1.4, .7, 1., .7, .4, normals))

    def test_scalar_generation_matches_observation_feedback(self):
        prefix = np.arange(8.) / 10
        f, c, ell, omega = .4, 1.5, .2, .8
        state = predictor_state(prefix, f, ell)
        normals = np.random.default_rng(10).normal(size=(3, 25))
        got = scalar_paths(state, f+ell*c, c, ell, omega, normals)
        state = np.full(3, state)
        for h in range(25):
            expected = c*state+np.sqrt(omega)*normals[:, h]
            np.testing.assert_allclose(got[:, h], expected)
            state = f*state+ell*expected

    def test_gaussian_conditional_moments(self):
        normals = np.random.default_rng(11).normal(size=(40000, 15))
        mean, variance = scalar_moments(.8, .9, 1.2, .15, .6, 15)
        paths = scalar_paths(.8, .9, 1.2, .15, .6, normals)
        np.testing.assert_allclose(paths.mean(axis=0), mean, atol=.018)
        np.testing.assert_allclose(paths.var(axis=0), variance, atol=.023)

    def test_constant_state_conditional_covariance(self):
        mean, variance = constant_posterior(np.full(10, 2.))
        self.assertAlmostEqual(mean, 20/11)
        self.assertAlmostEqual(variance, 1/11)
        normals = np.random.default_rng(12).normal(size=(60000, 6))
        paths = constant_paths(mean, variance, 1., normals)
        np.testing.assert_allclose(paths.mean(axis=0), mean, atol=.02)
        expected = np.eye(6)+variance*np.ones((6, 6))
        np.testing.assert_allclose(np.cov(paths, rowvar=False), expected, atol=.025)

    def test_higher_order_ar_moments(self):
        prefix, b, omega = [1., -.5, .7], [.3, -.2, .1], .8
        normals = np.random.default_rng(13).normal(size=(60000, 20))
        mean, variance = ar_moments(prefix, b, omega, 20)
        paths = ar_paths(prefix, b, omega, normals)
        np.testing.assert_allclose(paths.mean(axis=0), mean, atol=.018)
        np.testing.assert_allclose(paths.var(axis=0), variance, atol=.025)

    def test_memory_limits(self):
        case = memory_completion()
        models = case["models"]
        self.assertGreater(models["state"]["mean"][-1], 1.8)
        self.assertLess(abs(models["ar"]["mean"][-1]), .01)
        self.assertAlmostEqual(models["state"]["variance"][-1], 1+1/1001)
        self.assertAlmostEqual(models["ar"]["variance"][-1], 2., places=5)

    def test_saved_results_and_plot_reproduction(self):
        data = Path(__file__).resolve().parents[1]/"documents/figures"
        saved = json.loads((data/"lecture05-completions.json").read_text())
        synthetic = json.loads((data/"lecture05-synthetic.json").read_text())
        self.assertEqual(saved["input_sha256"], hashlib.sha256(
            (data/"lecture05-synthetic.json").read_bytes()).hexdigest())
        for name, checksum in saved["source_sha256"].items():
            self.assertEqual(checksum, hashlib.sha256(
                (data.parents[1]/"scripts"/name).read_bytes()).hexdigest())
        self.assertEqual(saved["fitted"], fitted_completion(synthetic))
        self.assertEqual(saved["memory"], memory_completion())
        with tempfile.TemporaryDirectory() as temporary:
            write_plots(saved, temporary)
            for name in ("lecture05-completion-fit.tex", "lecture05-completion-memory.tex"):
                self.assertEqual((Path(temporary)/name).read_bytes(), (data/name).read_bytes())


if __name__ == "__main__":
    unittest.main()
