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
    """Eyebrow, handle, Oxford rule, strapline - one locked-up composition.

    The newspaper "ears" (NO. 02 / EST. MMXXV / PRIVATE PRESS) that were here
    are gone. They were charming and far too loud for a quiet page, and the
    folio at the foot already carries that idea with one character.
    """
    H = 232 * SS
    im = Image.new("RGB", (W, H), paper)
    d = ImageDraw.Draw(im)
    m = 60 * SS

    d.rectangle([m, 40 * SS, W - m, 40 * SS + 2 * SS], fill=ink)

    eyebrow = "THE SECOND ACCOUNT"
    f_eye = font("CourierPrimeB.ttf", 14)
    w = tracked_width(d, eyebrow, f_eye, 8)
    tracked(d, ((W - w) / 2, 58 * SS), eyebrow, f_eye, ink, 8)

    title = "namans1201"
    f_title = font("TT2020.ttf", 66)
    w = tracked_width(d, title, f_title, 5)
    tracked(d, ((W - w) / 2, 92 * SS), title, f_title, ink, 5)

    # Oxford rule: thick over thin. The standard newspaper lockup under a
    # nameplate, and the only custom rule in the whole design.
    rm = 150 * SS
    d.rectangle([rm, 176 * SS, W - rm, 176 * SS + 5 * SS], fill=ink)
    d.rectangle([rm, 187 * SS, W - rm, 187 * SS + 2 * SS], fill=ink)

    strap = "A FORWARDING ADDRESS"
    f_strap = font("CourierPrime.ttf", 14)
    w = tracked_width(d, strap, f_strap, 9)
    tracked(d, ((W - w) / 2, 202 * SS), strap, f_strap, ink, 9)

    im.save(path)
    return im.size


def ornament(ink, paper, path):
    """A hairline rule broken by three diamonds - a printer's ornament."""
    H = 40 * SS
    im = Image.new("RGB", (W, H), paper)
    d = ImageDraw.Draw(im)
    cy = H // 2
    m = 60 * SS
    gap = 44 * SS
    d.rectangle([m, cy - SS, W // 2 - gap, cy + SS], fill=ink)
    d.rectangle([W // 2 + gap, cy - SS, W - m, cy + SS], fill=ink)

    def diamond(cx, r):
        d.polygon([(cx, cy - r), (cx + r, cy), (cx, cy + r), (cx - r, cy)], fill=ink)

    diamond(W // 2 - 24 * SS, 3 * SS)
    diamond(W // 2, 6 * SS)
    diamond(W // 2 + 24 * SS, 3 * SS)
    im.save(path)
    return im.size


print("masthead-light", masthead(INK, PAPER, os.path.join(HERE, "masthead-light.png")))
print("masthead-dark ", masthead(PAPER, INK, os.path.join(HERE, "masthead-dark.png")))
print("rule-light    ", ornament(INK, PAPER, os.path.join(HERE, "rule-light.png")))
print("rule-dark     ", ornament(PAPER, INK, os.path.join(HERE, "rule-dark.png")))


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


def tracked_caps(word):
    """Letterspacing with &nbsp;, one between letters and three between words.

    No-break spaces, not thin spaces: U+00A0 exists in every font on every
    platform (no tofu), and being non-breaking it can never wrap mid-word.
    """
    return "&nbsp;&nbsp;&nbsp;".join(
        "&nbsp;".join(w) for w in word.split(" "))


README = """<!-- ══════════════════════════════════════════════════════════════════ -->
<!--  VERSO - the quiet sheet. Recto is github.com/Namans12.            -->
<!--                                                                    -->
<!--  INK       #000000 / #ffffff only. No hue, anywhere, ever.         -->
<!--  PLATES    assets/*.png|gif - opaque fields, served twice via      -->
<!--            <picture>. Opaque and not transparent on purpose:       -->
<!--            prefers-color-scheme reads the OS, not GitHub's theme   -->
<!--            menu, so transparent ink can land black-on-black.       -->
<!--  RULES     --- exactly twice. Always a blank line before one, or   -->
<!--            markdown turns the line above into an <h2>.             -->
<!--  ORNAMENT  one dinkus, written &#42; so it is not parsed as <hr>.  -->
<!--  TYPE      set by assets/make-art.py. Re-run it after any edit.    -->
<!--  ABSENT    headings, bullets, tables, stats, projects, employer,   -->
<!--            emoji, colour, and a second ornament.                   -->
<!-- ══════════════════════════════════════════════════════════════════ -->

<div align="center">

<picture>
  <source media="(prefers-color-scheme: dark)" srcset="{raw}/masthead-dark.png" />
  <img src="{raw}/masthead-light.png" width="800" alt="namans1201 - a forwarding address" />
</picture>

</div>

---

<div align="center">

<picture>
  <source media="(prefers-color-scheme: dark)" srcset="{raw}/plate-dark.gif" />
  <img src="{raw}/plate-light.gif" width="380" alt="Halftone plate of the author at a desk" />
</picture>

<br/>

<sub>THE AUTHOR AT THE DESK &#183; UNDATED</sub>

</div>

<div align="center"><sub>&#42;&nbsp;&nbsp;&#42;&nbsp;&nbsp;&#42;</sub></div>

<div align="center">

<sub>{see_also}</sub>

{main}

</div>

<div align="center">

<sub>{correspondence}</sub>

{rest}

</div>

<div align="center">

<details>
<summary><sub>{colophon}</sub></summary>

<br/>

<sub>Set in TT2020 Style E, after a 1960s typewriter.</sub><br/>
<sub>Plate screened to eight tones on a paper-white field.</sub><br/>
<sub>Composed in Markdown; no stylesheet was consulted.</sub><br/>
<sub>Second impression, kept quiet.</sub>

</details>

</div>

---

<div align="center"><sub>&#8212;&nbsp; ii &nbsp;&#8212;</sub></div>
""".format(
    raw=RAW,
    main=main,
    rest=rest,
    see_also=tracked_caps("SEE ALSO"),
    correspondence=tracked_caps("CORRESPONDENCE"),
    colophon=tracked_caps("COLOPHON"),
)

out = os.path.join(os.path.dirname(HERE), "README.md")
open(out, "w", encoding="utf-8").write(README)
print("wrote", out, "(%d badges, %d lines)" % (len(LINKS), README.count("\n") + 1))
