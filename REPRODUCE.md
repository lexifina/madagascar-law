# Reproduce

Data retrieved 2026-10-28. The build is deterministic: the same data gives the same commit hashes.

## Sources and requests

CNLEGIS (https://cnlegis.gov.mg/), the official legal database of the Direction du CNLEGIS (Secrétariat Général du
Gouvernement, Primature). It serves each text's official French HTML inside the JSON of its search endpoints: a search is
two POSTs in one session, the search form (`page_find_direct_mots/` or `page_num_find_direct/`, field `txt_recherche`)
and then the data endpoint (`page_data_result_direct_mots/` or `page_num_data_find_direct/`, field `var_pg_limit`).
The build reads two searches (four requests), sent one at a time with a User-Agent and a pause, cached in
`tools/cache` (git-ignored) with each answer's sha256:
- `mots` search "Constitution de la" (limit 0,300): `mots-e085dea8fb596eb2.json`, sha256 `02dbde5ca36aa86a666e61ac99143fed3fea1d22292a7308f83cb672b4e36f31`
- `num` search "2009-001" (limit 0,50): `num-08b5130173a25f0e.json`, sha256 `5a968250dc3b130ac32c9a4e82bdfb853e40b83221376ff5a01a3de2842bff99`

The four texts used, with the sha256 of each official HTML (UTF-8):
- lc/98-001: CNLEGIS record 34738, html_fichier_fr sha256 `275f7b88df704f5c4636aee121772867a7bd0583558c5504ea1d0b7bfa04d077`
- lc/2007-001: CNLEGIS record 39326, html_fichier_fr sha256 `a790d0a30f7590f0298790703982f416102ac0a1a6024fc262fdcdfee5fb59c1`
- lc/2009-001: CNLEGIS record 40058, html_fichier_fr sha256 `87dcaf8ff430a9c92375c7e204e56f591acd81b15115273ffe3d127310ad2443`
- constitution/2010: CNLEGIS record 51445, html_fichier_fr sha256 `176e4d38889d48ce4690860b6c762805b3e976cf1e9e045afce8117554469fa0`

robots.txt (checked 2026-10-28): `User-agent: GPTBot / Disallow: /`, `User-agent: * / Disallow:`, no rule for ClaudeBot,
Claude-Web or anthropic-ai. CNLEGIS publishes no terms of use (see LICENSE). Before the build, the gate checks and the
exploration made about 45 further requests to cnlegis.gov.mg, one at a time (home and section pages, scripts, searches
for the constitutional acts, Ordonnance n° 62-041 and the 1992 Constitution PDF, which is a scanned image with an OCR
layer and was not used).

## Steps

1. `python -X utf8 tools/build.py --repo <dir>` (online once; then `--offline` rebuilds from the cache).
   `--verify-rebuild` builds again in a temporary folder and compares HEAD.
2. `python -X utf8 tools/check_repo.py --repo <dir> --record`, `python -X utf8 tools/test_repo.py --repo <dir> --record`.
3. Build again (the documentation then carries the results of step 2) and run `--verify-rebuild`.

Tool versions: Python 3.12 (standard library only), git, curl (Windows). Builder blob hashes (`git hash-object`):
- `build.py`: `06f085765382b013e01dc149a50a66d822648641`
- `source.py`: `e542be79a3e00aed95ae5cc76ddcde4e4d39a94c`
- `parse.py`: `bf7e20002971be438db61fd350caced5bd4a314b`
- `reproduce.py`: `7cb133cf2c1b241bd3e0178df4c9d8b7db451b64`
- `check_repo.py`: `25e4f353cfb8a65a255b35c6483cec6b3da02a77`
- `test_repo.py`: `02aea390986fc315db31ea4d8579ca71c768725e`
- `mglaw.py`: `1489cef20f752c90fa11ca3ea4cede30c5ef55a5`

## Method

- `parse.lines`: every block element of the HTML ends a line; inline markup is dropped; entities decoded; U+00A0 becomes
  a space; soft hyphens and zero-width characters are removed; runs of whitespace become one space; empty lines dropped.
- `parse.constitution`: from the line `PREAMBULE` (`PRÉAMBULE` in 2010) up to the annex formula ("Vu pour être annexé
  ...", 1998 and 2007) or the promulgation line (2010). A line starting "Article <number>" opens an article; the number
  is kept as printed and the separator after it (".", ".-", ";-") is dropped; TITRE / SOUS-TITRE / CHAPITRE / SECTION
  lines and the lines after them up to the next article are headings (`structure.md`). The build stops on duplicate or
  out-of-order article numbers.
- 1998, 2007, 2010: the official text of the act. 2009: the 2007 text with article 15 replaced by the one quoted
  paragraph of LC 2009-001 art. 1 (the build stops unless the enacting clause reads exactly "Les dispositions de
  l'article 15 de la Constitution sont modifiées comme suit :" and one "Article 15 (nouveau)" paragraph follows).
- Commit dates: noon, UTC+3 (Madagascar has kept UTC+3 without summer time over the whole record). The in-force day
  of each act and how it was read is in its `In-force-basis:` trailer and in acts.csv.

## Decisions by hand, and AI

No model wrote legal text or ran at build time. The code was written by Claude Code with Claude Opus 5.5
(`claude-opus-5-5`), which also chose the country after the gate checks (Senegal: jo.gouv.sn unreachable; Côte d'Ivoire:
the gazette needs a login and a purchased download code; Burkina Faso: paid gazette and no official consolidation after
the 2015 revision) and read the in-force rules. Decisions by hand:
- the 1998 text as a labelled baseline (no usable 1992 original or LC 95-001);
- the in-force days of LC 98-001, 2007-001 and 2009-001 (earliest possible day; see the trailers);
- one folder for every version, so that a file name holds the article of that number in the text in force (as for
  Luxembourg's 2023 revision), with the renumbering of 2007 and the replacement of 2010 labelled in the commits;
- no second act: CNLEGIS publishes no consolidated texts, so no other act's history could be checked.

## Verification record

- check_repo.py: 4 versions: 666 files compared byte for byte with the official texts, 0 mismatches; letters-and-digits check of the whole texts (lc/98-001 64369 chars; lc/2007-001 59059 chars; constitution/2010 73921 chars); 2009 replay changes article 15 only; 0 problems
- test_repo.py: 6/6 passed
