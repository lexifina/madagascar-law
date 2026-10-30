# Madagascar: law history in git

The law of Madagascar as a git history, in French: one file per article, one commit per law on the day it took effect, and the law that made each change as the commit's author. `git blame` names the law behind every paragraph; `git log` lists every change to an article; `tools/on.py` gives the text in force on any date. Source: CNLEGIS (cnlegis.gov.mg), the official legal database of the Secrétariat Général du Gouvernement (Primature).

It follows the shared design of [lexifina/global-law](https://github.com/lexifina/global-law).

**What is in it now**

| Folder | Act | Versions | History |
| --- | --- | ---: | --- |
| `constitution/` | Constitution de la République de Madagascar | 4 | The 1992 Constitution as revised in 1995 and 1998 (from 10 April 1998), the 2007 revision, the 2009 change to article 15, and the Constitution of 11 December 2010 in force today |
| `loi-2014-006/` | Loi n° 2014-006 sur la lutte contre la cybercriminalité | 2 | As enacted (10 September 2014), and article 20 as replaced by Loi n° 2016-031 (19 April 2017) |
| `loi-2014-038/` | Loi n° 2014-038 sur la protection des données à caractère personnel | 1 | As enacted (22 July 2015); CNLEGIS lists no amendment |
| `mariage-regimes-matrimoniaux/` | Loi n° 2007-022 relative au mariage et aux régimes matrimoniaux | 1 | As promulgated (Journal officiel n° 3163 of 28 January 2008), in force from 30 January 2008; from the Ministry of Justice's published copy. Later amendments, if any, are not checked |
| `successions-testaments-donations/` | Loi n° 68-012 relative aux successions, testaments et donations | 1 | As published (Journal officiel n° 598 of 13 July 1968), in force from 4 January 1969 (six months after promulgation, art. 127); from the Ministry of Justice's published copy. Later amendments, if any, are not checked |
| `code-du-travail/` | Code du travail | 2 | Loi n° 2003-044 (from 23 February 2005), replaced by the new Code du travail, Loi n° 2024-014 (from 6 November 2024) |

## A lawyer's questions as git commands

| Question | Command |
| --- | --- |
| What did article 15 of the Constitution say on 1 June 2008? | `python tools/on.py 2008-06-01 constitution art-015` |
| ... and on 1 June 2009, after LC 2009-001? | `python tools/on.py 2009-06-01 constitution art-015` |
| The same, with raw git (bash) | `git show $(git rev-list -1 --before="2009-06-01T23:59:59Z" main -- constitution/art-015.md):constitution/art-015.md` |
| The same, in PowerShell | `$r = git rev-list -1 --before="2009-06-01T23:59:59Z" main -- constitution/art-015.md; git show "$($r):constitution/art-015.md"` |
| Online insult before and after Loi 2016-031 dropped prison terms | `python tools/on.py 2017-04-18 loi-2014-006 art-020`, then `2017-04-19` |
| Exactly what Loi 2016-031 changed, word by word | `git show --word-diff law/loi-2016-031` |
| Who wrote each line of article 20? | `git blame loi-2014-006/art-020.md` |
| Every law in the record, in order | `git log --reverse --format="%ad %an" --date=short main` |
| The whole Constitution on a date | `python tools/on.py 2000-01-01 constitution` |

Tags: `law/<key>` marks each law's commit, `<act>/<in-force day>` each version. After a rebuild, refresh tags with `git fetch --force --tags`: a plain fetch keeps stale tags.

## Dates

- Each commit is dated at **noon, Indian/Antananarivo (UTC+3), on the day the text took effect**. Promulgation and Journal officiel dates are trailers (`Enacted:`, `Published:`); the in-force day is in `In-force:`, which the tools read.
- **Default rule.** Ordonnance n° 62-041 du 19 septembre 1962, art. 3: "Les lois ne deviennent obligatoires, qu'un jour franc après l'arrivée du Journal officiel, constatée à la sous-préfecture par l'apposition d'un timbre à date." The arrival day is not printed, so a law with no in-force clause is dated the Journal officiel date + 2 days, the earliest possible day (later where the issue arrived later). This applies to LC 98-001, Loi 2014-006, Loi 2014-038, Loi 2016-031, Loi 2003-044 and Loi 2024-014.
- **Urgency.** LC 2007-001 (art. 3) and LC 2009-001 (art. 2) took effect "immédiatement" once broadcast or posted (Ordonnance n° 62-041 art. 4). The broadcast day is not printed, so the promulgation day is used.
- **The 2010 Constitution** took effect on promulgation (art. 164), 11 December 2010.
- Promulgation and publication can be far apart: Loi 2014-038 was promulgated on 9 January 2015 and printed in JO n° 3630 on 20 July 2015; Loi 2016-031 was promulgated on 23 August 2016 and printed on 17 April 2017.

## Read this before comparing versions

- **The first Constitution version is a baseline.** LC 98-001 annexes the whole 1992 Constitution as revised in 1995 and 1998. CNLEGIS has no usable text of the 1992 original (a scanned PDF; this record uses no OCR) or of LC 95-001, so the 1998 text is committed by the publisher as the oldest version available.
- **2007 renumbered the articles.** From article 57 on, a file holds a different article before and after 2007.
- **2010 is a new constitution.** Before and after 2010, `constitution/art-015.md` holds articles of different constitutions.
- **2024 is a new Code du travail.** Before and after 6 November 2024, `code-du-travail/art-040.md` holds articles of different codes. Loi 2024-014 is read from the official PDF CNLEGIS links (text layer, pdftotext); its words are checked against the PDF, its paragraph breaks are as pdftotext gives them.
- **Two versions are replayed**, because CNLEGIS publishes no consolidated texts: the Constitution in 2009 (the 2007 text with article 15 replaced by the words LC 2009-001 quotes) and Loi 2014-006 in 2017 (article 20 replaced by the words Loi 2016-031 quotes). The build stops unless the amending act reads exactly as a single replacement.

## How it is checked

- Every version of every act is read back from git on the day it took effect and on the day before (`tools/check_repo.py`); both must match `corpus.json`. Results are in `REPRODUCE.md`.
- Health checks: no merge commits, commit dates never go backwards, nothing dated in the future, and every commit's trailers parse.
- Today's text is the official text of the latest act: the 2010 Constitution and Loi 2014-038 as printed by CNLEGIS, and Loi 2014-006 with article 20 as quoted in Loi 2016-031.
- The repository is rebuilt from the same data a second time and must give identical hashes.

## What "author" means

The author of a commit is the law that made the change, with an e-mail address that cannot exist (`loi-2016-031@cnlegis.invalid`), so `git blame` and `git log --author` name laws. The committer is always Lexifina. Blame credits whole lines (one paragraph per line); use `git log -p --word-diff` for the words.

## What it does not show

- **The Code pénal.** CNLEGIS holds no text of the Code pénal itself, only its amending laws, and those before 1998 have no text; no official consolidated Code pénal with a text layer was found. It is left out.
- **Amendments to Loi n° 2007-022** (marriage and matrimonial property) **and Loi n° 68-012** (successions). Their texts are the Ministry of Justice's copies of the laws as published in the Journal officiel (28 January 2008 and 13 July 1968); later amending laws were not searched for. The exposé des motifs of Loi n° 68-012 is left out.
- The 1992 original Constitution and LC 95-001 as separate versions, and the earlier constitutions (1959, 1975).
- Acts that changed how the Constitution worked without changing its words: Ordonnance n° 2009-001 of 17 March 2009, the Charte de la Transition (2009), and the events since October 2025. CNLEGIS lists the 2010 Constitution as "En vigueur" on 28 October 2026. Words unchanged does not mean law unchanged.
- Implementing decrees (for example Décret n° 2023-1541 for Loi 2014-038) and decisions of the Haute Cour constitutionnelle reviewing laws before promulgation.
- The Malagasy text, which is also official.

## How it is built

Lexifina reads the sources listed here and records each act's dated versions, and the laws that made each change, in one corpus file. `tools/build.py` writes this repository from that file, and the same corpus always gives the same commit hashes; `REPRODUCE.md` gives the details and the checks. A model (Claude) wrote Lexifina's code; it wrote no legal text, and no model runs when the history is built.

No AI model wrote or changed legal text. Claude Opus 5.5 (`claude-opus-5-5`) wrote the scripts and chose the sources; see `REPRODUCE.md`.

## Licence

CNLEGIS publishes no terms of use; reuse terms are unclear, and the repository is private. See `LICENSE`.

---

## En français

L'histoire du droit malgache dans git : un fichier par article, un commit par loi au jour de son entrée en vigueur, la loi qui a fait la modification en auteur du commit. Source : CNLEGIS (cnlegis.gov.mg), Secrétariat Général du Gouvernement, Primature.

- `constitution/` : la Constitution de 1992 révisée (en vigueur au 10 avril 1998), la révision de 2007, l'article 15 modifié en 2009, et la Constitution du 11 décembre 2010.
- `loi-2014-006/` : la loi sur la lutte contre la cybercriminalité, et son article 20 modifié par la loi n° 2016-031.
- `loi-2014-038/` : la loi sur la protection des données à caractère personnel.
- `mariage-regimes-matrimoniaux/` : la loi n° 2007-022 du 20 août 2007 relative au mariage et aux régimes matrimoniaux, telle que promulguée (JO n° 3163 du 28 janvier 2008), d'après la copie publiée par le Ministère de la Justice (justice.gov.mg).
- `successions-testaments-donations/` : la loi n° 68-012 du 4 juillet 1968 relative aux successions, testaments et donations, telle que publiée (JO n° 598 du 13 juillet 1968), en vigueur six mois après sa promulgation, d'après la copie du Ministère de la Justice.
- `code-du-travail/` : la loi n° 2003-044, remplacée par la loi n° 2024-014 portant Code du travail.

Dates : midi, heure d'Antananarivo, au jour de l'entrée en vigueur. À défaut de clause, l'ordonnance n° 62-041 art. 3 (un jour franc après l'arrivée du Journal officiel) : la date du JO + 2 jours, le jour le plus tôt possible. Texte en vigueur à une date : `python tools/on.py AAAA-MM-JJ constitution art-015`. Le Code pénal n'y figure pas : CNLEGIS n'en publie pas de texte consolidé.
