#!/usr/bin/env python3
"""Generate the follow-up report tables and PGFPlots from saved results."""
import csv
import math
from collections import defaultdict
import numpy as np
import lecture09_representation_experiment as base

OUT = base.OUT


def read(name):
    with (OUT / name).open() as stream:
        return list(csv.DictReader(stream))


def median(rows, key):
    return float(np.median([float(r[key]) for r in rows]))


def number(x):
    if abs(x) >= 1000:
        exponent = int(math.floor(math.log10(abs(x))))
        return rf"${x/10**exponent:.1f}\times10^{{{exponent}}}$"
    return f"{x:.3f}"


def table(name, header, rows, columns):
    text = [rf"\begin{{tabular}}{{{columns}}}", r"\toprule", " & ".join(header)+r" \\", r"\midrule"]
    text.extend(" & ".join(row)+r" \\" for row in rows)
    text.extend([r"\bottomrule", r"\end{tabular}"])
    (OUT / name).write_text("\n".join(text)+"\n")


def linear_assets():
    paths, selected = read("followup-ridge-paths.csv"), read("followup-ridge-selected.csv")
    rows=[]
    for p in [4,8,12,20,40,80,164]:
        endpoint=[r for r in paths if r["basis"]=="legendre_equal" and int(r["p"])==p and float(r["ridge_lambda"])==0]
        chosen=[r for r in selected if r["basis"]=="legendre_equal" and int(r["p"])==p and r["selection"]=="lambda_with_fixed_p"]
        rows.append([f"Legendre, $p={p}$", number(median(endpoint,"l2")),number(median(chosen,"l2"))])
    endpoint=[r for r in paths if r["basis"]=="mixed_weighted" and float(r["ridge_lambda"])==0]
    chosen=[r for r in selected if r["basis"]=="mixed_weighted"]
    rows.append(["weighted mixed, $p=164$",number(median(endpoint,"l2")),number(median(chosen,"l2"))])
    table("followup-ridge-table.tex",["features","unpenalized","validation-selected ridge"],rows,"lrr")
    plot=[r"\begin{tikzpicture}",r"\begin{axis}[width=0.94\textwidth,height=6.3cm,ymode=log,",
          r"xlabel={$\log_{10}\lambda$ (penalty decreases to the right)},x dir=reverse,",
          r"ylabel={median population squared error},legend style={font=\small,at={(0.5,1.02)},anchor=south,legend columns=2},grid=major]"]
    for basis,p,label,color in [("legendre_equal",4,"Legendre, $p=4$","courseblue"),
                               ("legendre_equal",12,"Legendre, $p=12$","orange"),
                               ("legendre_equal",164,"Legendre, $p=164$","black"),
                               ("mixed_weighted",164,"weighted mixed, $p=164$","teal!70!black")]:
        groups=defaultdict(list)
        for r in paths:
            if r["basis"]==basis and int(r["p"])==p and float(r["ridge_lambda"])>0:
                groups[float(r["ridge_lambda"])].append(float(r["l2"]))
        coords=" ".join(f"({math.log10(lam):.5f},{np.median(values):.9g})" for lam,values in sorted(groups.items()))
        plot.extend([rf"\addplot[thick,{color}] coordinates {{{coords}}};",rf"\addlegendentry{{{label}}}"])
    plot.extend([r"\end{axis}",r"\end{tikzpicture}"])
    (OUT / "followup-ridge-figure.tex").write_text("\n".join(plot)+"\n")


def gram_assets():
    grams=read("followup-fixed-gram.csv")
    names=[("redundant","redundant scalar"),("frozen_relu","frozen ReLU"),
           ("mixed_head","mixed: low-degree block"),("mixed_tail","mixed: high-degree block"),
           ("poly_mixed_raw","mixed: full weighted map"),("poly_mixed_standard","mixed: standardized"),
           ("legendre_equal_164","Legendre: 164 equal weights")]
    rows=[]
    for key,label in names:
        rs=[r for r in grams if r["representation"]==key]
        rows.append([label]+[number(median(rs,c)) for c in ["mean_abs_cosine","max_abs_cosine","participation_rank"]])
    table("followup-gram-table.tex",["representation","mean $|C_{ij}|$","max $|C_{ij}|$","$r(K)$"],rows,"lrrr")


def long_assets():
    rows,history=read("followup-long-training.csv"),read("followup-long-history.csv")
    names=[("redundant","redundant scalar","courseblue"),("frozen_relu","frozen ReLU","orange"),
           ("trainable_relu","trained ReLU","black"),("poly_mixed_raw","weighted polynomial","teal!70!black")]
    table_rows=[]
    for c,label,_ in names:
        rs=[r for r in rows if r["condition"]==c]
        ever=sum(bool(r["first_stable_step"]) for r in rs)
        final=sum(float(r["final_maximum_residual"])<=base.TOLERANCE for r in rs)
        table_rows.append([label,f"{ever}/20",f"{final}/20",number(median(rs,"final_l2")),number(median(rs,"extended_selected_l2"))])
    table("followup-long-table.tex",["representation","ever stable","final fits","final error","selected error"],table_rows,"lrrrr")
    plot=[r"\begin{tikzpicture}",r"\begin{groupplot}[group style={group size=2 by 1,horizontal sep=1.85cm},",
          r"width=0.45\textwidth,height=5.9cm,xmode=log,ymode=log,xlabel={Adam steps},",
          r"tick label style={font=\small},label style={font=\small},title style={font=\small},grid=major]",
          r"\nextgroupplot[ylabel={median population squared error},title={(a) Population error},",
          r"legend style={font=\scriptsize,at={(0.98,0.02)},anchor=south east}]"]
    for metric in ["l2","training_mse"]:
        if metric=="training_mse":
            plot.append(r"\nextgroupplot[ylabel={median training MSE},title={(b) Training loss},ymin=1e-12,ymax=1]")
        for c,label,color in names:
            groups=defaultdict(list)
            for r in history:
                step=int(r["step"])
                if r["condition"]==c and (step<=1000 or step%1000==0):
                    groups[step].append(float(r[metric]))
            coords=" ".join(f"({step},{max(1e-12,float(np.median(values))):.9g})" for step,values in sorted(groups.items()))
            plot.append(rf"\addplot[thick,{color}] coordinates {{{coords}}};")
            if metric=="l2":
                plot.append(rf"\addlegendentry{{{label}}}")
    plot.extend([r"\end{groupplot}",r"\end{tikzpicture}"])
    (OUT / "followup-long-figure.tex").write_text("\n".join(plot)+"\n")


if __name__=="__main__":
    linear_assets()
    gram_assets()
    if (OUT / "followup-long-training.csv").exists():
        long_assets()
