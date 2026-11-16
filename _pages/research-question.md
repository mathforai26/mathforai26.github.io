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
2. **First draft, due Sunday, October 11, at 11:59 p.m. Edmonton time (end of Week 6):** approximately 1–3 pages. The instructor will return feedback. [Submit the first draft on Canvas](https://canvas.ualberta.ca/courses/37231/assignments/823020).
3. **Revised note, due Sunday, November 29, at 11:59 p.m. Edmonton time (end of Week 12):** approximately 2–5 pages incorporating the feedback. [Submit the revised note on Canvas](https://canvas.ualberta.ca/courses/37231/assignments/823021).

Together, the drafts and revision process account for 10% of the course grade. The first draft receives qualitative feedback. The revised note is graded out of 100 points using the rubric below.

## What the final note should establish

The note should make clear:

- the precise question;
- why answering it would clarify something important about modern AI;
- the mathematical objects, information protocol, learner, resource bounds, or evaluation criterion involved;
- what is already known and what remains unknown;
- which assumptions may be doing essential work;
- what positive result, lower bound, construction, counterexample, or empirical distinction would count as progress;
- how the question was narrowed or improved after feedback.

The question should identify a substantive uncertainty that is not already an immediate consequence of known results. The note does not have to answer the question or contain an original theorem. Precision, coherence, technical understanding, and a clear separation between known results and conjecture matter more than ambition.

## Grading rubric for the revised note

### Motivation and significance: 15 points

The note explains why the question is worth asking, what larger issue in modern AI it concerns, and what different answers would teach us. Stating that the broad topic is important is not enough; the motivation must apply to the proposed question.

- **13--15:** The note gives a specific and convincing account of why the question matters and what would be learned from different possible answers.
- **10--12:** The relevance is clear, but some consequences of answering the question remain general or implicit.
- **6--9:** The note motivates the broad area but gives little question-specific justification.
- **0--5:** The motivation is absent, materially overstated, or disconnected from the question.

### Novelty and substance: 15 points

The note identifies a substantive uncertainty that is not already an immediate consequence of known results. Novelty may lie in the question itself, a comparison, an assumption, a regime, a proposed mechanism, or an empirical distinction. The note should explain why the question is more than a routine corollary, minor variation, or repetition of an existing result.

- **13--15:** The note clearly identifies a nontrivial uncertainty and explains what is new about the proposed question relative to known results.
- **10--12:** The question appears substantive, but its novelty or the distinction from the closest known result needs some clarification.
- **6--9:** The note suggests a potentially useful direction but does not establish that the stated question goes beyond routine consequences or familiar variants.
- **0--5:** The question is already answered by the cited work, follows immediately from known results, or has no identifiable substantive content.

### Related work and positioning: 20 points

The note identifies the closest relevant theoretical or empirical work, describes what that work establishes, and states the assumptions needed to compare it with the proposed question. Citations must support the claims attributed to them. The goal is a focused account of the literature needed to locate the question, not an exhaustive survey.

- **18--20:** The related work is accurate, well selected, and technically specific, and the relation to the proposed question is explicit.
- **14--17:** The central literature is relevant and mostly accurate, but an important assumption, conclusion, or comparison needs clarification.
- **8--13:** The note names related work but summarizes it too broadly, relies on unsupported claims, or leaves its relation to the question unclear.
- **0--7:** The necessary related work is largely absent or materially misrepresented.

### Soundness and feasibility: 30 points

The question must be defined well enough that its possible answers can be distinguished, and the mathematical or empirical reasoning must be internally consistent. The note should also give a credible initial attack plan. Examples include adapting a method used on a related problem, studying a restricted case, carrying out a preliminary calculation, constructing a counterexample, or designing an experiment that distinguishes competing explanations. The note must explain how the proposed approach bears on the question and what outcomes would count as progress.

The attack plan does not have to guarantee success. Theoretical research is inherently uncertain; feasibility means that the note gives a reasoned way to begin and a plausible route to informative partial progress. An analogy with an existing proof technique can be enough when the note explains why the technique may apply. For an empirical question, listing experiments is not enough unless the note explains how their possible outcomes would distinguish the competing answers.

- **27--30:** The question and setup are precise and internally consistent. The proposed approach is technically grounded, addresses the question, and could produce informative partial progress.
- **21--26:** The main question is sound and the initial approach is plausible, but one consequential definition, assumption, methodological step, or interpretation remains unclear.
- **13--20:** The topic is identifiable, but important parts of the question or setup remain underspecified, or the note lists methods without explaining how their outcomes would answer the question.
- **0--12:** The question cannot be interpreted reliably, the reasoning contains serious inconsistencies, or the note gives no meaningful way to begin investigating it.

### Writing and presentation: 10 points

The note is self-contained, coherent, and direct. The motivation, formal setup, related work, proposed question, and initial approach concern the same issue. Notation and terminology are consistent, claims have clear status, and citations allow the reader to identify the sources.

- **9--10:** The note is clear, coherent, and technically careful throughout.
- **7--8:** Minor writing, organization, notation, or citation problems do not impede the argument.
- **4--6:** Recurrent presentation problems make parts of the question or reasoning difficult to follow.
- **0--3:** Presentation problems prevent reliable assessment of substantial parts of the note.

### Response to feedback: 10 points

The revision note identifies substantive changes from the first draft and explains how those changes sharpened, narrowed, corrected, or otherwise improved the question. The final note should address the important issues raised in the feedback. A suggestion may be declined when the revision note gives a technically sound reason.

- **9--10:** The final note responds thoughtfully to the main feedback and makes the warranted substantive changes. A strong first draft can receive full credit with few changes when the revision note gives sound reasons for retaining the original choices.
- **7--8:** The revision addresses most important feedback, with one significant issue only partly resolved.
- **4--6:** The revision makes some relevant changes but leaves central feedback unaddressed or explains the changes only generally.
- **0--3:** The revision does not engage substantively with the feedback or omits the required revision note.

| Criterion | Points |
| --- | ---: |
| Motivation and significance | 15 |
| Novelty and substance | 15 |
| Related work and positioning | 20 |
| Soundness and feasibility | 30 |
| Writing and presentation | 10 |
| Response to feedback | 10 |
| **Total** | **100** |

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
