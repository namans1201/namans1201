#!/usr/bin/env python3
"""Build the small, self-contained artwork for the Compact and Editorial READMEs."""
from html import escape
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
FONT = '-apple-system, BlinkMacSystemFont, Segoe UI, sans-serif'


def svg(width, height, title, body):
    return f'<svg xmlns="http://www.w3.org/2000/svg" width="{width}" height="{height}" viewBox="0 0 {width} {height}" role="img" aria-label="{escape(title, quote=True)}"><title>{escape(title)}</title>{body}</svg>\n'


def button(label, width, primary=False, dark=False, editorial=False):
    background = ('#a44e26' if editorial else '#176c5b') if primary else ('#161b22' if dark else '#f6f8fa')
    ink = '#ffffff' if primary else ('#e6edf3' if dark else '#24292f')
    border = background if primary else ('#30363d' if dark else '#d1d9e0')
    body = f'<rect x=".5" y=".5" width="{width-1}" height="37" rx="5" fill="{background}" stroke="{border}"/>'
    body += f'<text x="{width/2}" y="24" text-anchor="middle" fill="{ink}" font-family="{FONT}" font-size="12" font-weight="600">{escape(label)}</text>'
    return svg(width, 38, label, body)


def project(name, description, stack, dark, compact=False):
    paper, ink, muted, border, accent = ('#0d1117','#e6edf3','#9aabb8','#30363d','#8bd8bf') if dark else ('#ffffff','#1f2328','#59636e','#d1d9e0','#176c5b')
    if compact:
        import textwrap
        lines = textwrap.wrap(description, width=43)
        body = f'<rect x=".5" y=".5" width="419" height="140" rx="7" fill="{paper}" stroke="{border}"/>'
        body += f'<text x="20" y="31" fill="{accent}" font-family="{FONT}" font-size="18" font-weight="600">{escape(name)} ↗</text>'
        for i, text in enumerate(lines):
            body += f'<text x="20" y="{62+i*21}" fill="{ink}" font-family="{FONT}" font-size="15">{escape(text)}</text>'
        body += f'<text x="20" y="116" fill="{muted}" font-family="{FONT}" font-size="13">{escape(stack)}</text>'
        return svg(420,141,name,body)
    body = f'<rect x=".5" y=".5" width="759" height="113" rx="7" fill="{paper}" stroke="{border}"/>'
    for y, text, color, size, weight in [(30, name+' ↗',accent,17,600),(59,description,ink,15,400),(88,stack,muted,12,400)]:
        body += f'<text x="23" y="{y}" fill="{color}" font-family="{FONT}" font-size="{size}" font-weight="{weight}">{escape(text)}</text>'
    return svg(760,114,name,body)


def main():
    buttons = ROOT/'assets/buttons'
    projects = ROOT/'assets/projects'
    editorial = ROOT/'designs/editorial/assets'
    for folder in (buttons, projects, editorial):
        folder.mkdir(parents=True, exist_ok=True)
    for dark in (False,True):
        theme = 'dark' if dark else 'light'
        for label,width,key in [('LinkedIn',100,'linkedin'),('Email',80,'email')]:
            (buttons/f'{key}-{theme}.svg').write_text(button(label,width,dark=dark))
            (editorial/f'{key}-{theme}.svg').write_text(button(label,width,dark=dark))
        (buttons/f'repositories-{theme}.svg').write_text(button('All projects ↗',116,dark=dark))
        for key,name,description,stack in [
            ('clip-clap','clip-clap','A personal clipboard for snippets, code, and diagrams.','Next.js · Supabase'),
            ('recalllm','RecallLM','Agent memory with episodic recall and knowledge graphs.','Python · Neo4j · Groq'),
            ('scrollfolio','Scrollfolio','A scroll-animated portfolio of projects.','React · TypeScript · GSAP'),
            ('stellar-voyager','Stellar Voyager','A scroll-driven 3D voyage from Earth to Kepler-452b.','Three.js · JavaScript')]:
            (projects/f'{key}-{theme}.svg').write_text(project(name,description,stack,dark))
            (projects/f'{key}-{theme}-compact.svg').write_text(project(name,description,stack,dark,compact=True))
        title_ink = '#e6edf3' if dark else '#1f2328'
        title = f'<text x="0" y="38" fill="{title_ink}" font-family="{FONT}" font-size="32" font-weight="650" letter-spacing="-.8">Hey, I&#39;m Naman.</text>'
        (ROOT/f'assets/intro-title-{theme}.svg').write_text(svg(360,54,"Hey, I'm Naman.",title))
        paper, ink, muted, accent = ('#0d1117','#e6edf3','#a4aeb9','#eda779') if dark else ('#ffffff','#1f2328','#59636e','#a44e26')
        body = f'<rect width="840" height="228" fill="{paper}"/><path d="M2 20v188" stroke="{accent}" stroke-width="4"/>'
        body += f'<g font-family="{FONT}"><text x="28" y="38" fill="{muted}" font-size="13" letter-spacing="2">NAMAN SHRIMAL / @Namans12</text><text x="26" y="106" fill="{ink}" font-size="48" font-weight="650" letter-spacing="-1">Always building.</text><text x="26" y="161" fill="{ink}" font-size="48" font-weight="650" letter-spacing="-1">Always curious.</text><text x="28" y="203" fill="{muted}" font-size="18">Web development · AI agents · Experiments in code</text></g>'
        (editorial/f'header-{theme}.svg').write_text(svg(840,228,'Naman Shrimal. Always building. Always curious.',body))
    (buttons/'main-profile.svg').write_text(button('Main profile ↗',142,primary=True))
    (editorial/'experiments.svg').write_text(button('Experiments ↗',142,primary=True,editorial=True))


if __name__ == '__main__':
    main()
