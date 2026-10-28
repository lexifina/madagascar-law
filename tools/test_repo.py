"""Functional smoke test of the built Madagascar repository: the things a reader does with it work. Standard library only.

    python -X utf8 scripts/madagascar-law/test_repo.py --repo ../madagascar-law [--record]
    python -X utf8 tools/test_repo.py                   # from inside the repository

It asserts that:
1. `git blame` on article 15 as amended in 2009 names two acts (LC 98-001 for the heading, LC 2009-001 for the text);
2. tools/mglaw.py gives the text before and after LC 2009-001 and the 2010 Constitution, each equal to the file at that
   day's tag, and refuses a day before the record;
3. `git log --follow` on article 15 lists its acts in the order they took effect;
4. every tag resolves to a commit, and every commit has an ISO `In-force:` trailer;
5. no commit is authored by Lexifina except the documentation commit (the last one), and every law author uses an
   `.invalid` address;
6. every git or tool command in the README's table runs and prints something.
With --record the result is written to verification.json next to this script (for REPRODUCE.md).
"""
import argparse
import json
import re
import shlex
import subprocess
import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
LAW = re.compile(r'^(Loi constitutionnelle n° \d+-\d+|Constitution du 11 décembre 2010)$')
F15 = 'constitution/article-015.md'


def default_repo() -> Path:
    if (HERE.parent / '.git').exists():
        return HERE.parent
    return HERE.parents[2] / 'madagascar-law'


class Smoke:
    def __init__(self, repo: Path):
        self.repo = repo
        self.results = []

    def git(self, *args):
        out = subprocess.run(['git', *args], cwd=self.repo, capture_output=True, text=True, encoding='utf-8')
        if out.returncode:
            raise AssertionError(f'git {" ".join(args)}: {out.stderr.strip()}')
        return out.stdout

    def tool(self, *args, ok=True):
        out = subprocess.run([sys.executable, '-X', 'utf8', 'tools/mglaw.py', *args], cwd=self.repo,
                             capture_output=True, text=True, encoding='utf-8')
        if ok and out.returncode:
            raise AssertionError(f'mglaw {" ".join(args)}: {out.stderr.strip()}')
        return out.stdout if ok else out

    def check(self, name, fn):
        try:
            detail = fn() or ''
            self.results.append((name, True, detail))
            print(f'PASS {name}: {detail}')
        except AssertionError as exc:
            self.results.append((name, False, str(exc)))
            print(f'FAIL {name}: {exc}')

    def blame(self):
        out = self.git('blame', '--line-porcelain', 'lc/2009-001', '--', F15)
        authors = {l[7:] for l in out.splitlines() if l.startswith('author ')}
        assert all(LAW.match(a) for a in authors), f'unexpected authors {authors}'
        assert 'Loi constitutionnelle n° 2009-001' in authors and len(authors) >= 2, f'authors {authors}'
        now = {l[7:] for l in self.git('blame', '--line-porcelain', 'main', '--', F15).splitlines()
               if l.startswith('author ')}
        assert 'Constitution du 11 décembre 2010' in now and all(LAW.match(x) for x in now), f'main: {now}'
        return (f'{F15} at lc/2009-001 by {", ".join(sorted(authors))}; on main by {", ".join(sorted(now))} '
                f'(the unchanged heading line keeps its first author)')

    def on_date(self):
        done = []
        for tag, before, after in [('lc/2009-001', '2009-01-18', '2009-01-19'),
                                   ('constitution/2010', '2010-12-10', '2010-12-11'),
                                   ('lc/2007-001', '2007-04-26', '2007-04-27')]:
            a, b = self.tool(before, 'constitution', '15'), self.tool(after, 'constitution', '15')
            assert a and b and a != b, f'no change between {before} and {after}'
            assert b == self.git('show', f'{tag}:{F15}'), f'{after} is not the file at {tag}'
            assert a == self.git('show', f'{tag}~1:{F15}'), f'{before} is not the file before {tag}'
            done.append(f'{before} != {after}')
        whole = self.tool('2000-01-01', 'constitution')
        assert whole.startswith('PREAMBULE') and '# Article 152' in whole, 'whole text on 2000-01-01'
        early = self.tool('1998-04-09', 'constitution', ok=False)
        assert early.returncode != 0 and 'not in the record' in early.stderr, 'a day before the record must fail'
        return 'article 15: ' + '; '.join(done) + '; whole text in reading order; 1998-04-09 refused'

    def follow(self):
        out = self.git('log', '--follow', '--format=%an%x09%(trailers:key=In-force,valueonly,separator=)', 'main', '--',
                       F15)
        rows = [l.split('\t') for l in out.splitlines() if l]
        days = [d.strip() for _, d in rows]
        assert len(rows) >= 3, f'{len(rows)} commits'
        assert days == sorted(days, reverse=True), f'not in date order {days}'
        assert all(LAW.match(a) for a, _ in rows), f'authors {[a for a, _ in rows]}'
        return f'{F15}: ' + ', '.join(f'{a} {d}' for a, d in rows)

    def tags_and_trailers(self):
        tags = self.git('tag').split()
        assert len(tags) == 4, f'tags {tags}'
        for t in tags:
            self.git('rev-parse', '--verify', '-q', f'{t}^{{commit}}')
        rows = self.git('log', '--format=%H%x09%an%x09%(trailers:key=In-force,valueonly,separator=)', 'main').splitlines()
        bad = [r for r in rows if not re.fullmatch(r'\d{4}-\d{2}-\d{2}', r.split('\t')[2].strip())]
        assert not bad, f'missing or malformed In-force {bad[:2]}'
        parsed = subprocess.run(['git', 'log', '--format=%(trailers:only,unfold)%x00', 'main'], cwd=self.repo,
                                capture_output=True, text=True, encoding='utf-8').stdout.split('\x00')
        assert all('In-force:' in p for p in parsed if p.strip()), 'a trailer block does not parse'
        return f'{len(tags)} tags resolve; {len(rows)} commits carry In-force; trailer blocks parse'

    def lexifina(self):
        rows = self.git('log', '--format=%H%x09%an%x09%ae%x09%cn', 'main').splitlines()
        by_lex = [r for r in rows if r.split('\t')[1] == 'Lexifina']
        assert len(by_lex) == 1 and by_lex[0] == rows[0], f'{len(by_lex)} commits by Lexifina'
        assert all(r.split('\t')[3] == 'Lexifina' for r in rows), 'a committer other than Lexifina'
        assert all(r.split('\t')[2].endswith('.invalid') for r in rows[1:]), 'a law author without .invalid'
        return f'only the documentation commit {rows[0][:10]} is by Lexifina; {len(rows) - 1} law commits'

    def readme(self):
        text = (self.repo / 'README.md').read_text(encoding='utf-8')
        table = text[text.index('## The questions'):text.index('PowerShell splits')]
        cmds = [c for c in re.findall(r'`([^`]+)`', table) if c.startswith(('git ', 'python '))]
        assert len(cmds) >= 8, f'only {len(cmds)} commands found'
        for c in cmds:
            args = shlex.split(c)
            if args[0] == 'python':
                args[0:1] = [sys.executable, '-X', 'utf8']
            out = subprocess.run(args, cwd=self.repo, capture_output=True, text=True, encoding='utf-8')
            assert out.returncode == 0, f'{c}: exit {out.returncode} {out.stderr.strip()[:200]}'
            assert out.stdout.strip(), f'{c}: printed nothing'
        return f'{len(cmds)} README commands ran and printed output'


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument('--repo', default=None)
    ap.add_argument('--record', action='store_true')
    args = ap.parse_args()
    sys.stdout.reconfigure(encoding='utf-8')
    s = Smoke(Path(args.repo) if args.repo else default_repo())
    s.check('blame names the acts', s.blame)
    s.check('text before and after each act', s.on_date)
    s.check('log --follow in date order', s.follow)
    s.check('tags resolve, In-force on every commit', s.tags_and_trailers)
    s.check('only the documentation commit is by Lexifina', s.lexifina)
    s.check('README commands run', s.readme)
    ok = all(r[1] for r in s.results)
    print(f'{sum(r[1] for r in s.results)}/{len(s.results)} passed')
    if args.record:
        p = HERE / 'verification.json'
        rec = json.loads(p.read_text(encoding='utf-8')) if p.exists() else {}
        rec['smoke'] = {'passed': sum(r[1] for r in s.results), 'total': len(s.results),
                        'results': [{'test': n, 'ok': o, 'detail': d} for n, o, d in s.results]}
        p.write_text(json.dumps(rec, indent=1, sort_keys=True, ensure_ascii=False) + '\n', encoding='utf-8',
                     newline='\n')
    raise SystemExit(0 if ok else 1)


if __name__ == '__main__':
    main()
