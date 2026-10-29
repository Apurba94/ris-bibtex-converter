import os
import tempfile
import unittest

from ris_bibtex_converter.cli import main
from ris_bibtex_converter.core import parse_bibtex, parse_ris, write_bibtex, write_ris

RIS = """TY  - JOUR
AU  - Watson, James D.
AU  - Crick, Francis
TI  - Molecular structure of nucleic acids
JO  - Nature
PY  - 1953/04/25/
VL  - 171
IS  - 4356
SP  - 737
EP  - 738
DO  - 10.1038/171737a0
KW  - DNA
KW  - structure
ER  -

TY  - CHAP
AU  - Doe, Jane
ED  - Editor, Ed
TI  - A Chapter
T2  - The Big Book
PY  - 2020
SN  - 978-3-16-148410-0
PB  - Springer
ER  -
"""


class RisTests(unittest.TestCase):
    def test_parse_ris(self):
        a, b = parse_ris(RIS)
        self.assertEqual(a["type"], "article")
        self.assertEqual(a["authors"], ["Watson, James D.", "Crick, Francis"])
        self.assertEqual(a["year"], "1953")
        self.assertEqual(a["pages"], "737--738")
        self.assertEqual(a["keywords"], ["DNA", "structure"])
        self.assertEqual(b["type"], "incollection")
        self.assertEqual(b["booktitle"], "The Big Book")
        self.assertEqual(b["editors"], ["Editor, Ed"])

    def test_ris_to_bibtex_generates_unique_keys(self):
        bib = write_bibtex(parse_ris(RIS + RIS))
        keys = [r["key"] for r in parse_bibtex(bib)]
        self.assertEqual(keys, ["watson1953", "doe2020", "watson1953a", "doe2020a"])

    def test_bibtex_round_trip_preserves_fields(self):
        recs = parse_ris(RIS)
        again = parse_bibtex(write_bibtex(recs))
        for r1, r2 in zip(recs, again):
            for k in ("title", "year", "authors", "doi", "pages", "keywords"):
                self.assertEqual(r1.get(k), r2.get(k), k)

    def test_ris_round_trip(self):
        recs = parse_ris(RIS)
        again = parse_ris(write_ris(recs))
        self.assertEqual([r["title"] for r in recs], [r["title"] for r in again])
        self.assertEqual(again[0]["pages"], "737--738")

    def test_bibtex_to_ris_types_and_pages(self):
        ris = write_ris(parse_bibtex("@inproceedings{k, author={A, B and C, D}, title={T}, "
                                     "booktitle={Proc}, year=2021, pages={5-9}}"))
        self.assertIn("TY  - CONF", ris)
        self.assertIn("SP  - 5\nEP  - 9", ris)
        self.assertIn("T2  - Proc", ris)
        self.assertIn("ID  - k", ris)

    def test_cli_infers_direction(self):
        with tempfile.TemporaryDirectory() as d:
            src, out = os.path.join(d, "lib.ris"), os.path.join(d, "lib.bib")
            with open(src, "w", encoding="utf-8") as fh:
                fh.write(RIS)
            self.assertEqual(main([src, "-o", out]), 0)
            with open(out, encoding="utf-8") as fh:
                self.assertEqual(len(parse_bibtex(fh.read())), 2)


if __name__ == "__main__":
    unittest.main()
