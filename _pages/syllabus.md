---
layout: page
title: Syllabus
nav_order: 3
permalink: /syllabus/
---

# Syllabus

| | |
|:--|:--|
| **Course** | CMPUT 654: Mathematical Foundations of Modern AI Systems |
| **Term** | Fall 2026, September 1-December 8 |
| **Instructor** | [Csaba Szepesvári](https://sites.ualberta.ca/~szepesva/) |
| **Format** | Twenty-seven 80-minute lectures |
| **Meeting time** | Tuesday and Thursday, 3:30–4:50pm; no classes during Fall Reading Week, November 9–13 |
| **Room** | ED 2-135 |
| **Office hours** | Arrange by private message on Slack |
| **Course communication** | [Course Slack](https://cmput654fall2026.slack.com); enrolled students receive the join link through course channels, and auditors may use the encoded invitation below |

## Course philosophy

The course is organized around questions and pointed mathematical results. Both positive explanations and limitations matter. We will separate:

- what a model can represent;
- what a learning algorithm can find;
- what data and feedback identify;
- what generalizes statistically;
- what is correct exactly;
- what additional inference-time computation changes;
- what has been proved from what has only been observed.

Basic models such as logistic regression appear because they expose these distinctions cleanly. Current systems appear throughout because the goal is to understand why the modern recipe could work.

## Assessment

| Component | Weight |
|:--|--:|
| Six homework assignments | 60% |
| Final oral examination | 20% |
| Scribing / polished lecture note | 10% |
| Research-question notes | 10% |
| **Total** | **100%** |

### Homework: 60%

There will be six equally weighted homework assignments, approximately one every two weeks. A typical assignment will cover two weeks of material and contain about four substantial problems, often divided into parts. Problems will ask students to prove results, work through revealing examples, construct counterexamples, and explain what a mathematical result says about an AI system.

The lowest two homework grades will be replaced by 80/100, with no request or explanation required, unless those grades already exceed 80/100. A zero for an unsubmitted assignment is eligible for this replacement. After the replacements, the six equally weighted grades determine the 60% homework component.

Assignments must be typeset using the provided [LaTeX homework template]({{ '/documents/misc_files/homework_template.tex' | relative_url }}) and submitted through [Canvas Assignments](https://canvas.ualberta.ca/courses/37231/assignments) as standardized ZIP archives containing the PDF, LaTeX source, and any supporting files. The naming convention and other submission details appear on the [coursework page]({% link _pages/coursework.md %}).

### Final oral examination: 20%

Each student will have an individual oral examination during the
final-examination period. The total examination time will be between 30 and 60
minutes, with approximately 30 minutes as the usual target. At least one week
beforehand, the instructor will publish a pool of approximately 8–12 possible
questions. At the beginning of the examination, the student will draw one
question at random from this pool.

The student will have 10 minutes to prepare. During this period, the student may
consult any amount of their own handwritten notes. Printed materials and
electronic devices are not permitted. The student may prepare a separate
handwritten exam note of unrestricted length.

The student will then present the answer at the board. During the presentation,
the student may consult only the exam note produced during the preparation
period; the original handwritten notes may no longer be used. The exam note
will not be collected. The instructor will ask follow-up questions throughout
the presentation to check and clarify the student's understanding. Grading will
be based on the correctness and depth of that understanding, the clarity and
organization of the explanations, the appropriate use of mathematical
formalism, and the student's responses to follow-up questions.

### Scribing / polished lecture note: 10%

Each student will sign up for one lecture and prepare a polished note. The note
should reconstruct the lecture's question, mathematical setup, central results
and arguments, relevance to modern AI, and the boundary of the conclusions. It
should be a useful mathematical exposition, not a transcript. Near the end,
include a compact **Glossary** collecting the important new vocabulary
introduced in the lecture. Include a term when the note gives it a technical
meaning needed to follow the lecture or when the term is likely to recur later
in the course. Persistent notation and diagram conventions also belong in the
glossary; ordinary mathematical words, implementation details, named models,
libraries, and terms confined to optional background can be omitted. Define
terms at first use in the main text; the glossary is a recap.

Throughout the course, every vector is a column vector. If a matrix stores one
vector per position, its rows contain the transposes of those vectors. Write
every row-shaped vector explicitly as a transpose. Whenever a matrix or tensor
is introduced, state what its rows, columns, and any additional axes index. If
a diagram uses a different spatial orientation from the algebraic convention,
make that difference explicit. Let equations carry transparent algebraic
operations. Use prose to explain purpose, structural meaning, design choices,
and consequences. Include a short
**Bibliographical notes** section in the style of *Bandit Algorithms*: use
narrative prose to explain the origins of the ideas, how the cited work relates
to the lecture, and where its scope differs. Put the ordinary reference list at
the very end, after any appendices.

From the first draft, use **endnotes** for short remarks that refine the material
and may be skipped on a first reading. An endnote is too short to require an
appendix; substantial proofs and extended discussions belong in appendices. Keep definitions,
assumptions, and explanations needed for the main argument in the main text.
Collect endnotes immediately after the take-home messages, before the
bibliographical notes. During revision, check whether short
ancillary remarks would fit there and whether the main text reads correctly
without them.

Start from the [LaTeX scribe template]({{ '/documents/misc_files/scribe_template.tex' | relative_url }}).
The [lecture-writing standards]({{ '/documents/misc_files/lecture-writing-standards.md' | relative_url }})
give the conventions for drafting and reviewing notes.

**Submission:** Send the completed scribe note to the instructor in a private
message on the course Slack. Attach both the LaTeX source (`.tex`) and the
compiled PDF (`.pdf`). Do not submit scribe notes through Canvas or post them
in a public Slack channel.

The note is due within two calendar days of the lecture: a Tuesday lecture is
due by the end of Thursday, ideally by the end of Wednesday; a Thursday lecture
is due by the end of Saturday, ideally by the end of Friday. The [course schedule]({% link _pages/schedule.md %}) links to each lecture's
notes and LaTeX source. Lectures 1 and 2 also serve as examples for scribing. The
editable signup sheet will be distributed through Slack.

### Research-question notes: 10%

Students will develop and refine a research question related to the course. The assignment concerns the quality and precision of the question; students are not required to solve it. A first draft will receive feedback, followed by a revised final note. See the [research-question page]({% link _pages/research-question.md %}).

## Homework schedule and late work

Homework 1 will be released after Lecture 3 on September 8, so students
encounter course material before receiving graded work. It and the later
assignments will then follow an approximately two-week cycle, with target due
weeks 3, 5, 7, 9, 11, and 13. Late homework is not accepted. The automatic
replacement of the two lowest grades covers ordinary illness, overload, and
missed work without individual negotiation.

## Course communication

Routine announcements and discussion will use the [course Slack workspace](https://cmput654fall2026.slack.com). Enrolled students will receive the join link through course channels. Binding deadlines and course documents will remain on this website or the official submission system.

Auditors may recover the invitation by applying **ROT13** to the letters in the
following string. Digits and punctuation stay unchanged; ROT13 is its own
inverse.

`uggcf://wbva.fynpx.pbz/g/pzchg654snyy2026/funerq_vaivgr/mg-48wt3113n-w15Safjc9d9SCpQmSVUO_j?fbhepr=depbqr`

This invitation was generated on September 1, 2026. Slack reports that it
expires after 30 days; auditors who arrive later should contact the instructor.

## Collaboration and sources

Students may discuss ideas with classmates unless an assignment states otherwise. Every submitted solution must be written independently and must acknowledge collaborators and all sources consulted, including books, papers, websites, course notes, code, and computational or AI tools. Students must understand and be able to explain every step of their submission. Sharing written solutions or consulting solutions from earlier offerings is prohibited.

Generative-AI assistance is discouraged because it can prevent the learning that homework is intended to produce. One potentially acceptable use is to discuss ideas with an AI system as one would with a classmate, without asking it to produce a solution, proof, or text for submission. Any use must be disclosed precisely. Students remain responsible for their own reasoning and must be able to explain every step of their work.
