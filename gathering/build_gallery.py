"""Rebuild the static wall gallery and verbatim goal list from workspace records."""
import html
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]


def build():
    goals = [{'line': n, 'goal': (ROOT / f'line-{n}/GOAL.md').read_text().strip()}
             for n in range(1, 5)]
    (ROOT / 'dist/goals.json').write_text(json.dumps(goals, indent=2) + '\n')
    groups = {f'Line {n}': [] for n in range(1, 5)}
    groups['Gathering'] = []
    for path in sorted((ROOT / 'dist').glob('*/*.json')):
        record = json.loads(path.read_text())
        attrs = {a['trait_type']: a['value'] for a in record['attributes']}
        if attrs['Wall'] not in groups:
            groups[attrs['Wall']] = []
        groups[attrs['Wall']].append((attrs['Number'], record, attrs))
    parts = ['''<!doctype html>
<html lang="en"><head><meta charset="utf-8">
<meta name="viewport" content="width=device-width,initial-scale=1">
<title>Pepeolithic walls</title>
<style>body{max-width:960px;margin:2rem auto;padding:0 1rem;background:#241a12;color:#f3dfbf;font:17px/1.5 Georgia,serif}img{display:block;width:100%;height:auto}figure{margin:1rem 0 2rem}h1,h2{font-weight:normal}a{color:#eed096}figcaption{padding:.5rem 0}section{margin:3rem 0}</style>
</head><body><h1>Pepeolithic</h1>
<p>Four crafts and a gathering hearth. Every recorded wall, newest first within each line.</p>
<main>''']
    escape = html.escape
    for wall, records in groups.items():
        parts.append('<section><h2>' + escape(wall) + '</h2>')
        for goal in goals:
            if wall == f"Line {goal['line']}":
                parts.append('<p>' + escape(goal['goal']) + '</p>')
        for number, record, attrs in sorted(records, key=lambda r: r[0], reverse=True):
            name, url = escape(record['name']), escape(record['image'], quote=True)
            alt = escape(wall + ' — ' + record['name'], quote=True)
            left = escape(attrs['Left behind'])
            parts.append(f'<figure><a href="{url}"><img loading="lazy" src="{url}" alt="{alt}"></a>'
                         f'<figcaption>{number}. {name} · Left behind: {left}</figcaption></figure>')
        parts.append('</section>')
    parts.append('</main></body></html>')
    (ROOT / 'dist/index.html').write_text('\n'.join(parts) + '\n')
    print(f'Built gallery with {sum(map(len, groups.values()))} walls and {len(goals)} goals')


if __name__ == '__main__':
    build()
