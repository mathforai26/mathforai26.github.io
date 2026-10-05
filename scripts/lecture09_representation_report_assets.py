#!/usr/bin/env python3
"""Generate tables and PGFPlots figures for the representation report."""

from __future__ import annotations

import csv
from collections import defaultdict
from pathlib import Path

import numpy as np


ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / "instructor-materials" / "lecture-plans" / "lecture09-representation-experiment"


def load() -> list[dict[str, object]]:
    rows = list(csv.DictReader((OUT / "confirmatory-results.csv").open()))
    for row in rows:
        for key in [
            "dataset",
            "seed",
            "steps",
            "final_l2",
            "validation_selected_l2",
            "final_maximum_residual",
        ]:
            row[key] = float(row[key])
        row["stable_interpolation"] = row["stable_interpolation"] == "True"
    return rows


def latex_number(value: float | None) -> str:
    return "--" if value is None else f"{value:.3f}"


def write_primary(rows: list[dict[str, object]]) -> None:
    conditions = ["redundant", "frozen_relu", "trainable_relu", "poly_mixed_raw"]
    labels = {
        "redundant": "redundant scalar",
        "frozen_relu": "frozen ReLU",
        "trainable_relu": "trained ReLU",
        "poly_mixed_raw": "polynomial",
    }
    lines = ["\\begin{tabular}{lrrrr}", "\\toprule", "representation & stable & median final & mean final & median selected \\\\", "\\midrule"]
    plot_rows = []
    medians = []
    for index, condition in enumerate(conditions, 1):
        subset = [row for row in rows if row["condition"] == condition]
        stable = [row for row in subset if row["stable_interpolation"]]
        final = [float(row["final_l2"]) for row in stable]
        selected = [float(row["validation_selected_l2"]) for row in subset]
        median_final = float(np.median(final)) if final else None
        mean_final = float(np.mean(final)) if final else None
        lines.append(
            f"{labels[condition]} & {len(stable)}/{len(subset)} & {latex_number(median_final)} & "
            f"{latex_number(mean_final)} & {np.median(selected):.3f} \\\\"
        )
        if median_final is not None:
            medians.append((index, median_final))
        for row in stable:
            plot_rows.append((index, float(row["final_l2"])))
    lines.extend(["\\bottomrule", "\\end{tabular}"])
    (OUT / "primary-summary-table.tex").write_text("\n".join(lines) + "\n")

    plot = [
        "\\begin{tikzpicture}",
        "\\begin{groupplot}[group style={group size=2 by 1,horizontal sep=1.7cm},width=0.45\\textwidth,height=5.3cm,",
        "tick label style={font=\\small},label style={font=\\small},title style={font=\\small}]",
        "\\nextgroupplot[ybar,ymin=0,ymax=1.08,ylabel={stable interpolation fraction},",
        "symbolic x coords={redundant,frozen,trained,polynomial},xtick=data,x tick label style={rotate=25,anchor=east},title={(a) Reliability}]",
    ]
    fractions = []
    for condition, short in zip(conditions, ["redundant", "frozen", "trained", "polynomial"]):
        subset = [row for row in rows if row["condition"] == condition]
        fractions.append((short, np.mean([row["stable_interpolation"] for row in subset])))
    plot.append("\\addplot[fill=courseblue!75,draw=courseblue] coordinates {" + " ".join(f"({x},{y:.3f})" for x, y in fractions) + "};")
    plot.extend([
        "\\nextgroupplot[ymode=log,xmin=0.5,xmax=4.5,ymin=0.02,ymax=1.4,ylabel={population $L^2$ error},",
        "xtick={1,2,3,4},xticklabels={redundant,frozen,trained,polynomial},x tick label style={rotate=25,anchor=east},title={(b) Successful interpolants}]",
        "\\addplot[only marks,mark=*,mark size=1.5pt,courseblue!55] coordinates {" + " ".join(f"({x},{y:.7f})" for x, y in plot_rows) + "};",
        "\\addplot[only marks,mark=-,mark size=7pt,very thick,orange] coordinates {" + " ".join(f"({x},{y:.7f})" for x, y in medians) + "};",
        "\\end{groupplot}",
        "\\end{tikzpicture}",
    ])
    (OUT / "primary-results.tex").write_text("\n".join(plot) + "\n")


def write_polynomial(rows: list[dict[str, object]]) -> None:
    bases = ["mixed", "legendre", "chebyshev"]
    labels = {"mixed": "mixed", "legendre": "Legendre", "chebyshev": "Chebyshev"}
    table = [
        "\\begin{tabular}{llrr}",
        "\\toprule",
        "basis & preprocessing & ReLU network & linear minimum norm \\\\",
        "\\midrule",
    ]
    plot_network, plot_linear = [], []
    x = 0
    for basis in bases:
        for preprocessing in ["raw", "standard"]:
            network_condition = f"poly_{basis}_{preprocessing}"
            linear_condition = f"linear_{basis}_{preprocessing}"
            network = [float(row["final_l2"]) for row in rows if row["condition"] == network_condition]
            linear = [float(row["final_l2"]) for row in rows if row["condition"] == linear_condition]
            network_median = float(np.median(network))
            linear_median = float(np.median(linear))
            table.append(
                f"{labels[basis]} & {preprocessing} & {network_median:.3f} & {linear_median:.3f} \\\\"
            )
            x += 1
            plot_network.append((x, network_median))
            plot_linear.append((x, linear_median))
        if basis != bases[-1]:
            table.append("\\addlinespace[2pt]")
    table.extend(["\\bottomrule", "\\end{tabular}"])
    (OUT / "polynomial-summary-table.tex").write_text("\n".join(table) + "\n")
    plot = [
        "\\begin{tikzpicture}",
        "\\begin{axis}[width=0.94\\textwidth,height=6.2cm,ymode=log,ymin=0.035,ymax=1.0,",
        "ylabel={median population $L^2$ error},xtick={1,2,3,4,5,6},",
        "xticklabels={mixed raw,mixed std.,Legendre raw,Legendre std.,Chebyshev raw,Chebyshev std.},",
        "x tick label style={rotate=25,anchor=east},legend style={at={(0.5,1.02)},anchor=south,legend columns=2},grid=major]",
        "\\addplot+[mark=square*,thick,courseblue] coordinates {" + " ".join(f"({x},{y:.7f})" for x, y in plot_network) + "};",
        "\\addlegendentry{ReLU network}",
        "\\addplot+[mark=triangle*,thick,orange] coordinates {" + " ".join(f"({x},{y:.7f})" for x, y in plot_linear) + "};",
        "\\addlegendentry{linear minimum norm}",
        "\\end{axis}",
        "\\end{tikzpicture}",
    ]
    (OUT / "polynomial-results.tex").write_text("\n".join(plot) + "\n")


def dataset_means(rows: list[dict[str, object]], condition: str) -> np.ndarray:
    grouped: dict[int, list[float]] = defaultdict(list)
    for row in rows:
        if row["condition"] == condition:
            grouped[int(row["dataset"])].append(float(row["final_l2"]))
    return np.array([np.mean(grouped[index]) for index in sorted(grouped)])


def bootstrap_interval(differences: np.ndarray) -> tuple[float, float, float]:
    rng = np.random.default_rng(654)
    indices = rng.integers(0, len(differences), size=(20_000, len(differences)))
    samples = np.mean(differences[indices], axis=1)
    lower, upper = np.quantile(samples, [0.025, 0.975])
    return float(np.mean(differences)), float(lower), float(upper)


def write_macros(rows: list[dict[str, object]]) -> None:
    network_difference = dataset_means(rows, "poly_mixed_standard") - dataset_means(rows, "poly_mixed_raw")
    linear_difference = dataset_means(rows, "linear_mixed_standard") - dataset_means(rows, "linear_mixed_raw")
    n_mean, n_low, n_high = bootstrap_interval(network_difference)
    l_mean, l_low, l_high = bootstrap_interval(linear_difference)
    macros = [
        f"\\newcommand{{\\NetworkScalingDifference}}{{{n_mean:.3f}}}",
        f"\\newcommand{{\\NetworkScalingLower}}{{{n_low:.3f}}}",
        f"\\newcommand{{\\NetworkScalingUpper}}{{{n_high:.3f}}}",
        f"\\newcommand{{\\LinearScalingDifference}}{{{l_mean:.3f}}}",
        f"\\newcommand{{\\LinearScalingLower}}{{{l_low:.3f}}}",
        f"\\newcommand{{\\LinearScalingUpper}}{{{l_high:.3f}}}",
    ]
    (OUT / "results-macros.tex").write_text("\n".join(macros) + "\n")


def main() -> None:
    rows = load()
    write_primary(rows)
    write_polynomial(rows)
    write_macros(rows)


if __name__ == "__main__":
    main()
