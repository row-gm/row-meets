"""Build the Meet Schedule page fragment (sanitizer-safe, no JS).

Page <h1>: Meet Schedule
Slug:      /page/events/meet-schedule
Output:    row_meet_schedule_embed.html

Reads two CSVs exported from the schedule workbook:
    data/groups.csv  — one row per group
    data/meets.csv   — one row per meet, one column per group code

The per-group "filter" is generated here, at build time. The CMS strips JavaScript,
so nothing on the page can filter itself. Every group's own list is written out
instead, which needs no script and works on a phone.

Rebuild and repaste whenever the workbook changes. Nothing is edited by hand in the
output; the CSVs are the single source of truth.
"""

import csv
import os

import content
from datetime import date

from row_page_helpers import (
    NAVY, TEAL, CYAN, RED, SAND, FOAM, INK, INK_SOFT, LINE, ROW_ALT,
    DISPLAY_FONT, BODY_FONT, MONO_FONT,
    p, h2, faq_item, faq_list, card, callout, data_table, hero, lanes_divider, wrap_page,
)

HERE = os.path.dirname(os.path.abspath(__file__))
# In the row-meets repo the scripts live in build/ and everything else hangs off the
# repo root. ROW_MEETS_ROOT lets the workflow point at the root without editing code.
ROOT = os.environ.get("ROW_MEETS_ROOT", HERE)
OUT_DIR = os.environ.get("ROW_MEETS_OUT", "/mnt/user-data/outputs")
GROUPS_CSV = os.path.join(ROOT, "data", "groups.csv")
MEETS_CSV = os.path.join(ROOT, "data", "meets.csv")

# Sample data falls back in so the layout can be reviewed before the real
# schedule is confirmed. Delete these two lines once data/meets.csv exists.
GROUPS_CSV = GROUPS_CSV if os.path.exists(GROUPS_CSV) else GROUPS_CSV.replace(".csv", "_sample.csv")
MEETS_CSV = MEETS_CSV if os.path.exists(MEETS_CSV) else MEETS_CSV.replace(".csv", "_sample.csv")

# One repo, two folders. Named row-meets rather than row-meet-calendars because
# GitHub Pages serves from the repo name: renaming it later would break every link
# on the site, which is the trap row-swimming-math is already stuck in.
MEETS_BASE = "https://row-gm.github.io/row-meets"
CAL_BASE = f"{MEETS_BASE}/calendars"

SEASON = "2026-27"
MEET_TYPES, _EVENT_TYPES, ELIGIBILITY = content.load_types(ROOT)
ELIGIBLE_NAMES = [n for n, _, _ in ELIGIBILITY]
ELIGIBLE_COLOUR = {n: h for n, h, _ in ELIGIBILITY}
POOL_NAMES = content.load_pool_types(ROOT)
_T, _F = content.load(ROOT, season=SEASON)
TEXT_FALLBACK = {n: _T.get(content.TAG_KEYS.get(n, ""), "") for n, _, _ in MEET_TYPES}

# "group"   — one block per group. What a family looks for, but 14 blocks is heavy.
# "pathway" — one block per pathway, with the groups named. Roughly a third the size.
# Flip this if the CMS editor struggles with the paste.
GROUP_DETAIL = "group"

# What each letter in a group column means.
# A group cell holds one or more of these, comma separated. Blank means the group
# is not racing. "Peak" in a group's cell marks the top of that group's calendar.
# Eligibility is NOT here: a meet either has qualifying standards or it does not,
# so it lives once on the meet, in the eligibility column.



def split_tags(cell):
    return [t.strip() for t in cell.replace(";", ",").split(",") if t.strip()]

# Tag colours. Every tag on this page carries white text, so every background here
# clears 4.5:1 against white. Measured, not eyeballed:
#   NAVY 14.2  TEAL 6.2  TIDE 5.4  PLUM 8.3  FLAG 5.3  INK_SOFT 7.1  AMBER 5.4
# Three colours are new to the ROW palette because the existing ones could not
# carry white text: CYAN measured 2.3:1 and SAND 1.2:1, and brand RED sat at 4.4:1,
# just under the line. TIDE is CYAN darkened, FLAG is RED darkened.
TIDE = "#12786C"    # dark cyan-green
PLUM = "#6E3D6B"    # dark plum
FLAG = "#C23A3A"    # dark red, for the one tag that stops a plan
AMBER = "#8A6420"   # dark bronze, for a date that is not settled

MEET_CATEGORY = {n: (h, FOAM) for n, h, _ in MEET_TYPES}

# A group cell holds one or more meet types, and may also hold an eligibility
# value that overrides the meet-level one for that group. That override is real:
# the same meet is often open to the senior groups and coach-selected for others.
# Qualifying standards are still meet-level, because a standard does not vary by
# group; a selection does.
MEET_TYPE_NAMES = [n for n, _, _ in MEET_TYPES]
GROUP_TAGS = MEET_TYPE_NAMES + ELIGIBLE_NAMES

CATEGORY_MEANING = [(n, d or TEXT_FALLBACK.get(n, "")) for n, _, d in MEET_TYPES]

QUALIFIER_MEANING = ("Qualifiers Only",
                     "You need to have already swum a qualifying time to enter this meet. "
                     "Your coach will tell you if you have one.")

MONTHS = ["January", "February", "March", "April", "May", "June",
          "July", "August", "September", "October", "November", "December"]


# ---------- data ----------

def _shows(g, kind):
    """True if this group should appear for `kind` ("meets" or "events").
    Falls back to the old show_on_page column so an older groups.csv still works."""
    v = g.get("show_" + kind)
    if v is None or not str(v).strip():
        v = g.get("show_on_page", "Yes")
    return str(v).strip().lower() in ("yes", "y", "true")


def load():
    with open(GROUPS_CSV, encoding="utf-8-sig") as f:
        groups = [g for g in csv.DictReader(f) if _shows(g, "meets")]
    groups.sort(key=lambda g: int(g["sort_order"]))

    with open(MEETS_CSV, encoding="utf-8-sig") as f:
        meets = list(csv.DictReader(f))

    codes = [g["group_code"] for g in groups]
    for m in meets:
        missing = [c for c in codes if c not in m]
        assert not missing, f"meets.csv is missing group columns: {missing}"
        m["_start"] = date.fromisoformat(m["start_date"].strip())
        m["_end"] = date.fromisoformat((m["end_date"] or m["start_date"]).strip())
        m["_going"] = {c: split_tags(m[c]) for c in codes if m[c].strip()}
        assert m["_going"], f"{m['meet_name']}: no group is racing this meet"
        # What the meet is, taken from the groups going. One type for most meets,
        # two where a pathway treats it differently.
        m["_types"] = sorted({t for v in m["_going"].values() for t in v
                              if t in MEET_TYPE_NAMES}, key=MEET_TYPE_NAMES.index)
        # What each group actually sees, once its own override is applied.
        m["_elig"] = {}
        for code, tags in m["_going"].items():
            own = [t for t in tags if t in ELIGIBLE_NAMES]
            m["_elig"][code] = own[0] if own else m["eligibility"].strip()
        host = m["hosted_by_row"].strip().lower()
        assert host in ("yes", "no"), f"{m['meet_name']}: hosted_by_row must be Yes or No"
        m["_home"] = host == "yes"
        conf = m["confirmed"].strip().lower()
        assert conf in ("yes", "no"), f"{m['meet_name']}: confirmed must be Yes or No"
        m["_confirmed"] = conf == "yes"
        bad = sorted({t for v in m["_going"].values() for t in v if t not in GROUP_TAGS})
        assert not bad, (f"{m['meet_name']}: group cells take {GROUP_TAGS} "
                         f"(comma separated) or blank. Got {bad}")
        assert m["eligibility"].strip() in ELIGIBLE_NAMES, (
            f"{m['meet_name']}: eligibility \"{m['eligibility'].strip()}\" is not on the "
            f"Types sheet. Valid: {', '.join(ELIGIBLE_NAMES)}")
        assert m["pool"].strip() in POOL_NAMES, \
            f"{m['meet_name']}: pool must be one of: {', '.join(POOL_NAMES)}"
        if m["confirm_by"].strip():
            m["_confirm"] = date.fromisoformat(m["confirm_by"].strip())
            assert m["_confirm"] <= m["_start"], \
                f"{m['meet_name']}: confirm by date is after the meet"
            # A year typo in a season that spans two calendar years passes every
            # other check: the date is real, and it is before the meet. Four of
            # them got through the first time.
            assert (m["_start"] - m["_confirm"]).days <= 180, (
                f"{m['meet_name']}: confirm by is "
                f"{(m['_start'] - m['_confirm']).days} days before the meet. "
                f"Check the year on {m['confirm_by'].strip()}.")
        else:
            m["_confirm"] = None
        assert m["_end"] >= m["_start"], f"{m['meet_name']}: end date is before the start date"

    meets.sort(key=lambda m: m["_start"])
    return groups, meets


def date_label(m):
    s, e = m["_start"], m["_end"]
    if s == e:
        return f"{MONTHS[s.month - 1][:3]} {s.day}"
    if s.month == e.month:
        return f"{MONTHS[s.month - 1][:3]} {s.day}&ndash;{e.day}"
    return f"{MONTHS[s.month - 1][:3]} {s.day} &ndash; {MONTHS[e.month - 1][:3]} {e.day}"


# ---------- components ----------

def h3(text, top="28px"):
    return (f'<h3 style="font-family:{DISPLAY_FONT};text-transform:uppercase;letter-spacing:0.01em;'
            f'color:{NAVY};font-size:18px;margin:{top} 0 10px;">{text}</h3>')


def pill(text, bg, fg=FOAM):
    return (f'<span style="display:inline-block;font-family:{MONO_FONT};font-weight:700;'
            f'font-size:10px;letter-spacing:0.06em;text-transform:uppercase;background:{bg};'
            f'color:{fg};border-radius:4px;padding:3px 7px;margin:0 5px 4px 0;'
            f'white-space:nowrap;">{text}</span>')


def cell_pill(text, bg, fg=FOAM):
    """Pill for use inside sched_table, which sets the font on the table element."""
    return (f'<span style="display:inline-block;background:{bg};color:{fg};font-size:11px;'
            f'font-weight:700;border-radius:4px;padding:3px 7px;white-space:nowrap;">{text}</span>')


def category_pill(cat, compact=False):
    bg, fg = MEET_CATEGORY.get(cat, (INK_SOFT, FOAM))
    return cell_pill(cat, bg, fg) if compact else pill(cat, bg, fg)


def status_note(m, block=False):
    """Only the exceptional case gets a tag. A Confirmed column would print "Yes"
    on nine rows in ten, which is a column of width spent saying nothing."""
    if m["_confirmed"]:
        return ""
    tag = pill("Not confirmed", AMBER)
    if block:
        return f'<span style="display:block;margin-top:6px;">{tag}</span>'
    return tag


def sched_table(headers, rows, widths, framed=True):
    """Schedule table. First column is the date, set in bold mono so it scans."""
    ths = "".join(
        f'<th style="width:{w};padding:11px 12px;background:{NAVY};color:{FOAM};">{hd}</th>'
        for hd, w in zip(headers, widths))
    # Font is set once on the table and inherited by every cell. Repeating it per
    # td cost roughly 60KB across this page, which is too much to paste into the CMS.
    td_l = f'padding:11px 12px;border-top:1px solid {LINE};'
    td0_l = td_l + f'font-family:{MONO_FONT};font-weight:700;color:{NAVY};white-space:nowrap;'
    trs = ""
    for i, row in enumerate(rows):
        bg = ROW_ALT if i % 2 == 1 else FOAM
        tds = f'<td style="{td0_l}">{row[0]}</td>'
        tds += "".join(f'<td style="{td_l}">{cell}</td>' for cell in row[1:])
        trs += f'<tr style="background:{bg};">{tds}</tr>'
    shell = (f'overflow-x:auto;border:1px solid {LINE};border-radius:10px;background:{FOAM};'
             + (f'box-shadow:0 6px 20px rgba(10,46,63,0.10);' if framed else ''))
    return (f'<div style="{shell}">'
            f'<table style="border-collapse:collapse;width:100%;min-width:720px;text-align:left;vertical-align:top;'
            f'font-family:{BODY_FONT};font-size:14px;color:{INK};line-height:1.5;">'
            f'<thead><tr style="font-family:{DISPLAY_FONT};text-transform:uppercase;'
            f'letter-spacing:0.03em;font-size:11.5px;">{ths}</tr></thead>'
            f'<tbody>{trs}</tbody></table></div>')


# ---------- sections ----------

groups, meets = load()
confirmed = [m for m in meets if m["_confirmed"]]

page_hero = hero(
    "ROW Swim Club",
    "Meet Schedule",
    f"Every meet in the {SEASON} season, and which ones your group is racing. "
    "Find your group and you can stop scrolling.")


# --- A. the season at a glance ---

def going_text(m):
    """Group codes as plain text. Priority is not colour coded here: the codes are
    a list of who is racing, and colouring them made the column look like a second
    legend the reader had to learn."""
    if len(m["_going"]) == len(groups):
        return f'<strong style="color:{NAVY};">Whole club</strong>'
    going = [g["group_code"] for g in groups if g["group_code"] in m["_going"]]
    return f'<span style="font-weight:700;color:{NAVY};">' + " &middot; ".join(going) + "</span>"


def meet_url(m):
    """Where a meet name points: whatever is in info_link, or nowhere.

    An earlier version also looked for a PDF named after the meet_id in a
    packages folder in the repo. That was dropped: it needed GitHub, which is
    the one part of this nobody should have to touch, and it meant two ways to
    get a link with one of them invisible from the spreadsheet.
    """
    return m["info_link"].strip()


def linked_name(m, colour=None, size=None):
    """Meet name, linked when there is somewhere to send people. Underlined rather
    than recoloured, so a linked meet and an unlinked one still read as the same
    kind of thing."""
    style = f'color:{colour or NAVY};font-weight:700;'
    if size:
        style += f'font-size:{size};'
    url = meet_url(m)
    if not url:
        return f'<span style="{style}">{m["meet_name"]}</span>'
    return (f'<a href="{url}" target="_blank" style="{style}text-decoration:underline;">'
            f'{m["meet_name"]}</a>')


def confirm_label(m):
    """The date a swimmer has to tell their coach by. Blank reads as a dash rather
    than an empty cell, so a missing date looks deliberate instead of broken."""
    v = m["confirm_by"].strip()
    if not v:
        return "&mdash;"
    d = date.fromisoformat(v)
    return f"{MONTHS[d.month - 1][:3]} {d.day}"


def elig_tag(m, code=None):
    """That group's eligibility, falling back to the meet's own."""
    val = (m["_elig"].get(code) if code else None) or m["eligibility"].strip()
    return cell_pill(val, ELIGIBLE_COLOUR.get(val, INK_SOFT))


def eligibility_tag(m, compact=False):
    """Two values, one vocabulary across the page and the spreadsheet.
    Red only on the one that can stop a family's plan."""
    val = m["eligibility"].strip()
    mk = cell_pill if compact else pill
    return mk(val, ELIGIBLE_COLOUR.get(val, INK_SOFT))


all_rows = []
for m in meets:
    where = f'{m["city"]}<br><span style="color:{INK_SOFT};font-size:13px;">{m["venue"]}</span>'
    name = (linked_name(m, size="15px") + '<br>'
            f'<span style="display:inline-block;margin-top:6px;">'
            + "".join(category_pill(t) for t in m["_types"])
            + f'{pill(m["pool"], INK_SOFT)}{status_note(m)}</span>')
    if m["_home"]:
        name += (f'<div style="color:{INK_SOFT};font-size:13px;margin-top:6px;">'
                 f'ROW hosts this meet. Officials and volunteers needed.</div>')
    if m["notes"].strip():
        name += (f'<div style="color:{INK_SOFT};font-size:13px;margin-top:6px;">'
                 f'{m["notes"].strip()}</div>')
    # The qualifier tag sits with the groups, not the meet name: it is a statement
    # about who may enter, so it belongs in the column that says who is racing.
    who = going_text(m) + f'<div style="margin:8px 0 0;">{eligibility_tag(m)}</div>'
    all_rows.append([date_label(m), name, where, who])

def button_link(text, url, bg=NAVY, fg=FOAM, size="15px", pad="13px 22px"):
    """A link that reads as a button. The CMS strips JavaScript, so this is an
    anchor wearing a button's clothes: no script, nothing to break."""
    return (f'<a href="{url}" target="_blank" style="display:inline-block;'
            f'font-family:{DISPLAY_FONT};text-transform:uppercase;letter-spacing:0.03em;'
            f'font-size:{size};background:{bg};color:{fg};padding:{pad};border-radius:8px;'
            f'text-decoration:none;white-space:nowrap;">{text}</a>')


# A card rather than a callout. This was one line of teal text and people were
# scrolling straight past it.
calendar_callout = (
    f'<div style="background:{FOAM};border:2px solid {TEAL};border-radius:12px;'
    f'padding:22px 24px;box-shadow:0 6px 20px rgba(10,46,63,0.10);">'
    f'<div style="font-family:{DISPLAY_FONT};text-transform:uppercase;letter-spacing:0.01em;'
    f'color:{NAVY};font-size:20px;margin:0 0 8px;">Never miss a Confirm By date</div>'
    f'<div style="font-family:{BODY_FONT};font-size:15px;color:{INK};line-height:1.6;'
    f'margin:0 0 16px;max-width:56em;">Your group has its own calendar. Add it once and '
    f'every meet lands in your digital calendar, including every '
    f'<strong>Confirm By</strong> date. When a date changes, it changes for you too.</div>'
    + button_link("Get your group&rsquo;s calendar", f"{CAL_BASE}/")
    + '</div>'
)


master_section = (
    h2("The season at a glance")
    + p("Every meet of the season in date order. The last column shows which groups are "
        "racing. Dates marked <strong>not confirmed</strong> may still move.")
    + sched_table(["Dates", "Meet", "Where", "Who is racing"], all_rows,
                  ["12%", "36%", "22%", "30%"])
    + h3("Meet types")
    + p("The tag beside each meet name says what that meet is for.", margin="0 0 12px")
    + data_table(
        ["Tag", "What it means"],
        [[category_pill(name), text] for name, text in CATEGORY_MEANING]
        + [[pill(QUALIFIER_MEANING[0], FLAG), QUALIFIER_MEANING[1]]])

)


# --- B. find your group ---

# The per-group blocks repeat once per group, so their markup is kept deliberately
# light. A full table shell per group pushed the page past 160KB, which is too much
# to paste into the CMS editor.
# Confirm By sits beside Meet Date on purpose. The two dates are what a family
# scans for, and splitting them across the table means reading every row twice.
GROUP_COLS = ["Meet Date", "Confirm By", "Meet Name", "Location", "Pool", "Meet Type",
              "Eligibility"]
GROUP_WIDTHS = ["11%", "11%", "26%", "14%", "8%", "16%", "14%"]


def meet_cells(m, tags=None, code=None):
    """One row of a group table. `tags` are that group's own meet types; without
    them the row falls back to the meet's overall category."""
    types = [t for t in (tags or m["_types"]) if t in MEET_TYPE_NAMES] or m["_types"]
    name = linked_name(m)
    if m["_home"]:
        name += (f'<span style="display:block;color:{INK_SOFT};font-size:12.5px;'
                 f'margin-top:4px;">At our pool. Officials needed.</span>')
    name += status_note(m, block=True)
    type_cell = " ".join(category_pill(t, True) for t in types)
    return [date_label(m), confirm_label(m), name, m["city"], m["pool"].strip(),
            type_cell, elig_tag(m, code)]


def block_shell(title, subtitle, body, cal_code=None):
    """A group's block. The calendar link sits in the header rather than only at
    the top of the page: a swimmer reading their own table should not have to
    scroll back up to learn a calendar exists."""
    link = ""
    if cal_code:
        link = ('<span style="margin-left:auto;">'
                + button_link("Add to calendar", f"{CAL_BASE}/#{cal_anchor(cal_code)}",
                              bg=TEAL, size="11px", pad="6px 12px")
                + '</span>')
    return (
        f'<div style="margin:0 0 18px;">'
        f'<div style="display:flex;gap:10px;align-items:baseline;margin:0 0 8px;">'
        f'<span style="font-family:{DISPLAY_FONT};text-transform:uppercase;font-size:14px;'
        f'color:{NAVY};">{title}</span>'
        f'<span style="font-family:{MONO_FONT};font-weight:700;font-size:11px;'
        f'letter-spacing:0.08em;color:{INK_SOFT};">{subtitle}</span>'
        f'{link}</div>{body}</div>')


def cal_anchor(code):
    """Matches the row anchors on the subscribe page."""
    return code.lower().replace(" ", "-")


def group_block(g):
    code = g["group_code"]
    mine = [m for m in meets if code in m["_going"]]
    if not mine:
        body = p("No meets scheduled yet.", size="14px", color=INK_SOFT, margin="0")
    else:
        body = sched_table(GROUP_COLS,
                           [meet_cells(m, m["_going"][code], code) for m in mine],
                           GROUP_WIDTHS, framed=False)
    return block_shell(g["display_name"], code, body, cal_code=code)


def pathway_block(pw):
    """Pathway view. Where groups inside a pathway differ, the meet name says which
    groups are going."""
    codes = [g["group_code"] for g in groups if g["pathway"] == pw]
    rows = []
    for m in meets:
        going = [x for x in codes if x in m["_going"]]
        if not going:
            continue
        cells = meet_cells(m, sorted({t for x in going for t in m["_going"][x]},
                             key=GROUP_TAGS.index))
        if len(going) < len(codes):
            cells[2] += (f'<span style="display:block;color:{INK_SOFT};font-size:13px;'
                         f'margin-top:4px;">{", ".join(going)} only</span>')
        rows.append(cells)
    body = (sched_table(GROUP_COLS, rows, GROUP_WIDTHS, framed=False) if rows
            else p("No meets scheduled yet.", size="14px", color=INK_SOFT, margin="0"))
    return block_shell(f"{pw} pathway", " &middot; ".join(codes), body)


pathways, seen_pw = [], set()
for g in groups:
    if g["pathway"] not in seen_pw:
        seen_pw.add(g["pathway"])
        pathways.append(g["pathway"])

group_section = h2("Meet schedule by pathway" if GROUP_DETAIL == "pathway"
                   else "Meet schedule by group") + p(
    "Find your group, then read down its table. Groups in the same pathway race the same "
    "meets, so they share one. The <strong>Confirm By</strong> date is when your family "
    "needs to tell us whether you are racing."
    if GROUP_DETAIL == "pathway" else
    "Your group's meets, in date order. The <strong>Confirm By</strong> date is when your "
    "family needs to tell us whether you are racing.")

if GROUP_DETAIL == "pathway":
    for pw in pathways:
        group_section += pathway_block(pw)
else:
    for pw in pathways:
        group_section += h3(f"{pw} pathway")
        for g in [g for g in groups if g["pathway"] == pw]:
            group_section += group_block(g)


# --- C. questions ---

faqs = (
    h2("Common questions")
    + faq_list(
        faq_item("Do I have to go to every meet on my group's list?",
                 "No. Racing is how you find out what your training is worth, so we hope you "
                 "race often. Talk to your coach about which meets matter most for you this "
                 "season.", 0)
        + faq_item("What does <strong>Confirm By</strong> mean?",
                   "It is the date we need your answer by. Log into your ROW member account "
                   "and confirm or decline each meet. If we do not hear from you by that "
                   "date, you are not entered.", 1)
        + faq_item("What if I cannot make a meet I am entered in?",
                   "Decline it in your ROW member account before the Confirm By date, and tell "
                   "your coach. After that date the club has usually paid your entry, so it "
                   "cannot be refunded.", 2)
        + faq_item("What does a <strong>Peak</strong> meet mean for me?",
                   "It is the top of your racing calendar, the biggest meet of your season. "
                   "Your training through the year is planned so you are at your best for it. "
                   "Not every group has one, and that is on purpose rather than something "
                   "missing.", 3)
        + faq_item("Why does the pool length matter?",
                   "A 25 metre pool is called short course and a 50 metre pool is called long "
                   "course. There are more turns in a short course race, so times from the two "
                   "are not compared with each other. You keep a best time in each.", 4)
        + faq_item("What are qualifying times?",
                   "Some meets only accept swimmers who have already swum a set time. Your coach "
                   "will tell you if you have one. Every meet marked <strong>All Welcome</strong> "
                   "is open to everyone in your group.", 5)
        + faq_item("Do my parents need to help at meets?",
                   "At the meets ROW hosts, yes. Those rows say <strong>At our pool. Officials "
                   "needed.</strong> A meet cannot run without officials and volunteers from our "
                   "own families. The Officiating page explains how to start, and no experience "
                   "is needed.", 6)
        + faq_item("Is this schedule final?",
                   "Meets marked not confirmed can still move. We update this page as soon as "
                   "anything changes, so check back before your family books travel.", 7)
    )
)

closing = callout(
    "Not sure which meets are right for you? Ask your coach on deck. For entries and payments, "
    "your family can email the club office at <strong>office@rowswimming.ca</strong>.")


full = wrap_page(
    page_hero,
    lanes_divider(),
    f'<div style="margin:28px 0 0;">{calendar_callout}</div>',
    f'<div style="margin:28px 0 0;">{master_section}</div>',
    f'<div style="margin:32px 0 0;">{group_section}</div>',
    f'<div style="margin:32px 0 0;">{faqs}</div>',
    closing,
)

OUT = os.path.join(OUT_DIR, "row_meet_schedule_embed.html")
os.makedirs(OUT_DIR, exist_ok=True)
with open(OUT, "w", encoding="utf-8") as f:
    f.write(full)

# A second output: a small page that holds the fragment and a Copy button, so
# publishing to the CMS needs no Python and no local checkout. Served from GitHub
# Pages, so it may carry script.
esc = (full.replace("&", "&amp;").replace("<", "&lt;").replace(">", "&gt;"))
built = date.today().isoformat()
copy_page = f"""<!DOCTYPE html>
<html lang="en"><head><meta charset="utf-8">
<meta name="viewport" content="width=device-width,initial-scale=1">
<title>ROW Meet Schedule &mdash; page HTML</title>
<style>
body{{font-family:Arial,Helvetica,sans-serif;max-width:900px;margin:0 auto;padding:24px;
color:#152225;line-height:1.6;}}
h1{{color:#0A2E3F;}}
.note{{border-left:4px solid #136B77;background:#EFFAF8;padding:14px 18px;
border-radius:0 8px 8px 0;margin:18px 0;}}
button{{font-family:inherit;font-size:15px;font-weight:700;background:#0A2E3F;color:#fff;
border:0;border-radius:6px;padding:12px 20px;cursor:pointer;}}
button:hover{{background:#136B77;}}
button.done{{background:#12786C;}}
textarea{{width:100%;height:150px;font-family:'Courier New',monospace;font-size:11px;
border:1px solid #DAD3C2;border-radius:8px;padding:10px;color:#4B5B60;}}
code{{font-family:'Courier New',monospace;font-weight:700;}}
</style></head><body>
<h1>Meet Schedule &mdash; page HTML</h1>
<p>Built {built} from the schedule spreadsheet.
{len(meets)} meets, {len(groups)} groups, {len(full):,} characters.</p>
<div class="note"><strong>To publish:</strong> copy below, open
<code>/page/events/meet-schedule</code> in the website editor, click
<strong>Source</strong>, select everything already there, and paste over it. Save.</div>
<p><button type="button" id="copy">Copy page HTML</button></p>
<textarea id="src" readonly>{esc}</textarea>
<script>
var b = document.getElementById('copy'), t = document.getElementById('src');
b.addEventListener('click', function () {{
  function done() {{
    b.textContent = 'Copied';
    b.classList.add('done');
    setTimeout(function () {{ b.textContent = 'Copy page HTML'; b.classList.remove('done'); }}, 1800);
  }}
  if (navigator.clipboard && window.isSecureContext) {{
    navigator.clipboard.writeText(t.value).then(done, fallback);
  }} else {{ fallback(); }}
  function fallback() {{
    t.select();
    try {{ document.execCommand('copy'); done(); }}
    catch (e) {{ alert('Select the text below and copy it manually.'); }}
  }}
}});
</script>
</body></html>"""

PAGE_OUT = os.environ.get("ROW_MEETS_PAGE_OUT", os.path.join(OUT_DIR, "row-meets", "page"))
os.makedirs(PAGE_OUT, exist_ok=True)
with open(os.path.join(PAGE_OUT, "index.html"), "w", encoding="utf-8") as f:
    f.write(copy_page)

print(f"wrote {OUT} {len(full)} chars")
print(f"wrote {os.path.join(PAGE_OUT, 'index.html')}")
print(f"{len(meets)} meets ({len(confirmed)} confirmed), {len(groups)} groups")
