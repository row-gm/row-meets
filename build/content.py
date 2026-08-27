<<<<<<< HEAD
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
    "schedule_title": "Meet &amp; Event Schedule",
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
    "doorway_title": "Find your group's meets",
    "doorway_body": ("Every meet of the season, filtered to your group. Add it to your "
                     "digital calendar while you are there, and it updates itself when a "
                     "date changes."),
    "doorway_button": "Open the {season} schedule",
    "calcard_title": "Never miss a Confirm By date",
    "calcard_body": ("Your group has its own calendar. Add it once and every meet lands in "
                     "your digital calendar, including every <strong>Confirm By</strong> "
                     "date. When a date changes, it changes for you too."),
    "calcard_button": "Get your group&rsquo;s calendar",
    "closing": ("Not sure which meets are right for you? Ask your coach on deck. For entries "
                "and payments, your family can email the club office at "
                "<strong>office@rowswimming.ca</strong>."),

    # The TeamUnify confirmation page. {code} is replaced by the confirm_code
    # column on the Meets or Events sheet. Set this once and every meet and event
    # links straight to its own confirmation screen.
    #
    # NOT YET VERIFIED. The sample URL supplied was the admin view
    # (/controller/cms/admin/index#/calendar-team-events/ev:NNNNN), which a
    # member cannot use. Open one event while signed in as an ordinary member,
    # copy the address, and put the member-facing pattern here.
    "confirm_url": "https://www.rowswimming.ca/controller/cms/index#/team-events/ev:{code}",
    "confirm_link_label": "Confirm",
    # SportsEngine's own walkthrough of committing to a meet or event. Linked
    # from a small ? beside the Confirm By heading rather than written out again
    # here: their article stays current, ours would not.
    "confirm_help_url": ("https://motion-help.sportsengine.com/en/articles/"
                         "8537937-how-to-commit-sign-up-for-a-meet-event"),
    "confirm_help_label": "How to confirm or decline",

    # --- shared ---
    "meets_heading": "Meets",
    "events_heading": "Events",
    "event_legend_heading": "Kinds of event",
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
     "decline each meet. If we do not hear from you by that date, you are not entered. "
     '<a href="https://motion-help.sportsengine.com/en/articles/'
     '8537937-how-to-commit-sign-up-for-a-meet-event" target="_blank">'
     "Step by step instructions</a>."),
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

DEFAULT_PALETTE = {
    "Navy": "#0A2E3F", "Deep Blue": "#26456E", "Teal": "#136B77", "Tide": "#12786C",
    "Plum": "#6E3D6B", "Rose": "#A33A6B", "Slate": "#3F5560", "Grey": "#4B5B60",
    "Olive": "#5C6B2F", "Clay": "#8C5A3C", "Amber": "#8A6420", "Red": "#C23A3A",
}

# Fallback only. The real list lives in the Types sheet.
DEFAULT_TYPES = [
    ("Meet", "Peak", "Navy", DEFAULT_TEXT["tag_peak"]),
    ("Meet", "Performance", "Teal", DEFAULT_TEXT["tag_performance"]),
    ("Meet", "Pathway Skills", "Tide", DEFAULT_TEXT["tag_pathway_skills"]),
    ("Meet", "Team", "Plum", DEFAULT_TEXT["tag_team"]),
    ("Event", "New Parent Meeting", "Deep Blue", ""),
    ("Event", "All Parent Meeting", "Deep Blue", ""),
    ("Event", "Annual General Meeting", "Deep Blue", ""),
    ("Event", "Social Event", "Rose", ""),
    ("Event", "Holiday", "Slate", ""),
    ("Event", "Pool Closure", "Slate", ""),
    ("Event", "Program Break", "Slate", ""),
    ("Event", "Registration", "Red", ""),
    ("Eligibility", "All Welcome", "Grey",
     "Open to everyone in your group. Confirm or decline as usual."),
    ("Eligibility", "Qualifiers Only", "Red", DEFAULT_TEXT["tag_qualifiers_only"]),
    ("Eligibility", "Coach Decision", "Olive",
     "Your coach chooses who is invited to this one. If the meet is on your "
     "swimmer\u2019s list, confirm or decline as usual."),
]


def _contrast(hex_colour):
    """Ratio of white text against this background."""
    h = hex_colour.lstrip("#")
    def chan(v):
        v = int(v, 16) / 255
        return v / 12.92 if v <= 0.03928 else ((v + 0.055) / 1.055) ** 2.4
    lum = 0.2126 * chan(h[0:2]) + 0.7152 * chan(h[2:4]) + 0.0722 * chan(h[4:6])
    return 1.05 / (lum + 0.05)


def load_types(root):
    """Meet and event types, from the Types sheet.

    Returns (meet_types, event_types), each a list of (name, hex, description) in
    sheet order. Colours are named rather than hex so the sheet can use a
    dropdown; the build rejects any colour that cannot carry white text, so a bad
    pick fails here rather than shipping something unreadable.
    """
    palette = dict(DEFAULT_PALETTE)
    path = os.path.join(root, "data", "palette.csv")
    if os.path.exists(path):
        with open(path, encoding="utf-8-sig") as f:
            for row in csv.DictReader(f):
                name = (row.get("colour") or "").strip()
                val = (row.get("hex") or "").strip()
                if name and val.startswith("#") and len(val) == 7:
                    palette[name] = val

    rows = []
    path = os.path.join(root, "data", "types.csv")
    if os.path.exists(path):
        with open(path, encoding="utf-8-sig") as f:
            for row in csv.DictReader(f):
                kind = (row.get("kind") or "").strip().title()
                name = (row.get("name") or "").strip()
                colour = (row.get("colour") or "").strip()
                desc = (row.get("description") or "").strip()
                order = (row.get("sort_order") or "").strip()
                if kind in ("Meet", "Event", "Eligibility") and name:
                    rows.append((kind, name, colour, desc,
                                 int(order) if order.isdigit() else 999))
        rows.sort(key=lambda r: r[4])
        rows = [(k, n, c, d) for k, n, c, d, _ in rows]
    if not rows:
        rows = list(DEFAULT_TYPES)

    out = {"Meet": [], "Event": [], "Eligibility": []}
    for kind, name, colour, desc in rows:
        assert colour in palette, (
            f'Type "{name}" uses colour "{colour}", which is not in the palette. '
            f"Pick one of: {', '.join(sorted(palette))}")
        hexc = palette[colour]
        assert _contrast(hexc) >= 4.5, (
            f'Type "{name}" uses {colour} ({hexc}), which is too light for white '
            f"text at {_contrast(hexc):.2f}:1. It needs 4.5:1 or more.")
        out[kind].append((name, hexc, desc))
    assert out["Meet"], "types.csv has no Meet rows"
    if not out["Eligibility"]:
        # Older Types sheets predate this kind. Fall back so a build never stops
        # because a sheet has not been updated yet.
        out["Eligibility"] = [
            ("All Welcome", palette["Grey"], ""),
            ("Qualifiers Only", palette["Red"], DEFAULT_TEXT["tag_qualifiers_only"]),
        ]
    return out["Meet"], out["Event"], out["Eligibility"]


def load_pool_types(root):
    """Pool types from the Types sheet (kind = Pool), sorted by sort_order.

    Pool types do not carry colours — they are displayed as plain text, not
    coloured tags — so this is a plain name list with no palette check.
    Falls back to the three built-in values if no Pool rows exist yet.
    """
    path = os.path.join(root, "data", "types.csv")
    if os.path.exists(path):
        names = []
        with open(path, encoding="utf-8-sig") as f:
            for row in csv.DictReader(f):
                kind = (row.get("kind") or "").strip().title()
                name = (row.get("name") or "").strip()
                order = (row.get("sort_order") or "").strip()
                if kind == "Pool" and name:
                    names.append((int(order) if order.isdigit() else 999, name))
        if names:
            names.sort()
            return [n for _, n in names]
    return ["25m", "50m", "OW"]


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
=======
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
    "schedule_title": "Meet &amp; Event Schedule",
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
    "doorway_title": "Find your group's meets",
    "doorway_body": ("Every meet of the season, filtered to your group. Add it to your "
                     "digital calendar while you are there, and it updates itself when a "
                     "date changes."),
    "doorway_button": "Open the {season} schedule",
    "calcard_title": "Never miss a Confirm By date",
    "calcard_body": ("Your group has its own calendar. Add it once and every meet lands in "
                     "your digital calendar, including every <strong>Confirm By</strong> "
                     "date. When a date changes, it changes for you too."),
    "calcard_button": "Get your group&rsquo;s calendar",
    "closing": ("Not sure which meets are right for you? Ask your coach on deck. For entries "
                "and payments, your family can email the club office at "
                "<strong>office@rowswimming.ca</strong>."),

    # The TeamUnify confirmation page. {code} is replaced by the confirm_code
    # column on the Meets or Events sheet. Set this once and every meet and event
    # links straight to its own confirmation screen.
    #
    # NOT YET VERIFIED. The sample URL supplied was the admin view
    # (/controller/cms/admin/index#/calendar-team-events/ev:NNNNN), which a
    # member cannot use. Open one event while signed in as an ordinary member,
    # copy the address, and put the member-facing pattern here.
    "confirm_url": "https://www.rowswimming.ca/controller/cms/index#/team-events/ev:{code}",
    "confirm_link_label": "Confirm",
    # SportsEngine's own walkthrough of committing to a meet or event. Linked
    # from a small ? beside the Confirm By heading rather than written out again
    # here: their article stays current, ours would not.
    "confirm_help_url": ("https://motion-help.sportsengine.com/en/articles/"
                         "8537937-how-to-commit-sign-up-for-a-meet-event"),
    "confirm_help_label": "How to confirm or decline",

    # --- shared ---
    "meets_heading": "Meets",
    "events_heading": "Events",
    "event_legend_heading": "Kinds of event",
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
     "decline each meet. If we do not hear from you by that date, you are not entered. "
     '<a href="https://motion-help.sportsengine.com/en/articles/'
     '8537937-how-to-commit-sign-up-for-a-meet-event" target="_blank">'
     "Step by step instructions</a>."),
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

DEFAULT_PALETTE = {
    "Navy": "#0A2E3F", "Deep Blue": "#26456E", "Teal": "#136B77", "Tide": "#12786C",
    "Plum": "#6E3D6B", "Rose": "#A33A6B", "Slate": "#3F5560", "Grey": "#4B5B60",
    "Olive": "#5C6B2F", "Clay": "#8C5A3C", "Amber": "#8A6420", "Red": "#C23A3A",
}

# Fallback only. The real list lives in the Types sheet.
DEFAULT_TYPES = [
    ("Meet", "Peak", "Navy", DEFAULT_TEXT["tag_peak"]),
    ("Meet", "Performance", "Teal", DEFAULT_TEXT["tag_performance"]),
    ("Meet", "Pathway Skills", "Tide", DEFAULT_TEXT["tag_pathway_skills"]),
    ("Meet", "Team", "Plum", DEFAULT_TEXT["tag_team"]),
    ("Event", "New Parent Meeting", "Deep Blue", ""),
    ("Event", "All Parent Meeting", "Deep Blue", ""),
    ("Event", "Annual General Meeting", "Deep Blue", ""),
    ("Event", "Social Event", "Rose", ""),
    ("Event", "Holiday", "Slate", ""),
    ("Event", "Pool Closure", "Slate", ""),
    ("Event", "Program Break", "Slate", ""),
    ("Event", "Registration", "Red", ""),
    ("Eligibility", "All Welcome", "Grey",
     "Open to everyone in your group. Confirm or decline as usual."),
    ("Eligibility", "Qualifiers Only", "Red", DEFAULT_TEXT["tag_qualifiers_only"]),
    ("Eligibility", "Coach Decision", "Olive",
     "Your coach chooses who is invited to this one. If the meet is on your "
     "swimmer\u2019s list, confirm or decline as usual."),
]


def _contrast(hex_colour):
    """Ratio of white text against this background."""
    h = hex_colour.lstrip("#")
    def chan(v):
        v = int(v, 16) / 255
        return v / 12.92 if v <= 0.03928 else ((v + 0.055) / 1.055) ** 2.4
    lum = 0.2126 * chan(h[0:2]) + 0.7152 * chan(h[2:4]) + 0.0722 * chan(h[4:6])
    return 1.05 / (lum + 0.05)


def load_types(root):
    """Meet and event types, from the Types sheet.

    Returns (meet_types, event_types), each a list of (name, hex, description) in
    sheet order. Colours are named rather than hex so the sheet can use a
    dropdown; the build rejects any colour that cannot carry white text, so a bad
    pick fails here rather than shipping something unreadable.
    """
    palette = dict(DEFAULT_PALETTE)
    path = os.path.join(root, "data", "palette.csv")
    if os.path.exists(path):
        with open(path, encoding="utf-8-sig") as f:
            for row in csv.DictReader(f):
                name = (row.get("colour") or "").strip()
                val = (row.get("hex") or "").strip()
                if name and val.startswith("#") and len(val) == 7:
                    palette[name] = val

    rows = []
    path = os.path.join(root, "data", "types.csv")
    if os.path.exists(path):
        with open(path, encoding="utf-8-sig") as f:
            for row in csv.DictReader(f):
                kind = (row.get("kind") or "").strip().title()
                name = (row.get("name") or "").strip()
                colour = (row.get("colour") or "").strip()
                desc = (row.get("description") or "").strip()
                order = (row.get("sort_order") or "").strip()
                if kind in ("Meet", "Event", "Eligibility") and name:
                    rows.append((kind, name, colour, desc,
                                 int(order) if order.isdigit() else 999))
        rows.sort(key=lambda r: r[4])
        rows = [(k, n, c, d) for k, n, c, d, _ in rows]
    if not rows:
        rows = list(DEFAULT_TYPES)

    out = {"Meet": [], "Event": [], "Eligibility": []}
    for kind, name, colour, desc in rows:
        assert colour in palette, (
            f'Type "{name}" uses colour "{colour}", which is not in the palette. '
            f"Pick one of: {', '.join(sorted(palette))}")
        hexc = palette[colour]
        assert _contrast(hexc) >= 4.5, (
            f'Type "{name}" uses {colour} ({hexc}), which is too light for white '
            f"text at {_contrast(hexc):.2f}:1. It needs 4.5:1 or more.")
        out[kind].append((name, hexc, desc))
    assert out["Meet"], "types.csv has no Meet rows"
    if not out["Eligibility"]:
        # Older Types sheets predate this kind. Fall back so a build never stops
        # because a sheet has not been updated yet.
        out["Eligibility"] = [
            ("All Welcome", palette["Grey"], ""),
            ("Qualifiers Only", palette["Red"], DEFAULT_TEXT["tag_qualifiers_only"]),
        ]
    return out["Meet"], out["Event"], out["Eligibility"]


def load_pool_types(root):
    """Pool types from the Types sheet (kind = Pool), sorted by sort_order.

    Pool types do not carry colours — they are displayed as plain text, not
    coloured tags — so this is a plain name list with no palette check.
    Falls back to the three built-in values if no Pool rows exist yet.
    """
    path = os.path.join(root, "data", "types.csv")
    if os.path.exists(path):
        names = []
        with open(path, encoding="utf-8-sig") as f:
            for row in csv.DictReader(f):
                kind = (row.get("kind") or "").strip().title()
                name = (row.get("name") or "").strip()
                order = (row.get("sort_order") or "").strip()
                if kind == "Pool" and name:
                    names.append((int(order) if order.isdigit() else 999, name))
        if names:
            names.sort()
            return [n for _, n in names]
    return ["25m", "50m", "OW"]


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
>>>>>>> 8fca356c335b481240b7f7642eff4d2996205929
