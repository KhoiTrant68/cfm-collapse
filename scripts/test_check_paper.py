"""Regression checks for stale submission build acceptance; no TeX required."""
import importlib.util
import json
from pathlib import Path
import tempfile
import unittest
from unittest.mock import patch

spec = importlib.util.spec_from_file_location('check_paper', Path(__file__).with_name('check_paper.py'))
checker = importlib.util.module_from_spec(spec)
spec.loader.exec_module(checker)
TEST_TMP = Path(__file__).resolve().parents[1] / 'tmp'
TEST_TMP.mkdir(exist_ok=True)


class ProvenanceTests(unittest.TestCase):
    def test_current_build_then_changed_source_and_products(self):
        with tempfile.TemporaryDirectory(dir=TEST_TMP) as folder:
            directory = Path(folder).resolve()
            assert directory.is_relative_to(TEST_TMP.resolve())
            source = directory / 'main.tex'
            source.write_text('current source')
            products = [directory / f'main.{ext}' for ext in ('aux', 'log', 'pdf', 'bbl')]
            for path in products:
                path.write_bytes(b'build output')
            snapshot = checker.hashes([source])
            (directory / 'build-manifest.json').write_text(json.dumps(dict(inputs=snapshot, products=checker.hashes(products))))
            with patch.object(checker, 'inputs', lambda: checker.hashes([source])):
                errors = []
                checker.check_provenance(directory, errors)
                self.assertEqual(errors, [])
                source.write_text('changed statement')
                checker.check_provenance(directory, errors)
                self.assertEqual(len(errors), 1)
                source.write_text('current source')
                products[0].write_bytes(b'old auxiliary cache')
                errors = []
                checker.check_provenance(directory, errors)
                self.assertEqual(len(errors), 1)

    def test_missing_manifest_does_not_accept_old_cache(self):
        with tempfile.TemporaryDirectory(dir=TEST_TMP) as folder:
            assert Path(folder).resolve().is_relative_to(TEST_TMP.resolve())
            errors = []
            checker.check_provenance(Path(folder), errors)
            self.assertEqual(len(errors), 1)

    def test_venue_page_cap_is_explicit(self):
        aux = r'\newlabel{endmain}{{6}{15}{Conclusion}{section.6}{}}'
        errors = []
        checker.check_page_limit(aux, errors)
        self.assertEqual(errors, [])
        checker.check_page_limit(aux, errors, 9)
        self.assertEqual(len(errors), 1)

    def test_oversized_float_rejected(self):
        errors = []
        checker.check_log('LaTeX Warning: Float too large for page by 12pt', errors)
        self.assertEqual(len(errors), 1)


if __name__ == '__main__':
    unittest.main()
