# How this repository was made (Madagascar)

This file is written by the build on 2026-10-28, the day the source data was retrieved. Everything below is enough to rebuild this repository hash for hash.

## Sources

| Source | Address | Retrieved | Requests | Licence |
| --- | --- | --- | ---: | --- |
| CNLEGIS (cnlegis.gov.mg) | <https://cnlegis.gov.mg/> | 2026-10-28 | 21 | No terms of use published. robots.txt (2026-10-28): GPTBot disallowed, all others allowed. |

Every response is cached by the sha256 of its URL, and the table above lists every source with its retrieval date. Lexifina keeps its fetch scripts privately; `tools/parse.py` reads only the cache and writes `corpus.json`, so the same cache always gives the same corpus.

## What is in it

| Act | Title | Versions | Span |
| --- | --- | ---: | --- |
| `constitution` | Constitution de la République de Madagascar | 4 | 1998-04-10 to 2010-12-11 |
| `loi-2014-006` | Loi n° 2014-006 du 17 juillet 2014 sur la lutte contre la cybercriminalité | 2 | 2014-09-10 to 2017-04-19 |
| `loi-2014-038` | Loi n° 2014-038 du 9 janvier 2015 sur la protection des données à caractère personnel | 1 | 2015-07-22 to 2015-07-22 |

The build made 7 commits:

| Commits | Kind |
| ---: | --- |
| 3 | first version of an act |
| 4 | one law on its in-force day |
| 0 | changes no amendment note explains, credited to the publisher |

Other counts:
- 0 commits on the branch `futur`: laws not yet in force on 2026-10-28.
- 0 commits dated 1 January 1970: in force before 1970, with the real day in their `In-force` trailer.
- 9 laws in the record.
- 13 tags.

## Dates

Each commit is dated at noon (Indian/Antananarivo) on the day the change took effect. The other dates, enacted and published, are trailers.

When a law gives no date of its own, the default rule applies: Ordonnance n° 62-041 du 19 septembre 1962 art. 3: "Les lois ne deviennent obligatoires, qu'un jour franc après l'arrivée du Journal officiel, constatée à la sous-préfecture par l'apposition d'un timbre à date" (art. 4: immediately on posting, in case of declared urgency). The earliest day, the JO date + 2, is used. https://cnlegis.gov.mg/uploads/O62-041-VF.pdf

## Commands, in order

```sh
# fill the cache from the sources listed above (network; Lexifina's fetch scripts are kept privately)
python -X utf8 tools/parse.py                  # cache -> corpus.json (no network)
python -X utf8 tools/build.py <folder> --repo <empty folder> --docs-date 2026-10-28
python -X utf8 tools/check_repo.py <repo> --corpus <folder>/corpus.json --write
python -X utf8 tools/build.py <folder> --repo <another empty folder> --docs-date 2026-10-28 --compare <repo>
```

In the main Lexifina repository these files live as follows:
- `fetch.py`, `parse.py` and `repo/`: in `scripts/madagascar-law/`.
- `build.py`, `check_repo.py` (`check.py` there) and `on.py`: in `scripts/gitlaw_common/`, with the corpus format in `SCHEMA.md`.

## Exact inputs

- `corpus.json` sha256 `9c30f65cb2fa1e85ab5d57b7f0292a65ac1ce5c4a5669b5f27a63eec5f9109d7` (548923 bytes)
- Script blob hashes (`git hash-object`):

| Script | Blob |
| --- | --- |
| build.py | `833a2433a3ea96fd87477ccc7a2ed47dc9e24b48` |
| check.py | `426d4cfb32ce103715be6a00865c0a7bca81a56a` |
| on.py | `644a6c0857fbcc72562032b58d57aa113fee0641` |
| fetch.py | `e47c2b758d82509094bccafa6244cd8bdc21ad12` |
| parse.py | `9493b0738d321c1a551622f6a89c994ae9b429e1` |

- Tools:
  - Python 3.14.0
  - git version 2.52.0.windows.1
  - curl 8.21.0 (Windows) libcurl/8.21.0 Schannel zlib/1.3.2 WinIDN WinLDAP

## Checks

7 versions of 3 acts read back from git on the day each took effect and on the day before: 0 mismatches. Trailers: 0 commits whose trailers git cannot parse. Health: 0 merge commits on main, 0 commit dates that go backwards, 0 commits dated after the build.

A second build from the same corpus into an empty folder gave identical hashes for all 7 history commits and 13 tags (history tip `61aa8dbb11eddc78a1a19e151c6a5c8c2e70a377`).

These results are from the check run on the build before this one, from the same corpus.

## Decisions made by hand

- Constitution: the first version (1998-04-10) is the whole text annexed to LC 98-001, credited to the publisher as the oldest version available (first_law null), naming the 1992 Constitution, LC 95-001 and LC 98-001: CNLEGIS has no usable text of the 1992 original (a scanned PDF, not read: no OCR) or of LC 95-001.
- Constitution: LC 98-001 has no in-force clause, so the default rule applies (Ordonnance n° 62-041 art. 3: one clear day after the Journal officiel reaches the sous-préfecture). JO n° 2495 is dated 1998-04-08, so 1998-04-10 is the earliest day (later where the issue arrived later).
- Constitution: LC 2007-001 art. 3 and LC 2009-001 art. 2 bring them into force "immédiatement" on radio and television broadcast or posting (Ordonnance n° 62-041 art. 4), independently of the Journal officiel. The broadcast day is not printed, so the promulgation day (2007-04-27, 2009-01-19), the earliest possible, is used.
- Constitution: the 2010 Constitution art. 164: "Elle entrera en vigueur dès sa promulgation"; promulgated 2010-12-11 (CNLEGIS record 51445).
- Constitution: LC 2009-001 is replayed on the 2007 text (article 15 replaced by the quoted paragraph); the parse stops unless the enacting clause and the quoted paragraph read exactly as expected and only article 15 changes.
- Constitution: one folder for every version (as in the earlier CNLEGIS build of this repository), so a file name holds the article of that number in the text in force; the 2007 renumbering and the 2010 replacement are labelled in the version notes. Every unit that differs in 2007 and 2010 is credited to that act, which enacted the whole text.
- Constitution: CNLEGIS lists no constitutional act after the 2010 Constitution and shows it "En vigueur" (searched 2026-10-28). Acts that changed how the Constitution worked without changing its words (Ordonnance n° 2009-001, the 2009 Charte de la Transition, the events of October 2025) are not shown.
- Loi n° 2014-006: no in-force clause; Ordonnance n° 62-041 art. 3 (one clear day after the JO arrives). JO n° 3574 is dated 2014-09-08, so 2014-09-10 is the earliest day.
- Loi n° 2016-031: no in-force clause; JO n° 3746 is dated 2017-04-17, so 2017-04-19 is the earliest day (Ordonnance n° 62-041 art. 3).
- Loi n° 2014-006: today's text is replayed: the 2014 text with article 20 replaced by the four paragraphs Loi n° 2016-031 art. 1 quotes ("Article 20 (nouveau)"). CNLEGIS notes for Loi 2014-006 name only Loi 2016-031 as amending it, and publishes no consolidated text; the parse stops unless only article 20 changes.
- Loi n° 2014-006: HCC décision n° 12-HCC/D3 du 16 juillet 2014 reviewed the law before promulgation; the promulgated text already reflects it, so it is not a change to the text.
- Loi n° 2014-038: no in-force clause; JO n° 3630 is dated 2015-07-20, so 2015-07-22 is the earliest day (Ordonnance n° 62-041 art. 3). CNLEGIS prints the promulgation as "Antananarivo, le 09 janvier 2015".
- Loi n° 2014-038: CNLEGIS shows it "En vigueur" and its notes name only the implementing Décret n° 2023-1541; searches for "2014-038" list no amending law (2026-10-28), so the act has one version, as enacted.
- Code pénal (Phase 1 spec) not built: CNLEGIS holds no text of the Code pénal itself, only amending laws, and those before 1998 have no text; no official consolidated Code pénal with a text layer was found. Loi n° 2014-006 (cybercrime, a penal statute with an amendment CNLEGIS publishes) was taken instead.
- Text normalisation (parse.py): curly single and double quotes become straight ones; runs of spaces collapse; NBSP, soft hyphens and zero-width characters are removed (cnparse.lines). CNLEGIS typing errors are kept.
- All texts are the French HTML CNLEGIS serves (html_fichier_fr). The Malagasy text, also official, is not used.

## What AI did and did not do

The fetch, parse and check scripts were written by Claude Code running Claude Opus 5.5 (`claude-opus-5-5`) under Lexifina's direction.

No model wrote, translated or corrected legal text. No model runs at build time. Every word of law in this repository comes from the official sources above, through code that anyone can rerun.

The commit messages are written by `build.py` from the source data.

Model use at data-build time:
- none at data-build time: no model read, wrote or summarised legal text. parse.py and fetch.py were written by Claude Code (Claude Opus 5.5, claude-opus-5-5); the act choice and in-force readings were made by that agent from the cached official texts and are listed in decisions.
