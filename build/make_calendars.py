"""Build one calendar file per group from the meet schedule.

Produces a folder of .ics files, one per group, plus an index page. Host the folder
on GitHub Pages and a swimmer's family subscribes once in their digital calendar;
every later rebuild updates it on its own.

Why .ics and not fourteen Google Calendars:
  - A Google Calendar has to be maintained by hand, fourteen times, every time a date
    moves. This is generated from data/meets.csv, so the schedule and the calendars
    cannot disagree.
  - Google Calendar, Apple Calendar and Outlook all subscribe to an .ics URL. Nobody
    needs a Google account.
  - Subscribing is not the same as importing. An imported file is a one-time copy and
    goes stale. A subscribed URL re-reads the file, so a moved meet moves in their
    calendar too. The index page says this plainly, because it is the step people get
    wrong.

Each group's calendar carries two kinds of entry:
  - the meet itself, as an all-day event across its dates
  - the Confirm By date, as an all-day reminder

Run after build_meet_schedule.py. Reads the same two CSVs.
"""

import csv
import os
from datetime import date, timedelta

HERE = os.path.dirname(os.path.abspath(__file__))
# In the row-meets repo the scripts live in build/ and everything else hangs off the
# repo root. ROW_MEETS_ROOT lets the workflow point at the root without editing code.
ROOT = os.environ.get("ROW_MEETS_ROOT", HERE)
OUT_DIR = os.environ.get("ROW_MEETS_OUT", "/mnt/user-data/outputs")
OUT = os.environ.get("ROW_MEETS_CAL_OUT",
                     "/mnt/user-data/outputs/row-meets/calendars")

GROUPS_CSV = os.path.join(ROOT, "data", "groups.csv")
MEETS_CSV = os.path.join(ROOT, "data", "meets.csv")
EVENTS_CSV = os.path.join(ROOT, "data", "events.csv")
PACKAGE_DIR = os.path.join(ROOT, "packages")
GROUPS_CSV = GROUPS_CSV if os.path.exists(GROUPS_CSV) else GROUPS_CSV.replace(".csv", "_sample.csv")
MEETS_CSV = MEETS_CSV if os.path.exists(MEETS_CSV) else MEETS_CSV.replace(".csv", "_sample.csv")

SEASON = "2026-27"
DOMAIN = "rowswimming.ca"
# Where the folder will be served from once the repo exists.
MEETS_BASE = "https://row-gm.github.io/row-meets"
PAGES_BASE = f"{MEETS_BASE}/calendars"
PACKAGE_BASE = f"{MEETS_BASE}/packages"

def tags_of(cell):
    return [t.strip() for t in cell.replace(";", ",").split(",") if t.strip()]


def esc(t):
    """Escape for iCalendar text values."""
    return (t.replace("\\", "\\\\").replace(";", r"\;")
             .replace(",", r"\,").replace("\n", r"\n"))


def fold(line):
    """iCalendar lines wrap at 75 octets, continued with a leading space."""
    out, cur = [], line
    while len(cur.encode("utf-8")) > 73:
        cut = 73
        while len(cur[:cut].encode("utf-8")) > 73:
            cut -= 1
        out.append(cur[:cut])
        cur = " " + cur[cut:]
    out.append(cur)
    return out


def slug(code):
    return code.lower().replace(" ", "-")


def _shows(g, kind):
    """True if this group should appear for `kind` ("meets" or "events").
    Falls back to the old show_on_page column so an older groups.csv still works."""
    v = g.get("show_" + kind)
    if v is None or not str(v).strip():
        v = g.get("show_on_page", "Yes")
    return str(v).strip().lower() in ("yes", "y", "true")


def load():
    with open(GROUPS_CSV, encoding="utf-8-sig") as f:
        groups = [g for g in csv.DictReader(f)
                  if _shows(g, "meets") or _shows(g, "events")]
    groups.sort(key=lambda g: int(g["sort_order"]))
    with open(MEETS_CSV, encoding="utf-8-sig") as f:
        meets = list(csv.DictReader(f))
    for m in meets:
        m["_start"] = date.fromisoformat(m["start_date"].strip())
        m["_end"] = date.fromisoformat((m["end_date"] or m["start_date"]).strip())
        m["_confirm"] = (date.fromisoformat(m["confirm_by"].strip())
                         if m["confirm_by"].strip() else None)
    meets.sort(key=lambda m: m["_start"])

    events = []
    if os.path.exists(EVENTS_CSV):
        with open(EVENTS_CSV, encoding="utf-8-sig") as f:
            events = list(csv.DictReader(f))
        for e in events:
            e["_start"] = date.fromisoformat(e["start_date"].strip())
            e["_end"] = date.fromisoformat((e["end_date"] or e["start_date"]).strip())
            e["_confirm"] = (date.fromisoformat(e["confirm_by"].strip())
                             if e["confirm_by"].strip() else None)
            e["_all"] = e["all_groups"].strip().lower() == "yes"
        events.sort(key=lambda e: e["_start"])
    return groups, meets, events


def ics_for(group, meets, events):
    code = group["group_code"]
    name = group["display_name"]
    lines = [
        "BEGIN:VCALENDAR",
        "VERSION:2.0",
        f"PRODID:-//ROW Swim Club//Meet Schedule {SEASON}//EN",
        "CALSCALE:GREGORIAN",
        "METHOD:PUBLISH",
        f"X-WR-CALNAME:ROW {code} Meets {SEASON}",
        f"X-WR-CALDESC:{esc(name)} meet schedule and confirmation dates.",
        "X-PUBLISHED-TTL:PT12H",
        "REFRESH-INTERVAL;VALUE=DURATION:PT12H",
    ]
    stamp = "20260809T000000Z"

    for m in meets:
        if not m.get(code, "").strip():
            continue
        tags = tags_of(m[code])
        tentative = m["confirmed"].strip().lower() != "yes"

        # DTEND is exclusive for all-day events, so add a day.
        d1 = m["_start"].strftime("%Y%m%d")
        d2 = (m["_end"] + timedelta(days=1)).strftime("%Y%m%d")
        title = m["meet_name"] + (" (not confirmed)" if tentative else "")
        if "Peak" in tags:
            title = "\u2605 " + title   # a star marks a group's peak meet
        desc = (f"{', '.join(tags)} for {code}. {m['pool']} pool.")
        if m["notes"].strip():
            desc += " " + m["notes"].strip()
        if m["_confirm"]:
            desc += f" Confirm by {m['_confirm'].isoformat()}."

        lines += [
            "BEGIN:VEVENT",
            f"UID:{m['meet_id']}-{slug(code)}@{DOMAIN}",
            f"DTSTAMP:{stamp}",
            f"DTSTART;VALUE=DATE:{d1}",
            f"DTEND;VALUE=DATE:{d2}",
            f"SUMMARY:{esc(title)}",
            f"LOCATION:{esc(m['venue'] + ', ' + m['city'])}",
            f"DESCRIPTION:{esc(desc)}",
            "STATUS:TENTATIVE" if tentative else "STATUS:CONFIRMED",
            "TRANSP:TRANSPARENT",
        ]
        # Calendar apps show URL as a clickable link on the event.
        # Same rule as the page: an explicit link wins, otherwise a package PDF
        # named after the meet_id, otherwise no link.
        url = m["info_link"].strip()
        if not url and os.path.exists(os.path.join(PACKAGE_DIR, f"{m['meet_id'].strip()}.pdf")):
            url = f"{PACKAGE_BASE}/{m['meet_id'].strip()}.pdf"
        if url:
            lines.append(f"URL:{url}")
        lines.append("END:VEVENT")

        if m["_confirm"]:
            c1 = m["_confirm"].strftime("%Y%m%d")
            c2 = (m["_confirm"] + timedelta(days=1)).strftime("%Y%m%d")
            lines += [
                "BEGIN:VEVENT",
                f"UID:{m['meet_id']}-{slug(code)}-confirm@{DOMAIN}",
                f"DTSTAMP:{stamp}",
                f"DTSTART;VALUE=DATE:{c1}",
                f"DTEND;VALUE=DATE:{c2}",
                f"SUMMARY:{esc('Confirm by: ' + m['meet_name'])}",
                f"DESCRIPTION:{esc('Log into your ROW member account and Confirm or Decline attendance.')}",
                "TRANSP:TRANSPARENT",
                # A day-before nudge, since the deadline is the point of this entry.
                "BEGIN:VALARM",
                "TRIGGER:-P1D",
                "ACTION:DISPLAY",
                f"DESCRIPTION:{esc('Confirm or decline ' + m['meet_name'] + ' by tomorrow')}",
                "END:VALARM",
                "END:VEVENT",
            ]

    for e in events:
        if not (e["_all"] or e.get(code, "").strip()):
            continue
        timed = e["start_time"].strip() and e["end_time"].strip()
        if timed:
            # A timed event needs a timezone; floating local time is what every
            # calendar app does with a naive DTSTART, which is what we want here.
            s = e["_start"].strftime("%Y%m%d") + "T" + e["start_time"].strip().replace(":", "") + "00"
            t = e["_end"].strftime("%Y%m%d") + "T" + e["end_time"].strip().replace(":", "") + "00"
            dt = [f"DTSTART:{s}", f"DTEND:{t}"]
        else:
            dt = [f"DTSTART;VALUE=DATE:{e['_start'].strftime('%Y%m%d')}",
                  f"DTEND;VALUE=DATE:{(e['_end'] + timedelta(days=1)).strftime('%Y%m%d')}"]
        tentative = e["confirmed"].strip().lower() != "yes"
        title = e["event_name"] + (" (not confirmed)" if tentative else "")
        desc = e["description"].strip() or e["event_type"].strip()
        if e["_confirm"]:
            desc += f" Confirm by {e['_confirm'].isoformat()}."
        ev = ["BEGIN:VEVENT", f"UID:{e['event_id']}-{slug(code)}@{DOMAIN}",
              f"DTSTAMP:{stamp}"] + dt + [
              f"SUMMARY:{esc(title)}",
              f"DESCRIPTION:{esc(desc)}",
              "STATUS:TENTATIVE" if tentative else "STATUS:CONFIRMED",
              "TRANSP:TRANSPARENT"]
        if e["location"].strip():
            ev.append(f"LOCATION:{esc(e['location'].strip())}")
        if e["info_link"].strip():
            ev.append(f"URL:{e['info_link'].strip()}")
        ev.append("END:VEVENT")
        lines += ev

        if e["_confirm"]:
            c1 = e["_confirm"].strftime("%Y%m%d")
            c2 = (e["_confirm"] + timedelta(days=1)).strftime("%Y%m%d")
            lines += [
                "BEGIN:VEVENT",
                f"UID:{e['event_id']}-{slug(code)}-confirm@{DOMAIN}",
                f"DTSTAMP:{stamp}",
                f"DTSTART;VALUE=DATE:{c1}",
                f"DTEND;VALUE=DATE:{c2}",
                f"SUMMARY:{esc('Confirm by: ' + e['event_name'])}",
                f"DESCRIPTION:{esc('Log into your ROW member account and Confirm or Decline attendance.')}",
                "TRANSP:TRANSPARENT",
                "BEGIN:VALARM", "TRIGGER:-P1D", "ACTION:DISPLAY",
                f"DESCRIPTION:{esc('Confirm or decline ' + e['event_name'] + ' by tomorrow')}",
                "END:VALARM",
                "END:VEVENT",
            ]

    lines.append("END:VCALENDAR")
    folded = []
    for ln in lines:
        folded += fold(ln)
    return "\r\n".join(folded) + "\r\n"


groups, meets, events = load()
os.makedirs(OUT, exist_ok=True)

# Files already in the folder, so a group that is retired or hidden does not leave
# an orphan calendar behind in the repo. Removal is announced rather than silent:
# anyone still subscribed to a deleted file will see their calendar stop updating.
existing = {fn for fn in os.listdir(OUT) if fn.endswith(".ics")} if os.path.isdir(OUT) else set()

written = []
for g in groups:
    body = ics_for(g, meets, events)
    fn = f"row-{slug(g['group_code'])}.ics"
    with open(os.path.join(OUT, fn), "w", encoding="utf-8", newline="") as f:
        f.write(body)
    n = body.count("BEGIN:VEVENT")
    written.append((g, fn, n))

# A plain index so a family can find their own file. Not a CMS fragment; this one
# is served from GitHub Pages, so it may carry a <style> block and real links.
# A copy button, not a link. Clicking an .ics link downloads the file, which is
# exactly the mistake the warning above it is about. Copying gives them the URL to
# paste, which is what subscribing needs. This page is served from GitHub Pages
# rather than the CMS, so it may carry script.
rows = "\n".join(
    f'<tr id="{slug(g["group_code"])}"><td>{g["display_name"]}</td>'
    f'<td><code>{g["group_code"]}</code></td>'
    f'<td>{n} entries</td>'
    f'<td><button type="button" class="copy" data-url="{PAGES_BASE}/{fn}">'
    f'Copy calendar link</button></td></tr>'
    for g, fn, n in written)

index = f"""<!DOCTYPE html>
<html lang="en"><head><meta charset="utf-8">
<meta name="viewport" content="width=device-width,initial-scale=1">
<title>ROW Meet Calendars {SEASON}</title>
<style>
body{{font-family:Arial,Helvetica,sans-serif;max-width:800px;margin:0 auto;padding:24px;
color:#152225;line-height:1.6;}}
h1{{color:#0A2E3F;}} table{{border-collapse:collapse;width:100%;margin:20px 0;}}
th{{background:#0A2E3F;color:#fff;text-align:left;padding:9px 11px;font-size:13px;}}
td{{border-top:1px solid #DAD3C2;padding:9px 11px;font-size:14px;}}
tr:nth-child(even) td{{background:#FAF8F2;}}
tr:target td{{background:#EFFAF8;box-shadow:inset 4px 0 0 #136B77;}}
tr:target td:first-child{{font-weight:700;}}
code{{font-family:'Courier New',monospace;font-weight:700;}}
button.copy{{font-family:inherit;font-size:13px;font-weight:700;background:#0A2E3F;
color:#fff;border:0;border-radius:6px;padding:8px 14px;cursor:pointer;white-space:nowrap;}}
button.copy:hover{{background:#136B77;}}
button.copy:focus-visible{{outline:3px solid #136B77;outline-offset:2px;}}
button.copy.done{{background:#12786C;}}
.note{{border-left:4px solid #3FBFB0;background:#EFFAF8;padding:14px 18px;border-radius:0 8px 8px 0;}}
</style></head><body>
<h1>ROW Meet Calendars {SEASON}</h1>
<p>Add your group's meets to your digital calendar. You get the meet dates and
every Confirm By date.</p>
<p>To confirm or decline a meet, log into your ROW member account.</p>
<div class="note"><strong>Subscribe, do not download.</strong> Copy your group's link and
add it as a calendar <em>by URL</em>. If you download the file instead, you get a copy that
never updates, and a moved meet will not move in your calendar.</div>
<h2>How to subscribe</h2>
<p><strong>Google Calendar</strong> (do this on a computer): Other calendars, +, From URL,
paste the link, Add calendar. It then appears on every device signed in to that account.</p>
<p><strong>iPhone or iPad:</strong> Settings, Apps, Calendar, Calendar Accounts, Add Account,
Other, Add Subscribed Calendar, paste the link.</p>
<p><strong>Outlook:</strong> Add calendar, Subscribe from web, paste the link.</p>
<h2>Your group</h2>
<p>Copy your group's link, then follow the steps above for your calendar app.</p>
<table><tr><th>Group</th><th>Code</th><th>Meets and reminders</th><th></th></tr>
{rows}
</table>
<p>Calendars refresh on their own, though some apps take up to a day. Meets marked
<em>not confirmed</em> can still move.</p>
<script>
document.querySelectorAll('button.copy').forEach(function (b) {{
  b.addEventListener('click', function () {{
    var url = b.dataset.url, label = b.textContent;
    function done() {{
      b.textContent = 'Copied';
      b.classList.add('done');
      setTimeout(function () {{ b.textContent = label; b.classList.remove('done'); }}, 1800);
    }}
    if (navigator.clipboard && window.isSecureContext) {{
      navigator.clipboard.writeText(url).then(done, fallback);
    }} else {{ fallback(); }}
    function fallback() {{
      // Older browsers, and any page not served over https.
      var t = document.createElement('textarea');
      t.value = url; t.setAttribute('readonly', '');
      t.style.position = 'fixed'; t.style.top = '-1000px';
      document.body.appendChild(t); t.select();
      try {{ document.execCommand('copy'); done(); }}
      catch (e) {{ window.prompt('Copy this link:', url); }}
      document.body.removeChild(t);
    }}
  }});
}});
</script>
</body></html>"""

with open(os.path.join(OUT, "index.html"), "w", encoding="utf-8") as f:
    f.write(index)

orphans = sorted(existing - {fn for _, fn, _ in written})
for fn in orphans:
    os.remove(os.path.join(OUT, fn))

print(f"wrote {len(written)} calendars to {OUT}")
if orphans:
    print(f"removed {len(orphans)} calendar(s) for groups no longer shown: "
          + ", ".join(orphans))
for g, fn, n in written:
    print(f"  {g['group_code']:8s} {fn:22s} {n:>3} entries")
