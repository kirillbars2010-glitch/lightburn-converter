import subprocess
import sys
import tempfile
import unittest
from pathlib import Path

import pymupdf as fitz
from vector_convert import make_path


class ConverterTests(unittest.TestCase):
    def test_quad_order_and_closed_subpath(self):
        q = fitz.Quad(fitz.Point(0, 0), fitz.Point(10, 0), fitz.Point(0, 10), fitz.Point(10, 10))
        self.assertEqual(make_path([('qu', q)]), 'M0,0 L0,10 L10,10 L10,0 Z')
        self.assertEqual(make_path([('l', fitz.Point(1, 1), fitz.Point(2, 2)), ('qu', q)], True),
                         'M1,1 L2,2 Z M0,0 L0,10 L10,10 L10,0 Z')

    def test_svg_conversion(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            source = root / 'input.svg'
            source.write_text('<svg xmlns="http://www.w3.org/2000/svg" width="20mm" height="10mm" viewBox="0 0 20 10"><rect x="1" y="1" width="10" height="5" fill="white"/></svg>', encoding='utf-8')
            result = subprocess.run([sys.executable, str(Path(__file__).with_name('vector_convert.py')), str(source), '-o', str(root / 'out'), '--dpi', '72'], capture_output=True, text=True, encoding='utf-8', errors='replace')
            self.assertEqual(result.returncode, 0, result.stderr)
            for ext in ('svg', 'pdf', 'png'):
                self.assertTrue((root / 'out' / ('input.' + ext)).is_file())
            with fitz.open(root / 'out' / 'input.pdf') as pdf:
                self.assertAlmostEqual(pdf[0].rect.width, 20 * 72 / 25.4, places=2)
                self.assertAlmostEqual(pdf[0].rect.height, 10 * 72 / 25.4, places=2)


if __name__ == '__main__':
    unittest.main()
