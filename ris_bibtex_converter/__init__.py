"""Convert reference libraries between RIS and BibTeX."""
from .core import parse_ris, write_ris, parse_bibtex, write_bibtex, ris_to_bibtex, bibtex_to_ris

__version__ = "0.1.0"
__all__ = ["parse_ris", "write_ris", "parse_bibtex", "write_bibtex", "ris_to_bibtex", "bibtex_to_ris"]
