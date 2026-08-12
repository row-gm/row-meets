"""Class-based page helpers for the meet pages.

Markup carries `row-` classes; all styling lives in the stylesheet pasted into
the page's CSS field. That is what lets tables stack into blocks on a phone
instead of scrolling sideways, since `@media` is the one at-rule the CMS allows.

Two rules that come from the sanitizer, not from taste:

  - `data-label` and `colspan` are rejected. A stacked cell is labelled with a
    hidden `<span class="row-lbl">` instead, shown only on narrow screens.
  - Only `style` and `class` are allowed on a `td`.

Colour is the one thing still set inline, on tags only. A tag's colour comes
from the Types sheet and can change without a stylesheet edit, so baking one
class per colour would put that decision back into code.
"""

CSS_EXTRA = """
/* Additions for the meet and event pages. Appended to the shared stylesheet;
   paste the combined file into the page's CSS field. */

.row-faq    { border:1px solid #DAD3C2; border-radius:10px; overflow:hidden;
              background:#FFFFFF; }
.row-faq-i  { padding:16px 20px; border-top:1px solid #DAD3C2; }
.row-faq-i:first-child { border-top:none; }
.row-faq-i:nth-child(even) { background:#FAF8F2; }
.row-faq-q  { font-weight:700; color:#0A2E3F; font-size:15px; margin-bottom:6px; }
.row-faq-a  { font-size:14.5px; color:#152225; line-height:1.65; }

.row-step   { display:flex; gap:14px; align-items:flex-start; margin:0 0 16px; }
.row-step-n { flex:none; width:28px; height:28px; border-radius:50%;
              background:#136B77; color:#FFFFFF; font-weight:700; font-size:13px;
              display:flex; align-items:center; justify-content:center; }
.row-step-t { font-weight:700; text-transform:uppercase; letter-spacing:0.05em;
              color:#0A2E3F; font-size:13px; margin:3px 0 4px; }
.row-step-b { font-size:14.5px; color:#152225; line-height:1.6; }

.row-btn    { display:inline-block; font-weight:700; text-transform:uppercase;
              letter-spacing:0.06em; font-size:14px; background:#0A2E3F;
              color:#FFFFFF; padding:15px 26px; border-radius:8px;
              text-decoration:none; }
.row-btn-alt { background:#3FBFB0; color:#0A2E3F; }

/* Tag colour is set inline because it comes from the Types sheet. Everything
   else about a tag lives here. */
.row-pill   { display:inline-block; font-weight:700; font-size:10.5px;
              letter-spacing:0.05em; text-transform:uppercase; color:#FFFFFF;
              border-radius:4px; padding:3px 7px; white-space:nowrap; }
/* Beats .row-table td:first-child, which would otherwise tint the pill text. */
.row-table td .row-pill,
.row-table td:first-child .row-pill { color:#FFFFFF; }

/* Vertical rhythm. The shared stylesheet gives .row-h2 no top margin, which is
   fine when a build script wraps each section in a div with its own margin. This
   page does not, so the spacing has to live here. Without it a call to action
   sits flush against the heading below it, which is worst on a phone where the
   two are full width and touching. */
.row-h2     { margin:36px 0 10px; }
.row-h2:first-of-type { margin-top:26px; }
.row-cta    { margin:26px 0; }
.row-card   { margin:0 0 6px; }
.row-scroll { margin:0 0 6px; }
.row-faq    { margin:2px 0 6px; }
.row-call   { margin:22px 0 0; }
.row-note   { margin:18px 0 0; }

.row-teal   { border-color:#136B77; }

@media (max-width: 600px) {
  .row-btn  { display:block; text-align:center; padding:15px 18px; }
  .row-step-n { width:24px; height:24px; font-size:12px; }

  /* Everything is full width and touching at this size, so the gaps do more
     work than they do on a desktop. */
  .row-h2   { margin:30px 0 10px; }
  .row-cta  { margin:22px 0; padding:22px 18px; }
  .row-call { margin:20px 0 0; }

  /* Stacked table rows read as one run of text without a little air. */
  .row-table tr { padding:14px 0; }
  .row-table tr + tr { margin-top:2px; }
}
"""

NAVY, TEAL, CYAN, INK_SOFT, FOAM = "#0A2E3F", "#136B77", "#3FBFB0", "#4B5B60", "#FFFFFF"
FLAG, AMBER = "#C23A3A", "#8A6420"


def hero(eyebrow, title, subtitle=""):
    sub = f'<p class="row-sub">{subtitle}</p>' if subtitle else ""
    return (f'<div class="row-hero"><span class="row-eyebrow">{eyebrow}</span>'
            f'<h1 class="row-h1">{title}</h1>{sub}</div>')


def h2(text):
    return f'<h2 class="row-h2">{text}</h2>'


def p(text, cls="row-body"):
    return f'<p class="{cls}">{text}</p>'


def note(text):
    return f'<p class="row-note">{text}</p>'


def card(inner):
    return f'<div class="row-card">{inner}</div>'


def callout(inner, warn=False):
    cls = "row-call row-warn" if warn else "row-call"
    return f'<div class="{cls}">{inner}</div>'


def pill(text, colour, fg=FOAM):
    """Background AND text colour inline, together.

    The two must travel as a pair. `.row-table td:first-child` in the shared
    stylesheet sets navy text, and a pill in that cell was picking it up over its
    own white, giving navy on teal. Setting both inline means a pill stays
    readable even with an empty CSS field, which is the state a page is in
    between the two pastes.
    """
    return (f'<span class="row-pill" style="background:{colour};color:{fg};">'
            f'{text}</span>')


def button(text, url, alt=False):
    cls = "row-btn row-btn-alt" if alt else "row-btn"
    return f'<a class="{cls}" href="{url}" target="_blank">{text}</a>'


def cta(title, body, link_text, url):
    """The big call to action. Uses the shared .row-cta, which is a link with a
    title, a line of body and a button inside it."""
    return (f'<a class="row-cta" href="{url}" target="_blank">'
            f'<b>{title}</b><span>{body}</span><em>{link_text}</em></a>')


def table(headers, rows):
    """Header row sits inside tbody, matching the stylesheet, which hides that
    first row on a phone and stacks the rest. Every cell repeats its column name
    in a hidden span so a stacked row still says what each value is."""
    ths = "".join(f"<th>{h}</th>" for h in headers)
    trs = ""
    for row in rows:
        tds = ""
        for n, cell in enumerate(row):
            lbl = f'<span class="row-lbl">{headers[n]}</span>' if headers[n] else ""
            tds += f"<td>{lbl}{cell}</td>"
        trs += f"<tr>{tds}</tr>"
    return (f'<div class="row-scroll"><table class="row-table">'
            f'<tbody><tr>{ths}</tr>{trs}</tbody></table></div>')


def faq(items):
    inner = "".join(
        f'<div class="row-faq-i"><div class="row-faq-q">{q}</div>'
        f'<div class="row-faq-a">{a}</div></div>' for q, a in items)
    return f'<div class="row-faq">{inner}</div>'


def step(n, title, body):
    return (f'<div class="row-step"><span class="row-step-n">{n}</span>'
            f'<div><div class="row-step-t">{title}</div>'
            f'<div class="row-step-b">{body}</div></div></div>')


def lanes():
    bars = "".join(
        f'<div style="flex:1;background:{c};"></div>'
        for c in ("#D64545", FOAM, TEAL, FOAM, CYAN, FOAM, "#D64545", FOAM))
    return (f'<div style="height:8px;display:flex;border-radius:4px;'
            f'overflow:hidden;margin:24px 0;">{bars}</div>')


def wrap(*sections):
    return '<div class="row-wrap">' + "".join(sections) + '</div>'


def stylesheet(shared_path):
    """The page's CSS field content: the shared file plus these additions."""
    with open(shared_path, encoding="utf-8") as f:
        return f.read().rstrip() + "\n" + CSS_EXTRA
