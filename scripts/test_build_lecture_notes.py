"""Regression checks for lecture revision dates; run with unittest discover -s scripts."""
from datetime import datetime, timezone
import os
from pathlib import Path
import subprocess
import tempfile
import unittest
from unittest.mock import patch

import build_lecture_notes as builder


class RevisionDates(unittest.TestCase):
    def setUp(self):
        self.directory = tempfile.TemporaryDirectory()
        self.addCleanup(self.directory.cleanup)
        self.root = Path(self.directory.name).resolve()
        self.notes = self.root / 'documents/scribes'
        self.notes.mkdir(parents=True)
        for name, value in [('ROOT', self.root), ('NOTES', self.notes)]:
            context = patch.object(builder, name, value)
            context.start()
            self.addCleanup(context.stop)
        self.source = self.notes / 'lecture01.tex'
        self.source.write_bytes(builder.revision_macro('not recorded') + b'\nLecture text.\n')
        self.exercise = self.root / 'documents/exercise.tex'
        self.exercise.write_text('An included exercise.\n')
        self.paths = {self.source, self.exercise}
        self.previous = {'revised': '2026-09-01 10:00 UTC-06:00',
                         'inputs': builder.fingerprints(self.paths)}

    def test_touch_and_generated_date_do_not_change_revision(self):
        os.utime(self.exercise, (1800000000, 1800000000))
        self.source.write_bytes(builder.REVISION.sub(
            lambda _: builder.revision_macro('2026-09-01 10:00 UTC-06:00'), self.source.read_bytes()))
        inputs = builder.fingerprints(self.paths)
        self.assertEqual(builder.revision_date(inputs, self.previous), self.previous['revised'])

    def test_included_file_change_uses_its_edit_time(self):
        self.exercise.write_text('A revised exercise.\n')
        epoch = 1789506000
        os.utime(self.exercise, (epoch, epoch))
        stamp = builder.revision_date(builder.fingerprints(self.paths), self.previous)
        actual = datetime.strptime(stamp, '%Y-%m-%d %H:%M UTC%z').timestamp()
        self.assertEqual(actual, epoch)

    def test_unrelated_file_does_not_change_revision(self):
        (self.root / 'documents/unrelated.tex').write_text('Another lecture.\n')
        self.assertEqual(builder.revision_date(builder.fingerprints(self.paths), self.previous),
                         self.previous['revised'])

    def test_committed_input_uses_git_time_after_checkout(self):
        subprocess.run(['git', 'init', '-q', str(self.root)], check=True)
        subprocess.run(['git', 'add', '.'], cwd=self.root, check=True)
        env = dict(os.environ, GIT_AUTHOR_DATE='2026-09-01T16:00:00+00:00',
                   GIT_COMMITTER_DATE='2026-09-01T16:00:00+00:00')
        subprocess.run(['git', '-c', 'user.name=Test', '-c', 'user.email=test@example.org',
                        'commit', '-qm', 'Initial source'], cwd=self.root, env=env, check=True)
        os.utime(self.source, (1800000000, 1800000000))
        epoch = builder.modified_time(self.source, builder.digest(self.source.read_bytes()))
        self.assertEqual(epoch, datetime(2026, 9, 1, 16, tzinfo=timezone.utc).timestamp())

    def test_recorder_tracks_actual_inputs_and_external_lecture_sources(self):
        other = self.notes / 'lecture02.tex'
        other.write_text('An earlier lecture.\n')
        figure = self.root / 'documents/figure.pdf'
        figure.write_bytes(b'figure')
        recorder = self.root / 'build.fls'
        recorder.write_text('\n'.join([
            'INPUT ../exercise.tex', 'INPUT ../exercise.tex', 'INPUT ../figure.pdf',
            f'INPUT {self.root}/outputs/lecture-labels/lecture02.aux',
            f'INPUT {self.root}/outputs/temporary.out', 'INPUT /usr/local/texlive/article.cls',
        ]))
        self.assertEqual(builder.recorded_inputs(recorder, self.source, {}),
                         {self.source, self.exercise, other, figure})

    def test_sync_rejects_changed_source(self):
        self.exercise.write_text('Changed since the recorded build.\n')
        with self.assertRaisesRegex(RuntimeError, 'source or inputs changed'):
            builder.verify({'lecture01': self.previous}, [self.source])

    def test_every_pdf_page_must_have_the_same_date(self):
        with patch.object(builder.subprocess, 'check_output', return_value=(
                'Page one\nLast revised: 2026-09-01 10:00 UTC-06:00\f'
                'Page two\nLast revised: 2026-09-02 10:00 UTC-06:00\f')):
            with self.assertRaisesRegex(RuntimeError, 'inconsistent revision dates'):
                builder.pdf_date(self.source.with_suffix('.pdf'))


if __name__ == '__main__':
    unittest.main()
