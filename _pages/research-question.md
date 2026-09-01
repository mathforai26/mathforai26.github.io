---
layout: page
title: Research question
nav_order: 6
permalink: /research-question/
---

# Research-question notes

The goal is to develop a good research question related to the mathematical foundations of modern AI. The assignment is about identifying and refining the question. You are not required to answer it or produce an original theorem.

## Deliverables

1. **Question sketch, encouraged by the end of Week 4:** a short paragraph identifying the phenomenon and the uncertainty.
2. **First draft, due at the end of Week 6:** approximately 1–3 pages. The instructor will return feedback.
3. **Revised note, due at the end of Week 12:** approximately 2–5 pages incorporating the feedback.

Together, the drafts and revision process account for 10% of the course grade. The detailed rubric will be posted before the first draft is due.

## What the final note should establish

The note should make clear:

- the precise question;
- why answering it would clarify something important about modern AI;
- the mathematical objects, information protocol, learner, resource bounds, or evaluation criterion involved;
- what is already known and what remains unknown;
- which assumptions may be doing essential work;
- what positive result, lower bound, construction, counterexample, or empirical distinction would count as progress;
- how the question was narrowed or improved after feedback.

Originality is welcome but unnecessary. Precision, coherence, technical understanding, and a clear separation between known results and conjecture matter more than ambition.

## Promising forms of question

- An empirical observation is puzzling (especially, if results are unexpectedly good). Is the phenomenon that is the subject of the observation real? Can theory explain what is happening?
- A claimed explanation of an empirical phenomenon relies on a toy model. Which prediction of that explanation distinguishes it from alternatives? Are there better versions of the toy model?
- A theorem assumes a particular distribution, symmetry, coverage condition, or initialization. Is that assumption necessary?
- Two training objectives share the same population optimum. When do finite data, misspecification, optimization, or sequential deployment make them behave differently?
- A negative result applies to a fixed-pass or bounded-memory model. Which additional resource removes the obstruction, and at what cost?
- A task is statistically easy but exact identification is expensive. Can a curriculum, verifier, or different information protocol close the gap?

These questions feel "small"; they are concerned with small alterations of a problem, or a statement. 
This is normal -- this is how one starts. An important point about developing a question is that it should feel genuinely interesting. As one thinks about the question, further questions may arise, the scope may broaden. One often reads some literature that feels relevant. Big conceptual questions are also fine, but usually are harder to develop.

Use the provided [LaTeX template]({{ '/documents/misc_files/research_question_template.tex' | relative_url }}).
