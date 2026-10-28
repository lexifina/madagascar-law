"""CNLEGIS (cnlegis.gov.mg, Direction du CNLEGIS, Primature) fetch layer for the Madagascar build. Standard library + curl.

CNLEGIS serves each text's official French HTML inside the JSON of its search endpoints. A search is two POSTs in one
session: the search form (sets the query in the session), then the data endpoint (returns `aaData` rows). Each answer
is cached on disk (cache/, self-gitignored) keyed by the query, so `--offline` rebuilds from the cache. At most one
request runs at a time here (the build needs four), with a pause between requests; robots.txt
(https://cnlegis.gov.mg/robots.txt, checked 2026-10-28) disallows only GPTBot.
"""
import datetime as dt
import hashlib
import json
import subprocess
import tempfile
import time
from pathlib import Path

HERE = Path(__file__).resolve().parent
CACHE = HERE / 'cache'
BASE = 'https://cnlegis.gov.mg/'
UA = 'LexifinaLawHistory/1.0 (madagascar-law@lexifina.com)'

# (form endpoint, data endpoint) per search kind
KINDS = {
    'mots': ('page_find_direct_mots/', 'page_data_result_direct_mots/'),
    'num': ('page_num_find_direct/', 'page_num_data_find_direct/'),
}


def _curl(args):
    for attempt in range(4):
        r = subprocess.run(['curl', '-sS', '-f', '--compressed', '-m', '120', '-A', UA, *args], capture_output=True)
        if r.returncode == 0:
            return r.stdout
        time.sleep(3 * (attempt + 1))
    raise SystemExit(f'curl failed: {args[-1]}: {r.stderr.decode(errors="replace")}')


def search(kind: str, query: str, limit: str, offline: bool = False) -> list:
    """aaData rows of one CNLEGIS search, cached."""
    CACHE.mkdir(exist_ok=True)
    (CACHE / '.gitignore').write_text('*\n', encoding='utf-8', newline='\n')
    key = hashlib.sha1(f'{kind}|{query}|{limit}'.encode()).hexdigest()
    f = CACHE / f'{kind}-{key[:16]}.json'
    if not f.exists():
        if offline:
            raise SystemExit(f'--offline: search {kind} {query!r} is not in the cache')
        form, data = KINDS[kind]
        with tempfile.TemporaryDirectory() as td:
            jar = str(Path(td) / 'jar.txt')
            _curl(['-c', jar, '-b', jar, '-o', str(Path(td) / 'form.html'), '--data-urlencode', f'txt_recherche={query}',
                   BASE + form])
            time.sleep(1)
            body = _curl(['-b', jar, '--data-urlencode', f'var_pg_limit={limit}', BASE + data])
        json.loads(body.decode('utf-8'))  # must be JSON
        f.write_bytes(body)
        log = CACHE / 'requests.jsonl'
        with log.open('a', encoding='utf-8', newline='\n') as fh:
            fh.write(json.dumps({'kind': kind, 'query': query, 'limit': limit, 'file': f.name, 'requests': 2,
                                 'sha256': hashlib.sha256(body).hexdigest()}) + '\n')
        stamp = CACHE / 'retrieved.txt'
        if not stamp.exists():
            stamp.write_text(dt.date.today().isoformat() + '\n', encoding='utf-8', newline='\n')
        time.sleep(1)
    return json.loads(f.read_bytes().decode('utf-8'))['aaData']


def retrieved() -> str:
    p = CACHE / 'retrieved.txt'
    if not p.exists():
        raise SystemExit('no cache/retrieved.txt: run once online')
    return p.read_text(encoding='utf-8').strip()


def record(rows: list, rid: str) -> dict:
    hit = [r for r in rows if str(r.get('id')) == rid]
    if len(hit) != 1:
        raise SystemExit(f'CNLEGIS record id {rid}: {len(hit)} rows')
    return hit[0]
