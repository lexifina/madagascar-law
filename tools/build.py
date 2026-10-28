"""Builds the Madagascar git-for-law repository: the Constitution, 1998 to today, from CNLEGIS (cnlegis.gov.mg).

    python -X utf8 build.py --repo DIR [--offline] [--docs-date YYYY-MM-DD] [--verify-rebuild]

Sources (official French HTML served by CNLEGIS, Direction du CNLEGIS, Primature; see source.py):
  - Loi constitutionnelle n° 98-001 du 8 avril 1998 (record 34738): annexes the whole Constitution of 18 September 1992
    as revised by LC 95-001 and LC 98-001 ("dans sa nouvelle rédaction"). This is the first version (a baseline).
  - Loi constitutionnelle n° 2007-001 du 27 avril 2007 (record 39326): annexes the whole revised, renumbered text.
  - Loi constitutionnelle n° 2009-001 du 19 janvier 2009 (record 40058): replaces article 15. This is the only version
    that is REPLAYED (the 2007 text with article 15 replaced by the act's quoted words).
  - Constitution de la République de Madagascar du 11 décembre 2010 (record 51445): a new constitution, in force on
    promulgation; it replaces the whole text.
No constitutional act after 2010 is listed by CNLEGIS (checked on the retrieval day).

One commit per act per in-force day, authored by the act, at noon in Antananarivo (UTC+3, no summer time). The text is
kept exactly as CNLEGIS prints it, line by line (parse.lines); nothing is normalised. Standard library only.
"""
import argparse
import datetime as dt
import json
import os
import re
import shutil
import stat
import subprocess
import sys
import tempfile
from pathlib import Path

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))
import parse as P  # noqa: E402
import source as S  # noqa: E402

FOLDER = 'constitution'
COMMITTER = ('Lexifina', 'madagascar-law@lexifina.com')
PUBLISHER = 'CNLEGIS (Primature)'
SEARCH_CONST = ('mots', 'Constitution de la', '0,300')   # holds records 34738, 39326, 51445
SEARCH_2009 = ('num', '2009-001', '0,50')                 # holds record 40058

ACTS = [
    {'id': '34738', 'search': SEARCH_CONST, 'tag': 'lc/98-001', 'author': 'Loi constitutionnelle n° 98-001',
     'email': 'lc-98-001@cnlegis.invalid', 'num_txt': '98-001', 'type_txt': 'Loi constitutionnelle',
     'enacted': '1998-04-08', 'jo': ('2495', '1998-04-08'), 'in_force': '1998-04-10', 'kind': 'baseline',
     'start': r'PREAMBULE', 'stop': r'Vu pour être annexé à la loi constitutionnelle n°98-001',
     'basis': ('no in-force clause; Ordonnance n° 62-041 art. 2-3: a law is published by insertion in the Journal '
               'officiel and binds one clear day after that issue reaches each sous-préfecture. JO n° 2495 is dated '
               '1998-04-08, so 1998-04-10 is the earliest day (later where the issue arrived later).'),
     'title': 'Loi constitutionnelle n° 98-001 du 8 avril 1998 portant révision de la Constitution'},
    {'id': '39326', 'search': SEARCH_CONST, 'tag': 'lc/2007-001', 'author': 'Loi constitutionnelle n° 2007-001',
     'email': 'lc-2007-001@cnlegis.invalid', 'num_txt': '2007-001', 'type_txt': 'Loi constitutionnelle',
     'enacted': '2007-04-27', 'jo': ('3104', '2007-05-03'), 'in_force': '2007-04-27', 'kind': 'revision',
     'start': r'PREAMBULE', 'stop': r'Vu pour être annexé à la Loi constitutionnelle n°2007-001',
     'basis': ('art. 3 of the act: in force "immédiatement ... dès qu\'elle aura reçu une publication par émission '
               'radiodiffusée et télévisée ou affichage", independently of the Journal officiel; the day of that '
               'broadcast is not printed, so the promulgation day 2007-04-27 (the earliest possible) is used.'),
     'title': 'Loi constitutionnelle n° 2007-001 du 27 avril 2007 portant révision de la Constitution'},
    {'id': '40058', 'search': SEARCH_2009, 'tag': 'lc/2009-001', 'author': 'Loi constitutionnelle n° 2009-001',
     'email': 'lc-2009-001@cnlegis.invalid', 'num_txt': '2009-001', 'type_txt': 'Loi',
     'enacted': '2009-01-19', 'jo': ('3236', '2009-02-19'), 'in_force': '2009-01-19', 'kind': 'amendment',
     'basis': ('art. 2 of the act: in force "immédiatement ... dès qu\'elle aura reçu une publication par émission '
               'radiodiffusée et télévisée ou affichage"; the day of that broadcast is not printed, so the '
               'promulgation day 2009-01-19 (the earliest possible) is used.'),
     'title': 'Loi constitutionnelle n° 2009-001 du 19 janvier 2009 modifiant les dispositions de l\'article 15 de '
              'la Constitution'},
    {'id': '51445', 'search': SEARCH_CONST, 'tag': 'constitution/2010', 'author': 'Constitution du 11 décembre 2010',
     'email': 'constitution-2010@cnlegis.invalid', 'num_txt': '2010', 'type_txt': 'Constitution',
     'enacted': '2010-12-11', 'jo': ('3350', '2011-01-20'), 'in_force': '2010-12-11', 'kind': 'replacement',
     'start': r'PRÉAMBULE', 'stop': r'Promulguée à Antananarivo, le 11 décembre 2010',
     'basis': 'art. 164: "Elle entrera en vigueur dès sa promulgation"; promulgated 2010-12-11.',
     'title': 'Constitution de la République de Madagascar du 11 décembre 2010 (Constitution de la Quatrième '
              'République)'},
]


# ---- data ------------------------------------------------------------------------------------------------------------
def ymd(d: str) -> str:
    """'27-04-2007' -> '2007-04-27'"""
    dd, mm, yy = d.split('-')
    return f'{yy}-{mm}-{dd}'


def load(offline: bool) -> list:
    out = []
    for a in ACTS:
        rec = S.record(S.search(*a['search'], offline=offline), a['id'])
        got = (rec['num_txt'], re.sub(r'<[^>]+>', '', rec['type_txt']).strip(), ymd(rec['date_txt']), rec['num_jo'],
               ymd(rec['date_jo']))
        want = (a['num_txt'], a['type_txt'], a['enacted'], a['jo'][0], a['jo'][1])
        if got != want:
            raise SystemExit(f'record {a["id"]}: CNLEGIS metadata {got} != expected {want}; review ACTS')
        out.append(dict(a, record=rec, lines=P.lines(rec['html_fichier_fr'])))
    return out


def amendment_2009(lines: list) -> str:
    """The new text of article 15, from LC 2009-001. Stops unless the act is the single replacement it was read as."""
    head = [l for l in lines if l.startswith('Article premier')]
    if head != ["Article premier. Les dispositions de l'article 15 de la Constitution sont modifiées comme suit :"]:
        raise SystemExit(f'LC 2009-001: enacting clause not as read: {head}')
    new = [l for l in lines if l.startswith('Article 15 (nouveau)')]
    if len(new) != 1:
        raise SystemExit('LC 2009-001: no single "Article 15 (nouveau)" line')
    m = P.ART.match(new[0])
    body = m.group(3)
    if not (body.startswith('"') and body.endswith('."')):
        raise SystemExit(f'LC 2009-001: article 15 text is not one quoted paragraph: {body[:60]}')
    return body[1:-1]


def versions(acts: list) -> list:
    """The full text after each act: [{'preamble', 'articles', 'structure'}], in act order."""
    out = []
    for a in acts:
        if a['kind'] == 'amendment':
            prev = json.loads(json.dumps(out[-1]))
            new = amendment_2009(a['lines'])
            hit = [x for x in prev['articles'] if x[0] == '15']
            if len(hit) != 1:
                raise SystemExit('LC 2009-001: article 15 not in the previous version')
            hit[0][2][:] = [new]
            a['changed'] = ['15']
            out.append(prev)
        else:
            out.append(P.constitution(a['lines'], a['start'], a['stop']))
    return out


# ---- rendering -------------------------------------------------------------------------------------------------------
def fname(key: str) -> str:
    """'15' -> 'article-015.md'; '82.1' -> 'article-082.1.md'"""
    n, _, sub = key.partition('.')
    return f'article-{int(n):03d}' + (f'.{sub}' if sub else '') + '.md'


def files_of(v: dict) -> dict:
    d = {'preambule.md': '\n'.join(v['preamble']) + '\n'}
    for key, printed, body in v['articles']:
        d[fname(key)] = f'# Article {printed}\n\n' + '\n'.join(body) + '\n'
    d['structure.md'] = ''.join(f'{h} [article {k}]\n' for h, k in v['structure'])
    return d


# ---- dates -----------------------------------------------------------------------------------------------------------
def stamp(day: str, sec: int = 0) -> str:
    """Noon in Antananarivo. Madagascar keeps UTC+3 all year (no summer time in the record, 1998 onward)."""
    d = dt.date.fromisoformat(day)
    if d.year < 1970:
        return f'1970-01-01T12:00:{sec:02d}+0300'
    return f'{d.isoformat()}T12:00:{sec:02d}+0300'


# ---- git -------------------------------------------------------------------------------------------------------------
def git(repo, *args, env=None, inp=None):
    e = dict(os.environ)
    for k in ('GIT_AUTHOR_NAME', 'GIT_AUTHOR_EMAIL', 'GIT_AUTHOR_DATE', 'GIT_COMMITTER_NAME', 'GIT_COMMITTER_EMAIL',
              'GIT_COMMITTER_DATE'):
        e.pop(k, None)
    e.update(env or {})
    r = subprocess.run(['git', '-c', 'core.autocrlf=false', '-c', 'core.safecrlf=false', '-c', 'commit.gpgsign=false',
                        '-c', 'tag.gpgsign=false', *args], cwd=repo, env=e, input=inp, capture_output=True, text=True,
                       encoding='utf-8')
    if r.returncode:
        raise SystemExit(f'git {" ".join(args)}: {r.stderr}')
    return r.stdout


def commit(repo, name, email, day, msg):
    ts = stamp(day)
    env = {'GIT_AUTHOR_NAME': name, 'GIT_AUTHOR_EMAIL': email, 'GIT_AUTHOR_DATE': ts,
           'GIT_COMMITTER_NAME': COMMITTER[0], 'GIT_COMMITTER_EMAIL': COMMITTER[1], 'GIT_COMMITTER_DATE': ts}
    git(repo, 'add', '-A')
    git(repo, 'commit', '-q', '--allow-empty', '-F', '-', env=env, inp=msg)


def rmtree(p):
    def fix(func, path, exc):
        os.chmod(path, stat.S_IWRITE)
        func(path)
    shutil.rmtree(p, onexc=fix)


def prepare(repo: Path):
    """Refuse a non-empty target that is not an earlier build of this repo (or the placeholder clone). Keep origin."""
    origin = ''
    if repo.exists() and any(repo.iterdir()):
        if not (repo / '.git').exists():
            raise SystemExit(f'{repo} is not empty and not a git repository')
        log = subprocess.run(['git', 'log', '--format=%cn|%ce|%s', '-200'], cwd=repo, capture_output=True, text=True,
                             encoding='utf-8').stdout.splitlines()
        ours = all(l.split('|')[1] == COMMITTER[1] or l.endswith('sources, before any law') for l in log if l)
        if not ours:
            raise SystemExit(f'{repo} holds commits that are not from this builder; refusing to overwrite')
        origin = subprocess.run(['git', 'remote', 'get-url', 'origin'], cwd=repo, capture_output=True,
                                text=True).stdout.strip()
        for p in repo.iterdir():
            rmtree(p) if p.is_dir() else p.unlink()
    repo.mkdir(parents=True, exist_ok=True)
    git(repo, 'init', '-q', '-b', 'main')
    if origin:
        git(repo, 'remote', 'add', 'origin', origin)


def sync(repo: Path, files: dict):
    d = repo / FOLDER
    if d.exists():
        rmtree(d)
    d.mkdir(parents=True)
    for name, text in sorted(files.items()):
        (d / name).write_text(text, encoding='utf-8', newline='\n')


def keys_of(v):
    return [a[0] for a in v['articles']]


def message(a: dict, v: dict, prev: dict | None) -> str:
    rec = a['record']
    src = f'Source: https://cnlegis.gov.mg/ (CNLEGIS record {a["id"]}, {a["type_txt"]} {a["num_txt"]})'
    pub = f'Published: JO n° {a["jo"][0]} du {a["jo"][1]}'
    n = len(v['articles'])
    if a['kind'] == 'baseline':
        lines = ['Constitution: texte révisé par la loi constitutionnelle n° 98-001', '', a['title'] + '.', '',
                 'The first version in this record: the whole Constitution of 18 September 1992 as revised by '
                 'loi constitutionnelle n° 95-001 (13 October 1995) and n° 98-001, annexed to LC 98-001 "dans sa '
                 'nouvelle rédaction". Its words are older than 1998 in part, but CNLEGIS gives no machine-readable '
                 'text of the 1992 original (a scanned PDF only) or of LC 95-001, so every line is credited to '
                 'LC 98-001 here. Read blame on this commit as "in force from 1998 at the latest".', '',
                 f'{n} articles (sub-numbered articles such as 82.1 are files of their own).', '',
                 'Kind: baseline', f'Consolidated: {a["enacted"]}']
    elif a['kind'] == 'revision':
        lines = ['Constitution: révision par la loi constitutionnelle n° 2007-001', '', a['title'] + '.', '',
                 'The act annexes the whole revised Constitution, adopted by referendum on 4 April 2007. The annex '
                 f'renumbers the articles ({len(prev["articles"])} to {n}; the sub-numbered articles are gone), so '
                 'from article 57 on a file name holds a different article before and after this commit: compare '
                 'texts, not paths, across this commit. Every line of the annex is credited to LC 2007-001, which '
                 'enacted it.', '', 'Kind: revision', 'Renumbered: yes']
    elif a['kind'] == 'amendment':
        lines = ['Constitution: article 15 (loi constitutionnelle n° 2009-001)', '', a['title'] + '.', '',
                 'Replaces the text of article 15. This version is REPLAYED: the 2007 text with article 15 replaced by '
                 'the words the act quotes; no official consolidation of 2009-2010 exists to compare it with. Every '
                 'other file is byte-identical to the previous commit (checked).', '', 'Kind: amendment',
                 'Affecting: constitution/article-015.md', 'Evidence: replay of LC 2009-001 art. 1 (one article '
                 'replaced by quoted text)']
    else:
        lines = ['Constitution du 11 décembre 2010 (Quatrième République)', '', a['title'] + '.', '',
                 'A new constitution, adopted by referendum on 17 November 2010 and promulgated on 11 December 2010. '
                 'It replaces the whole text: every file is rewritten and a file name now holds an article of the 2010 '
                 'Constitution, unrelated to the article of the same number before.', '',
                 f'{n} articles.', '', 'Kind: replacement']
    lines += [f'Enacted: {a["enacted"]}', pub, f'In-force: {a["in_force"]}', f'In-force-basis: {a["basis"]}', src]
    return '\n'.join(lines) + '\n'


def build(repo: Path, offline: bool, docs_date: str | None, wip: bool = False):
    acts = load(offline)
    vs = versions(acts)
    prepare(repo)
    prev = None
    for a, v in zip(acts, vs):
        sync(repo, files_of(v))
        commit(repo, a['author'], a['email'], a['in_force'], message(a, v, prev))
        git(repo, 'tag', a['tag'])
        prev = v
    (repo / '.gitattributes').write_text('* text eol=lf\n', encoding='utf-8', newline='\n')
    day = docs_date or S.retrieved()
    import reproduce
    reproduce.write_docs(repo, acts, vs, day, HERE, wip)
    git(repo, 'add', '-A')
    env = {'GIT_AUTHOR_NAME': COMMITTER[0], 'GIT_AUTHOR_EMAIL': COMMITTER[1], 'GIT_AUTHOR_DATE': stamp(day),
           'GIT_COMMITTER_NAME': COMMITTER[0], 'GIT_COMMITTER_EMAIL': COMMITTER[1], 'GIT_COMMITTER_DATE': stamp(day)}
    msg = ('Documentation, tools and REPRODUCE.md\n\nNo law text changes: README, LICENSE, REPRODUCE.md, corpus.json, '
           'acts.csv and the tools.\n\nKind: documentation\nIn-force: ' + day + '\n')
    git(repo, 'commit', '-q', '-F', '-', env=env, inp=msg)
    return git(repo, 'rev-parse', 'HEAD').strip(), acts, vs


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument('--repo', required=True)
    ap.add_argument('--offline', action='store_true')
    ap.add_argument('--docs-date', default=None, help='documentation commit day (default: the cache retrieval day)')
    ap.add_argument('--wip', action='store_true', help='README says "building" (for the wip branch only)')
    ap.add_argument('--verify-rebuild', action='store_true',
                    help='build again in a temporary folder and compare HEAD with --repo (does not touch --repo)')
    args = ap.parse_args()
    sys.stdout.reconfigure(encoding='utf-8')
    if args.verify_rebuild:
        want = git(Path(args.repo), 'rev-parse', 'HEAD').strip()
        with tempfile.TemporaryDirectory() as td:
            got, _, _ = build(Path(td) / 'r', True, args.docs_date)
        print('rebuild', got, 'repo', want, 'IDENTICAL' if got == want else 'DIFFERENT')
        raise SystemExit(0 if got == want else 1)
    head, acts, vs = build(Path(args.repo), args.offline, args.docs_date, args.wip)
    for a, v in zip(acts, vs):
        print(a['tag'], a['in_force'], len(v['articles']), 'articles')
    print('main', head)


if __name__ == '__main__':
    main()
