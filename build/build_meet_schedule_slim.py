"""Build the Meet & Event Schedule page fragment for the CMS.

Class-based markup against the shared stylesheet, so the tag legend stacks into
blocks on a phone instead of scrolling sideways. Two pastes per page: this HTML
into the content editor via Source, and the generated CSS into the page's CSS
field.

Nothing on this page comes from the meets or events data. That is deliberate:
there is nothing here that can go out of date, so it is pasted once and left
alone. The schedule itself lives on the hosted page, which updates itself.

Output: row_meet_schedule_slim_embed.html
        row_meet_schedule_slim.css
"""

import os

import content
import row_classes as R

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.environ.get("ROW_MEETS_ROOT", HERE)
OUT_DIR = os.environ.get("ROW_MEETS_OUT", "/mnt/user-data/outputs")
SHARED_CSS = os.path.join(HERE, "row_stylesheet.css")

SEASON = "2026-27"
TEXT, FAQ = content.load(ROOT, season=SEASON)
MEET_TYPES, _EVENT_TYPES = content.load_types(ROOT)

MEETS_BASE = "https://row-gm.github.io/row-meets"
SCHEDULE_URL = f"{MEETS_BASE}/schedule/"

TYPE_COLOUR = {n: h for n, h, _ in MEET_TYPES}
CATEGORY_MEANING = [(n, d or TEXT.get(content.TAG_KEYS.get(n, ""), ""))
                    for n, _, d in MEET_TYPES]
EXTRA_TAGS = [
    ("Qualifiers Only", R.FLAG, TEXT[content.TAG_KEYS["Qualifiers Only"]]),
    # "This page" would be a lie here: the pasted page does not update itself.
    # The schedule and the calendars do, so those are what this names.
    ("Not confirmed", R.AMBER, TEXT[content.TAG_KEYS["Not confirmed"]]),
]

page = R.wrap(
    R.hero("ROW Swim Club", TEXT["schedule_title"], TEXT["slim_subtitle"]),
    R.lanes(),
    R.cta(TEXT["doorway_title"], TEXT["doorway_body"],
          TEXT["doorway_button"], SCHEDULE_URL),
    R.h2(TEXT["legend_heading"]),
    R.p(TEXT["legend_intro"]),
    R.table(["Tag", "What it means"],
            [[R.pill(n, TYPE_COLOUR[n]), t] for n, t in CATEGORY_MEANING]
            + [[R.pill(n, c), t] for n, c, t in EXTRA_TAGS]),
    R.h2(TEXT["faq_heading"]),
    R.faq(FAQ),
    R.callout(TEXT["closing"]),
)

os.makedirs(OUT_DIR, exist_ok=True)
OUT = os.path.join(OUT_DIR, "row_meet_schedule_slim_embed.html")
with open(OUT, "w", encoding="utf-8") as f:
    f.write(page)

CSS_OUT = os.path.join(OUT_DIR, "row_meet_schedule_slim.css")
with open(CSS_OUT, "w", encoding="utf-8") as f:
    f.write(R.stylesheet(SHARED_CSS))

print(f"wrote {OUT} {len(page):,} chars")
print(f"wrote {CSS_OUT}")
