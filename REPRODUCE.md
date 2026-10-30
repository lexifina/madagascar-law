# How this repository was made (Madagascar)

This file is written by the build on 2026-10-30, the day the source data was retrieved.

## Sources

| Source | Address | Retrieved | Licence |
| --- | --- | --- | --- |
| CNLEGIS (cnlegis.gov.mg) | <https://cnlegis.gov.mg/> | 2026-10-28 | No terms of use published. |
| Ministère de la Justice (justice.gov.mg), "Textes sur la famille", via the Internet Archive | <http://www.justice.gov.mg:80/wp-content/uploads/textes/1TEXTES%20NATIONAUX/DROIT%20PRIVE/Textes%20sur%20la%20Famille/5.pdf> | 2026-10-30 | Official text published by the Ministry of Justice; no licence stated. |
| Ministère de la Justice (justice.gov.mg), "Textes sur la famille", via the Internet Archive | <http://www.justice.gov.mg:80/wp-content/uploads/textes/1TEXTES%20NATIONAUX/DROIT%20PRIVE/Textes%20sur%20la%20Famille/3.pdf> | 2026-10-30 | Official text published by the Ministry of Justice; no licence stated. |

Every word of law in this repository comes from these sources. Lexifina reads them and records each act's dated versions, and the laws that made each change, in one corpus file. This repository is built from that file.

## What is in it

| Act | Title | Versions | Span |
| --- | --- | ---: | --- |
| `constitution` | Constitution de la République de Madagascar | 4 | 1998-04-10 to 2010-12-11 |
| `loi-2014-006` | Loi n° 2014-006 du 17 juillet 2014 sur la lutte contre la cybercriminalité | 2 | 2014-09-10 to 2017-04-19 |
| `loi-2014-038` | Loi n° 2014-038 du 9 janvier 2015 sur la protection des données à caractère personnel | 1 | 2015-07-22 to 2015-07-22 |
| `code-du-travail` | Code du travail | 2 | 2005-02-23 to 2024-11-06 |
| `mariage-regimes-matrimoniaux` | Loi n° 2007-022 du 20 août 2007 relative au mariage et aux régimes matrimoniaux | 1 | 2008-01-30 to 2008-01-30 |
| `successions-testaments-donations` | Loi n° 68-012 du 4 juillet 1968 relative aux successions, testaments et donations | 1 | 1969-01-04 to 1969-01-04 |

The build made 11 commits:

| Commits | Kind |
| ---: | --- |
| 6 | first version of an act |
| 5 | one law on its in-force day |
| 0 | changes no amendment note explains, credited to the publisher |

Other counts:
- 0 commits on the branch `futur`: laws not yet in force on 2026-10-30.
- 1 commits dated 1 January 1970: in force before 1970, with the real day in their `In-force` trailer.
- 13 laws in the record.
- 21 tags.

## Dates

Each commit is dated at noon (Indian/Antananarivo) on the day the change took effect. The other dates, enacted and published, are trailers.

When a law gives no date of its own, the default rule applies: Ordonnance n° 62-041 du 19 septembre 1962 art. 3: "Les lois ne deviennent obligatoires, qu'un jour franc après l'arrivée du Journal officiel, constatée à la sous-préfecture par l'apposition d'un timbre à date" (art. 4: immediately on posting, in case of declared urgency). The earliest day, the JO date + 2, is used. https://cnlegis.gov.mg/uploads/O62-041-VF.pdf

## How the history is built

`tools/build.py` turns the corpus into this history in one pass: one commit per law, on the day it took effect. The same corpus always gives the same commit hashes. `tools/check_repo.py` reads every version back from git and compares it with the corpus. `tools/on.py` shows the law as it stood on any date. The corpus format is described in `tools/SCHEMA.md`.

- Corpus: sha256 `a5151d48ffe0182cf6647f899247845075276a46c624d1dc71dc80904f5b119b` (1125648 bytes).
- Builder blob hashes (`git hash-object`): `build.py` `a4faa25af85facb64b956b372f6b528aafdd7ec1`, `check.py` `3d00541d258745461ab52b1b0cb4e1716a27a95d`, `on.py` `644a6c0857fbcc72562032b58d57aa113fee0641`.
- Python 3.12.10; git version 2.46.0.windows.1.

## Checks

11 versions of 6 acts read back from git on the day each took effect and on the day before: 0 mismatches. Trailers: 0 commits whose trailers git cannot parse. Health: 0 merge commits on main, 0 commit dates that go backwards, 0 commits dated after the build.

A second build from the same corpus into an empty folder gave identical hashes for all 11 history commits and 21 tags (history tip `761fece310bd87792f5861aa703372b61e71ae5d`).

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
- Code du travail: Loi n° 2003-044 (promulgated 2004-07-28, JO n° 2956 of 2005-02-21) has no in-force clause, so 2005-02-23 is the earliest day (Ordonnance n° 62-041 art. 3). CNLEGIS notes name no amending law, only implementing texts.
- Code du travail: Loi n° 2024-014 (promulgated 2024-08-14, JO n° 4237 of 2024-11-04) replaces it (art. 394 repeals Loi 2003-044); no in-force clause, so 2024-11-06 is the earliest day. Its 395 articles share the folder with the 2003 code, so before and after this version a file holds an article of a different code; every unit that differs is credited to Loi 2024-014, which enacted the whole text.
- Code du travail 2024: CNLEGIS gives only a cover page in HTML and links the official PDF (L2024-014-VF.pdf, text layer, no OCR), read with pdftotext 4.00 (poppler): page numbers dropped; a paragraph cut by a page break is joined when the line before it does not end a sentence or the next starts in lower case; headings and articles that pdftotext runs into one line are split; the one article printed "Art. 40." is read as "Article 40". Paragraph breaks are as pdftotext gives them; the words are checked against the PDF.
- Code pénal (Phase 1 spec) not built: CNLEGIS holds no text of the Code pénal itself, only amending laws, and those before 1998 have no text; no official consolidated Code pénal with a text layer was found. Loi n° 2014-006 (cybercrime, a penal statute with an amendment CNLEGIS publishes) was taken instead.
- Text normalisation: curly single and double quotes become straight ones; runs of spaces collapse; NBSP, soft hyphens and zero-width characters are removed. CNLEGIS typing errors are kept.
- All texts are the French HTML CNLEGIS serves (html_fichier_fr). The Malagasy text, also official, is not used.
- Loi n° 2007-022 (mariage et régimes matrimoniaux): one version, the law as promulgated, from the Ministry of Justice's copy, which cites J.O. n° 3163 du 28/01/08, p. 131; dated 2008-01-30 by the default rule (Ordonnance n° 62-041 art. 3: one clear day after the J.O. arrives; the earliest day, J.O. date + 2), since the law fixes no date of its own (art. 156: "sera exécutée comme loi de l’Etat").
- Loi n° 2007-022: later amendments, if any, were not searched (CNLEGIS needs form submissions, which this build does not use), so this is the text as promulgated.
- Loi n° 2007-022: the title lines and J.O. citation printed above the formula are left out; titles, chapters and sections form the unit "structure"; the date and signature form the unit "signature".
- Loi n° 68-012 (successions, testaments et donations): one version, the law as published, from the Ministry of Justice's copy, which cites J.O. n° 598 du 13.07.68, p. 1438; dated 1969-01-04 by its art. 127 ("six mois après sa promulgation"), promulgated 4 July 1968.
- Loi n° 68-012: the Ministry's copy prints the exposé des motifs and the articles but no enacting formula or signature; the exposé is left out. Later amendments, if any, were not searched (CNLEGIS needs form submissions, which this build does not use).
- Loi n° 68-012: art. 75 is printed without the dash after its number ("Art. 75 Lorsque …"); it is read as art. 75.

## What AI did and did not do

The scripts that read the sources and build this repository were written by Claude Code running Claude Opus 5.5 (`claude-opus-5-5`) under Lexifina's direction.

No model wrote, translated or corrected legal text. No model runs at build time. Every word of law in this repository comes from the official sources above.

The commit messages are written by `build.py` from the source data.

Model use at data-build time:
- none at data-build time: no model read, wrote or summarised legal text. Lexifina's code was written by Claude Code (Claude Opus 5.5, claude-opus-5-5); the act choice and in-force readings were made with it from the official texts and are listed in decisions.
