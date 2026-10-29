"""RIS <-> BibTeX conversion through a neutral record format.

A record is a dict: type (BibTeX type), key, authors (list of 'Last, First'), editors, and
plain fields: title, journal, booktitle, year, volume, number, pages, publisher, doi, url,
abstract, keywords (list), issn, isbn, address, note.
"""
import re

RIS_TO_BIB = {"JOUR": "article", "JFULL": "article", "MGZN": "article", "BOOK": "book", "CHAP": "incollection",
              "CONF": "inproceedings", "CPAPER": "inproceedings", "THES": "phdthesis", "RPRT": "techreport",
              "UNPB": "unpublished", "ELEC": "online", "GEN": "misc", "DATA": "misc"}
BIB_TO_RIS = {"article": "JOUR", "book": "BOOK", "incollection": "CHAP", "inbook": "CHAP",
              "inproceedings": "CONF", "conference": "CONF", "phdthesis": "THES", "mastersthesis": "THES",
              "techreport": "RPRT", "unpublished": "UNPB", "online": "ELEC", "misc": "GEN"}
_SIMPLE = {"VL": "volume", "IS": "number", "PB": "publisher", "DO": "doi", "UR": "url", "N2": "abstract",
           "AB": "abstract", "SN": "issn", "CY": "address", "N1": "note"}
_RIS_LINE = re.compile(r"^([A-Z][A-Z0-9])  -\s?(.*)$")


def parse_ris(text):
    records, cur, sp = [], None, None
    for raw in text.splitlines():
        m = _RIS_LINE.match(raw.rstrip())
        if not m:
            continue
        tag, val = m.group(1), m.group(2).strip()
        if tag == "TY":
            cur, sp = {"type": RIS_TO_BIB.get(val, "misc"), "authors": [], "editors": [], "keywords": []}, None
        elif cur is None:
            continue
        elif tag == "ER":
            if sp:
                cur.setdefault("pages", sp)
            records.append(cur)
            cur = None
        elif tag in ("AU", "A1"):
            cur["authors"].append(val)
        elif tag in ("ED", "A2", "A3") and cur["type"] != "article":
            cur["editors"].append(val)
        elif tag in ("TI", "T1"):
            cur["title"] = val
        elif tag in ("JO", "JF", "T2", "JA", "BT"):
            target = "journal" if cur["type"] == "article" else "booktitle"
            if tag in ("JF", "T2", "BT") or target not in cur:
                cur[target] = val
        elif tag in ("PY", "Y1", "DA"):
            y = re.search(r"\d{4}", val)
            if y and "year" not in cur:
                cur["year"] = y.group(0)
        elif tag == "SP":
            sp = val
        elif tag == "EP":
            sp = (sp or "") + "--" + val
        elif tag == "KW":
            cur["keywords"].append(val)
        elif tag == "ID":
            cur["key"] = val
        elif tag in _SIMPLE:
            cur.setdefault(_SIMPLE[tag], val)
        if tag == "SN" and cur and cur["type"] == "book":
            cur["isbn"] = cur.pop("issn", val)
    return records


def _balanced_end(text, i):
    depth = 0
    for j in range(i, len(text)):
        depth += {"{": 1, "}": -1}.get(text[j], 0)
        if depth == 0:
            return j
    raise ValueError("unbalanced braces")


def parse_bibtex(text):
    records = []
    for m in re.finditer(r"@(\w+)\s*\{\s*([^,\s]+)\s*,", text):
        t = m.group(1).lower()
        if t in ("comment", "string", "preamble"):
            continue
        body = text[m.end():_balanced_end(text, text.index("{", m.start()))]
        f = {}
        for fm in re.finditer(r"([\w-]+)\s*=\s*(\{(?:[^{}]|\{(?:[^{}]|\{[^{}]*\})*\})*\}|\"[^\"]*\"|\d+)", body):
            v = fm.group(2)
            f[fm.group(1).lower()] = " ".join((v[1:-1] if v[0] in "{\"" else v).split())
        rec = {"type": t, "key": m.group(2),
               "authors": [a.strip() for a in re.split(r"\s+and\s+", f.pop("author", "")) if a.strip()],
               "editors": [a.strip() for a in re.split(r"\s+and\s+", f.pop("editor", "")) if a.strip()],
               "keywords": [k.strip() for k in re.split(r"[;,]", f.pop("keywords", "")) if k.strip()]}
        rec.update(f)
        records.append(rec)
    return records


def _make_key(rec, used):
    a = rec["authors"][0] if rec["authors"] else "anon"
    last = a.split(",")[0] if "," in a else a.split()[-1]
    base = re.sub(r"[^A-Za-z]", "", last).lower() + rec.get("year", "")
    key, n = base, 0
    while key in used:
        n += 1
        key = base + "abcdefghijklmnopqrstuvwxyz"[(n - 1) % 26]
    used.add(key)
    return key


_BIB_ORDER = ["title", "journal", "booktitle", "year", "volume", "number", "pages", "publisher", "address",
              "doi", "url", "issn", "isbn", "abstract", "note"]


def write_bibtex(records):
    used, out = set(), []
    for r in records:
        key = r.get("key") or _make_key(r, used)
        used.add(key)
        lines = ["@%s{%s," % (r["type"], key)]
        if r.get("authors"):
            lines.append("  author = {%s}," % " and ".join(r["authors"]))
        if r.get("editors"):
            lines.append("  editor = {%s}," % " and ".join(r["editors"]))
        for k in _BIB_ORDER + sorted(set(r) - set(_BIB_ORDER) - {"type", "key", "authors", "editors", "keywords"}):
            if r.get(k):
                lines.append("  %s = {%s}," % (k, r[k]))
        if r.get("keywords"):
            lines.append("  keywords = {%s}," % ", ".join(r["keywords"]))
        lines.append("}")
        out.append("\n".join(lines))
    return "\n\n".join(out) + "\n"


def write_ris(records):
    out = []
    for r in records:
        lines = ["TY  - " + BIB_TO_RIS.get(r["type"], "GEN")]
        lines += ["AU  - " + a for a in r.get("authors", [])]
        lines += ["ED  - " + a for a in r.get("editors", [])]
        if r.get("title"):
            lines.append("TI  - " + r["title"])
        if r.get("journal"):
            lines.append("JO  - " + r["journal"])
        if r.get("booktitle"):
            lines.append("T2  - " + r["booktitle"])
        if r.get("year"):
            lines.append("PY  - " + r["year"])
        for tag, k in (("VL", "volume"), ("IS", "number")):
            if r.get(k):
                lines.append("%s  - %s" % (tag, r[k]))
        if r.get("pages"):
            sp, _, ep = re.split(r"\s*-{1,2}\s*|–", r["pages"]) + ["", ""] if False else r["pages"].partition("--")
            if not ep and "-" in sp:
                sp, _, ep = sp.partition("-")
            lines.append("SP  - " + sp.strip())
            if ep:
                lines.append("EP  - " + ep.strip())
        for tag, k in (("PB", "publisher"), ("CY", "address"), ("SN", "issn"), ("SN", "isbn"), ("DO", "doi"),
                       ("UR", "url"), ("AB", "abstract"), ("N1", "note")):
            if r.get(k):
                lines.append("%s  - %s" % (tag, r[k]))
        lines += ["KW  - " + k for k in r.get("keywords", [])]
        if r.get("key"):
            lines.append("ID  - " + r["key"])
        lines.append("ER  - ")
        out.append("\n".join(lines))
    return "\n\n".join(out) + "\n"


def ris_to_bibtex(text):
    return write_bibtex(parse_ris(text))


def bibtex_to_ris(text):
    return write_ris(parse_bibtex(text))
