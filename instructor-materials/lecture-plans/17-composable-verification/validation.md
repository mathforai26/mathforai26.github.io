# Validation: composable textual verification

Date: 2026-11-01. Private technical companion; no publication.

## Semantic certificate layer, runtime corollary, and universality — 2026-11-01

The introduction now places the construction in the line from finite rule
systems, abstract proof systems, and proof-carrying code to modern learned
verifier and debate methods. The paragraph states the present question at the
level needed for orientation; detailed comparisons remain in the
bibliographical notes.

The note now separates the semantic certificate result from its implementation.
Section 2 defines soundness relative to the truth set, finite rule libraries,
certificates, and finite-rule certifiability. The certificate theorem proves by
induction that every answer certificate over truth-preserving rules ends in a
correct answer. Justifications, model calls, verifier competence, and runtime
data structures no longer enter this theorem.

Section 3 relates finite textual rules to finitary inference systems, Post
canonical systems, unrestricted grammars, Cook--Reckhow proof systems, and
mechanical proof checking. Its universality theorem states the recursively
enumerable expressive power obtained when intermediate assertion
representations may be chosen. The text distinguishes a general finitary rule
schema from modus ponens and gives the precise curried-implication encoding
when implication is available.

Sections 4--6 now implement the semantic result. A rule library contains rules
only; a separate annotation assigns justification texts. The target verifier
is sound when every accepted annotated rule is truth-preserving. For any
finite sound library, exact comparison with its finite annotated query table
defines a sound target map. The revised runtime theorem derives reliability by
invoking the certificate theorem, preserves certificates mechanically, and
obtains completeness by exhaustive search. A new corollary states directly
that finite-rule certifiability supplies a finite query bound and a sound
bounded verifier target.

The long-input definitions and propositions now use semantic sound libraries;
accepted annotations enter only when invoking the runtime theorem. The
bibliographical notes compare the construction with Post systems,
Cook--Reckhow proof systems, proof-carrying code including untrusted proof
rules, foundational proof certificates, trained mathematical verifiers,
debate, doubly efficient debate, and prover--verifier legibility training.

The mathematical audit checked the types of libraries, annotations,
certificates, goal claims, and target maps; the induction in the certificate
theorem; both directions of the recursively enumerable correspondence; the
finite-table verifier construction; and the quantifier order in the runtime
reliability and completeness claims. All 61 executable tests pass. A forced
33-page build has no warnings, unresolved references, or overfull/underfull
boxes. Every page was rendered and visually inspected, with full-size checks
of the new certificate theorem, universality discussion, runtime theorem and
corollaries, and bibliographical notes. No publication was performed.

## Short-to-long development and generated coverage rules — 2026-11-01

The short-request examples now precede the long-input abstraction. Their final
subsection identifies the precise length-sensitive calls: interpreting the
complete arithmetic question, judging the desk specification with the complete
request quoted, and interpreting the concrete tax rules and facts. General
logical rules, list rules, and the final `Goal(x,y)` comparison remain valid
with long runtime substitutions.

The fixed-parser construction was replaced by a coverage-certificate
construction. A generator may propose a parsing derivation, reduction
sequence, sequential certificate, dependency certificate, or exact
reconstruction. The runtime performs only generic operations on strings,
substitutions, intervals, and references. The verifier judges the bounded
semantic rules, including finishing rules that connect a complete input
summary to an answer.

Arithmetic parsing and reduction now motivate the general definition. The
note defines the lossless textual constructor `Account(x,m)` and calls a family
compositionally accountable when one finite accepted library derives such a
claim for every request in the family. The new lifting theorem uses finite
accepted accounting and solution libraries. Extending an exact account claim
to `Goal(x,y)` gives the coverage assumption used by the runtime theorem.
The main text distinguishes this formal result from the compositional
verification thesis: a human-clear organization is expected to admit such a
representation when its verifier questions have a uniform fixed length bound.

The long-input examples now begin with arithmetic expressions. The generator
may certify a parse through grammar schemas or account for the expression by
an exact reduction sequence; no arithmetic parser is built into the runtime.
The tax example now describes the generator as proposing the block and list
organization. Exact concatenation, interval use, sequential processing, and
the final comparison account for the complete tax input, including
exclusions.

All 61 runtime tests pass. A forced 31-page build has no warnings, unresolved
references, or overfull/underfull boxes. The complete PDF was rendered and
visually inspected, with targeted full-size inspection of the new coverage
theorem, informal thesis, arithmetic reduction, and tax transitions. No
publication was performed.

## Reader orientation and operational vocabulary — 2026-10-31

The introduction now defines a runtime at its first use as an ordinary
software program that controls model calls and leaves the detailed architecture
to Section 2.

Section 2 begins from the semantic objects defined in Section 1 and then
introduces a model call, the generator and verifier functions, candidate,
certificate, record, claim, checking question, and verifier call in dependency
order. A four-step account gives the complete data flow, a separate paragraph
assigns responsibilities to the three components, and a one-record arithmetic
example traces the path from request to returned answer. Only then does the
section introduce templates, rules, the target verifier map, and the formal
certificate definition. The text identifies the generate-then-verify order and
the sequence of generator attempts as choices made for a simple runtime and
completeness proof. Verification may be interleaved with generation, and later
proposals may depend on earlier verifier judgments. New technical terms are
marked at their definitions.

Section 3 distinguishes the fixed candidate format from a generator's
arbitrary output, explains interval resolution before the pseudocode uses it,
and then defines the full runtime from the generator, verifier, and checker.
Routine pseudocode helpers remain prose operations rather than receiving
additional mathematical state spaces.

The fourth record field is now called `justification`. The note and executable
companion state that this text may help the verifier assess a statement or
rule; the runtime never treats it as an established claim or an additional
premise. The former abstract phrase “explicit explanation” has been replaced
by the defined term “certificate.” The quotation scheme now defines its
decoding map before naming the pair of maps, uses notation distinct from the
later long-input parser, and states the injectivity used in the reliability
proof.

All 61 runtime tests pass. A forced 30-page build has no warnings, unresolved
references, or overfull/underfull boxes. Pages 1--7, covering the introduction,
Sections 1--4, the algorithm, and the theorem proof, were rendered and visually
inspected. No publication was performed.

## Long-format addition and consolidated tax treatment — 2026-10-31

The short-request section now ends with the simple tax example. All discussion
of unbounded inputs has moved to a separate long-format-input section. Its
first example gives a complete uniform construction for addition of two
arbitrarily long decimal strings: bounded digit transitions, a suffix-summary
rule, an exact finishing rule, and a proposition proving a fixed query bound
and a $2n+2$-record certificate. The following paragraph briefly indicates how
other arithmetic operations and fixed formal proof calculi use analogous local
summaries.

The structured tax example is the second subsection of the long-format-input
section. The former standalone section about a tax code exceeding the verifier
buffer was removed. Its useful content is now a compact extension of the tax
example: ordered provision records, prefix-execution summaries, an
order-sensitive calculation, the answer-condition rule, and one uniform
coverage proposition. Repeated input construction, answer linking, rejection
logic, and runtime explanations were deleted. A final paragraph explains how
named cross-references lead from a sequence to a labelled dependency graph.

All 61 runtime tests pass. A forced 28-page build has no warnings, unresolved
references, or overfull/underfull boxes. The long-addition pages and the
rewritten long-tax pages were rendered and visually inspected. No publication
was performed.

## Direct statements and the three-record arithmetic example — 2026-10-31

The certificate presentation now distinguishes a direct statement from a
parameterized rule. A direct statement has no premises or holes. The runtime
recognizes that case mechanically and sends a statement query without empty
premise and conclusion scaffolding. Parameterized implications retain the
general rule format.

The grade-school arithmetic subsection now begins with the possible one-call
certificate and then traces a three-record certificate: interpretation of the
question, evaluation of the expression, and one reusable implication connecting
those claims to the answer. The text specifies the generator's bindings and
premise references, the material sent to the verifier, and the runtime's exact
comparisons. The executable companion exports the matching accepted trace and
three complete English checking questions. The earlier twelve-record evaluator
remains available as the granular version used by later examples.

The subsection also explains why an arbitrarily long arithmetic expression
requires compositional syntax. A parsed expression tree supports local
evaluation records; unbounded intermediate numerals require an additional
digit-and-carry decomposition.

All 61 runtime tests pass. A forced 28-page build has no warnings, unresolved
references, or overfull/underfull boxes. The revised arithmetic pages and the
updated query-construction appendix were rendered and visually inspected. No
publication was performed.

## Generic compositional treatment of long inputs — 2026-10-31

The two informal input subsections were removed from Section 1. The section
now ends with the precise distinction used later: input format affects
completeness, while the general runtime theorem proves reliability for every
string request whenever it returns an answer.

A new section after the runtime theorem defines a compositional input format.
It consists of a finite ranked collection of labels, a compositional renderer,
and a lossless partial parser. Bounded semantic leaves are checked directly;
unbounded opaque-data leaves are handled by fixed universal rules with text
holes. Fixed constructor rules lift summaries from children to their parent.
The new lifting theorem proves by induction over the parsed tree that these
local checks establish a summary of the exact complete request and discharge
the finite-explanation assumption of the runtime theorem. Its statement keeps
task-specific solution reasoning as a separate premise and states the
competence condition needed to invoke the runtime theorem.

The runtime performs the syntactic parse and exposes the tree to the
generator. The generator proposes the summaries, task-specific reasoning, and
answer. The existing checker receives ordinary literal bindings and therefore
needs no semantic parser. The structured-tax and long-code sections now state
how their block, list, and sequence constructions instantiate the generic
method. The short-request examples remain applications of the original
runtime theorem.

The mathematical audit checked the types of the parser, renderer, tree and
string constructors, the round-trip identities, finiteness of the combined
library, and the dependence of the uniform query bound. Opaque-data leaves
were included because the tax family permits arbitrarily long quoted names.
All 60 runtime tests pass. The final 28-page build has no warnings, unresolved
references, or overfull/underfull boxes. Pages 7--10 and the revised tax
transitions were rendered and visually inspected. No publication was
performed.

## Rewritten Section 1 and explicit English `Ask` construction — 2026-10-31

The user-rewritten first section received local grammatical and typographical
corrections without changing its organization. A subsequent correction defines
`S = Sigma*`, states that every text has the type required of an answer while
`Q` determines correctness, removes the repeated definition of `dom(Q)`, and
defines reliability relative to `Q` through the graph of the partial system
map. The quotation-parser presentation was left unchanged at the user's
request.

Appendix A now explains how the runtime constructs an English checking
question. It states `Ask(r,e) = PROMPT || "\n\n" || QueryBody(r,e)`, displays
the fixed English instructions, includes the executable `query_body` and
`render_query` functions directly from `query_text.py`, and gives the complete
body for the direct judgment `1 + 1 = 2`. The construction is mechanical and
does not interpret the supplied rule.

All 60 runtime tests pass. The isolated build has 26 pages and no warnings,
unresolved references, or overfull/underfull boxes. Every page was rendered
and visually inspected, with the revised Section 1 and Appendix A checked at
higher resolution. The checked PDF replaced `note.pdf`. No publication was
performed.

## Mathematical setup and Section 1 — 2026-10-31

The document is now titled *Unbounded reliability from composable textual
verification*, with the subtitle *A task-independent runtime with bounded
verifier calls*. The introduction defines the intended contrast: requests,
answers, and verification arguments have no fixed length bound, while each
verifier call does. Section 1 is titled *The reliability objective and the
input model* and opens by stating that it defines the correctness objective
and the input structure used by the later construction.

Section 1 now works over finite strings in a fixed finite alphabet. It defines
quotation by a map and a partial parser satisfying
`P(quote(s) || t) = (s,t)`, with a length-prefixed construction as an example.
UTF-8 and JSON now appear only in the implementation appendix. The main text
also states the required cost property of the runtime operations: parsing,
copying, concatenation, quotation, and comparison are fixed syntactic
algorithms, linear in the text they read or produce.

The semantic setup now chooses the correctness relation `Q`, the set of true
assertions `T`, and the goal constructor jointly. The exact English goal
constructor remains displayed, and the compatibility condition is
`T cap range(Goal) = Goal[Q]`. The target family satisfies
`D subseteq dom(Q)`. Reliability is
`graph(F|_dom(Q)) subseteq Q`, while completeness on the target family is
`D subseteq dom(F)`. The text explains that behavior outside `dom(Q)` is
irrelevant unless input classification is included in the task, and gives the
corresponding totalization with a distinguished answer. The runtime theorem
and proof use the revised types and restricted reliability statement.

The isolated final build has 25 pages and no warnings, unresolved references,
or overfull/underfull boxes. All pages were rendered and visually inspected;
pages 2--5 were also inspected at higher resolution. The implementation is
unchanged, so the preceding executable-example tests remain applicable. The
checked PDF replaced `note.pdf`. Repository-wide `git diff --check` reports
only the pre-existing trailing whitespace in `documents/scribes/lecture04.tex`.
No publication was performed.

## Revised introduction — 2026-10-31

The second introduction paragraph now states the central mechanism at the conceptual level: a generator proposes records, a checking model judges direct claims and general implications, and the runtime checks each use and stores the resulting claims. It also states the missing connection to the original problem: the runtime accepts the record sequence only when the mechanically constructed final claim says that the proposed answer correctly answers the exact original request. The input assumption is now named where the broad conclusion is stated. Short requests enter directly; requests of arbitrary size are mildly structured, meaning that they explicitly state the scope and composition needed to combine their parts. For such inputs, the introduction claims bounded checking without unduly limiting the power of the complete arrangement or sacrificing reliability. The following paragraph now transitions directly to the mechanism by saying that general rules and their particular uses are checked separately, then assigns the three component roles. Section 1.2 defines the input term, and the take-home messages and glossary use it consistently. The soundness, finite-library, and completeness-by-search conditions are introduced only after the required objects have been defined. A separate theorem-preview paragraph that repeated those conditions was removed.

The unsupported statement that explicit scope and composition are mild requirements satisfied by most practical scenarios was removed. The introduction now makes the narrower claim established by the examples: the long-request families considered in the note use those conventions. The mathematical statements and implementation are unchanged.

The source passes `git diff --check`. The isolated 24-page build has no warnings, unresolved references, overfull boxes, or underfull boxes. The revised first page was rendered and visually inspected; pagination is unchanged. The checked PDF replaced `note.pdf`. No publication was performed.

## Worked input conventions and rejected candidates — 2026-10-30

The examples now implement the input conventions in both the note and the executable generators. The desk certificate starts by checking the proposed answer requirements against the complete free-text request; the finishing rule uses that checked specification. Its accepted construction has **163 records**. The long tax requests delimit Definitions, Part E, and Case blocks, state their scope and composition, and use exact input intervals proposed by the generator. Section 6 displays a complete input generated from the code. Section 7 adds ordered cap provisions alongside deductions: cap-then-deduct yields 19,999, whereas deduct-then-cap yields 20,000 and the opposite eligibility answer.

The prose distinguishes interpreting a request, accounting for its complete source text, and calculating an answer. The prefix execution claim explicitly does the latter two together. The former technical uses of “reading” were replaced with the operation intended. Exact query files, TeX excerpts, trace milestones, and measurements were regenerated together. The generic `runtime.py`, reusable `example_rules.py`, and query renderer `query_text.py` are byte-for-byte unchanged from the preceding revision.

Each worked scenario now includes rejected proposals. Eight executable cases in `traces/rejected/` cover a missing desk entry, an opposite simple-tax answer, an arithmetic answer inconsistent with the calculation, a false multiplication, an omitted active tax exclusion, an omitted deduction, reordered provisions, and an oversized direct query for a correct answer. The traces record the actual first failure, accepted claims, model queries and verdicts, exact unequal texts, or the oversized query that was not sent. The index identifies each case and its rejection reason. All cases use the same runtime, verifier fixture, and bound as the successful examples.

The mathematical audit checked the desk specification and finishing rule, its revised record count, the exact block bindings, the meanings of the tax scope and exception conventions, and the mixed-provision induction. Both deduction and cap preserve a balance in 0 through K, so the finite-library argument and bound **4m + 2ℓ + 32** still hold. The central theorem and proof are unchanged. Independent review by `/root/lecture17_review` approved these constructions and all eight failure explanations, and independently ran the tests. Two English precision fixes from that review were applied: desk lines must consist of one sentence after excluding the newline, and a Part E clause excludes the applicant only when it applies.

Validation commands:

```sh
python3 examples.py
python3 -m unittest -q test_runtime.py
latexmk -g -pdf -interaction=nonstopmode -halt-on-error -outdir=/tmp/lecture17-worked-inputs/build note.tex
```

All **60 tests passed**, including source/query synchronization, exact rejected-trace reproduction, missing specification premises, changed scope markers, wrong source intervals, and order-sensitive computation. The fixture accepts **775 distinct queries**, with maximum complete query length **4,417 bytes**. The 301-provision code occupies **18,107 bytes**, its complete request **18,671 bytes**, and its accepted certificate has **934 records**. The 512-exclusion request occupies **55,750 bytes** and is checked with queries no longer than **4,115 bytes**. `traces/statistics.json` contains the current measurements; earlier sections below retain historical measurements.

The writing gate covered component responsibilities, the short-to-long-input transition, terminology, typed notation, proof and claim status, standalone reading, and the deletion test. Comparative passages remain Lecture 14's finite-controller result and Lecture 16's model/runtime motivation. Optional copying costs remain in an endnote. No exercises or new external results were introduced; the prescribed order of endnotes, bibliographical notes, glossary, appendices, and references is preserved.

The isolated build has **24 pages**, no warnings, no unresolved references, and no overfull or underfull boxes. Every page was rendered and visually inspected, including the new input display, desk specification, rejection explanations, mixed-provision formulas, and measurement table. The final wording changes were rendered and their affected pages checked again. The checked PDF replaces `note.pdf`. Revised text/code files pass direct trailing-whitespace checks. Repository-wide `git diff --check` still reports only the previously noted whitespace in `documents/scribes/lecture04.tex:2030`, which was not changed.

The revision updates the private companion source, PDF, example generators, asset generation, tests, generated TeX, traces, and this validation record. The canonical Lecture 17 files were not edited. No commit, push, upload, or publication was performed.

## Free text, long-input conventions, and the coverage distinction — 2026-10-30

Section 1 now treats short free-text requests before long requests. A short request is quoted in full when the verifier checks the proposed answer requirements; the output may still be long. Long-input conventions identify block roles, composition and scope, named definitions and references, and explicit exceptions. The conventions guide certificate construction; coverage remains a separate existence requirement, proved only for the stated example families. The tax-code introduction connects its supplied structure to those conventions.

The runtime listing now writes `Resolve(bindings, x, y, A)` explicitly, matching the existing input, answer, and earlier-claim sources in `runtime.py`. The explanation after `CHECK` distinguishes the final exact-text comparison from the verified inferences establishing the claim's truth. It explains why hiding an arbitrary request behind a hole cannot justify an answer: the checked rule must hold for every substitution. Copying costs and a possible shared representation are deferred to an endnote. Bibliographical notes attribute the relevant conventions to SBVR 1.5, Sections 13 and 16.3–16.4, and Cramer's 2013 Naproche thesis, Section 7.2; both primary sources were checked.

The writing gate covered the opening-to-theorem development, sentence coherence, direct wording, deletion test, standalone reading, responsibilities, claim status, and source attribution. Comparison passages were Lecture 16's reading guide and model/runtime motivation, and Lecture 14's finite-controller corollary and interpretation. The independent reviewer `/root/lecture17_review` reported PASS with no must-fix findings, including the distinction between conventions and guaranteed coverage. No exercises were added or changed. Endnotes, bibliographical notes, glossary, appendices, and references retain the prescribed order.

All mathematical definitions, the coverage assumption, theorem and proposition statements, proofs, and mathematical displays match the preceding source. The code, generated query excerpts, and traces are unchanged. All **55 tests passed**, including source/query synchronization checks (`python3 -m unittest -q test_runtime.py`).

The final isolated build (`latexmk -g -pdf -interaction=nonstopmode -halt-on-error -outdir=/tmp/lecture17-input-coverage/build note.tex`) has **22 pages** and no warnings, unresolved references, overfull boxes, or underfull boxes. All pages were rendered and visually inspected. Two `Needspace` adjustments keep query introductions with their text; the four affected pages were rendered and inspected again, and the remaining page images are unchanged. Endnote forward and return destinations are present. The checked PDF replaced `note.pdf`.

Changed deliverables are `note.tex`, `note.pdf`, and this validation record. The changed text files have no trailing whitespace. Repository-wide `git diff --check` still reports the pre-existing trailing whitespace in `documents/scribes/lecture04.tex:2030`, which was left untouched. The canonical Lecture 17 files were not edited. No commit, push, upload, or publication was performed.

## General introduction and earlier explanation of responsibilities — 2026-10-30

The opening now develops the reliability problem, bounded verification as the learning target, and the division of work before introducing notation. It explicitly separates checking a general rule from checking its use. A desk-list illustration explains how short rule queries justify growing stored claims. Section 1 loses the repeated explanation, and Section 7 now gives a brief reminder tied to the code-prefix construction. The source is shorter overall.

The standalone-reading, deletion, comparative-prose, operational, and claim-status audits passed. Independent review approved the organization and component responsibilities after three small wording and repetition repairs. Mathematical definitions, assumptions, statements, proofs, and runtime listings match the preceding source. Code and generated assets are unchanged; the existing 55-test validation remains applicable.

The isolated build in `/tmp/lecture17-general-introduction/build` has **20 pages**, no warnings, no unresolved references, and no overfull/underfull boxes. All pages were rendered and visually inspected. Two local pagination adjustments keep verifier-query labels with their text; the affected pages were rendered and inspected again. The checked PDF replaced `note.pdf`. Only `note.tex`, `note.pdf`, and this validation record changed locally in this revision.

## Section 7 overview and component responsibilities — 2026-10-30

Section 7 now explains the general method before the allowance-code construction. The opening separates the generator's choice of pieces, context-explicit claims and rules; the verifier's judgments of short general rules and direct claims; and the runtime's exact substitutions, premise comparisons, storage, and final connection to the original request. The overview explains why instantiated claims can grow while verifier inputs remain short. A new subsection marks the start of the specific code example.

The local prose, standalone-reading, operational, and mathematical-consistency audits passed. Independent review requested a more precise final-comparison sentence so that the overview still permits checked reformulations; that repair was applied. All mathematical environments, assumptions, proofs, and runtime listings are unchanged, as verified against the preceding source. Code and generated query assets are unchanged, so the preceding 55-test result remains applicable without another test run.

The isolated build in `/tmp/lecture17-section7-overview/build` has **20 pages**, no warnings, no unresolved references, and no overfull/underfull boxes. The entire PDF was rendered. Pages 1–12 are pixel-identical to the previously checked version; all eight changed pages were visually inspected. The checked PDF replaced `note.pdf`. This revision changes only `note.tex`, `note.pdf`, and this validation record, locally.

## Readable queries, reliability, and a code larger than the buffer — 2026-10-30

The current PDF has **20 pages**. Verifier queries now contain English premises and conclusions with explicit text holes, instead of JSON syntax trees. `query_text.py` renders the four existing template operations and provides a decoder for representation checks. Escaping and variable-length fences distinguish literal text, placeholders, nested quotation, and evidence. The generic checker's validation, substitution, premise matching, and final input/answer comparison are unchanged.

The displayed query excerpts, common instructions, prefix-claim definition, and measurement table are generated from the executable templates into `generated/`. Exact complete queries are saved in `traces/queries/`. Synchronization tests compare these files with their current code-derived content. Self-contained claims no longer carry an empty context wrapper; arithmetic and Boolean assertions distinguish numeral text from its value. Proposition 5.1 now states both rejection of every incorrect desk answer and coverage of the specified correct-answer family.

Section 7 adds a separate worked example in which the code itself exceeds the buffer. Its 301 allowance provisions each deduct one unit from earnings of 20,300. Every provision affects eligibility: 301 leave income 19,999 (Yes), whereas 300 leave 20,000 (No). The code occupies **18,065 bytes**, the complete request **18,461 bytes**, and the maximum complete verifier query **4,099 bytes**. The certificate has **934 records**. The generator constructs exact prefix-execution claims and supplies two scalar calculations per allowance. The runtime applies the same template and reference operations as before. The final reading rule combines the complete allowance text with the case and the previous exclusion construction.

Proposition 7.1 covers arbitrarily many allowance provisions and exclusions with one finite library for each fixed numeric bound K. The proof keeps every intermediate balance and deduction in 0 through K, checks soundness of the append and reading rules, and derives the bound 4m+2ℓ+32 on certificate records. The family explicitly uses canonical decimal numeral texts. Reliability still applies to all candidate generators under the main theorem's assumptions.

Validation:

- **55 tests passed**, including presentation roundtrips, adversarial quotation/fence/placeholder cases, source-to-answer checks, a complete code exceeding the buffer, rejection of an omitted allowance or an unsupported balance, empty and capped allowance sequences, and composition with the existing exclusion rules.
- The reproducible verifier fixture contains **771 complete queries**. All displayed measurements come from `traces/statistics.json`.
- Independent review checked both mathematical guarantees, the English queries, exact source reconstruction, the record count, and the prose sequence; all 55 tests also passed in that review. The requested canonical-numeral and roadmap corrections were applied.
- The standalone-reading, notation, deletion-test, claim-status, and operational passes checked the changed examples, new section, central theorem connections, glossary, and appendix. No exercises or new external results were introduced. The comparative prose review used the earlier Lecture 14 and Lecture 16 passages already selected for this companion.
- The isolated final build has no warnings, undefined references, or overfull/underfull boxes. All 20 pages were rendered and visually inspected; the four pages changed by the final wording corrections were rendered and checked again. The checked PDF was copied to `note.pdf`.
- Direct trailing-whitespace checks passed for the revised source, code, generated TeX, and this record. The writing-standards diff passes `git diff --check`.

Commands: `python3 examples.py`; `python3 -m unittest -q test_runtime.py`; `latexmk -g -pdf -interaction=nonstopmode -halt-on-error -outdir=/tmp/lecture17-readable-queries/build note.tex`.

All revisions remain local to the private companion, together with the earlier requested writing-standard update. The canonical Lecture 17 sources and published files were not changed. The sections below describe earlier revisions and their then-current measurements.

## Input handling and modular examples — 2026-10-30

That revision produced a **15-page PDF**. Section 1 now explains how bounded general rules apply to long stored texts, and how a reading certificate accounts for the complete input. Sections 5–6 share logical rules and typed expression evaluation. Desk instructions combine separately checked requirements before list assembly; the simple tax derivation uses complete sentences and general propositional rules; arithmetic establishes the question-to-expression equivalence before evaluating; the full tax example combines a complete source reading with deductions, income calculations, comparisons, and Boolean evaluation. Alternate arithmetic wording and negative tax cases have complete traces.

The mathematical review checked the logical rules under a common context, canonical numeral conventions, the reformulation rule's answer equivalence, typed evaluation including negative intermediate values, and the coverage family with variable case figures and unbounded exclusion lists. The family uses canonical numeral inputs in 0 through K and includes all required constants and scalar judgments in its finite library. Its certificate bound is 2m+36. An independent reviewer checked the exposition and implementation, reran all 41 tests, reproduced the table, and approved the construction after clarification of the numeral convention, the empty text, and the inclusion of zero in the natural numbers.

The generic `runtime.py`, runtime pseudocode, and central theorem and proof are unchanged. New shared templates are in `example_rules.py`; `examples.py`, `test_runtime.py`, and the exported traces were revised. `note.tex`, `note.pdf`, this validation record, and the historical-status notice in `prose-audit.md` were updated. The canonical Lecture 17 files were not modified.

Validation commands:

```sh
python3 -m unittest -q test_runtime.py
python3 examples.py
latexmk -g -pdf -interaction=nonstopmode -halt-on-error -outdir=/tmp/lecture17-input-examples/build note.tex
```

All **41 tests passed**. The fixture contains **156 distinct complete queries**, with a maximum of **5,750 bytes**. The 512-exclusion input has **55,552 bytes** and **1,060 records**, using the same query bound. The one-long-name case contains an 11,500-character name and likewise uses that bound. `traces/statistics.json` records all measurements.

The standalone-reading and deletion-test passes retained the requested explanations and removed repeated construction details by referring to the shared rules. The opening, theorem transition, and interpretation passages were compared with Lectures 14 and 16. Definitions, source-reading assumptions, proof quantifiers, record counts, bibliography placement, glossary, and appendix order were checked. No exercises or new external theorem attributions were introduced.

The isolated build has no warnings, unresolved references, or overfull/underfull boxes. All 15 pages were rendered and visually inspected, including the complete runtime listing, inference displays, tax derivation, arithmetic reformulation, and measurement table. The checked PDF was copied to `note.pdf`. Direct whitespace checks passed for all revised text/code files. All work remains local.

## Deletion-test revision — 2026-10-30

That revision produced a **12-page PDF**. A second complete reading removed another 591 source words, applying the test of what the reader would lose from each deletion. `prose-audit.md` updates the original 70 decisions and records further cuts. The deletion test is now in the lecture-writing standards and their pre-delivery audit.

The independent reviewer confirmed that the revised prose preserves the mathematical conditions and operational meaning. All mathematical statement and display blocks, code listings, example quotations, and the exact verifier prompt match the previous version. The opening, central result, examples, and conclusion were reviewed for coherence and compared with the relevant passages in Lectures 14 and 16. The runtime listing now stays on one page.

The final build used `latexmk -g -pdf -interaction=nonstopmode -halt-on-error -outdir=/tmp/lecture17-deletion-pass/build note.tex`. Its final log has no warnings or unresolved references. An earlier in-place PDF failed parsing; the isolated rebuild passed `pdfinfo` and full-page rendering. All 12 final pages were visually checked, and the checked PDF was copied to `note.pdf`.

Direct whitespace checks passed for the revised source, audit, and standards; `git diff --check` passed for the standards. The local changes are `note.tex`, `note.pdf`, `prose-audit.md`, this validation record, and `documents/misc_files/lecture-writing-standards.md`. No publication was performed.

## First prose revision — 2026-10-30

That revision produced a **13-page PDF**. `prose-audit.md` recorded decisions for 70 passages. The revision removed about 1,050 source words by deleting repeated disclaimers and consolidating necessary qualifications where they affect the argument.

An independent review confirmed that the cuts preserve the assumptions, theorem conditions, and operational specification. The opening now explicitly requires rules accepted by the verifier. All displayed mathematical blocks, formal statements, quotations, and code listings are unchanged.

The PDF was rebuilt with `latexmk -g -pdf -interaction=nonstopmode -halt-on-error note.tex`; the log has no warnings or undefined references. Every page was visually checked, including the changed final pages. The implementation is unchanged, so the earlier test results below remain applicable. This revision updates `note.tex`, `note.pdf`, this record, and the new prose audit locally.

The remaining sections record validation of the original 15-page version.

## Deliverables and scope

- `note.tex` and `note.pdf`: the explicit composition assumption, one generic runtime, the reliability/preservation/search theorem and its proof, four scenario examples, and precise scope limits.
- `runtime.py`: generic candidate checker, source-interval copying, template instantiation, explanation encoder, sequential search, and exhaustive candidate enumeration.
- `examples.py`: untrusted generators plus a finite verifier fixture. No semantic task logic occurs in the runtime.
- `test_runtime.py`: 33 protocol tests.
- `traces/`: full candidate records and accepted claims for five worked cases, all 58 exact verifier questions, and measured statistics.
- The parent planning index links this companion as the current technical result.

The canonical `documents/scribes/lecture17.tex` and `.pdf` were not edited or rebuilt. The earlier research note and prototype remain available. Ordinary mathematical language coverage is explicitly postponed. The result does not claim arbitrary tax-code coverage, practical learnability, efficient search, or robustness to noisy checking.

## Mathematical and operational audit

The audit fixed `Q` and the supported-assertion semantics before defining certificates. The accepted library is fixed for the whole task family; its bound counts the complete prompt, rule text, and evidence. Bindings, input lengths, and global references remain in runtime memory. Every rule is universally quantified over arbitrary strings; required typing and context appear in its premises or literal content.

The proof checks an induction over stored claims, exact premise matching, the final binding to both original request and answer, serialization of already explicit explanations, and termination of each finite candidate check in exhaustive search. The verifier may accept ground assertions without supplied proofs. Malformed semantic assertions are the verifier's responsibility; the runtime rejects only mechanical format or binding failures.

The coverage constructions are separate from the definition of acceptance. The desk construction covers every forty-entry sequence from a fixed finite suitable-entry set. The arithmetic construction covers the stated request template over fixed finite input-number sets when the required ground judgments are accepted. The long-code construction covers a fixed five-section cross-reference core, two cases, and arbitrary finite lists of false-flag exclusions with arbitrary text names. Its six rules account for the entire variable exclusion list and fact list. Adding or omitting a clause invalidates the original certificate through the final whole-input comparison.

All example acceptance claims explicitly retain verifier competence and a sufficiently large query bound. The input interval positions in the arithmetic example were checked against actual strings: `[43,45)`, `[50,52)`, `[56,57)`; the answer interval is `[0,3)`.

## Independent review

The separate reviewer `/root/lecture17_review` reviewed the theorem, proof, runtime, examples, and prose without editing. The reviewer found no blocking soundness, source-fidelity, or implementation issue and independently reproduced all size measurements. The review requested an explicit carry-forward of competence and query-bound assumptions into the example coverage claims; Section 5 now states those assumptions.

A second, narrow review covered the executable encoder, search loop, exhaustive generator, corrected intervals, and the revised assumption paragraph. The reviewer reported PASS and independently reran all 33 tests successfully. The reviewer also checked that enumeration replaces invalid UTF-8 byte strings only with rejected candidates and still reaches every valid finite encoding.

## Tests and quantitative evidence

Command: `python3 -m unittest -v test_runtime.py`.

Result: **33 tests passed**. The suite checks all scenarios, positive and negative tax answers, wrong answers, omitted and reordered premises, forward references, extra bindings, invalid intervals, changed source facts, omitted exclusions, added exceptions, false rules, evidence misuse, malformed JSON/templates, Unicode quotation, nonrecursive insertion, encoder preservation, sequential search, and enumeration boundaries.

Command: `python3 examples.py`.

Result: all worked and scale cases accepted using one unchanged 58-question fixture. Maximum complete question length: **4,155 bytes**.

| Example | Input bytes | Records | Maximum query bytes |
| --- | ---: | ---: | ---: |
| Forty desk instructions | 267 | 82 | 2,157 |
| Simple tax | 485 | 5 | 3,120 |
| Arithmetic | 58 | 4 | 2,269 |
| Full tax, three exclusions, either age | 1,343 | 9 | 4,155 |
| Full tax, 512 exclusions | 55,552 | 1,027 | 4,155 |
| Full tax, one 8,310-character name | 17,699 | 5 | 4,155 |

The fixture is an explicit table of designated semantic judgments, not a trained verifier. Tests validate the protocol, not the soundness of arbitrary model judgments. The soundness arguments for the table's rules are in the note.

## Expository pre-delivery gate

1. **Question and result map:** the opening states the natural-language AI reliability problem; Sections 1–4 define the assumption and prove the runtime theorem before examples.
2. **Topic sentences and motivation:** section openings and theorem transitions identify their purpose; the short-excerpt failure explains why composition rules are needed.
3. **Claim status:** assumptions, conditional theorems, constructive example coverage, test measurements, and unresolved coverage/learning questions are distinct.
4. **Operational specification:** record fields, source selector types, interval conventions, template semantics, complete queries, pseudocode, encoder, and search are specified. The implementation is linked to the mathematical operations.
5. **Standalone prose and coherence:** reviewed directly and independently. No prior conversation is needed to identify who supplies claims, how requests bind to answers, or why the input bound is uniform.
6. **Comparative prose:** compared the opening, theorem interpretation, and finite-target discussion with Lecture 14's finite-controller construction and Lecture 16's natural-language runtime motivation. The note preserves the distinction between finite local capability, external memory, system coverage, and learning.
7. **Notation:** strings, relations, templates, substitutions, rules, target/verifier maps, generator, source selectors, and stored texts have explicit types. Explanations are nonempty sequences; source selectors are distinct from resolved strings. No probability argument is used.
8. **Attribution:** Lamport and Metamath primary sources were checked. Background comparisons remain in bibliographical notes; no priority or broad-prose coverage claim is attributed to them.
9. **Deferred material and glossary:** necessary assumptions remain in the main text. Exact JSON and prompt conventions and reproduction instructions are in appendices. Glossary follows bibliographical notes; references are last. There are no ancillary endnotes or exercises to audit in this technical companion.
10. **Scope:** no change to delivered notes or student-facing artifacts. The companion and implementation are private local work.

## Build, visual review, and repository checks

Command: `latexmk -g -pdf -interaction=nonstopmode -halt-on-error note.tex`.

The PDF has **15 pages**. The final LaTeX log contains no undefined references, citation warnings, font warnings, overfull boxes, or underfull boxes. An initial missing color definition and a long constructor line were corrected before delivery.

Rendered the complete PDF with `pdftoppm -r 95 -png` and inspected every page. Checked theorem/proof placement, pseudocode, definition panels, tables, equations, quotations, headers, page numbers, and appendix transitions. After revisions, compared rendered-page hashes and inspected all changed pages again. No clipping, overlap, or illegible symbols remained.

Changed private sources pass a direct trailing-whitespace check. Repository-wide `git diff --check` reports pre-existing trailing whitespace in `documents/scribes/lecture04.tex:2030`; that unrelated file was not changed.

No commit, push, upload, or publication was performed.
