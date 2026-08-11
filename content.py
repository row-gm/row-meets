"""Page copy, loaded from the spreadsheet.

Every sentence a swimmer reads lives in the Text and FAQ sheets, not in a Python
file. Change a word there, publish, and it is live. No script edit, no upload.

The defaults below are the fallback: if data/text.csv is missing or a key has
been deleted, the build uses the default rather than failing or printing a blank.
That means adding a new key here first, then to the sheet, never breaks a build
in between.
"""

import csv
import os

DEFAULT_TEXT = {
    # --- hosted schedule page ---
    "schedule_eyebrow": "ROW Swim Club",
    "schedule_title": "Meet Schedule",
    "schedule_subtitle": ("Our {season} meet schedule &mdash; updated regularly as "
                          "information is confirmed. Choose your group to see just yours."),
    "group_label": "View Your Group",
    "group_all": "All groups",
    "schedule_empty": "No meets listed for this group yet.",
    "groupcard_body": ("Add these meets to your calendar, including every Confirm By date. "
                       "To confirm, log into your ROW member account."),
    "groupcard_button": "Copy calendar link",

    # --- slim CMS page ---
    "slim_subtitle": ("Where you race this season, what each meet is for, and how to get "
                      "your group's dates into your calendar."),
    "doorway_title": "See the full schedule",
    "doorway_body": ("Every meet, with a filter for your group. It updates the moment a date "
                     "changes, so what you see there is always current."),
    "doorway_button": "Open the {season} schedule",
    "calcard_title": "Never miss a Confirm By date",
    "calcard_body": ("Your group has its own calendar. Add it once and every meet lands in "
                     "your digital calendar, including every <strong>Confirm By</strong> "
                     "date. When a date changes, it changes for you too."),
    "calcard_button": "Get your group&rsquo;s calendar",
    "closing": ("Not sure which meets are right for you? Ask your coach on deck. For entries "
                "and payments, your family can email the club office at "
                "<strong>office@rowswimming.ca</strong>."),

    # --- shared ---
    "legend_heading": "Reading the tags",
    "legend_intro": ("Not every meet asks the same thing of you. These are the tags you will "
                     "see beside each meet name on the schedule."),
    "faq_heading": "How meets work",

    # --- tag meanings ---
    "tag_peak": "The top of your racing calendar. This is the biggest meet of your season.",
    "tag_performance": "You prepare for this one, and you race it chasing a personal best.",
    "tag_pathway_skills": "You put what you have been working on in training to the test.",
    "tag_team": ("You race for the team, and you are there for the swimmers beside you."),
    "tag_qualifiers_only": ("You need to have already swum a qualifying time to enter this "
                            "meet. Your coach will tell you if you have one."),
    "tag_not_confirmed": ("These meets have not yet confirmed their dates, or their ability "
                          "to accept our entries for our expected group size. The schedule "
                          "and the calendar links update automatically as confirmation is "
                          "received."),
}

DEFAULT_FAQ = [
    ("Do I have to go to every meet on my group's list?",
     "No. Racing is how you find out what your training is worth, so we hope you race often. "
     "Talk to your coach about which meets matter most for you this season."),
    ("What does <strong>Confirm By</strong> mean?",
     "It is the date we need your answer by. Log into your ROW member account and confirm or "
     "decline each meet. If we do not hear from you by that date, you are not entered."),
    ("What if I cannot make a meet I am entered in?",
     "Decline it in your ROW member account before the Confirm By date, and tell your coach. "
     "After that date the club has usually paid your entry, so it cannot be refunded."),
    ("Why does the pool length matter?",
     "A 25 metre pool is called short course and a 50 metre pool is called long course. There "
     "are more turns in a short course race, so times from the two are not compared with each "
     "other. You keep a best time in each."),
    ("What are qualifying times?",
     "Some meets only accept swimmers who have already swum a set time. Your coach will tell "
     "you if you have one. Every meet marked <strong>All Welcome</strong> is open to everyone "
     "in your group."),
    ("Do my parents need to help at meets?",
     "At the meets ROW hosts, yes. Those meets say <strong>At our pool. Officials needed.</strong> "
     "on the schedule. A meet cannot run without officials and volunteers from our own "
     "families. The Officiating page explains how to start, and no experience is needed."),
    ("Is the schedule final?",
     "Meets marked not confirmed can still move. The schedule updates as soon as anything "
     "changes, so check it before your family books travel."),
]

TAG_KEYS = {
    "Peak": "tag_peak",
    "Performance": "tag_performance",
    "Pathway Skills": "tag_pathway_skills",
    "Team": "tag_team",
    "Qualifiers Only": "tag_qualifiers_only",
    "Not confirmed": "tag_not_confirmed",
}


def load(root, season=""):
    """Return (text, faq). Sheet values win; anything missing falls back."""
    text = dict(DEFAULT_TEXT)
    path = os.path.join(root, "data", "text.csv")
    if os.path.exists(path):
        with open(path, encoding="utf-8-sig") as f:
            for row in csv.DictReader(f):
                key = (row.get("key") or "").strip()
                val = (row.get("value") or "").strip()
                # A blank cell means "use the default", not "show nothing".
                if key and val:
                    text[key] = val

    faq = list(DEFAULT_FAQ)
    path = os.path.join(root, "data", "faq.csv")
    if os.path.exists(path):
        rows = []
        with open(path, encoding="utf-8-sig") as f:
            for row in csv.DictReader(f):
                q = (row.get("question") or "").strip()
                a = (row.get("answer") or "").strip()
                show = (row.get("show") or "Yes").strip().lower()
                if q and a and show in ("yes", "y", "true"):
                    rows.append((q, a))
        if rows:
            faq = rows

    if season:
        text = {k: v.replace("{season}", season) for k, v in text.items()}
    return text, faq
