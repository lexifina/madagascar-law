"""Writes the repository's documentation: README.md, LICENSE, REPRODUCE.md, corpus.json, acts.csv, and copies the tools.
Called by build.py; deterministic (no clock, no network). verification.json (written by check_repo.py and test_repo.py
with --record) is read when it exists, so the second build carries the results of the checks on the first."""
import hashlib
import json
import shutil
import subprocess
from pathlib import Path

TOOLS = ('build.py', 'source.py', 'parse.py', 'reproduce.py', 'check_repo.py', 'test_repo.py')


def blob(p: Path) -> str:
    return subprocess.run(['git', 'hash-object', str(p)], capture_output=True, text=True).stdout.strip()


def write_docs(repo: Path, acts, vs, day: str, here: Path, wip: bool = False):
    ver = {}
    vp = here / 'verification.json'
    if vp.exists():
        ver = json.loads(vp.read_text(encoding='utf-8'))
    first, last = acts[0]['in_force'], acts[-1]['in_force']
    corpus = {
        'corpus': 'mg/national/acts',
        'name': 'Malagasy law: the Constitution (1992 Constitution as revised, 1998-2010; Constitution of 2010)',
        'label': 'Madagascar',
        'language': 'fr',
        'acts': [a['title'] for a in acts],
        'history_from': first,
        'record_to': day,
        'record_note': (f'From the 1998 revised text (in force {first} at the earliest) to the Constitution of 11 '
                        f'December 2010 (in force {last}); CNLEGIS lists no constitutional act after 2010 on {day}, '
                        f'the day the data was retrieved and checked.'),
        'in_force_trailer': 'In-force',
        'baseline_trailer': 'Consolidated',
        'has_future_branch': False,
        'built': day,
        'dates': {'commit': 'in-force', 'other_trailers': ['Enacted', 'Published', 'In-force-basis'],
                  'time': '12:00 Indian/Antananarivo (UTC+3; no summer time)'},
        'scope': {
            'trailer': 'Applies',
            'when_absent': 'this corpus records no scope notes (no commit carries Applies:); the absence is not a '
                           'statement that the change reaches every case',
            'default_reach': {
                'rule': 'immediate effect without retroactivity (Ordonnance n° 62-041 du 19 septembre 1962, art. 8); '
                        'no punishment without a law promulgated and published before the act (Constitution 2010, '
                        'art. 13)',
                'meaning': 'a new law applies to situations already established when it does not alter the effects '
                           'already produced by an earlier legal situation; procedural laws apply to pending cases '
                           'not yet decided on the merits; interpretive laws reach back only where the legislature '
                           'clearly says so',
                'authority': 'Ordonnance n° 62-041 du 19 septembre 1962 relative aux dispositions générales de droit '
                             'interne et de droit international privé, art. 8 (CNLEGIS, uploads/O62-041-VF.pdf); '
                             'Constitution du 11 décembre 2010, art. 13',
                'decided_here': False}},
        'replayed': 'partial: only the 2009 version (LC 2009-001, article 15) is replayed; the 1998, 2007 and 2010 '
                    'versions are whole official texts',
        'tool': 'tools/mglaw.py',
        'citation': {'file': '(constitution)/article-0*([0-9]+(?:\\.[0-9]+)?)\\.md',
                     'cites': '([Aa]rticle|[Aa]rt\\.) ?{n}([^0-9]|$)'},
    }
    (repo / 'corpus.json').write_text(json.dumps(corpus, indent=2, ensure_ascii=False) + '\n', encoding='utf-8',
                                      newline='\n')
    rows = ['tag,author,kind,enacted,journal_officiel,in_force,articles_after,cnlegis_record,in_force_basis']
    for a, v in zip(acts, vs):
        rows.append(','.join('"' + str(x).replace('"', '""') + '"' for x in [
            a['tag'], a['author'], a['kind'], a['enacted'], f'JO n° {a["jo"][0]} du {a["jo"][1]}', a['in_force'],
            len(v['articles']), a['id'], a['basis']]))
    (repo / 'acts.csv').write_text('\n'.join(rows) + '\n', encoding='utf-8', newline='\n')

    (repo / 'LICENSE').write_text(
        'Source of the legal texts: CNLEGIS, the legal database of the Direction du CNLEGIS, Secrétariat Général du\n'
        'Gouvernement, Primature, Republic of Madagascar: https://cnlegis.gov.mg/\n\n'
        'Terms of use: CNLEGIS publishes none. Its pages carry only the footer "© 2018 DIRCNLEGIS ." (checked\n'
        f'{day}; /mentions-legales/, /cgu/ and /conditions-utilisation/ return the generic search page). Its robots.txt\n'
        'disallows GPTBot and allows every other agent. The reuse terms for the legal texts are therefore unclear:\n'
        'this repository is private and is not to be published until they are settled.\n\n'
        'The texts are official acts of the Republic of Madagascar, as printed by CNLEGIS. Only the Journal officiel\n'
        'de la République de Madagascar is authoritative. The 2009 version is derived (replayed) from official texts\n'
        'by the method in REPRODUCE.md; it is not published by CNLEGIS.\n\n'
        'Attribution for the legal texts: "Texts: CNLEGIS, Direction du CNLEGIS (Primature), https://cnlegis.gov.mg/".\n\n'
        'The history (commits and commit messages), the tables and the tools are dedicated to the public domain under\n'
        'CC0 1.0 Universal: https://creativecommons.org/publicdomain/zero/1.0/legalcode\n',
        encoding='utf-8', newline='\n')

    ok = ''
    if ver:
        c, s = ver.get('check', {}), ver.get('smoke', {})
        ok = (f'- check_repo.py: {c.get("summary", "not recorded")}\n'
              f'- test_repo.py: {s.get("passed", "?")}/{s.get("total", "?")} passed\n')
    table = '\n'.join(f'| `{a["tag"]}` | {a["author"]} | {a["kind"]} | {a["enacted"]} | JO n° {a["jo"][0]} du '
                      f'{a["jo"][1]} | {a["in_force"]} | {len(v["articles"])} |' for a, v in zip(acts, vs))
    status = ('**Status: building, sources CNLEGIS (cnlegis.gov.mg). Work in progress on the `wip` branch; not '
              'final.**\n\n') if wip else ''
    (repo / 'README.md').write_text(f'''# The Constitution of Madagascar, change by change

{status}The Constitution of Madagascar as a git repository, in French, from the revised text of 1998 to the Constitution of
11 December 2010 that is in force today. Each constitutional act is one commit, credited to that act and dated the day it
took effect, at noon in Antananarivo. Source: CNLEGIS (cnlegis.gov.mg), the official legal database of the Primature.

## The questions, as git commands

| Question | Command |
| --- | --- |
| What did article 15 say on 1 June 2008? | `python tools/mglaw.py 2008-06-01 constitution 15` |
| ... and on 1 June 2009, after LC 2009-001? | `python tools/mglaw.py 2009-06-01 constitution 15` |
| The whole Constitution as it stood on 1 January 2000 | `python tools/mglaw.py 2000-01-01 constitution` |
| Which act wrote each line of article 15 in 2009? | `git blame lc/2009-001 -- constitution/article-015.md` |
| Every change to the file article-015.md, with its act and day | `git log --follow --format="%an %(trailers:key=In-force,valueonly,separator=)" main -- constitution/article-015.md` |
| Exactly what LC 2009-001 changed, word by word | `git show --word-diff lc/2009-001 -- constitution/article-015.md` |
| Everything one act changed | `git show --stat lc/2009-001` |
| The acts, with their in-force days | `git log --format="%an, in force %(trailers:key=In-force,valueonly,separator=)" main` |
| One tag per act | `git tag --list` |
| How the in-force day of each act was read | `git log --format="%an: %(trailers:key=In-force-basis,valueonly,separator=)" main` |

PowerShell splits `git show $(...):path`; use `$r = git rev-list -1 main; git show "$($r):constitution/article-015.md"`.
For a date, prefer `tools/mglaw.py`, which reads the `In-force:` trailer: `git rev-list --before=DATE` compares commit
times in your own time zone and flips at noon on the day itself.

## The acts

| Tag | Author | Kind | Enacted | Published | In force | Articles |
| --- | --- | --- | --- | --- | --- | --- |
{table}

See [`acts.csv`](acts.csv). CNLEGIS lists no constitutional act after the 2010 Constitution (checked {day}).

## The dates, and which one we use

Each act has the day it was promulgated (`Enacted:`), the Journal officiel issue that printed it (`Published:`), and
the day it took effect (`In-force:`). **Commits are dated the day the text took effect**, at noon in Antananarivo (UTC+3).
How that day was read is in each commit's `In-force-basis:` trailer:
- the 2010 Constitution took effect on promulgation (art. 164);
- LC 2007-001 and LC 2009-001 took effect "immédiatement" once broadcast on radio and television or posted, without
  waiting for the Journal officiel. The broadcast day is not printed, so the promulgation day is used: the earliest
  possible day;
- LC 98-001 has no in-force clause. Under Ordonnance n° 62-041 art. 3 a law binds one clear day after the Journal
  officiel reaches each sous-préfecture; the issue is dated 8 April 1998, so 10 April 1998 is the earliest day.

## What "author" means

The author of a commit is the act that made the text (`Loi constitutionnelle n° 2009-001`, address
`lc-2009-001@cnlegis.invalid`), so `git blame` names the act. The committer is always `Lexifina`.

## Read this before comparing versions

- **The first version is a baseline.** LC 98-001 annexes the whole 1992 Constitution as revised in 1995 and 1998.
  CNLEGIS has no usable text of the 1992 original (a scanned PDF) or of LC 95-001, so all its lines are credited to
  LC 98-001: read them as "in force from 1998 at the latest" (`Kind: baseline`, `Consolidated:` trailer).
- **2007 renumbered the articles.** LC 2007-001 annexes the whole revised text with new numbers (170 articles and
  sub-articles became 160), so from article 57 on, a file holds a different article before and after 2007. Compare texts
  across that commit, not paths. Every line of the 2007 annex is credited to LC 2007-001, which enacted it.
- **2010 is a new constitution.** It rewrites every file; `constitution/article-015.md` before and after 2010 are
  different articles of different constitutions.
- **Blame credits whole lines to the act that first printed them**: one line is one paragraph, and a line a later act
  printed again unchanged (a heading such as `# Article 15`, or a paragraph the 2010 Constitution kept word for word)
  keeps its first author. Use `--word-diff` for the words.

## How it is checked

`tools/check_repo.py` reads every version back from git and compares it with the official text, byte for byte, file
by file (1998, 2007 and 2010 against the act's own text; 2009 against the 2007 text with article 15 replaced by the
words LC 2009-001 quotes, and every other file unchanged), and again as a stream of letters and digits taken straight
from the official text, without the article parser. `tools/test_repo.py` checks that the commands above work. See
[`REPRODUCE.md`](REPRODUCE.md).
{ok}
## Files

`constitution/article-NNN.md` is one article (`article-082.1.md` a sub-numbered one); the `#` line is its number as
printed, then one line per paragraph, exactly as CNLEGIS prints it (its typography, including its typing errors, is
kept). `preambule.md` is the preamble, `structure.md` the titles, sub-titles and chapters, each with the article it opens.

## What it does not show

- The 1992 original and LC 95-001 as separate versions (no usable text on CNLEGIS), and the earlier constitutions
  (1959, 1975).
- Acts that changed how the Constitution worked without changing its words, for example Ordonnance n° 2009-001 of
  17 March 2009 conferring full powers on a military directorate, the Charte de la Transition ratified by Ordonnance
  n° 2009-009, or anything since October 2025 (2026 laws are promulgated by the "Présidence de la Refondation de la
  République"). CNLEGIS lists the 2010 Constitution as "En vigueur" on {day}. Words unchanged does not mean law unchanged.
- The Malagasy text, which is also official.

## Licence

CNLEGIS publishes no terms of use; reuse is unclear and the repository is private. See [`LICENSE`](LICENSE).
Tools, history and tables: CC0.
''', encoding='utf-8', newline='\n')

    cache = here / 'cache'
    reqs = []
    if (cache / 'requests.jsonl').exists():
        reqs = [json.loads(l) for l in (cache / 'requests.jsonl').read_text(encoding='utf-8').splitlines() if l]
    used = sorted({(a['search'][0], a['search'][1], a['search'][2]) for a in acts})
    data_rows = []
    for kind, q, lim in used:
        r = next((x for x in reqs if (x['kind'], x['query'], x['limit']) == (kind, q, lim)), None)
        data_rows.append(f'- `{kind}` search "{q}" (limit {lim}): '
                         + (f'`{r["file"]}`, sha256 `{r["sha256"]}`' if r else 'not in requests.jsonl'))
    rec_rows = '\n'.join(f'- {a["tag"]}: CNLEGIS record {a["id"]}, html_fichier_fr sha256 '
                         f'`{hashlib.sha256(a["record"]["html_fichier_fr"].encode("utf-8")).hexdigest()}`'
                         for a in acts)
    blobs = '\n'.join(f'- `{n}`: `{blob(here / n)}`' for n in TOOLS) + f'\n- `mglaw.py`: `{blob(here / "repo/tools/mglaw.py")}`'
    (repo / 'REPRODUCE.md').write_text(f'''# Reproduce

Data retrieved {day}. The build is deterministic: the same data gives the same commit hashes.

## Sources and requests

CNLEGIS (https://cnlegis.gov.mg/), the official legal database of the Direction du CNLEGIS (Secrétariat Général du
Gouvernement, Primature). It serves each text's official French HTML inside the JSON of its search endpoints: a search is
two POSTs in one session, the search form (`page_find_direct_mots/` or `page_num_find_direct/`, field `txt_recherche`)
and then the data endpoint (`page_data_result_direct_mots/` or `page_num_data_find_direct/`, field `var_pg_limit`).
The build reads two searches (four requests), sent one at a time with a User-Agent and a pause, cached in
`tools/cache` (git-ignored) with each answer's sha256:
{chr(10).join(data_rows)}

The four texts used, with the sha256 of each official HTML (UTF-8):
{rec_rows}

robots.txt (checked {day}): `User-agent: GPTBot / Disallow: /`, `User-agent: * / Disallow:`, no rule for ClaudeBot,
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
{blobs}

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

{ok or '(not yet recorded)'}''', encoding='utf-8', newline='\n')

    tools = repo / 'tools'
    tools.mkdir(exist_ok=True)
    for n in TOOLS:
        shutil.copyfile(here / n, tools / n)
    shutil.copyfile(here / 'repo/tools/mglaw.py', tools / 'mglaw.py')
