# Lecture presentations

lecture05.tex is the editable Beamer source; all diagrams are native TikZ.
lecture05.pdf includes 33 main slides and 16 backup slides. The main sequence
is designed for the course's 80-minute lecture, with discussion; backup material
is not part of that time allocation.

The organizing comparison is a neural controller with external memory,
a scaffolded neural interpreter, and a self-contained neural interpreter
(with CoT or direct output). The main slides compare neural verification,
memory requirements, and the division of execution between model and scaffold.

Build from this directory:

    latexmk -norc -pdf -interaction=nonstopmode -halt-on-error -file-line-error lecture05.tex

The -norc flag makes this standalone build independent of personal LaTeX recipes.
No continuous/background compilation is needed.

Check the lecture's operational semantics and numerical calculations:

    python3 check_lecture05.py

The checker compares a recursive evaluator with the explicit continuation
machine in the slides. It covers all core operations, scope restoration,
rollback, argument evaluation order, 1,022 Boolean lists, and 2,000 generated
expressions. It checks our formalization, not the papers' neural models.

Sources and distinctions between paper results and lecture formalizations are
included in the slides. The private canonical lecture plan contains the timing
and course-topic allocation.

A backup slide records a source discrepancy found during checking: Schuurmans's
Table 1 has a right move for (G, 0), while prompt G and displayed test 12 have a
left move. The lecture's mathematical construction follows the table.
