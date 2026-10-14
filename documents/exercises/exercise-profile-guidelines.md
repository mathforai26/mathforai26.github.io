# Exercise-profile guidelines

Rate an exercise from the student's task, not from the brevity of a finished
solution. Assume that the student has learned the stated prerequisites and the
relevant lecture material, but has not seen the solution or been told which
method to use beyond the prompt and its hints.

Rate the required parts as one exercise. Optional extensions do not affect the
ratings. Use three separate judgments:

- **Difficulty** is the hardest intellectual step needed to find a correct
  solution.
- **Technical load** is the total amount and density of calculation, proof,
  notation, case analysis, and bookkeeping after the main ideas are known.
- **Estimated time** includes understanding the question, finding the approach,
  carrying it out, checking it, and writing a clear solution.

Do not infer one rating from another. A short proof can be difficult but
technically light. A long calculation can be conceptually direct but
technically dense.

## Difficulty

1. **Direct application.** The prompt identifies the relevant definition,
   identity, or procedure, and applying it requires no consequential choice.
2. **Familiar method.** The student must select or adapt a standard method,
   connect two nearby facts, or supply a short intermediate argument.
3. **Several ideas or a non-obvious reduction.** The student must discover a
   useful representation, coordinate several results, or organize a
   multi-stage argument whose plan is not immediate from the prompt.
4. **Substantial challenge.** The exercise requires a new synthesis, a delicate
   proof with several possible approaches or failure points, or a substantial
   construction beyond routine course work.

Judge the highest required conceptual hurdle, not the average difficulty of
the parts. A hint lowers difficulty only when it reveals that hurdle. A hint
that merely names a first step does not make the remaining argument direct.

## Technical load

1. **Light.** One short calculation or proof, with little notation and no
   substantial case analysis.
2. **Sustained.** Several linked calculations or proof steps, multiple parts,
   or moderate algebraic, probabilistic, or index bookkeeping.
3. **Dense.** Long or delicate algebra, several cases or interacting
   conditions, measure-theoretic or matrix bookkeeping, or many dependent
   derivations that must remain consistent.

Count all required output. In particular, a four-part exercise is not normally
technical-load 1 even if each individual step is standard.

## Estimated time

1. Under 20 minutes.
2. 20--45 minutes.
3. 45--90 minutes.
4. More than 90 minutes.

Estimate a serious first solution by a prepared student, not the time needed to
read or reproduce the model solution. Sum the work across required parts and
include verification and exposition. When uncertain at a boundary, compare the
exercise with established anchors in the same and adjacent lectures.

## Work types and learning gain

List a work type only when the student must produce that kind of output:

- `\exproof`: justify a general claim or bound;
- `\excalculation`: derive or evaluate an explicit mathematical quantity;
- `\exconstruction`: supply an example, counterexample, model, algorithm, or
  other object;
- `\excomputation`: write or run code, or carry out an explicitly computational
  experiment;
- `\exinterpretation`: explain, compare, diagnose, or state the consequence of
  a result.

Keep the canonical order above. Subject matter alone does not determine the
work type. For example, an exercise about an algorithm is not computational
unless the student must implement or run it.

State one learning gain that identifies the transferable conclusion or method.
Do not restate the sequence of subparts and do not promise a broader lesson than
the required work establishes.

## Supplementary-material marker

Use `\suppmark` when an exercise is based on supplementary lecture material.
The marker is independent of the exercise profile: it does not encode
difficulty, technical load, estimated time, or required work, and it does not
make the exercise optional when the exercise is assigned.

## Calibration procedure

Apply this procedure whenever creating or revising an exercise:

1. Solve the required parts without consulting the model solution.
2. Identify the hardest step that the prompt and hints do not supply.
3. Outline every calculation, proof obligation, case, and written explanation.
4. Assign difficulty from step 2 and technical load from step 3.
5. Estimate the full attempt time, including checking and writing.
6. Verify the work-type icons against the outputs explicitly requested.
7. Compare the result with nearby anchor exercises. Reconsider an outlier unless
   its prompt supplies a clear reason for it.
8. Recalibrate after observing student attempts. Record the reason before
   changing a scale definition; observed time alone need not imply a difficulty
   change.

As a final consistency check, reject profiles that describe only the polished
solution. Common warning signs are difficulty 1 for a problem requiring the
student to recognize an unstated theorem, technical load 1 for several required
derivations, and a time estimate that omits later parts.
