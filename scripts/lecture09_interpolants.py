#!/usr/bin/env python3
"""Generate the one-dimensional interpolation comparison for Lecture 9."""

from __future__ import annotations

import math
import random
import shutil
import subprocess
import tempfile
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
OUTPUT = ROOT / "documents" / "figures" / "lecture09-polynomial-interpolants.tex"
PLOT_SOURCE = ROOT / "documents" / "figures" / "lecture09-polynomial-interpolants-plot.tex"
PLOT_PDF = ROOT / "documents" / "figures" / "lecture09-polynomial-interpolants-plot.pdf"

SEED = 9
N = 20
M = 4
D = 160
SIGMA = 0.28
GRID_SIZE = 1201


def target(x: float) -> float:
    return 0.55 + 0.55 * math.sin(math.pi * x / 2.0) - 0.15 * math.cos(math.pi * x)


def legendre_features(x: float, count: int) -> list[float]:
    values = [1.0]
    if count == 1:
        return values
    p_prev, p_now = 1.0, x
    values.append(math.sqrt(3.0) * p_now)
    for degree in range(1, count - 1):
        p_next = ((2 * degree + 1) * x * p_now - degree * p_prev) / (degree + 1)
        values.append(math.sqrt(2 * degree + 3) * p_next)
        p_prev, p_now = p_now, p_next
    return values


def chebyshev_features(x: float, count: int) -> list[float]:
    values = [1.0]
    if count == 1:
        return values
    t_prev, t_now = 1.0, x
    values.append(math.sqrt(2.0) * t_now)
    for _degree in range(1, count - 1):
        t_next = 2.0 * x * t_now - t_prev
        values.append(math.sqrt(2.0) * t_next)
        t_prev, t_now = t_now, t_next
    return values


def solve(matrix: list[list[float]], rhs: list[float]) -> list[float]:
    """Solve a dense linear system by Gaussian elimination with pivoting."""
    n = len(rhs)
    augmented = [row[:] + [value] for row, value in zip(matrix, rhs)]
    for column in range(n):
        pivot = max(range(column, n), key=lambda row: abs(augmented[row][column]))
        if abs(augmented[pivot][column]) < 1e-12:
            raise RuntimeError("Interpolation Gram matrix is numerically singular")
        augmented[column], augmented[pivot] = augmented[pivot], augmented[column]
        scale = augmented[column][column]
        for entry in range(column, n + 1):
            augmented[column][entry] /= scale
        for row in range(n):
            if row == column:
                continue
            factor = augmented[row][column]
            if factor == 0.0:
                continue
            for entry in range(column, n + 1):
                augmented[row][entry] -= factor * augmented[column][entry]
    return [augmented[row][n] for row in range(n)]


def minimum_norm_coefficients(features: list[list[float]], responses: list[float]) -> list[float]:
    gram = [
        [sum(left * right for left, right in zip(row_i, row_j)) for row_j in features]
        for row_i in features
    ]
    dual = solve(gram, responses)
    return [
        sum(dual[row] * features[row][column] for row in range(len(features)))
        for column in range(len(features[0]))
    ]


def evaluate_legendre_series(coefficients: list[float], x: float) -> float:
    return sum(a * value for a, value in zip(coefficients, legendre_features(x, len(coefficients))))


def evaluate_weighted_series(coefficients: list[float], x: float) -> float:
    low = legendre_features(x, M)
    tail = chebyshev_features(x, M + D)[M:]
    scaled = low + [value / math.sqrt(D) for value in tail]
    return sum(a * value for a, value in zip(coefficients, scaled))


def coordinates(points: list[tuple[float, float]]) -> str:
    return "\n".join(f"({x:.7f},{y:.7f})" for x, y in points)


def main() -> None:
    rng = random.Random(SEED)
    inputs = sorted(rng.uniform(-0.96, 0.96) for _ in range(N))
    responses = [target(x) + rng.gauss(0.0, SIGMA) for x in inputs]

    weighted_features = []
    equal_features = []
    for x in inputs:
        low = legendre_features(x, M)
        tail = chebyshev_features(x, M + D)[M:]
        weighted_features.append(low + [value / math.sqrt(D) for value in tail])
        equal_features.append(legendre_features(x, M + D))

    weighted_coefficients = minimum_norm_coefficients(weighted_features, responses)
    equal_coefficients = minimum_norm_coefficients(equal_features, responses)

    grid = [-1.0 + 2.0 * index / (GRID_SIZE - 1) for index in range(GRID_SIZE)]
    truth = [(x, target(x)) for x in grid]
    weighted = [(x, evaluate_weighted_series(weighted_coefficients, x)) for x in grid]
    equal = [(x, evaluate_legendre_series(equal_coefficients, x)) for x in grid]
    observations = list(zip(inputs, responses))

    weighted_residual = max(
        abs(evaluate_weighted_series(weighted_coefficients, x) - y)
        for x, y in observations
    )
    equal_residual = max(
        abs(evaluate_legendre_series(equal_coefficients, x) - y)
        for x, y in observations
    )
    weighted_risk = sum((prediction - target(x)) ** 2 for x, prediction in weighted) / GRID_SIZE
    equal_risk = sum((prediction - target(x)) ** 2 for x, prediction in equal) / GRID_SIZE

    plot_content = rf"""% Generated by scripts/lecture09_interpolants.py; edit the generator.
\documentclass[varwidth=160mm,border=0pt]{{standalone}}
\usepackage{{pgfplots}}
\pgfplotsset{{compat=1.18}}
\usepackage{{xcolor}}
\definecolor{{courseblue}}{{HTML}}{{17365D}}
\begin{{document}}
\centering
\pgfplotsset{{lNineInterpolation/.style={{
  width=76mm,height=48mm,xmin=-1,xmax=1,ymin=-1.05,ymax=1.55,
  axis lines=left,tick align=outside,grid=major,grid style={{black!8}},
  tick label style={{font=\scriptsize}},label style={{font=\small}},
  title style={{font=\small}},scaled ticks=false,
  xlabel={{input $x$}},ylabel={{prediction}}}}}}
\begin{{tikzpicture}}
\begin{{axis}}[lNineInterpolation,title={{(a) Weighted minimum norm}}]
\addplot[black,densely dashed,line width=1pt] coordinates {{
{coordinates(truth)}
}};
\addplot[courseblue,line width=1.15pt] coordinates {{
{coordinates(weighted)}
}};
\addplot[only marks,mark=*,mark size=1.35pt,black] coordinates {{
{coordinates(observations)}
}};
\end{{axis}}
\end{{tikzpicture}}\hfill
\begin{{tikzpicture}}
\begin{{axis}}[lNineInterpolation,title={{(b) Equal Legendre penalties}},ylabel={{}}]
\addplot[black,densely dashed,line width=1pt] coordinates {{
{coordinates(truth)}
}};
\addplot[red!70!black,line width=1.15pt] coordinates {{
{coordinates(equal)}
}};
\addplot[only marks,mark=*,mark size=1.35pt,black] coordinates {{
{coordinates(observations)}
}};
\end{{axis}}
\end{{tikzpicture}}
\vspace{{-1mm}}
\begin{{center}}
\footnotesize
\tikz\draw[black,densely dashed,line width=1pt] (0,0)--(5mm,0);
true regression function\qquad
\tikz\draw[courseblue,line width=1.15pt] (0,0)--(2.5mm,0);
\tikz\draw[red!70!black,line width=1.15pt] (2.5mm,0)--(5mm,0);
selected interpolant\qquad
\tikz\draw[black,fill=black] (2.5mm,0) circle (1.2pt);
training response
\end{{center}}
\end{{document}}
"""
    wrapper_content = rf"""% Generated by scripts/lecture09_interpolants.py; edit the generator.
\begin{{figure}}[htbp]
\centering
\includegraphics[width=\linewidth]{{../figures/lecture09-polynomial-interpolants-plot.pdf}}
\caption{{Both panels use the same $n={N}$ observations from
$X\sim\operatorname{{Unif}}[-1,1]$ and
$Y=f^\star(X)+\cN(0,{SIGMA}^2)$, where
$f^\star(x)=0.55+0.55\sin(\pi x/2)-0.15\cos(\pi x)$, and the same space of
dimension ${M + D}$. Both rules interpolate. The weighted norm distinguishes
the first $m={M}$ features; equal Legendre penalties minimize $L^2(\mu)$ norm.}}
\label{{fig:polynomial-interpolants}}
\end{{figure}}
"""
    rebuild_plot = not PLOT_PDF.exists() or not PLOT_SOURCE.exists() or PLOT_SOURCE.read_text() != plot_content
    if rebuild_plot:
        PLOT_SOURCE.write_text(plot_content)
        with tempfile.TemporaryDirectory(prefix="lecture09-figure-") as directory:
            subprocess.run(
                [
                    "latexmk", "-norc", "-pdf", "-interaction=nonstopmode",
                    "-halt-on-error", f"-outdir={directory}", str(PLOT_SOURCE),
                ],
                cwd=PLOT_SOURCE.parent,
                check=True,
                stdout=subprocess.DEVNULL,
            )
            shutil.copy2(Path(directory) / PLOT_SOURCE.with_suffix(".pdf").name, PLOT_PDF)
        print(f"rebuilt {PLOT_PDF.relative_to(ROOT)}")
    else:
        print(f"reused {PLOT_PDF.relative_to(ROOT)}")
    OUTPUT.write_text(wrapper_content)
    print(f"wrote {OUTPUT.relative_to(ROOT)}")
    print(f"maximum interpolation residuals: weighted={weighted_residual:.2e}, equal={equal_residual:.2e}")
    print(f"grid L2 errors: weighted={weighted_risk:.4f}, equal={equal_risk:.4f}")
    print(
        "prediction ranges: "
        f"weighted=[{min(y for _, y in weighted):.3f}, {max(y for _, y in weighted):.3f}], "
        f"equal=[{min(y for _, y in equal):.3f}, {max(y for _, y in equal):.3f}]"
    )


if __name__ == "__main__":
    main()
