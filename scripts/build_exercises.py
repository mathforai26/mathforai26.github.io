#!/usr/bin/env python3
"""Build an instructor exercise book, or homework solutions and a student template.

Outputs are self-contained source/PDF bundles. No publication is performed.
"""
import argparse
import json
from pathlib import Path
import re
import shutil
import subprocess
import sys

ROOT = Path(__file__).resolve().parents[1]
BANK = ROOT / 'documents/exercises'
PRIVATE = ROOT / 'instructor-materials/exercises'


def reference_lectures(entries):
    return sorted({e['lecture'] for e in entries}
                  | {n for e in entries for n in e.get('reference_lectures', [])})


def available_reference_lectures(entries):
    """Return referenced lectures whose scribe-note sources currently exist."""
    return [n for n in reference_lectures(entries)
            if (ROOT / f'documents/scribes/lecture0{n}.tex').exists()]


def tex(text):
    return ''.join({'\\': r'\textbackslash{}', '&': r'\&', '%': r'\%', '$': r'\$',
                    '#': r'\#', '_': r'\_', '{': r'\{', '}': r'\}',
                    '~': r'\textasciitilde{}', '^': r'\textasciicircum{}'}.get(c, c) for c in text)


def build(folder, entries, title, revision, instructions, solutions, book=False):
    folder.mkdir(parents=True, exist_ok=True)
    for name in ('course-exercises.sty', 'reader-preamble.tex'):
        shutil.copy2(BANK / name, folder / name)
    lectures = available_reference_lectures(entries)
    local_labels=set()
    for e in entries:
        local_labels.update(re.findall(r'\\label(?:\[[^]]*\])?\{([^}]+)\}', (BANK/e['file']).read_text()))
        solution=PRIVATE/'solutions'/(e['id']+'-solution.tex')
        if solutions and solution.exists():
            local_labels.update(re.findall(r'\\label(?:\[[^]]*\])?\{([^}]+)\}',solution.read_text()))
    # Keep links to lecture facts functional even when the bundle is moved.
    for n in lectures:
        stem = f'lecture0{n}'
        aux=(ROOT / f'outputs/lecture-labels/{stem}.aux').read_text().splitlines()
        external=[]
        for line in aux:
            if line.startswith(r'\HyperFirstAtBeginDocument'):
                # xr-hyper needs this marker to recognize five-field labels;
                # without it, extra empty fields corrupt external link targets.
                external.append(r'\HyperFirstAtBeginDocument{}')
            match=re.match(r'\\newlabel\{([^}]+)\}',line)
            # thmtools stores executable restatement metadata as labels.
            # Export public references only; xr-hyper cannot import that data.
            if (match and not match[1].startswith('thmt@@')
                    and match[1].removesuffix('@cref') not in local_labels):
                external.append(line)
        (folder/(stem+'.aux')).write_text('\n'.join(external)+'\n')
        shutil.copy2(ROOT / f'documents/scribes/{stem}.pdf', folder)
    lines = [r'\newcommand{\documenttitle}{'+tex(title)+'}',
             r'\newcommand{\documentrevision}{'+tex(revision)+'}',
             r'\input{reader-preamble.tex}']
    for n in lectures:
        lines.append(r'\externaldocument{lecture0'+str(n)+'}[lecture0'+str(n)+'.pdf]')
    if not book:
        lines.append(r'\renewcommand{\thetheorem}{\arabic{theorem}}')
    if not solutions:
        lines += [r'\newcommand{\studentname}{YOUR NAME}', r'\newcommand{\studentid}{YOUR STUDENT ID}']
    lines += [r'\begin{document}',r'\begin{center}\Large\bfseries '+tex(title)+r'\end{center}',
              tex(instructions)+r'\par\medskip',r'\exerciseinstructions']
    if not solutions:
        lines.append(r'\noindent Name: \studentname\quad Student ID: \studentid\par\medskip')
    current = None
    for e in entries:
        ident = e['id']
        if book and current != e['lecture']:
            if current is not None: lines.append(r'\clearpage')
            current = e['lecture']
            lines += [r'\section{Lecture '+str(current)+'}',r'\setcounter{courseexercise}{0}']
        if not book:
            if e.get('assigned'):
                lines.append(r'\noindent\textbf{Assigned work:} '+tex(e['assigned'])+r'\par')
            points=e.get('points', {})
            if points:
                lines.append(r'\noindent\textbf{Points:} '+tex(', '.join(f'{k}: {v}' for k,v in points.items()))+
                             '; total '+str(sum(points.values()))+r'.\par')
        shutil.copy2(BANK / e['file'], folder)
        lines.append(r'\input{'+e['file']+'}')
        lines.append(r'\begin{exercisesolution}')
        if solutions:
            filename=ident+'-solution.tex'
            source=PRIVATE / 'solutions' / filename
            if source.exists():
                shutil.copy2(source, folder)
                lines.append(r'\input{'+filename+'}')
            else:
                lines.append(r'\missingsolution{Solution file is missing.}')
        else:
            lines.append('Write your solution here.')
        lines.append(r'\end{exercisesolution}')
    lines.append(r'\end{document}')
    (folder / 'document.tex').write_text('\n'.join(lines)+'\n')
    (folder / 'selection.json').write_text(json.dumps(entries, indent=2)+'\n')
    (folder / 'README.txt').write_text('Compile with: latexmk -pdf -interaction=nonstopmode -halt-on-error document.tex\n'
                                     'Keep the supplied lecture PDFs and auxiliary files for external references.\n')
    with (folder/'build.txt').open('w') as log:
        result = subprocess.run(['latexmk','-norc','-pdf','-interaction=nonstopmode','-halt-on-error','document.tex'],
                       cwd=folder,stdout=log,stderr=subprocess.STDOUT,check=False)
    if result.returncode:
        raise RuntimeError((folder/'build.txt').read_text()[-5000:])
    log=(folder/'document.log').read_text()
    if re.search(r'undefined references|multiply defined|Reference .* undefined',log):
        raise RuntimeError(f'Unresolved or ambiguous references: {folder}/document.log')
    print('Built:',title, '(with solutions)' if solutions else '(student template)')


def main():
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--homework',type=Path,help='Homework selection JSON; otherwise build the instructor book')
    parser.add_argument('--release',help='Save an immutable local homework release under instructor-materials/exercises/releases')
    args=parser.parse_args()
    if args.release and (not args.homework or not re.fullmatch(r'[A-Za-z0-9][A-Za-z0-9_.-]*',args.release)):
        parser.error('--release requires --homework and a simple release name')
    catalog=json.loads((BANK/'catalog.json').read_text())
    if args.homework:
        config=json.loads(args.homework.read_text())
        lookup={e['id']:e for e in catalog}
        entries=[dict(lookup[e['id']],**{k:v for k,v in e.items() if k!='id'}) for e in config['exercises']]
        if len({e['id'] for e in entries})!=len(entries): parser.error('An exercise must not appear twice')
        for e in entries:
            if any(not isinstance(v,(int,float)) or v<0 for v in e.get('points',{}).values()):
                parser.error('Points must be nonnegative numbers')
        target=(PRIVATE/'releases'/args.release) if args.release else ROOT/'outputs/homeworks'/args.homework.stem
        if args.release and target.exists(): parser.error('Release already exists; choose a new revision')
    else:
        entries=catalog
        target=ROOT/'outputs/instructor-exercises'
    # Reject concurrent edits rather than saving a mixed source revision.
    inputs=[*BANK.glob('*.tex'),*BANK.glob('*.sty'),BANK/'catalog.json',
            *[ROOT/f'documents/scribes/lecture0{n}.tex' for n in available_reference_lectures(entries)],
            *[PRIVATE/'solutions'/(e['id']+'-solution.tex') for e in entries]]
    if args.homework: inputs.append(args.homework)
    before={p:p.read_bytes() if p.exists() else None for p in inputs}
    # Refresh labels and reference PDFs from the same current sources.
    lectures=[f'documents/scribes/lecture0{n}.tex' for n in available_reference_lectures(entries)]
    with (ROOT/'tmp/exercise-reference-build.log').open('w') as log:
        subprocess.run([sys.executable,str(ROOT/'scripts/build_lecture_notes.py'),*lectures],cwd=ROOT,
                       stdout=log,stderr=subprocess.STDOUT,check=True)
    # Build in a fresh directory so student templates cannot retain old solution files.
    import tempfile
    with tempfile.TemporaryDirectory(prefix='exercise-bundle-') as directory:
        stage=Path(directory)
        if args.homework:
            for mode in ('solutions','student'):
                build(stage/mode,entries,config['title'],config['revision'],config['instructions'],mode=='solutions')
            shutil.copy2(args.homework,stage/'homework.json')
        else:
            build(stage,entries,'Instructor exercise book','WORKING DRAFT',
                  'All exercises and solutions, grouped by lecture. Unfinished solutions are marked explicitly.',True,True)
        # Save build inputs with hashes for identifying a release independently of compilation time.
        import hashlib
        hashes={str(p.relative_to(stage)):hashlib.sha256(p.read_bytes()).hexdigest()
                for p in stage.rglob('*') if p.is_file() and p.suffix in ('.tex','.sty','.pdf','.json')}
        (stage/'manifest.json').write_text(json.dumps(hashes,indent=2)+'\n')
        if any((p.read_bytes() if p.exists() else None)!=content for p,content in before.items()):
            raise RuntimeError('Inputs changed during the build; rerun to obtain a consistent bundle')
        if args.release and target.exists():
            raise RuntimeError('Release already exists; it will not be overwritten')
        if target.exists(): shutil.rmtree(target)
        target.parent.mkdir(parents=True,exist_ok=True)
        shutil.copytree(stage,target)
    print('Saved:',target)


if __name__=='__main__':
    (ROOT/'tmp').mkdir(exist_ok=True)
    main()
