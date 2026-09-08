#!/usr/bin/env python3
"""Build lecture PDFs, then synchronize website timestamps from PDF footers."""
import argparse
import json
from pathlib import Path
import re
import shutil
import subprocess
import tempfile

ROOT = Path(__file__).resolve().parents[1]
NOTES = ROOT / 'documents/scribes'
DATA = ROOT / '_data/pdf_builds.json'
STAMP = re.compile(r'Compiled:\s*(\d{4}-\d{2}-\d{2}\s+\d{2}:\d{2}\s+UTC[+-]\d{2}:\d{2})')


def timestamps():
    result = {}
    for pdf in sorted(NOTES.glob('lecture*.pdf')):
        pages = subprocess.check_output(
            ['pdftotext', '-layout', str(pdf), '-'], text=True).split('\f')
        stamps = []
        for page in pages:
            if not page.strip():
                continue
            matches = STAMP.findall(page)
            if len(matches) != 1:
                raise RuntimeError(f'{pdf.name}: expected one compilation footer on every page')
            stamps.append(' '.join(matches[0].split()))
        if not stamps or len(set(stamps)) != 1:
            raise RuntimeError(f'{pdf.name}: inconsistent compilation timestamps')
        result[pdf.stem] = stamps[0]
    DATA.parent.mkdir(exist_ok=True)
    temporary = DATA.with_suffix('.json.tmp')
    temporary.write_text(json.dumps(result, indent=2) + '\n')
    temporary.replace(DATA)
    for name, stamp in result.items():
        print(f'{name}: {stamp}')


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('lectures', nargs='*', help='Source paths; defaults to all lecture*.tex')
    parser.add_argument('--sync-only', action='store_true', help='Read existing PDFs without compiling')
    args = parser.parse_args()
    if not args.sync_only:
        sources = [Path(p).resolve() for p in args.lectures] if args.lectures else sorted(NOTES.glob('lecture*.tex'))
        for source in sources:
            if source.parent != NOTES or source.suffix != '.tex':
                parser.error('Sources must be .tex files in documents/scribes')
            dependencies = [source, *sorted((ROOT / 'documents/exercises').glob('*.tex')),
                            *sorted((ROOT / 'documents/exercises').glob('*.sty'))]
            before = {p: p.read_bytes() for p in dependencies}
            with tempfile.TemporaryDirectory(prefix='lecture-build-') as directory:
                subprocess.run(['latexmk', '-norc', '-g', '-pdf', '-interaction=nonstopmode',
                                '-halt-on-error', f'-outdir={directory}', source.name],
                               cwd=source.parent, check=True)
                if any(p.read_bytes() != content for p, content in before.items()):
                    raise RuntimeError(f'{source.name} changed during compilation; PDF not replaced')
                references = ROOT / 'outputs/lecture-labels'
                references.mkdir(parents=True, exist_ok=True)
                shutil.copy2(Path(directory) / source.with_suffix('.aux').name, references)
                shutil.copy2(Path(directory) / source.with_suffix('.pdf').name,
                             source.with_suffix('.pdf'))
    timestamps()


if __name__ == '__main__':
    main()
