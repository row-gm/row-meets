"""Build the slim Meet Schedule page (sanitizer-safe, no JS).

The split this page assumes: the CMS holds what does not change, the hosted page
holds what does. Meet dates move; what a Peak meet is, how entries work and who
officiates do not. So the dates live on the hosted schedule and this page carries
everything around them.

Nothing on this page comes from the spreadsheet, which is the point: there is
nothing here that can go out of date. Paste it once and leave it. Only the hosted
schedule changes, and that changes itself.

Output: row_meet_schedule_slim_embed.html
"""

import os

from row_page_helpers import (
    NAVY, TEAL, CYAN, RED, SAND, FOAM, INK, INK_SOFT, LINE, ROW_ALT,
    DISPLAY_FONT, BODY_FONT, MONO_FONT,
    p, faq_item, faq_list, card, callout, data_table, hero,
    lanes_divider, wrap_page,
)

HERE = os.path.dirname(os.path.abspath(__file__))
OUT_DIR = os.environ.get("ROW_MEETS_OUT", "/mnt/user-data/outputs")

MEETS_BASE = "https://row-gm.github.io/row-meets"
SCHEDULE_URL = f"{MEETS_BASE}/schedule/"
CAL_BASE = f"{MEETS_BASE}/calendars"

SEASON = "2026-27"

TIDE, PLUM, FLAG, AMBER = "#12786C", "#6E3D6B", "#C23A3A", "#8A6420"
MEET_CATEGORY = {
    "Peak": (NAVY, FOAM),
    "Performance": (TEAL, FOAM),
    "Pathway Skills": (TIDE, FOAM),
    "Team": (PLUM, FOAM),
}
CATEGORY_MEANING = [
    ("Peak", "The top of your racing calendar. This is the biggest meet of your season."),
    ("Performance", "You prepare for this one, and you race it chasing a personal best."),
    ("Pathway Skills", "You put what you have been working on in training to the test."),
    ("Team", "You race for the team, and you are there for the swimmers beside you."),
]
EXTRA_TAGS = [
    ("Qualifiers Only", FLAG,
     "You need to have already swum a qualifying time to enter this meet. "
     "Your coach will tell you if you have one."),
    # "This page" would be a lie here: the pasted page does not update itself.
    # The schedule and the calendars do, so those are what this names.
    ("Not confirmed", AMBER,
     "These meets have not yet confirmed their dates, or their ability to accept our "
     "entries for our expected group size. The schedule and the calendar links update "
     "automatically as confirmation is received."),
]

# ---------- components ----------

UI_FONT = "Arial, Helvetica, sans-serif"


def h2(text, top="34px"):
    """Local override. The shared helper sets Arial Black, which is hard work at
    heading sizes; bold Arial with wider tracking reads better and still reads as
    a heading."""
    return (f'<h2 style="font-family:{UI_FONT};font-weight:700;text-transform:uppercase;'
            f'letter-spacing:0.06em;color:{NAVY};font-size:17px;margin:{top} 0 12px;">'
            f'{text}</h2>')


def h3(text, top="28px"):
    return (f'<h3 style="font-family:{UI_FONT};font-weight:700;text-transform:uppercase;'
            f'letter-spacing:0.06em;color:{NAVY};font-size:15px;margin:{top} 0 10px;">{text}</h3>')


def pill(text, bg, fg=FOAM):
    return (f'<span style="display:inline-block;font-family:{UI_FONT};font-weight:700;'
            f'font-size:10.5px;letter-spacing:0.05em;text-transform:uppercase;background:{bg};'
            f'color:{fg};border-radius:4px;padding:3px 7px;margin:0 5px 4px 0;'
            f'white-space:nowrap;">{text}</span>')


def category_pill(cat):
    bg, fg = MEET_CATEGORY[cat]
    return pill(cat, bg, fg)


def button_link(text, url, bg=NAVY, fg=FOAM, size="14px", pad="15px 26px"):
    """A link wearing a button's clothes. No script, so nothing to strip."""
    return (f'<a href="{url}" target="_blank" style="display:inline-block;'
            f'font-family:{UI_FONT};font-weight:700;text-transform:uppercase;'
            f'letter-spacing:0.06em;'
            f'font-size:{size};background:{bg};color:{fg};padding:{pad};border-radius:8px;'
            f'text-decoration:none;white-space:nowrap;">{text}</a>')


# ---------- sections ----------

page_hero = hero(
    "ROW Swim Club",
    "Meet Schedule",
    "Where you race this season, what each meet is for, and how to get your group's "
    "dates into your calendar.")

doorway = (
    f'<div style="background:{NAVY};border-radius:12px;padding:26px 28px;'
    f'box-shadow:0 8px 26px rgba(10,46,63,0.22);">'
    f'<div style="font-family:{UI_FONT};font-weight:700;text-transform:uppercase;letter-spacing:0.05em;'
    f'color:{FOAM};font-size:22px;margin:0 0 8px;">See the full schedule</div>'
    f'<div style="font-family:{BODY_FONT};font-size:15px;color:{FOAM};line-height:1.6;'
    f'margin:0 0 18px;max-width:56em;opacity:0.92;">Every meet, with a filter for your group. '
    f'It updates the moment a date changes, so what you see there is always current.</div>'
    + button_link(f"Open the {SEASON} schedule", SCHEDULE_URL, bg=CYAN, fg=NAVY)
    + '</div>'
)

calendar_card = (
    f'<div style="background:{FOAM};border:2px solid {TEAL};border-radius:12px;'
    f'padding:22px 24px;box-shadow:0 6px 20px rgba(10,46,63,0.10);">'
    f'<div style="font-family:{UI_FONT};font-weight:700;text-transform:uppercase;letter-spacing:0.05em;'
    f'color:{NAVY};font-size:20px;margin:0 0 8px;">Never miss a Confirm By date</div>'
    f'<div style="font-family:{BODY_FONT};font-size:15px;color:{INK};line-height:1.6;'
    f'margin:0 0 16px;max-width:56em;">Your group has its own calendar. Add it once and every '
    f'meet lands in your digital calendar, including every '
    f'<strong>Confirm By</strong> date. When a date changes, it changes for you too.</div>'
    + button_link("Get your group&rsquo;s calendar", f"{CAL_BASE}/", size="13px",
                  pad="13px 22px")
    + '</div>'
)

types_section = (
    h2("Reading the tags")
    + p("Not every meet asks the same thing of you. These are the tags you will see beside "
        "each meet name on the schedule.", margin="0 0 12px")
    + data_table(
        ["Tag", "What it means"],
        [[category_pill(name), text] for name, text in CATEGORY_MEANING]
        + [[pill(name, colour), text] for name, colour, text in EXTRA_TAGS])
)

faqs = (
    h2("How meets work")
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
        + faq_item("Why does the pool length matter?",
                   "A 25 metre pool is called short course and a 50 metre pool is called long "
                   "course. There are more turns in a short course race, so times from the two "
                   "are not compared with each other. You keep a best time in each.", 3)
        + faq_item("What are qualifying times?",
                   "Some meets only accept swimmers who have already swum a set time. Your "
                   "coach will tell you if you have one. Every meet marked "
                   "<strong>All Welcome</strong> is open to everyone in your group.", 4)
        + faq_item("Do my parents need to help at meets?",
                   "At the meets ROW hosts, yes. Those meets say "
                   "<strong>At our pool. Officials needed.</strong> on the "
                   "schedule. A meet cannot run without officials and volunteers from our own "
                   "families. The Officiating page explains how to start, and no experience is "
                   "needed.", 5)
        + faq_item("Is the schedule final?",
                   "Meets marked not confirmed can still move. The schedule updates as soon as "
                   "anything changes, so check it before your family books travel.", 6)
    )
)

closing = callout(
    "Not sure which meets are right for you? Ask your coach on deck. For entries and payments, "
    "your family can email the club office at <strong>office@rowswimming.ca</strong>.")

full = wrap_page(
    page_hero,
    lanes_divider(),
    f'<div style="margin:28px 0 0;">{doorway}</div>',
    f'<div style="margin:20px 0 0;">{calendar_card}</div>',
    f'<div style="margin:34px 0 0;">{types_section}</div>',
    f'<div style="margin:34px 0 0;">{faqs}</div>',
    closing,
)

os.makedirs(OUT_DIR, exist_ok=True)
OUT = os.path.join(OUT_DIR, "row_meet_schedule_slim_embed.html")
with open(OUT, "w", encoding="utf-8") as f:
    f.write(full)
print(f"wrote {OUT} {len(full):,} chars")
