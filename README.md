# The Constitution of Madagascar, change by change

**Status: building, sources CNLEGIS (cnlegis.gov.mg). Work in progress on the `wip` branch; not final.**

The Constitution of Madagascar as a git repository, in French, from the revised text of 1998 to the Constitution of
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
| `lc/98-001` | Loi constitutionnelle n° 98-001 | baseline | 1998-04-08 | JO n° 2495 du 1998-04-08 | 1998-04-10 | 170 |
| `lc/2007-001` | Loi constitutionnelle n° 2007-001 | revision | 2007-04-27 | JO n° 3104 du 2007-05-03 | 2007-04-27 | 160 |
| `lc/2009-001` | Loi constitutionnelle n° 2009-001 | amendment | 2009-01-19 | JO n° 3236 du 2009-02-19 | 2009-01-19 | 160 |
| `constitution/2010` | Constitution du 11 décembre 2010 | replacement | 2010-12-11 | JO n° 3350 du 2011-01-20 | 2010-12-11 | 168 |

See [`acts.csv`](acts.csv). CNLEGIS lists no constitutional act after the 2010 Constitution (checked 2026-10-28).

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
- check_repo.py: 4 versions: 666 files compared byte for byte with the official texts, 0 mismatches; letters-and-digits check of the whole texts (lc/98-001 64369 chars; lc/2007-001 59059 chars; constitution/2010 73921 chars); 2009 replay changes article 15 only; 0 problems
- test_repo.py: 6/6 passed

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
  République"). CNLEGIS lists the 2010 Constitution as "En vigueur" on 2026-10-28. Words unchanged does not mean law unchanged.
- The Malagasy text, which is also official.

## Licence

CNLEGIS publishes no terms of use; reuse is unclear and the repository is private. See [`LICENSE`](LICENSE).
Tools, history and tables: CC0.
