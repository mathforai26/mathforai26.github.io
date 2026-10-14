# Shared exercises

For exercise design, organization, and placement in lecture notes, follow the
[lecture-writing standards](../misc_files/lecture-writing-standards.md#exercises-and-solutions).

Edit an exercise here, not in a lecture or generated homework. Each `.tex` file
is one complete chunk: required introductory tools, the exercise with all its
parts, and its hints. `catalog.json` records its stable ID, lecture, and order.
Lecture sources include these files directly. Keep the lecture inclusion order
and catalog order consistent when adding or moving exercises.

The `exercisechunk` environment handles printed numbering; the ID does not
change when the printed number changes. The `hints` environment owns hint
formatting. Keep exercise labels unique throughout the course.

When several focused exercises develop one topic, give each exercise its own
stable ID, chunk, profile, and solution, and give their catalog entries the
same `group` value. Add one matching `\exercisegroup{...}` before the inputs in
the lecture source. The bundle builder prints catalog groups automatically.
If split solutions share substantial text, `solution_file` may override the
usual `<id>-solution.tex` filename and `solution_dependencies` may list private
helper files that the solution bundle must copy.

General instructions require justification for every answer, including yes/no
answers. Their wording is shared in `\exerciseinstructions` in
`course-exercises.sty`. Lecture exercise sections invoke this command; the
builder includes it automatically in the instructor book and both homework
variants, in addition to the assignment-specific JSON instructions.
When editing prompts, specify the output or quantity students should determine;
avoid vague requests such as "What happens?".

## Exercise profiles

Use the [exercise-profile guidelines](exercise-profile-guidelines.md) to assign
and audit the ratings. They define the student model, separate intellectual
difficulty from execution burden, and give the required calibration procedure.

Place `\exerciseprofile` immediately after the exercise title and label:

{% raw %}
```tex
\exerciseprofile{2}{2}{2}{\exproof\quad\excalculation}{%
Derive the forward recursion and explain why it avoids enumerating hidden
trajectories.}
```
{% endraw %}

The first argument is difficulty: 1 is a direct application, 2 uses a familiar
method, 3 combines several ideas, and 4 is a substantial challenge. The second
is technical load: 1 is light, 2 is sustained, and 3 is dense. The third is
estimated time: 1 is under 20 minutes, 2 is 20--45 minutes, 3 is 45--90
minutes, and 4 is more than 90 minutes. The fourth lists one or more task types
in this canonical order: `\exproof`, `\excalculation`, `\exconstruction`,
`\excomputation`, and `\exinterpretation`. Omit inapplicable types without
changing the order of those retained. The final argument is one specific
learning gain.

The printed profile uses mountains for difficulty, cogs for technical load,
and hourglasses for time. Filled pictograms show the rating and pale pictograms
show the unused part of the scale. The profile line contains pictograms only;
the target pictogram introduces the learning-gain sentence below it.
Estimate time for the non-optional parts; optional extensions do not affect the
hourglass rating.
`\exerciseinstructions` prints the complete legend once at the start of every
exercise section or bundle. Do not use the ratings as prerequisites or grading
weights. Revisit estimates after students have attempted the exercise.

A superscript asterisk, produced by `\suppmark`, marks an exercise based on
supplementary lecture material. It is separate from the exercise profile: it
does not encode difficulty and does not make the exercise optional when the
exercise is assigned.

Solutions are separate files in the private checkout:
`instructor-materials/exercises/solutions/<id>-solution.tex`.
They exist independently of homework selection. Mark unfinished work with
`\missingsolution{what remains}`. The instructor book displays every solution,
including these markers. These placeholders do not claim mathematical review.

## Solution-writing standards

Follow [solution-writing-standards.tex](solution-writing-standards.tex) when
writing or reviewing model solutions. It is phrased for students so that the
same text can be included in future homework instructions; it is not yet
included automatically. In particular, add the short reason behind a claim,
show enough intermediate algebra for mental verification, and connect the
argument to the lecture using named results and stable LaTeX references.
Prefer formula-led proofs throughout: write explicit calculations, inequality
chains, and logical implications, with brief reasons for the steps. Avoid
extended prose that merely narrates a calculation or optimization argument.
Define events by explicit mathematical conditions and index ranges before
using them. Avoid prose placeholders inside probabilities or indicators;
write the actual event unions, intersections, and inclusions used in proofs.
Keep these rules in the reusable standards when revising future solutions.

Keep model answers in the private solution files. Match the exercise's part
labels, cover its optional extensions, and retain explicit unfinished markers
until every requested argument is supplied. Review mathematical correctness
separately from compilation; then rebuild, check references and warnings,
and inspect the affected PDF pages. A successful build is not a proof audit.

If a solution refers to another lecture, list that lecture number in the
exercise's optional `reference_lectures` catalog field. The builder then
includes that lecture's references and PDF even in a single-exercise homework.

## Building bundles

From the repository root:

```sh
python3 scripts/build_exercises.py
python3 scripts/build_exercises.py --homework instructor-materials/exercises/homeworks/example.json
```

The first command builds `outputs/instructor-exercises/document.pdf`, grouped
by lecture. The second builds `outputs/homeworks/example/solutions/document.pdf`
and `outputs/homeworks/example/student/document.pdf`. Each output folder is a
self-contained LaTeX bundle; compile `document.tex` there with `latexmk -pdf`.
The student bundle has editable empty solution environments and contains no
solution source files. Working outputs are ignored by Git and not published.

Homework JSON supplies a title, revision, instructions, and an ordered list of
exercise IDs. Optional `points` is either the mark value for a whole exercise
or a map from required printed part labels to marks. Parts omitted from a map
may be declared optional in the homework's general instructions. The homework
prints the allocation and its total outside the unchanged chunk.
Homework solutions currently include the whole solution for each selected chunk.
The sample is a development example, not an assigned or published homework.

Builds refresh lecture PDFs and their labels first. References to facts outside
the selected chunks link to the bundled lecture PDFs; local labels resolve in
the homework/book. Keep those PDFs with the bundle. Shared notation needed by
standalone documents is in `reader-preamble.tex`.

For a local frozen homework release:

```sh
python3 scripts/build_exercises.py --homework path/to/homework.json --release hw1-r1
```

Set the JSON revision to the intended student-visible revision first. Releases
are stored under `instructor-materials/exercises/releases/`; an existing release
name is refused. Each includes the selection, both document variants, reference
PDFs, and content hashes. Further lecture edits do not update a release. Issue a
new revision and a short correction notice when an assigned problem changes.
Compilation time records the build time; the revision identifies the assignment.
This command does not publish anything or change website links.
