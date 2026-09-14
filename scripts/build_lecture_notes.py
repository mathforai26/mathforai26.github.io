#!/usr/bin/env python3
"""Build lecture PDFs with persistent source-revision dates for PDFs and the website."""
import argparse
from datetime import datetime
import hashlib
import json
import os
from pathlib import Path
import re
import shutil
import subprocess
import tempfile
import time

ROOT = Path(__file__).resolve().parents[1]
NOTES = ROOT / 'documents/scribes'
DATA = ROOT / '_data/lecture_revisions.json'
REVISION = re.compile(rb'(?m)^\\newcommand\{\\lecturerevised\}\{[^\r\n]*\}$')
STAMP = re.compile(r'Last revised:\s*(\d{4}-\d{2}-\d{2}\s+\d{2}:\d{2}\s+UTC[+-]\d{2}:\d{2})')


def digest(content):
    # The generated date is metadata, not a revision to the lecture itself.
    return hashlib.sha256(REVISION.sub(b'', content)).hexdigest()


def fingerprints(paths):
    return {str(p.relative_to(ROOT)): digest(p.read_bytes()) for p in sorted(paths)}


def modified_time(path, fingerprint):
    """Use Git's recorded change time for committed content; mtime for local edits."""
    relative = str(path.relative_to(ROOT))
    committed = subprocess.run(['git', 'show', f'HEAD:{relative}'], cwd=ROOT,
                               stdout=subprocess.PIPE, stderr=subprocess.DEVNULL)
    if committed.returncode == 0 and digest(committed.stdout) == fingerprint:
        return int(subprocess.check_output(
            ['git', 'log', '-1', '--format=%ct', '--', relative], cwd=ROOT, text=True))
    return path.stat().st_mtime


def revision_date(inputs, previous):
    if inputs == previous.get('inputs'):
        return previous['revised']
    changed = [name for name, value in inputs.items()
               if previous.get('inputs', {}).get(name) != value]
    # Removing an input also changes the source that included it.
    if not changed:
        raise RuntimeError('Input list changed without a source change; rebuild all lectures')
    latest = max(modified_time(ROOT / name, inputs[name]) for name in changed)
    date = datetime.fromtimestamp(latest).astimezone()
    stamp = date.strftime('%Y-%m-%d %H:%M UTC%z')
    return stamp[:-2] + ':' + stamp[-2:]


def recorded_inputs(recorder, source, records):
    """Read actual local inputs from TeX's recorder, including nested inputs and figures."""
    paths = {source}
    for line in recorder.read_text().splitlines():
        if not line.startswith('INPUT '):
            continue
        path = (source.parent / line[6:]).resolve()
        if not path.is_relative_to(ROOT):
            continue
        # External lecture labels are generated; track their source dependencies.
        if path.suffix == '.aux':
            lecture = NOTES / (path.stem + '.tex')
            if lecture != source and lecture.is_file():
                paths.add(lecture)
                paths.update(ROOT / name for name in records.get(path.stem, {}).get('inputs', {}))
        elif not path.is_relative_to(ROOT / 'outputs'):
            paths.add(path)
    return paths


def pdf_date(pdf):
    pages = subprocess.check_output(
        ['pdftotext', '-layout', str(pdf), '-'], text=True).split('\f')
    stamps = []
    for page in pages:
        if not page.strip():
            continue
        matches = STAMP.findall(page)
        if len(matches) != 1:
            raise RuntimeError(f'{pdf.name}: expected one revision footer on every page')
        stamps.append(' '.join(matches[0].split()))
    if not stamps or len(set(stamps)) != 1:
        raise RuntimeError(f'{pdf.name}: inconsistent revision dates')
    return stamps[0]


def verify(records, sources):
    for source in sources:
        record = records.get(source.stem, {})
        paths = [ROOT / name for name in record.get('inputs', {})]
        if not paths or any(not p.is_file() for p in paths) or fingerprints(paths) != record['inputs']:
            raise RuntimeError(f'{source.name}: source or inputs changed; run the lecture builder')
        expected = record['revised']
        macro = REVISION.findall(source.read_bytes())
        if macro != [revision_macro(expected)] or pdf_date(source.with_suffix('.pdf')) != expected:
            raise RuntimeError(f'{source.name}: source, PDF, and revision record disagree; rebuild')
        print(f'{source.stem}: Last revised: {expected}')


def revision_macro(stamp):
    return ('\\newcommand{\\lecturerevised}{' + stamp + '}').encode()


def save_records(records):
    DATA.parent.mkdir(exist_ok=True)
    temporary = DATA.with_suffix('.json.tmp')
    temporary.write_text(json.dumps(records, indent=2, sort_keys=True) + '\n')
    temporary.replace(DATA)


def build(source, records, references, tex_env):
    original = source.read_bytes()
    source_stat = source.stat()
    if len(REVISION.findall(original)) != 1:
        raise RuntimeError(f'{source.name}: retain the template\'s lecturerevised command')
    started = time.time_ns()
    with tempfile.TemporaryDirectory(prefix='lecture-build-') as directory:
        directory = Path(directory)
        draft = directory / source.name
        draft.write_bytes(original)
        command = ['latexmk', '-norc', '-g', '-pdf', '-recorder', '-interaction=nonstopmode',
                   '-halt-on-error', f'-outdir={directory}', str(draft)]
        subprocess.run(command, cwd=source.parent, env=tex_env, check=True)
        paths = recorded_inputs(draft.with_suffix('.fls'), source, records)
        if any(p.stat().st_mtime_ns > started for p in paths):
            raise RuntimeError(f'{source.name}: an input changed during compilation; retry')
        inputs = fingerprints(paths)
        stamp = revision_date(inputs, records.get(source.stem, {}))
        revised = REVISION.sub(lambda _: revision_macro(stamp), original)
        if revised != original:
            draft.write_bytes(revised)
            subprocess.run(command, cwd=source.parent, env=tex_env, check=True)
        if (source.read_bytes() != original or fingerprints(paths) != inputs
                or recorded_inputs(draft.with_suffix('.fls'), source, records) != paths):
            raise RuntimeError(f'{source.name}: an input changed during compilation; retry')
        if pdf_date(draft.with_suffix('.pdf')) != stamp:
            raise RuntimeError(f'{source.name}: PDF footer does not match revision date')
        # Keep the date in the downloadable source, so it also works outside this builder.
        if revised != original:
            source.write_bytes(revised)
            # Writing metadata must not become another lecture's source edit time.
            os.utime(source, ns=(source_stat.st_atime_ns, source_stat.st_mtime_ns))
        shutil.copy2(draft.with_suffix('.aux'), references)
        shutil.copy2(draft.with_suffix('.pdf'), source.with_suffix('.pdf'))
        records[source.stem] = {'revised': stamp, 'inputs': inputs}
        save_records(records)


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('lectures', nargs='*', help='Source paths; defaults to all lecture*.tex')
    parser.add_argument('--sync-only', action='store_true',
                        help='Verify existing PDFs and revision records without compiling')
    args = parser.parse_args()
    sources = [Path(p).resolve() for p in args.lectures] if args.lectures else sorted(NOTES.glob('lecture*.tex'))
    if any(p.parent != NOTES or p.suffix != '.tex' for p in sources):
        parser.error('Sources must be .tex files in documents/scribes')
    records = json.loads(DATA.read_text()) if DATA.exists() else {}
    if not args.sync_only:
        references = ROOT / 'outputs/lecture-labels'
        references.mkdir(parents=True, exist_ok=True)
        tex_env = os.environ.copy()
        # xr-hyper reads labels from earlier lectures in a fresh checkout too.
        tex_env['TEXINPUTS'] = str(references) + os.pathsep + tex_env.get('TEXINPUTS', '')
        for source in sources:
            build(source, records, references, tex_env)
    verify(records, sources)


if __name__ == '__main__':
    main()
