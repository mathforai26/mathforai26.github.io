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

Every lecture page shows its compilation time, including a UTC offset. The
standalone scribe template includes the same footer. Recompiling unchanged
notes also updates this timestamp.

Build the notes and synchronize the timestamps shown beside website PDF links:

```sh
python3 scripts/build_lecture_notes.py
```

Pass source paths to build selected lectures. If PDFs were compiled in an
editor, run `python3 scripts/build_lecture_notes.py --sync-only` before publishing.
The helper reads the footer on every PDF page and writes `_data/pdf_builds.json`;
a website rebuild alone does not change these values. Beneath each lecture's
description in `_pages/schedule.md`, use
`{% include lecture-notes.html lecture="lecture03" %}` with the corresponding
PDF basename. This supplies the standard PDF and LaTeX links and timestamp.
Keep each updated PDF, source, shared dependencies, and timestamp data together
when publishing. Follow the [publication checks](documents/misc_files/lecture-writing-standards.md#website-publication)
and verify the live schedule and downloads after deployment.
