# CMPUT 654 — Mathematical Foundations of Modern AI Systems

Source for the Fall 2026 course website.

Public site: <https://mathforai26.github.io/>

## Structure

- `_pages/`: public course pages.
- `documents/assignments/`: assignment source and PDFs.
- `documents/misc_files/`: reusable LaTeX templates.
- `course-design-decisions.md`: internal decision ledger; it is not linked from the public site.
- `lecture-plans/`: local link to the canonical plans in the separate private
  instructor repository; it is excluded from the public site and repository.

Lecture authors and editors should follow the
[lecture-writing standards](documents/misc_files/lecture-writing-standards.md),
including the placement of short optional refinements in endnotes. The
[scribe template](documents/misc_files/scribe_template.tex) includes endnote
support; [AGENTS.md](AGENTS.md) requires these rules when agents write new
notes and revise existing ones.

## Local preview

Install the Ruby dependencies with `bundle install`, then run `./startlocalservice`.

## Lecture PDF versions

Every lecture page and its schedule entry show the same **Last revised** date,
including a UTC offset. It changes when the lecture source or an included file
changes. Unchanged rebuilds, copies, and checkouts preserve the recorded date.

Build the notes and update their revision records:

```sh
python3 scripts/build_lecture_notes.py
```

Pass source paths to build selected lectures. The builder records the actual
local inputs used by LaTeX and their content hashes in `_data/lecture_revisions.json`.
For changed inputs it uses their last Git change time, or their modification time
for uncommitted edits. It also writes the date into the source's `\lecturerevised`
command, so the downloaded LaTeX retains it when compiled separately.

After editing, use the builder before publishing. `--sync-only` checks existing
sources, PDFs, and records; it rejects stale files. A website rebuild alone does
not change revision dates. Beneath each lecture's
description in `_pages/schedule.md`, use
`{% include lecture-notes.html lecture="lecture03" %}` with the corresponding
PDF basename. This supplies the standard PDF and LaTeX links and timestamp.
Keep each updated PDF, source, shared dependencies, and revision records together
when publishing. Follow the [publication checks](documents/misc_files/lecture-writing-standards.md#website-publication)
and verify the live schedule and downloads after deployment.
