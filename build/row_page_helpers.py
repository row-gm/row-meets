"""
ROW Swim Club — reusable page-building helpers.

Upload this file alongside any new page request so future sessions have the
literal, current helper functions to import/paste from, instead of
re-deriving them from old build scripts. Keep this file in sync whenever a
helper changes — see ROW_Embedded_Page_Build_Guide.md for the full writeup
of conventions, sanitizer rules, and verification steps.

Last synced: color baseline update — eyebrow tags and small circular/pill
badges use FOAM (#FFFFFF) instead of CYAN for text on a NAVY background.
"""

# ================= Colors =================
NAVY = "#0A2E3F"
TEAL = "#136B77"
CYAN = "#3FBFB0"
RED = "#D64545"
SAND = "#F3EFE4"
FOAM = "#FFFFFF"
INK = "#152225"
INK_SOFT = "#4B5B60"
LINE = "#DAD3C2"
ROW_ALT = "#FAF8F2"   # alternating row background (used in lists/FAQs)

# ================= Fonts =================
DISPLAY_FONT = "'Arial Black', Arial, Helvetica, sans-serif"
BODY_FONT = "Arial, Helvetica, sans-serif"
MONO_FONT = "'Courier New', Courier, monospace"
BASE = "https://www.rowswimming.ca"


def p(text, size="16px", color=INK, margin="0 0 16px"):
    return f'<p style="font-family:{BODY_FONT};font-size:{size};color:{color};line-height:1.65;margin:{margin};">{text}</p>'


def h2(text):
    return (f'<h2 style="font-family:{DISPLAY_FONT};text-transform:uppercase;letter-spacing:0.02em;'
            f'color:{NAVY};margin:0 0 8px;font-size:24px;">{text}</h2>')


def faq_item(question, answer_html, i=0):
    bg = "#FAF8F2" if i % 2 == 1 else FOAM
    return (
        f'<div style="padding:18px 22px;background:{bg};border-top:1px solid {LINE};">'
        f'<div style="font-family:{BODY_FONT};font-size:15.5px;font-weight:700;color:{NAVY};margin-bottom:6px;">{question}</div>'
        f'<div style="font-family:{BODY_FONT};font-size:14.5px;color:{INK};line-height:1.65;">{answer_html}</div>'
        f'</div>'
    )


def faq_list(faq_html):
    return (f'<div style="border:1px solid {LINE};border-radius:10px;overflow:hidden;'
            f'box-shadow:0 6px 20px rgba(10,46,63,0.10);background:{FOAM};">{faq_html}</div>')


def card(inner_html, pad="24px 26px"):
    return (f'<div style="background:{FOAM};border:1px solid {LINE};border-radius:12px;'
            f'padding:{pad};">{inner_html}</div>')


def callout(body_html, warn=False):
    border = RED if warn else CYAN
    bg = "#FBEEEE" if warn else "#EFFAF8"
    return (f'<div style="border-left:4px solid {border};background:{bg};'
            f'border-radius:0 10px 10px 0;padding:16px 20px;margin:20px 0 0;font-size:14.5px;'
            f'color:{INK};font-family:{BODY_FONT};line-height:1.6;">{body_html}</div>')


def step_card(number, title, body_html):
    return (
        f'<div style="display:flex;gap:16px;padding:20px 0;border-top:1px solid {LINE};">'
        f'<span style="flex:none;font-family:{MONO_FONT};font-weight:700;font-size:15px;'
        f'width:34px;height:34px;border-radius:50%;background:{TEAL};color:{FOAM};'
        f'display:flex;align-items:center;justify-content:center;">{number}</span>'
        f'<div>'
        f'<h3 style="font-family:{DISPLAY_FONT};text-transform:uppercase;letter-spacing:0.01em;'
        f'color:{NAVY};font-size:16px;margin:0 0 6px;">{title}</h3>'
        f'<div style="font-family:{BODY_FONT};font-size:14.5px;color:{INK};line-height:1.6;">{body_html}</div>'
        f'</div></div>'
    )


def doc_row(label, href, i=0, badge_type="PDF"):
    bg = "#FAF8F2" if i % 2 == 1 else FOAM
    badge_bg = NAVY if badge_type == "LINK" else RED
    badge_fg = CYAN if badge_type == "LINK" else FOAM
    return (
        f'<div style="padding:14px 18px;background:{bg};border-top:1px solid {LINE};">'
        f'<span style="display:inline-block;font-family:{MONO_FONT};font-weight:700;font-size:10px;'
        f'letter-spacing:0.04em;background:{badge_bg};color:{badge_fg};border-radius:4px;padding:2px 7px;'
        f'margin-right:10px;vertical-align:middle;">{badge_type}</span>'
        f'<a href="{href}" target="_blank" style="font-family:{BODY_FONT};font-size:15px;font-weight:700;'
        f'color:{NAVY};text-decoration:none;">{label}</a>'
        f'</div>'
    )


def circular_badge(text, size_px=54, font_size_px=19, bg=NAVY, color=FOAM):
    """Small circular badge (initials, step numbers, etc). Text on NAVY = FOAM per current baseline."""
    return (
        f'<div style="flex:none;width:{size_px}px;height:{size_px}px;border-radius:50%;background:{bg};'
        f'display:flex;align-items:center;justify-content:center;">'
        f'<span style="font-family:{DISPLAY_FONT};font-size:{font_size_px}px;color:{color};">{text}</span></div>'
    )


def eyebrow(text):
    """Small-caps label at the top of every hero. Text on NAVY = FOAM per current baseline."""
    return (f'<span style="font-family:{MONO_FONT};font-size:13px;font-weight:700;letter-spacing:0.14em;'
            f'text-transform:uppercase;color:{FOAM};margin-bottom:14px;display:block;">{text}</span>')


def hero(eyebrow_text, title, subtitle=""):
    subtitle_html = ""
    if subtitle:
        subtitle_html = (f'<p style="max-width:660px;margin:16px 0 0;font-size:16px;color:#CBDDE1;'
                          f'line-height:1.6;font-family:{BODY_FONT};">{subtitle}</p>')
    return f'''<div style="background:radial-gradient(1100px 500px at 15% -10%, #114C5E 0%, {NAVY} 55%, #062029 100%);
color:{FOAM};padding:44px 32px;border-radius:14px;">
{eyebrow(eyebrow_text)}
<h1 style="font-family:{DISPLAY_FONT};text-transform:uppercase;letter-spacing:0.01em;color:{FOAM};
font-size:34px;line-height:1.1;font-weight:800;margin:0;">{title}</h1>
{subtitle_html}
</div>'''


def lanes_divider():
    lanes_colors = [RED, FOAM, TEAL, FOAM, CYAN, FOAM, RED, FOAM]
    lanes = "".join(f'<div style="flex:1;background:{c};"></div>' for c in lanes_colors)
    return f'<div style="height:8px;display:flex;border-radius:4px;overflow:hidden;margin:24px 0;">{lanes}</div>'


# ============ Coaching framework layer-page components ============
# Recovered August 2026. The decisions record says framework_ui.py was merged
# into this file and deleted; the merge dropped these. They were rebuilt from the
# live How We Plan Training markup, so they match what is already published.
# Every mono run carries font-weight:700 per the build guide.


def list_shell(inner_html):
    """Bordered, shadowed container that holds a run of rows."""
    return (f'<div style="border:1px solid {LINE};border-radius:10px;overflow:hidden;'
            f'background:{FOAM};box-shadow:0 6px 20px rgba(10,46,63,0.10);">{inner_html}</div>')


def layer_row(number, page_title, question, body, i=0, current=False):
    """One row of the four-layer map. The heading is the real page title, so it
    matches the site navigation; the question it answers leads the body.
    No links: only the hub carries cross-page links."""
    bg = ROW_ALT if i % 2 == 1 else FOAM
    chip = ""
    if current:
        chip = (f'<span style="flex:none;font-family:{MONO_FONT};font-weight:700;font-size:9.5px;'
                f'letter-spacing:0.05em;text-transform:uppercase;background:{TEAL};color:{FOAM};'
                f'border-radius:4px;padding:3px 7px;margin-top:3px;">On this page</span>')
    return (
        f'<div style="display:flex;gap:16px;padding:14px 20px;background:{bg};'
        f'border-top:1px solid {LINE};align-items:flex-start;">'
        f'<span style="flex:none;font-family:{MONO_FONT};font-weight:700;font-size:12px;'
        f'width:26px;height:26px;border-radius:50%;background:{NAVY};color:{FOAM};'
        f'display:flex;align-items:center;justify-content:center;">{number}</span>'
        f'<div style="flex:1;">'
        f'<div style="font-family:{DISPLAY_FONT};text-transform:uppercase;font-size:12.5px;'
        f'letter-spacing:0.01em;color:{NAVY};margin:2px 0 4px;">{page_title}</div>'
        f'<div style="font-family:{BODY_FONT};font-size:13.5px;color:{INK};line-height:1.5;">'
        f'<strong>{question}.</strong> {body}</div>'
        f'</div>{chip}</div>'
    )


def parent_row(page_title, what_it_does, body, current=False):
    """The parent page sits above the four numbered layers in the map. Not a
    layer, so no number: a PARENT badge instead of a numbered circle."""
    chip = ""
    if current:
        chip = (f'<span style="flex:none;font-family:{MONO_FONT};font-weight:700;font-size:9.5px;'
                f'letter-spacing:0.05em;text-transform:uppercase;background:{TEAL};color:{FOAM};'
                f'border-radius:4px;padding:3px 7px;margin-top:3px;">On this page</span>')
    return (
        f'<div style="display:flex;gap:16px;padding:14px 20px;background:{SAND};'
        f'align-items:flex-start;">'
        f'<span style="flex:none;font-family:{MONO_FONT};font-weight:700;font-size:9px;'
        f'letter-spacing:0.06em;text-transform:uppercase;background:{NAVY};color:{FOAM};'
        f'border-radius:4px;padding:5px 7px;margin-top:2px;">Parent</span>'
        f'<div style="flex:1;">'
        f'<div style="font-family:{DISPLAY_FONT};text-transform:uppercase;font-size:12.5px;'
        f'letter-spacing:0.01em;color:{NAVY};margin:2px 0 4px;">{page_title}</div>'
        f'<div style="font-family:{BODY_FONT};font-size:13.5px;color:{INK};line-height:1.5;">'
        f'<strong>{what_it_does}.</strong> {body}</div>'
        f'</div>{chip}</div>'
    )


def role_badge(role):
    """LOAD / UNLOAD / ENTRY. Coach wording. Family pages use BUILDING / EASING / STARTING."""
    bg = {"LOAD": RED, "UNLOAD": TEAL, "ENTRY": NAVY}[role]
    return (f'<span style="display:inline-block;font-family:{MONO_FONT};font-weight:700;'
            f'font-size:10px;letter-spacing:0.08em;background:{bg};color:{FOAM};'
            f'border-radius:4px;padding:3px 8px;">{role}</span>')


def phase_row(name, tagline, role, length, body, meta, zones=(), i=0):
    """One of the six training phases."""
    bg = ROW_ALT if i % 2 == 1 else FOAM
    zl = zone_line(*zones) if zones else ""
    return (
        f'<div style="display:flex;gap:22px;padding:18px 22px;background:{bg};'
        f'border-top:1px solid {LINE};">'
        f'<div style="flex:none;width:190px;">'
        f'<div style="font-family:{DISPLAY_FONT};text-transform:uppercase;letter-spacing:0.01em;'
        f'color:{NAVY};font-size:15px;line-height:1.2;margin:0 0 5px;">{name}</div>'
        f'<div style="font-family:{BODY_FONT};font-size:13px;font-style:italic;color:{TEAL};'
        f'margin:0 0 8px;">{tagline}</div>'
        f'{role_badge(role)}'
        f'<div style="font-family:{MONO_FONT};font-size:12.5px;font-weight:700;color:{INK_SOFT};'
        f'margin:9px 0 0;">{length}</div>'
        f'</div>'
        f'<div style="flex:1;">'
        f'<div style="font-family:{BODY_FONT};font-size:14px;color:{INK};line-height:1.6;'
        f'margin:0 0 10px;">{body}</div>'
        f'{zl}'
        f'<div style="font-family:{MONO_FONT};font-size:12px;font-weight:700;letter-spacing:0.03em;'
        f'text-transform:uppercase;color:{INK_SOFT};">{meta}</div>'
        f'</div></div>'
    )


def zone_tag(colour):
    """A zone pill: colour, number, short title. Always all three, so the tag
    explains itself and no page needs a zone legend of its own.
    Colours come from ZONES in layers_common.py."""
    from layers_common import ZONE
    num, title, bg, fg, br = ZONE[colour]
    return (f'<span style="display:inline-block;font-family:{MONO_FONT};font-weight:700;'
            f'font-size:10.5px;letter-spacing:0.06em;text-transform:uppercase;'
            f'background:{bg};color:{fg};border:1px solid {br};border-radius:4px;'
            f'padding:3px 8px;margin:0 6px 4px 0;white-space:nowrap;">'
            f'{colour} {num} &nbsp;{title}</span>')


def zone_line(*colours):
    """The zone row inside a phase card."""
    tags = "".join(zone_tag(c) for c in colours)
    return (f'<div style="margin:0 0 8px;">'
            f'<span style="display:inline-block;font-family:{MONO_FONT};font-weight:700;'
            f'font-size:12px;letter-spacing:0.03em;text-transform:uppercase;color:{INK_SOFT};'
            f'margin:0 8px 4px 0;">Zones</span>{tags}</div>')


def numbered_row(number, text, i=0):
    """A numbered rule. Teal circle, unlike the navy circles on the layer map."""
    bg = ROW_ALT if i % 2 == 1 else FOAM
    return (
        f'<div style="display:flex;gap:14px;align-items:flex-start;padding:12px 20px;'
        f'background:{bg};border-top:1px solid {LINE};">'
        f'<span style="flex:none;font-family:{MONO_FONT};font-weight:700;font-size:13px;'
        f'width:26px;height:26px;border-radius:50%;background:{TEAL};color:{FOAM};'
        f'display:flex;align-items:center;justify-content:center;">{number}</span>'
        f'<div style="font-family:{BODY_FONT};font-size:14px;color:{INK};line-height:1.55;'
        f'padding-top:3px;">{text}</div></div>'
    )


def data_table(headers, rows):
    """Prose table for layer pages. First cell of each row is bold navy.
    Mono only in the header, so it carries font-weight:700."""
    ths = "".join(
        f'<th style="padding:10px 14px;text-align:left;font-family:{MONO_FONT};font-weight:700;'
        f'font-size:11px;letter-spacing:0.06em;text-transform:uppercase;color:{FOAM};'
        f'background:{NAVY};">{h}</th>' for h in headers)
    trs = ""
    for i, row in enumerate(rows):
        bg = ROW_ALT if i % 2 == 1 else FOAM
        tds = ""
        for n, cell in enumerate(row):
            weight = f'font-weight:700;color:{NAVY};' if n == 0 else f'color:{INK};'
            tds += (f'<td style="padding:11px 14px;font-family:{BODY_FONT};font-size:13.5px;'
                    f'border-top:1px solid {LINE};background:{bg};line-height:1.45;'
                    f'vertical-align:top;{weight}">{cell}</td>')
        trs += f'<tr>{tds}</tr>'
    return (f'<div style="overflow-x:auto;border:1px solid {LINE};border-radius:10px;">'
            f'<table style="width:100%;border-collapse:collapse;">'
            f'<tbody><tr>{ths}</tr>{trs}</tbody></table></div>')


def lede(text):
    """The muted sentence that sits under an h2 and introduces a table or list."""
    return (f'<p style="font-family:{BODY_FONT};font-size:14px;color:{INK_SOFT};line-height:1.65;'
            f'margin:0 0 14px;">{text}</p>')


def wrap_page(*sections):
    """Assemble a full page from hero/section HTML strings, inside the standard 1000px SAND wrapper."""
    wrap_style = f'max-width:1000px;margin:0 auto;font-family:{BODY_FONT};background:{SAND};padding:24px;'
    return f'<div style="{wrap_style}">' + ''.join(sections) + '</div>'


if __name__ == "__main__":
    # Quick self-test: build a tiny sample page and run the sanitizer checks.
    import re

    sample = wrap_page(
        hero("ROW Swim Club", "Sample Page", "A quick self-test of the helper module."),
        lanes_divider(),
        card(h2("Section") + p("Body copy.")),
    )

    print("Sample page length:", len(sample))
    print("id= occurrences:", len(re.findall(r'\bid=', sample)))
    print("mailto count:", sample.count('mailto:'))
    print("script tag:", '<script' in sample)
    print("style tag present (inline is fine, <style> tag is not):", '<style' in sample)
