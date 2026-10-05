#!/usr/bin/env python3
"""Generate figures and result tables for the Lecture 9 NN experiment report."""

from __future__ import annotations

import argparse
import csv
import json
import math
import shutil
import subprocess
import tempfile
from pathlib import Path

import numpy as np

import lecture09_nn_interpolation as experiment


ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / "instructor-materials" / "lecture-plans" / "lecture09-nn-experiment"


def read_csv(name: str) -> list[dict[str, str]]:
    with (OUT / name).open(newline="") as stream:
        return list(csv.DictReader(stream))


def write_csv(name: str, rows: list[dict[str, object]]) -> None:
    with (OUT / name).open("w", newline="") as stream:
        writer = csv.DictWriter(stream, fieldnames=list(rows[0].keys()))
        writer.writeheader()
        writer.writerows(rows)


def reproduce_best_snapshots(metadata: dict[str, object]) -> None:
    best = metadata["best_run"]
    assert isinstance(best, dict)
    config = experiment.Configuration(
        depth=int(best["depth"]),
        width=int(best["width"]),
        learning_rate=float(best["learning_rate"]),
        init_scale=float(best["init_scale"]),
        seed=int(best["seed"]),
        activation=str(best.get("activation", metadata.get("activation", "tanh"))),
    )
    first_step = int(best["first_interpolation_step"])
    final_step = int(best["steps"])
    snapshot_steps = {100, first_step, final_step}
    x, y, grid, truth = experiment.make_data()
    model = experiment.TanhMLP(config)
    optimizer = experiment.Adam(model, config.learning_rate)
    snapshots: dict[int, np.ndarray] = {}
    snapshot_metrics: dict[int, dict[str, float]] = {}
    for step in range(1, final_step + 1):
        _, grad_weights, grad_biases = model.gradients(x, y)
        optimizer.step(model, grad_weights, grad_biases)
        if step in snapshot_steps:
            prediction, _ = model.forward(grid)
            snapshots[step] = prediction[:, 0].copy()
            snapshot_metrics[step] = experiment.metrics(model, x, y, grid, truth)

    final_error = snapshot_metrics[final_step]["l2_error"]
    if abs(final_error - float(best["l2_error"])) > 1e-10:
        raise RuntimeError("Reproduced best run does not match stored search result")
    write_csv(
        "best-snapshots.csv",
        [
            {
                "x": float(grid[index, 0]),
                "truth": float(truth[index, 0]),
                "early": float(snapshots[100][index]),
                "first_interpolation": float(snapshots[first_step][index]),
                "final": float(snapshots[final_step][index]),
            }
            for index in range(len(grid))
        ],
    )
    (OUT / "best-snapshot-metrics.json").write_text(
        json.dumps({str(step): values for step, values in snapshot_metrics.items()}, indent=2) + "\n"
    )


def write_architecture_summary() -> None:
    rows = read_csv("coarse-results.csv")
    summaries: list[dict[str, object]] = []
    for depth in (1, 2):
        widths = sorted({int(row["width"]) for row in rows if int(row["depth"]) == depth})
        for width in widths:
            selected = [
                row for row in rows if int(row["depth"]) == depth and int(row["width"]) == width
            ]
            interpolating = [row for row in selected if row["final_interpolates"] == "True"]
            summaries.append(
                {
                    "depth": depth,
                    "width": width,
                    "parameter_count": int(selected[0]["parameter_count"]),
                    "interpolation_fraction": len(interpolating) / len(selected),
                    "best_interpolating_l2": (
                        min(float(row["l2_error"]) for row in interpolating) if interpolating else "nan"
                    ),
                }
            )
    write_csv("architecture-summary.csv", summaries)


def write_result_fragments(metadata: dict[str, object]) -> None:
    replicated = read_csv("replicated-results.csv")
    summaries = read_csv("configuration-summaries.csv")
    stable = metadata["best_configuration_by_median"]
    best = metadata["best_run"]
    assert isinstance(stable, dict) and isinstance(best, dict)
    stable_runs = [
        row
        for row in replicated
        if int(row["depth"]) == int(stable["depth"])
        and int(row["width"]) == int(stable["width"])
        and float(row["learning_rate"]) == float(stable["learning_rate"])
        and float(row["init_scale"]) == float(stable["init_scale"])
    ]
    median_early = float(np.median([float(row["minimum_recorded_l2_error"]) for row in stable_runs]))
    median_early_step = int(np.median([int(row["minimum_recorded_l2_step"]) for row in stable_runs]))
    coarse = read_csv("coarse-results.csv")
    depth_one_final = sum(row["final_interpolates"] == "True" for row in coarse if row["depth"] == "1")
    depth_two_final = sum(row["final_interpolates"] == "True" for row in coarse if row["depth"] == "2")
    depth_two_ever = sum(row["interpolated"] == "True" for row in coarse if row["depth"] == "2")
    prefix = "NN" if metadata.get("activation", "tanh") == "tanh" else "ReLU"
    macros = rf"""% Generated by scripts/lecture09_nn_report_assets.py.
\newcommand{{\{prefix}BestObservedLTwo}}{{{float(best['l2_error']):.3f}}}
\newcommand{{\{prefix}BestObservedFirstLTwo}}{{{float(best['first_interpolation_l2_error']):.3f}}}
\newcommand{{\{prefix}BestObservedParameters}}{{{int(best['parameter_count']):,}}}
\newcommand{{\{prefix}StableMedianFinal}}{{{float(stable['median_final_l2_error']):.3f}}}
\newcommand{{\{prefix}StableMedianFirst}}{{{float(stable['median_first_interpolation_l2_error']):.3f}}}
\newcommand{{\{prefix}StableMedianEarly}}{{{median_early:.3f}}}
\newcommand{{\{prefix}StableEarlyStep}}{{{median_early_step}}}
\newcommand{{\{prefix}StableMinimumFinal}}{{{float(stable['minimum_final_l2_error']):.3f}}}
\newcommand{{\{prefix}StableMaximumFinal}}{{{float(stable['maximum_final_l2_error']):.3f}}}
\newcommand{{\{prefix}StableParameters}}{{{int(stable['parameter_count']):,}}}
\newcommand{{\{prefix}DepthOneFinalCount}}{{{depth_one_final}}}
\newcommand{{\{prefix}DepthTwoFinalCount}}{{{depth_two_final}}}
\newcommand{{\{prefix}DepthTwoEverCount}}{{{depth_two_ever}}}
"""
    (OUT / "results-macros.tex").write_text(macros)

    table_rows = []
    for row in summaries[:6]:
        fraction = float(row["final_interpolation_fraction"])
        median = row["median_final_l2_error"]
        interval = (
            f"{float(row['minimum_final_l2_error']):.3f}--{float(row['maximum_final_l2_error']):.3f}"
            if median
            else "--"
        )
        table_rows.append(
            f"{int(row['width'])} & {float(row['learning_rate']):g} & "
            f"{float(row['init_scale']):g} & {int(row['parameter_count']):,} & "
            f"{fraction:.1f} & {float(median):.3f} & {interval} \\\\"  # type: ignore[arg-type]
        )
    (OUT / "configuration-table.tex").write_text("\n".join(table_rows) + "\n")


def compile_standalone(name: str, content: str) -> None:
    source = OUT / f"{name}.tex"
    source.write_text(content)
    with tempfile.TemporaryDirectory(prefix=f"{name}-") as directory:
        subprocess.run(
            [
                "latexmk",
                "-norc",
                "-pdf",
                "-interaction=nonstopmode",
                "-halt-on-error",
                f"-outdir={directory}",
                str(source),
            ],
            cwd=OUT,
            check=True,
            stdout=subprocess.DEVNULL,
        )
        shutil.copy2(Path(directory) / f"{name}.pdf", OUT / f"{name}.pdf")


def figure_preamble() -> str:
    return r"""\documentclass[varwidth=165mm,border=1pt]{standalone}
\usepackage{pgfplots}
\pgfplotsset{compat=1.18}
\usepackage{xcolor}
\definecolor{courseblue}{HTML}{17365D}
\definecolor{courseorange}{HTML}{C65D21}
\begin{document}
"""


def write_figures(metadata: dict[str, object]) -> None:
    best = metadata["best_run"]
    assert isinstance(best, dict)
    first_step = int(best["first_interpolation_step"])
    final_step = int(best["steps"])
    ymax = 3.2 if metadata.get("activation", "tanh") == "relu" else 2.1
    fit = figure_preamble() + rf"""
\centering
\pgfplotsset{{fitaxis/.style={{width=79mm,height=57mm,xmin=-1,xmax=1,ymin=-0.9,ymax={ymax},
  axis lines=left,grid=major,grid style={{black!8}},tick label style={{font=\scriptsize}},
  label style={{font=\small}},title style={{font=\small}},xlabel={{input $x$}},ylabel={{prediction}}}}}}
\begin{{tikzpicture}}
\begin{{axis}}[fitaxis,title={{(a) Early iterate: step 100}}]
\addplot[black,densely dashed,line width=1pt] table[x=x,y=truth,col sep=comma] {{best-snapshots.csv}};
\addplot[courseblue,line width=1.1pt] table[x=x,y=early,col sep=comma] {{best-snapshots.csv}};
\addplot[only marks,mark=*,mark size=1.3pt,black] table[x=x,y=y,col sep=comma] {{training-data.csv}};
\end{{axis}}
\end{{tikzpicture}}\hfill
\begin{{tikzpicture}}
\begin{{axis}}[fitaxis,title={{(b) Interpolating iterate: step {final_step}}},ylabel={{}}]
\addplot[black,densely dashed,line width=1pt] table[x=x,y=truth,col sep=comma] {{best-snapshots.csv}};
\addplot[courseorange,line width=1.1pt] table[x=x,y=final,col sep=comma] {{best-snapshots.csv}};
\addplot[only marks,mark=*,mark size=1.3pt,black] table[x=x,y=y,col sep=comma] {{training-data.csv}};
\end{{axis}}
\end{{tikzpicture}}
\end{{document}}
"""
    compile_standalone("nn-fit-comparison", fit)

    trajectory = figure_preamble() + rf"""
\begin{{tikzpicture}}
\begin{{loglogaxis}}[
  width=150mm,height=65mm,xmin=10,xmax={final_step * 1.08},ymin=5e-5,ymax=2,
  grid=both,grid style={{black!8}},xlabel={{Adam steps}},ylabel={{error}},
  tick label style={{font=\scriptsize}},label style={{font=\small}},
  legend style={{font=\scriptsize,at={{(0.5,-0.22)}},anchor=north,legend columns=3}}]
\addplot[courseblue,line width=1.1pt,mark=*] table[x=step,y=l2_error,col sep=comma] {{best-history.csv}};
\addlegendentry{{population $L^2$ error}}
\addplot[courseorange,line width=1.1pt,mark=square*] table[x=step,y=maximum_training_residual,col sep=comma] {{best-history.csv}};
\addlegendentry{{maximum training residual}}
\addplot[black,densely dashed,domain=10:{final_step * 1.08},samples=2] {{1e-3}};
\addlegendentry{{interpolation tolerance}}
\addplot[black!45,dotted] coordinates {{({first_step},5e-5) ({first_step},2)}};
\end{{loglogaxis}}
\end{{tikzpicture}}
\end{{document}}
"""
    compile_standalone("nn-training-trajectory", trajectory)

    architecture = figure_preamble() + r"""
\centering
\pgfplotsset{summaryaxis/.style={width=79mm,height=55mm,axis lines=left,grid=major,
  grid style={black!8},tick label style={font=\scriptsize},label style={font=\small},
  title style={font=\small},xlabel={hidden-layer width}}}
\begin{tikzpicture}
\begin{axis}[summaryaxis,title={(a) Fraction interpolating at final iterate},ymin=0,ymax=1.05,
  ylabel={fraction among 9 settings},legend style={font=\scriptsize,at={(0.5,-0.25)},anchor=north,legend columns=2}]
\addplot[courseblue,line width=1.1pt,mark=*] table[x=width,y=interpolation_fraction,col sep=comma,
  restrict expr to domain={\thisrow{depth}}{1:1}] {architecture-summary.csv};
\addlegendentry{one hidden layer}
\addplot[courseorange,line width=1.1pt,mark=square*] table[x=width,y=interpolation_fraction,col sep=comma,
  restrict expr to domain={\thisrow{depth}}{2:2}] {architecture-summary.csv};
\addlegendentry{two hidden layers}
\end{axis}
\end{tikzpicture}\hfill
\begin{tikzpicture}
\begin{axis}[summaryaxis,title={(b) Best interpolating error in coarse search},ymode=log,
  ymin=0.08,ymax=2,ylabel={population $L^2$ error}]
\addplot[courseorange,line width=1.1pt,mark=square*] table[x=width,y=best_interpolating_l2,col sep=comma,
  restrict expr to domain={\thisrow{depth}}{2:2},unbounded coords=jump] {architecture-summary.csv};
\end{axis}
\end{tikzpicture}
\end{document}
"""
    compile_standalone("nn-architecture-summary", architecture)


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--activation", choices=("tanh", "relu"), default="tanh")
    args = parser.parse_args()
    global OUT
    OUT = experiment.output_directory(args.activation)
    metadata = json.loads((OUT / "search-metadata.json").read_text())
    reproduce_best_snapshots(metadata)
    write_architecture_summary()
    write_result_fragments(metadata)
    write_figures(metadata)
    print(f"wrote report assets under {OUT.relative_to(ROOT)}")


if __name__ == "__main__":
    main()
