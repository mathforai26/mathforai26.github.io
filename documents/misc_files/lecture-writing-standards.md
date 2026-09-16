# Lecture-writing standards

These rules apply from the first draft of new lecture notes and throughout
revisions of existing notes.

## Organization

Use this structure, omitting optional material when it is unnecessary:

1. **Opening.** Give the lecture identity, purpose, and a short reading guide.
   Identify prerequisites and distinguish material covered in class from later
   additions when relevant.
2. **Main exposition.** Develop the guiding question through its mathematical
   setup, central results, arguments, and implications for AI. Use substantive
   headings that follow this development. State the point before a derivation
   and explain its consequence afterward.
3. **Optional reading**, when needed. Place a separate optional-reading section
   after the main exposition and before the take-home messages.
4. **Take-home messages.** Collect the main conclusions compactly.
5. **Endnotes.** Print the numbered endnotes immediately after the take-home
   messages with `\printendnotes`.
6. **Bibliographical notes**, then the **References**. Use
   `\section*{Bibliographical notes}` for narrative attribution, source
   comparisons, and further reading. Follow it with the ordinary reference
   list.
7. **Glossary.** Use `\section*{Glossary}`. Recap important technical terms,
   persistent notation, and diagram conventions; define them first in the
   exposition. Omit incidental names and ordinary mathematical vocabulary.
8. **Exercises.** Collect the lecture's exercises in one section, in the order
   of the ideas they develop.
9. **Appendices**, when needed. Collect substantial deferred proofs and
   background, ordered by their first substantive use in the main text.
   Restate each deferred result immediately before its `proof` environment.

Keep the main argument complete for a first reading. Mark supplementary
material clearly, refer to it where it becomes useful, and keep the reading
guide consistent with its actual placement.

## Exposition and notation

- Preserve the substance of the instructor's corrections. Improve wording
  only while retaining the clarification, qualification, or distinction it
  introduced. Compare revisions against the current source, not an older draft.
- At a definition in the exposition, mark the newly introduced technical term
  with \emph{}. Give its notation and meaning there. A heading alone does not
  identify which terms in the following paragraph are being defined.
- Explain the purpose of an operation or architectural choice beside its
  mathematics. Interleave motivation, definition, and immediate interpretation;
  keep compact formula summaries when useful.
- Justify assumptions used in an explanation. For a heuristic, state the
  simplifying model, explain why it is relevant, and distinguish its conclusion
  from a guarantee about trained models.
- Identify a domain-specific example where it appears: for example, say
  "in a coding task" before discussing variable declarations, identifiers,
  scope, or type information. Preserve that context when moving the example.
- Keep paper citations and source comparisons in the bibliographical notes.
  Preserve attribution and qualifications when relocating them.
- Start from the shared notation and theorem declarations in
  `scribe_template.tex`. Use `\E`, `\P`, `\I`, `\R`, `\KL`, `\TV`, and the
  `\cA`--`\cZ` family instead of adding local variants for the same objects.
  Use \(n\) for the number of independent training examples.
- Use sentence case in optional theorem-environment titles. Put a worked
  example in the `example` environment when later text refers to it or when
  its beginning and end would otherwise be hard to identify.
- Reserve `\boxed{}` for objects that are literally represented as boxes in a
  diagram. State important mathematical conclusions in numbered theorem or
  equation environments so they can be referenced consistently.
- Add a short mathematical-background paragraph or appendix when an elementary
  term is needed but may be unfamiliar. State how related terms differ; for
  example, explain when a discrepancy is a norm, metric, or pseudometric.

## Exercises and solutions

- Give each exercise a short descriptive title, a clear mathematical task,
  and only the setup needed to attempt it. State its learning purpose briefly
  when that purpose would otherwise be unclear. Supply any additional tools
  before their use and refer to established lecture results by stable labels.
- Keep each exercise focused. Split a long set when it develops several
  distinct ideas; retain parts together when they build one argument. Use
  `(a), (b), ...` for parts, identify dependencies, and mark optional extensions.
- Ask for a specific calculation, proof, construction, or comparison. Invoke
  the shared `\exerciseinstructions` once for the section: every answer,
  including a yes/no answer, requires justification.
- Put hints after the questions, using the shared `hints` environment. A hint
  should suggest a useful step while leaving the intended work to the student.
- Keep canonical exercise files in `documents/exercises/` and include them
  from the lecture. Preserve stable IDs and labels; keep the inclusion order
  and `catalog.json` order synchronized when adding, moving, or splitting
  exercises. Use `exercisechunk` for printed numbering.
- Write or update the matching private solution with each exercise. Match all
  part labels and optional extensions, including after a split. Keep model
  answers in `instructor-materials/exercises/solutions/<id>-solution.tex`;
  lecture appendices contain deferred exposition proofs, not exercise solutions.
  Retain explicit `\missingsolution{...}` markers until unfinished work is resolved.
- Follow the [solution-writing standards](../exercises/solution-writing-standards.tex):
  use explicit calculations and short justifications, connect to named lecture
  results, and check assumptions and boundary cases. Mathematical correctness
  must be checked separately from compilation.

The [exercise guide](../exercises/README.md) describes source files, shared
formatting, cross-lecture references, and the book and homework builds.

## Endnotes

An endnote is a short remark that refines the material and may be skipped on a
first reading. It is too short to require an appendix. Examples include an
alternative convention, an exact refinement of a bound, or a small
implementation observation.

- Keep definitions, assumptions, and qualifications needed for the main
  argument in the main text. Its explanation must remain correct and readable
  when every endnote is skipped. Substantial proofs and extended discussions
  belong in appendices.
- From the first draft, place short optional refinements directly in endnotes.
  During revision, review existing ancillary remarks for possible relocation
  there. Preserve their content and references; a remark's being short does
  not by itself make it optional.
- Place `\endnote{...}` beside the statement it refines. Make the note
  understandable from that statement, and use a short descriptive opening
  when helpful. Put a cross-reference label after the command:
  `\endnote{...}\label{en:example}`.
- Retain the template's `enotez` setup and `\printendnotes`. Print the endnotes
  immediately after the take-home messages, before the bibliographical notes
  and reference list, with links in both directions. Use unnumbered displays
  inside notes so their numbering does not depend on the section in which the
  endnotes are printed.

## Completion checks

For new notes and revisions, check section order, exercise/solution alignment,
and the main argument with optional material omitted. Preserve definitions,
rationale, and conceptual distinctions when reorganizing. Rebuild the affected
notes and exercise bundles; check numbering, references, endnote return links,
and the rendered pages, including transitions between sections.

## Website publication

- Keep edits and rebuilds local unless the user explicitly requests
  publication. Do not publish intermediate revisions automatically.
- Publish completed student-facing notes as both PDF and LaTeX source. Put
  **Lecture notes: PDF · LaTeX** directly beneath the corresponding lecture's
  description on the course schedule, with the PDF's **Last revised** date. Use
  this label consistently; the coursework column is for coursework milestones.
- Use `_includes/lecture-notes.html` for schedule links, for example
  `{% include lecture-notes.html lecture="lecture01" %}`. Add links when the
  files are published. Publish the source's shared exercise dependencies too.
- Retain the template's `\lecturerevised` command in new notes. Build with
  `python3 scripts/build_lecture_notes.py`; it records changes to each lecture
  and its actual source dependencies in `_data/lecture_revisions.json`.
  The PDF and website show the same last revision date. Unchanged rebuilds,
  copies, and checkouts must preserve it. Use `--sync-only` to verify existing
  files; changed sources require a rebuild. Publish each PDF, its matching
  source and dependencies, and its revision record together.
- Build and inspect the schedule before deployment. After deployment finishes,
  verify the live schedule, both links for every updated lecture, and that
  the served files and displayed timestamps match the intended release.
  Report publication only after these checks; distinguish local builds and
  commits from material available on the website.
