"""Command-line interface for ris-bibtex-converter."""
import argparse
import os
import sys

from .core import bibtex_to_ris, ris_to_bibtex


def main(argv=None):
    ap = argparse.ArgumentParser(prog="ris-bibtex-converter", description="Convert between RIS and BibTeX.")
    ap.add_argument("input")
    ap.add_argument("-o", "--output", help="output file; format is inferred from its extension")
    ap.add_argument("--to", choices=["bib", "ris"], help="target format (default: the opposite of the input)")
    args = ap.parse_args(argv)

    ext = os.path.splitext(args.input)[1].lower()
    to = args.to or (os.path.splitext(args.output)[1].lower().lstrip(".") if args.output else None)
    if to not in ("bib", "ris"):
        to = "bib" if ext in (".ris", ".txt") else "ris"
    with open(args.input, encoding="utf-8-sig", errors="replace") as fh:
        text = fh.read()
    out = ris_to_bibtex(text) if to == "bib" else bibtex_to_ris(text)
    if args.output:
        with open(args.output, "w", encoding="utf-8") as fh:
            fh.write(out)
    else:
        sys.stdout.write(out)
    return 0
