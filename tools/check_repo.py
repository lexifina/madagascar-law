"""Checks the built repository against the official texts (read from the builder's cache, so it runs offline).

    python -X utf8 check_repo.py --repo DIR [--record]

1. Every law commit (one per tag): the files under constitution/ equal, byte for byte, the files rendered from the
   official text of that version: the act's own text for 1998, 2007 and 2010; for 2009 the 2007 text with article 15
   replaced by the paragraph LC 2009-001 quotes.
2. Independently of the article parser: the letters and digits of each whole-text version, taken straight from the
   official HTML between the preamble and the closing formula, equal the letters and digits of the repository's files
   at that commit, read in reading order (preamble, then each article preceded by the headings structure.md gives it).
3. The 2009 commit changes article-015.md only, and its new text is the act's quoted paragraph verbatim.
4. Each commit's author, In-force trailer and tag are as listed in build.ACTS; the last commit is the documentation.
Blobs are read through `git ls-tree` + `git cat-file --batch`.
"""
import argparse
import json
import re
import subprocess
import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))
import build as B  # noqa: E402
import parse as P  # noqa: E402

ALNUM = re.compile(r'[^0-9A-Za-zÀ-ɏœŒ]+')


def blobs(repo, commit, folder):
    names = [n for n in subprocess.run(['git', 'ls-tree', '-r', '--name-only', commit, folder + '/'], cwd=repo,
                                       capture_output=True, text=True, encoding='utf-8').stdout.split('\n') if n]
    p = subprocess.run(['git', 'cat-file', '--batch'], cwd=repo, input=''.join(f'{commit}:{n}\n' for n in names).encode(),
                       capture_output=True)
    out, buf, i = {}, p.stdout, 0
    for n in names:
        j = buf.index(b'\n', i)
        size = int(buf[i:j].split()[2])
        out[n.split('/', 1)[1]] = buf[j + 1:j + 1 + size].decode('utf-8')
        i = j + 1 + size + 1
    return out


def reading_order(files: dict) -> str:
    heads = {}
    for line in files['structure.md'].splitlines():
        m = re.fullmatch(r'(.*) \[article ([0-9.]+)\]', line)
        heads.setdefault(B.fname(m.group(2)), []).append(m.group(1))
    parts = [files['preambule.md']]
    arts = sorted((n for n in files if n.startswith('article-')),
                  key=lambda n: tuple(int(x) for x in re.findall(r'\d+', n)))
    for n in arts:
        parts += heads.get(n, [])
        text = files[n]
        parts.append(re.sub(r'^# ', '', text, count=1))
    return '\n'.join(parts)


def official_slice(lines, start, stop) -> str:
    i = next(k for k, l in enumerate(lines) if re.fullmatch(start, l))
    j = next(k for k in range(i + 1, len(lines)) if re.match(stop, lines[k]))
    return '\n'.join(lines[i:j])


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument('--repo', required=True)
    ap.add_argument('--record', action='store_true')
    a = ap.parse_args()
    sys.stdout.reconfigure(encoding='utf-8')
    repo = a.repo
    acts = B.load(offline=True)
    vs = B.versions(acts)
    log = subprocess.run(['git', 'log', '--reverse', '--format=%H%x09%an%x09%ae%x09%(trailers:key=In-force,valueonly,'
                          'separator=)', 'main'], cwd=repo, capture_output=True, text=True,
                         encoding='utf-8').stdout.splitlines()
    rows = [l.split('\t') for l in log]
    problems = []
    if len(rows) != len(acts) + 1 or rows[-1][1] != 'Lexifina':
        problems.append(f'{len(rows)} commits; expected {len(acts)} law commits and the documentation commit')
    files_checked = 0
    alnum_checked = []
    prev = None
    for (h, au, em, inf), act, v in zip(rows, acts, vs):
        tag = subprocess.run(['git', 'rev-parse', act['tag'] + '^{commit}'], cwd=repo, capture_output=True,
                             text=True).stdout.strip()
        if tag != h:
            problems.append(f'{act["tag"]} does not point at its commit')
        if (au, em, inf.strip()) != (act['author'], act['email'], act['in_force']):
            problems.append(f'{act["tag"]}: author/In-force {au} {em} {inf}')
        got = blobs(repo, h, B.FOLDER)
        want = B.files_of(v)
        for n in sorted(set(got) | set(want)):
            files_checked += 1
            if got.get(n) != want.get(n):
                problems.append(f'{act["tag"]}: {n} differs from the official text')
        if act['kind'] != 'amendment':
            off = ALNUM.sub('', official_slice(act['lines'], act['start'], act['stop']))
            rep = ALNUM.sub('', reading_order(got))
            if off != rep:
                k = next((i for i, (x, y) in enumerate(zip(off, rep)) if x != y), min(len(off), len(rep)))
                problems.append(f'{act["tag"]}: letters/digits differ at {k}: {off[k - 30:k + 30]!r} vs {rep[k - 30:k + 30]!r}')
            alnum_checked.append(f'{act["tag"]} {len(off)} chars')
        else:
            changed = sorted(n for n in set(got) | set(prev) if got.get(n) != prev.get(n))
            if changed != ['article-015.md']:
                problems.append(f'{act["tag"]}: changed {changed}, expected only article-015.md')
            new = B.amendment_2009(act['lines'])
            if got['article-015.md'] != f'# Article 15\n\n{new}\n':
                problems.append(f'{act["tag"]}: article 15 is not the act\'s quoted text')
        prev = got
    summary = (f'{len(acts)} versions: {files_checked} files compared byte for byte with the official texts, '
               f'{sum(1 for p in problems if "differs" in p)} mismatches; letters-and-digits check of the whole texts '
               f'({"; ".join(alnum_checked)}); 2009 replay changes article 15 only; {len(problems)} problems')
    print(summary)
    for p in problems:
        print('PROBLEM', p)
    if a.record:
        vp = HERE / 'verification.json'
        rec = json.loads(vp.read_text(encoding='utf-8')) if vp.exists() else {}
        rec['check'] = {'summary': summary, 'problems': problems}
        vp.write_text(json.dumps(rec, indent=1, sort_keys=True, ensure_ascii=False) + '\n', encoding='utf-8',
                      newline='\n')
    raise SystemExit(1 if problems else 0)


if __name__ == '__main__':
    main()
