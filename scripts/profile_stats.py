#!/usr/bin/env python3
"""Generate repository-owned contribution cards using GitHub's GraphQL API.

Requires Python 3.9+, gh, and GH_TOKEN (or an existing gh login).
Only aggregate dates/counts are saved; no repository or private activity details.
"""
import argparse
from datetime import date, datetime, timedelta
from html import escape
import json
from pathlib import Path
import subprocess
from zoneinfo import ZoneInfo

ROOT = Path(__file__).resolve().parents[1]


def graphql(query, **variables):
    payload = json.dumps({'query': query, 'variables': variables})
    result = subprocess.run(['gh', 'api', 'graphql', '--input', '-'], input=payload,
                            text=True, capture_output=True, check=True)
    data = json.loads(result.stdout)
    if data.get('errors'):
        raise RuntimeError('GitHub could not return contribution data')
    return data['data']['user']


def fetch_days(username, today):
    user = graphql('query($login:String!){user(login:$login){createdAt}}', login=username)
    created = date.fromisoformat(user['createdAt'][:10])
    days = {}
    query = '''query($login:String!, $from:DateTime!, $to:DateTime!) {
      user(login:$login) { contributionsCollection(from:$from,to:$to) {
        contributionCalendar { weeks { contributionDays { date contributionCount } } }
      } }
    }'''
    for year in range(created.year, today.year + 1):
        start = max(created, date(year, 1, 1))
        end = min(today, date(year, 12, 31))
        user = graphql(query, login=username, **{
            'from': f'{start.isoformat()}T00:00:00Z',
            'to': f'{end.isoformat()}T23:59:59Z',
        })
        weeks = user['contributionsCollection']['contributionCalendar']['weeks']
        for week in weeks:
            for day in week['contributionDays']:
                d = date.fromisoformat(day['date'])
                if start <= d <= end:
                    days[d] = day['contributionCount']
    # Fail rather than replacing a good card with partial or empty history.
    expected = (today - created).days + 1
    if len(days) != expected:
        raise RuntimeError(f'Incomplete calendar: expected {expected} days, got {len(days)}')
    return created, days


def calculate_stats(days, today):
    """Today may be unfinished: keep yesterday's streak alive until today ends."""
    history = sorted(d for d in days if d <= today)
    total = sum(days[d] for d in history)
    longest = run = 0
    longest_start = longest_end = run_start = previous = None
    for d in history:
        if days[d] > 0:
            if previous is None or d != previous + timedelta(days=1):
                run = 0
            if run == 0:
                run_start = d
            run += 1
            if run > longest:
                longest, longest_start, longest_end = run, run_start, d
        else:
            run = 0
        previous = d
    anchor = today if days.get(today, 0) > 0 else today - timedelta(days=1)
    cursor = anchor
    current = 0
    while days.get(cursor, 0) > 0:
        current += 1
        cursor -= timedelta(days=1)
    return {'total': total, 'current': current, 'longest': longest,
            'current_start': (cursor + timedelta(days=1)).isoformat() if current else None,
            'current_end': anchor.isoformat() if current else None,
            'longest_start': longest_start.isoformat() if longest_start else None,
            'longest_end': longest_end.isoformat() if longest_end else None}


def pretty_date(value):
    return date.fromisoformat(value).strftime('%d %b %Y').lstrip('0')


def span(start, end):
    if not start:
        return 'A new day, a new start'
    if start == end:
        return pretty_date(start)
    return f'{pretty_date(start)} – {pretty_date(end)}'


def render_card(stats, username, created, updated, dark=False, compact=False):
    paper, tile, ink, muted, line, accent = (
        ('#0d1117', '#161e25', '#e6edf3', '#9aabb8', '#303d46', '#8bd8bf') if dark else
        ('#ffffff', '#f3f8f6', '#1f2328', '#59696b', '#d1ded8', '#176c5b'))
    width, height = (420, 370) if compact else (840, 205)
    cells = [
        (f"{stats['total']:,}", 'Total contributions', f'Since {pretty_date(created)}'),
        (str(stats['current']), 'Current streak', span(stats['current_start'], stats['current_end'])),
        (str(stats['longest']), 'Longest streak', span(stats['longest_start'], stats['longest_end']))]
    out = [f'<svg xmlns="http://www.w3.org/2000/svg" width="{width}" height="{height}" viewBox="0 0 {width} {height}" role="img" aria-labelledby="title desc">',
           f'<title id="title">{escape(username)} contribution statistics</title>',
           f'<desc id="desc">{stats["total"]} total contributions, {stats["current"]} day current streak, {stats["longest"]} day longest streak. Updated {escape(updated)}.</desc>',
           f'<rect x=".5" y=".5" width="{width-1}" height="{height-1}" rx="10" fill="{paper}" stroke="{line}"/>',
           '<g font-family="-apple-system, BlinkMacSystemFont, Segoe UI, sans-serif">']
    for i, (value, label, detail) in enumerate(cells):
        if compact:
            x, y = 28, 30 + i * 100
            out += [f'<text x="{x}" y="{y+8}" fill="{muted}" font-size="14">{label}</text>',
                    f'<text x="{width-28}" y="{y+30}" text-anchor="end" fill="{accent if i==1 else ink}" font-size="36" font-weight="600">{value}{" d" if i else ""}</text>',
                    f'<text x="{x}" y="{y+37}" fill="{muted}" font-size="12">{escape(detail)}</text>']
            if i < 2:
                out += [f'<path d="M28 {y+67}H392" stroke="{line}"/>']
        else:
            x = 140 + i * 280
            if i == 1:
                out += [f'<rect x="291" y="20" width="258" height="140" rx="8" fill="{tile}"/>']
            out += [f'<text x="{x}" y="57" text-anchor="middle" fill="{muted}" font-size="14">{label}</text>',
                    f'<text x="{x}" y="108" text-anchor="middle" fill="{accent if i==1 else ink}" font-size="40" font-weight="600">{value}<tspan font-size="16">{(" day" if value == "1" else " days") if i else ""}</tspan></text>',
                    f'<text x="{x}" y="139" text-anchor="middle" fill="{muted}" font-size="11">{escape(detail)}</text>']
    out += [f'<text x="{width/2}" y="{height-20}" text-anchor="middle" fill="{muted}" font-size="11">Updated {escape(updated)} · GitHub contribution calendar</text>', '</g></svg>']
    return '\n'.join(out) + '\n'


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--username', default='namans1201')
    parser.add_argument('--output', type=Path, default=ROOT / 'assets/generated')
    args = parser.parse_args()
    today = datetime.now(ZoneInfo('Asia/Kolkata')).date()
    created, days = fetch_days(args.username, today)
    stats = calculate_stats(days, today)
    args.output.mkdir(parents=True, exist_ok=True)
    for dark in (False, True):
        for compact in (False, True):
            name = f'stats-{"dark" if dark else "light"}{"-compact" if compact else ""}.svg'
            (args.output/name).write_text(render_card(stats, args.username, created.isoformat(),
                                                     today.strftime('%d %b %Y'), dark, compact))
    record = {'username': args.username, 'created': created.isoformat(), 'as_of': today.isoformat(),
              'timezone': 'Asia/Kolkata', **stats}
    (args.output/'stats.json').write_text(json.dumps(record, indent=2) + '\n')
    print(json.dumps(record, indent=2))


if __name__ == '__main__':
    main()
