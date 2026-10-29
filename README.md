# ris-bibtex-converter

**Lossless-as-possible conversion between RIS (EndNote, Zotero, Mendeley, Scopus, Web of
Science, PubMed exports) and BibTeX (LaTeX, Overleaf, JabRef), in both directions.**

Part of the *Research Automation Toolkit*: 100 open tools for daily research work.

## Why

Databases and co-authors export references as RIS, while LaTeX needs BibTeX, and Word-based
collaborators need the reverse. Online converters upload your library to a third party and often
lose page ranges, editors or keywords. This tool works offline and is scriptable.

## Features

- Type mapping (JOUR/BOOK/CHAP/CONF/THES/RPRT/ELEC/...) to and from BibTeX entry types
- Authors and editors, page ranges (`SP`/`EP` <-> `pages = {737--738}`), keywords, DOI, URL, abstract, ISSN/ISBN
- Dates like `1953/04/25/` reduced to the year
- Automatic unique citation keys (`watson1953`, `watson1953a`) when RIS has no `ID`
- Direction inferred from file extensions; handles UTF-8 BOM exports

## Usage

```bash
pip install .
ris-bibtex-converter scopus_export.ris -o refs.bib
ris-bibtex-converter refs.bib -o for_endnote.ris
ris-bibtex-converter refs.bib --to ris > out.ris
```

## Testing

```bash
python -m unittest discover -s tests -t .
```

## License

MIT (c) JANIN A APURBA
