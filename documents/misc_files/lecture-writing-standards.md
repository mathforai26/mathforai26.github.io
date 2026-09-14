# Lecture-writing standards

These rules apply to both lectures and to later revisions.

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
- Verify mathematical references and inspect the rebuilt PDFs. Reorganization
  must not silently remove definitions, rationale, or conceptual distinctions.
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
- In appendices, restate each result immediately before its deferred proof and
  use a `proof` environment. Order appendices by the first substantive use of
  their material in the main text.
