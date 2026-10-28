"""Turns a CNLEGIS HTML text into lines, and lines into the provisions of a constitution. No AI, no fuzzy matching.

lines(html): every block element (p, li, div, blockquote, h1-h6, td, br) ends a line; inline tags are dropped; entities
are decoded; U+00A0 becomes a space; U+00AD (soft hyphen) and zero-width characters are removed; runs of whitespace
become one space; empty lines are dropped. List items keep no marker (CNLEGIS prints none in the text itself).

constitution(lines, start, stop): the preamble, the structural headings (TITRE, Sous-titre, CHAPITRE, SECTION) and the
articles, from the line that matches `start` up to (not including) the first line matching `stop`.
"""
import html as H
import re
from html.parser import HTMLParser

BLOCK = {'p', 'li', 'div', 'blockquote', 'h1', 'h2', 'h3', 'h4', 'h5', 'h6', 'td', 'th', 'tr', 'ul', 'ol', 'table'}
DROP = re.compile('[­​‌‍⁠﻿]')
WS = re.compile(r'[ \t\r\n     ]+')


class _P(HTMLParser):
    def __init__(self):
        super().__init__(convert_charrefs=True)
        self.out, self.buf = [], []

    def flush(self):
        s = WS.sub(' ', DROP.sub('', ''.join(self.buf))).strip()
        if s:
            self.out.append(s)
        self.buf = []

    def handle_starttag(self, tag, attrs):
        if tag in BLOCK or tag == 'br':
            self.flush()

    def handle_endtag(self, tag):
        if tag in BLOCK:
            self.flush()

    def handle_data(self, data):
        self.buf.append(data)


def lines(html: str) -> list:
    p = _P()
    p.feed(html)
    p.close()
    p.flush()
    return p.out


# "Article premier .", "Article 15 .-", "Article 53 ;-", "Article 98.1 .", "Article 134. 1.", "Article 155 -",
# "Article 15 (nouveau)." The number is kept as printed (group 1); the separator after it is not part of the text kept.
ART = re.compile(r'^Article\s+(premier|\d+(?:\.\s?\d+(?=\s*\.))?)\s*(\(nouveau\))?\s*[.;:,]?\s*[-–—]?\s*(.*)$')
# a structural heading: TITRE / SOUS-TITRE / CHAPITRE / SECTION (2010 art. 152 prints a stray dot: ".CHAPITRE II").
# In capitals it may carry its title on the same line; the short form ("TITRE II", "Sous-titre premier") is followed by
# a title line. Every line from a heading up to the next article belongs to the heading (titles run over lines).
HEAD_CAPS = re.compile(r'^\.?(TITRE|SOUS[- ]TITRE|CHAPITRE|SECTION)\b')
HEAD_SEC = re.compile(r'^Sections?\s+\d+\s*:')  # "Section 1 : de la ..." (PDF texts, e.g. Loi 2024-014)
HEAD_SHORT = re.compile(r'^\.?(titre|sous[- ]titre|chapitre|section)\s+(premier|unique|[ivxl]+|il|\d+)\s*$', re.I)


def art_key(num: str) -> str:
    """'premier' -> '1'; '98.1' -> '98.1'; '134. 1' -> '134.1'."""
    n = num.replace(' ', '')
    return '1' if n == 'premier' else n


def constitution(ls: list, start: str, stop: str) -> dict:
    """{'preamble': [lines], 'articles': [(key, number as printed, [body lines])], 'structure': [(heading, article key)]}

    Lines from the one that fully matches `start` up to (not including) the first that starts with `stop`."""
    i = next(k for k, l in enumerate(ls) if re.fullmatch(start, l))
    j = next(k for k in range(i + 1, len(ls)) if re.match(stop, ls[k]))
    pre, arts, struct, cur, pending, expect_title = [], [], [], None, [], False
    for l in ls[i:j]:
        if expect_title:
            pending.append(l)
            expect_title = False
            continue
        m = ART.match(l)
        if m:
            key = art_key(m.group(1))
            cur = (key, ' '.join(m.group(1).split()), [m.group(3)] if m.group(3) else [])
            arts.append(cur)
            struct += [(h, key) for h in pending]
            pending = []
            continue
        if HEAD_SHORT.match(l):
            pending.append(l)
            expect_title = True
            continue
        if HEAD_CAPS.match(l) or HEAD_SEC.match(l):
            pending.append(l)
            continue
        if pending:  # a heading's title can run over several lines; headings are always followed by an article
            pending.append(l)
            continue
        (pre if cur is None else cur[2]).append(l)
    if pending:
        raise ValueError(f'heading at the end: {pending}')
    keys = [a[0] for a in arts]
    if len(set(keys)) != len(keys):
        raise ValueError(f'duplicate article numbers {sorted(k for k in set(keys) if keys.count(k) > 1)}')
    order = [tuple(int(x) for x in k.split('.')) for k in keys]
    if order != sorted(order):
        raise ValueError('articles out of order')
    return {'preamble': pre, 'articles': arts, 'structure': struct}


def text_of(html: str) -> str:
    return H.unescape(html)
