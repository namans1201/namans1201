"""Typeset the masthead, ornamental rules and colophon badges for the decoy page.

Everything here exists because GitHub strips CSS: no letterspacing, no rules,
no small caps, no control over type. So the typography is rendered to PNG and
the badges are built as URLs. Run:

    cd assets && python make-art.py

Fonts (both open-licensed) are fetched on first run and gitignored.
"""
import base64
import os
import urllib.request

from PIL import Image, ImageDraw, ImageFont

HERE = os.path.dirname(os.path.abspath(__file__))

# TT2020 Style E over Special Elite: TT2020 is a genuine typewriter revival with
# real ink spread, where Special Elite is distressed to the point of looking like
# a Halloween flyer. Letterpress is precise; grunge is the tell of a fake.
FONTS = {
    "TT2020.ttf":
        "https://cdn.jsdelivr.net/gh/ctrlcctrlv/TT2020@master/dist/TT2020StyleE-Regular.ttf",
    "CourierPrime.ttf":
        "https://github.com/google/fonts/raw/main/ofl/courierprime/CourierPrime-Regular.ttf",
    "CourierPrimeB.ttf":
        "https://github.com/google/fonts/raw/main/ofl/courierprime/CourierPrime-Bold.ttf",
}
for name, url in FONTS.items():
    p = os.path.join(HERE, name)
    if not os.path.exists(p):
        print("fetching", name)
        urllib.request.urlretrieve(url, p)

SS = 2                      # rendered at 2x, displayed at half
W = 800 * SS
INK = (0, 0, 0)
PAPER = (255, 255, 255)


def font(name, size):
    return ImageFont.truetype(os.path.join(HERE, name), size * SS)


def tracked(draw, xy, text, fnt, fill, tracking):
    """Draw text with letterspacing. PIL has no tracking, and neither does
    GitHub markdown, so spacing out caps has to be done a glyph at a time."""
    x, y = xy
    for ch in text:
        draw.text((x, y), ch, font=fnt, fill=fill)
        x += draw.textlength(ch, font=fnt) + tracking * SS
    return x


def tracked_width(draw, text, fnt, tracking):
    w = sum(draw.textlength(c, font=fnt) for c in text)
    return w + tracking * SS * max(len(text) - 1, 0)


def masthead(ink, paper, path):
    """Just the handle and a hairline. Nothing else.

    The eyebrow, Oxford rule and strapline that used to be here are gone by
    request - small and simple beats a full newspaper lockup on a page that now
    carries real sections beneath it.
    """
    title = "namans1201"
    f_title = font("TT2020.ttf", 40)

    # Measure first, then size the canvas to the type. A fixed 1600px plate
    # left the word filling a third of it, so displaying the plate at 420px
    # rendered the name at ~139px - illegible. The plate must hug the word.
    probe = ImageDraw.Draw(Image.new("RGB", (1, 1)))
    tw = tracked_width(probe, title, f_title, 4)
    pad = 26 * SS
    cw = int(tw + pad * 2)
    ch = 96 * SS

    im = Image.new("RGB", (cw, ch), paper)
    d = ImageDraw.Draw(im)
    tracked(d, (pad, 18 * SS), title, f_title, ink, 4)

    # A hairline the width of the word: it underlines the name rather than
    # dividing the sheet.
    d.rectangle([pad, 74 * SS, pad + tw, 74 * SS + 2 * SS], fill=ink)

    im.save(path)
    return im.size


print("masthead-light", masthead(INK, PAPER, os.path.join(HERE, "masthead-light.png")))
print("masthead-dark ", masthead(PAPER, INK, os.path.join(HERE, "masthead-dark.png")))


# ── colophon badges ────────────────────────────────────────────────────────
# shields.io always renders badge text in white, at every background value -
# there is no dark-text option. So the plate is always black: in light mode it
# reads as a letterpress ink slug, and in dark mode the plate disappears into
# the page and leaves clean white caps. Correct in both, and no <picture> needed.
ICONS = {
    "gmail":     "https://cdn.jsdelivr.net/npm/simple-icons@latest/icons/gmail.svg",
    "linkedin":  "https://cdn.jsdelivr.net/npm/simple-icons@latest/icons/linkedin.svg",
    "instagram": "https://cdn.jsdelivr.net/npm/simple-icons@latest/icons/instagram.svg",
    "x":         "https://cdn.jsdelivr.net/npm/simple-icons@latest/icons/x.svg",
    "github":    "https://cdn.jsdelivr.net/npm/simple-icons@latest/icons/github.svg",
    "globe":     "https://cdn.jsdelivr.net/npm/lucide-static/icons/globe.svg",
}


def white_icon_b64(url):
    req = urllib.request.Request(url, headers={"User-Agent": "make-art"})
    svg = urllib.request.urlopen(req, timeout=30).read().decode()
    # simple-icons paths are unfilled; lucide is stroked. Force both to white.
    svg = svg.replace("<svg ", '<svg fill="#ffffff" ', 1)
    svg = svg.replace('stroke="currentColor"', 'stroke="#ffffff"')
    return base64.b64encode(svg.encode()).decode()


LINKS = [
    ("MAIN  PROFILE", "github",    "https://github.com/Namans12"),
    ("EMAIL",         "gmail",     "mailto:namans1201@gmail.com"),
    ("LINKEDIN",      "linkedin",  "https://www.linkedin.com/in/naman-shrimal12/"),
    ("WEBSITE",       "globe",     "https://namanshrimal.indevs.in"),
    ("INSTAGRAM",     "instagram", "https://instagram.com/namans.exe"),
    ("X",             "x",         "https://x.com/Namanshrimal12"),
]

def badge(label, icon, href):
    b64 = white_icon_b64(ICONS[icon])
    src = ("https://img.shields.io/badge/%s-000000?style=for-the-badge"
           "&logo=data:image/svg%%2Bxml;base64,%s" % (label.replace(" ", "%20"), b64))
    return '<a href="%s"><img src="%s" alt="%s" /></a>' % (
        href, src, label.replace("  ", " ").title())


main = badge(*LINKS[0])
rest = "\n".join(badge(*l) for l in LINKS[1:])

RAW = "https://raw.githubusercontent.com/namans1201/namans1201/master/assets"
# The intro clip is referenced from the MAIN repo rather than duplicated here,
# so the two profiles are guaranteed to be showing the identical file - and the
# 5.5 MB is not carried twice.
MAIN_RAW = "https://raw.githubusercontent.com/Namans12/Namans12/master/assets"

MIRROR = "https://github-readme-stats-sigma-five.vercel.app"
SNAKE = "https://raw.githubusercontent.com/namans1201/namans1201/output"

# Monochrome card palettes. Everything stays black and white; only the polarity
# flips between schemes.
LIGHT = "bg_color=FFFFFF&title_color=000000&text_color=222222&icon_color=000000&border_color=000000&border_radius=0"
DARK = "bg_color=000000&title_color=FFFFFF&text_color=DDDDDD&icon_color=FFFFFF&border_color=FFFFFF&border_radius=0"


def tracked_caps(word):
    """Letterspacing with &nbsp;, one between letters and three between words.

    No-break spaces, not thin spaces: U+00A0 exists in every font on every
    platform (no tofu), and being non-breaking it can never wrap mid-word.
    """
    return "&nbsp;&nbsp;&nbsp;".join(
        "&nbsp;".join(w) for w in word.split(" "))


def pic(light_src, dark_src, alt, width):
    return (
        '<picture>\n'
        '  <source media="(prefers-color-scheme: dark)" srcset="%s" />\n'
        '  <img src="%s" width="%s" alt="%s" />\n'
        '</picture>' % (dark_src, light_src, width, alt)
    )


def card(path, alt, width):
    return pic("%s/%s&%s" % (MIRROR, path, LIGHT),
               "%s/%s&%s" % (MIRROR, path, DARK), alt, width)


def section(title):
    return "---\n\n<div align=\"center\">\n\n<sub><b>%s</b></sub>\n" % tracked_caps(title)


REPOS = ["clip-clap", "github-profiler", "notion-like",
         "tradify", "llm", "apple-web"]
pins = "\n".join(
    '<a href="https://github.com/namans1201/%s">%s</a>'
    % (r, card("api/pin/?username=namans1201&repo=" + r, r, "46%%"))
    for r in REPOS)

CERTS = [
    "Databricks%20Certified%20Data%20Engineer%20Associate",
    "Azure%20AI%20Engineer%20Associate",
    "Azure%20AI%20Fundamentals",
]
RECOGNITION = [
    "2nd%20Place%20%C2%B7%20Formidium%20Hackathon",
    "2nd%20Place%20%C2%B7%20Honeywell%20Hackathon",
    "Finalist%20%C2%B7%20Lumen%20Hackathon",
    "Published%20%C2%B7%20Primera%20%26%20Pegasus",
]


def flat(label):
    return ('<img src="https://img.shields.io/badge/%s-000000?style=flat-square" '
            'alt="%s" />' % (label, label.replace("%20", " ").replace("%C2%B7", "-")))


certs = "\n".join(flat(c) + "\n<br/>" for c in CERTS)
recog = "\n".join(flat(r) + "\n<br/>" for r in RECOGNITION)


README = """<!-- ══════════════════════════════════════════════════════════════════ -->
<!--  namans1201 - second account. Main profile: github.com/Namans12    -->
<!--                                                                    -->
<!--  GENERATED FILE. Edit assets/make-art.py and re-run it; hand edits  -->
<!--  here are overwritten. The handle is typeset into a PNG, so         -->
<!--  changing it in markdown alone would leave the masthead stale.      -->
<!--                                                                    -->
<!--  INK      black and white throughout. The intro clip is the one    -->
<!--           colour element, and it is deliberately the same file the -->
<!--           main profile uses.                                       -->
<!--  PLATES   opaque fields, served twice via <picture>. Opaque on     -->
<!--           purpose: prefers-color-scheme reads the OS, not GitHub's -->
<!--           theme menu, so transparent ink can land black-on-black.  -->
<!--  RULES    always leave a blank line before ---, or markdown turns  -->
<!--           the line above into an <h2>.                             -->
<!-- ══════════════════════════════════════════════════════════════════ -->

<div align="center">

<picture>
  <source media="(prefers-color-scheme: dark)" srcset="{raw}/masthead-dark.png" />
  <img src="{raw}/masthead-light.png" width="306" alt="namans1201" />
</picture>

{main}

{rest}

<br/>

<img src="{main_raw}/naman-intro.gif" width="520" alt="At the desk" />

</div>

{s_about}
<br/>

<sub>A second bench. Smaller experiments, half-finished ideas,<br/>
and the occasional thing that turns out to work.</sub>

<br/><br/>

<sub>The considered work lives on the main profile.<br/>
This is where it gets tried first.</sub>

<br/>

</div>

{s_work}
<br/>

{pins}

</div>

{s_creds}
<br/>

{certs}

<br/>

{recog}

</div>

{s_activity}
<br/>

{stats}
{langs}

<br/><br/>

{graph}

<br/>

<picture>
  <source media="(prefers-color-scheme: dark)" srcset="{snake}/snake-dark.svg" />
  <img src="{snake}/snake-light.svg" width="100%" alt="Contribution grid" />
</picture>

</div>
""".format(
    raw=RAW,
    main_raw=MAIN_RAW,
    snake=SNAKE,
    main=main,
    rest=rest,
    pins=pins,
    certs=certs,
    recog=recog,
    s_about=section("ABOUT"),
    s_work=section("FEATURED WORK"),
    s_creds=section("CREDENTIALS"),
    s_activity=section("ACTIVITY"),
    stats=card("api?username=namans1201&show_icons=true&hide_title=true&hide_rank=true",
               "Statistics", "46%"),
    langs=card("api/top-langs/?username=namans1201&layout=compact&langs_count=6&hide_title=true",
               "Languages", "38%"),
    graph=pic(
        "https://github-readme-activity-graph.vercel.app/graph?username=namans1201"
        "&bg_color=FFFFFF&color=000000&line=000000&point=000000&area=false&hide_border=false&custom_title=Contribution%20Activity",
        "https://github-readme-activity-graph.vercel.app/graph?username=namans1201"
        "&bg_color=000000&color=FFFFFF&line=FFFFFF&point=FFFFFF&area=false&hide_border=false&custom_title=Contribution%20Activity",
        "Contribution activity", "92%"),
)

out = os.path.join(os.path.dirname(HERE), "README.md")
open(out, "w", encoding="utf-8").write(README)
print("wrote", out, "(%d badges, %d lines)" % (len(LINKS), README.count("\n") + 1))
