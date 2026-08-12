"""Build the hosted schedule page.

This one is served from GitHub Pages, not the CMS, so it may carry script and a
stylesheet. That is what makes the group filter and the responsive layout
possible, neither of which the pasted page can do.

It reads data/meets.csv at load time, so it is current the moment a publish
lands. The data is also written into the file as a fallback, so the page still
works if the fetch fails, and so it can be opened straight off disk to preview.

Output: schedule/index.html
"""

import csv
import json
import os

import content
from datetime import date

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.environ.get("ROW_MEETS_ROOT", HERE)
OUT = os.environ.get("ROW_MEETS_SCHEDULE_OUT", os.path.join(ROOT, "schedule"))

SEASON = "2026-27"

# Page copy comes from the Text sheet in the spreadsheet.
TEXT, _FAQ = content.load(ROOT, season=SEASON)
MEET_TYPES, EVENT_TYPES = content.load_types(ROOT)
NAVY, TEAL, CYAN, RED = "#0A2E3F", "#136B77", "#3FBFB0", "#D64545"
SAND, FOAM, INK, INK_SOFT, LINE = "#F3EFE4", "#FFFFFF", "#152225", "#4B5B60", "#DAD3C2"
ROW_ALT = "#FAF8F2"
TIDE, PLUM, FLAG, AMBER = "#12786C", "#6E3D6B", "#C23A3A", "#8A6420"

DISPLAY = "'Arial Black', Arial, Helvetica, sans-serif"
BODY = "Arial, Helvetica, sans-serif"
MONO = "'Courier New', Courier, monospace"
UI = "Arial, Helvetica, sans-serif"

def _shows(g, kind):
    """True if this group should appear for `kind` ("meets" or "events").
    Falls back to the old show_on_page column so an older groups.csv still works."""
    v = g.get("show_" + kind)
    if v is None or not str(v).strip():
        v = g.get("show_on_page", "Yes")
    return str(v).strip().lower() in ("yes", "y", "true")


with open(os.path.join(ROOT, "data", "groups.csv"), encoding="utf-8-sig") as f:
    groups = [g for g in csv.DictReader(f)
              if _shows(g, "meets") or _shows(g, "events")]
groups.sort(key=lambda g: int(g["sort_order"]))

with open(os.path.join(ROOT, "data", "meets.csv"), encoding="utf-8-sig") as f:
    meets = list(csv.DictReader(f))
meets.sort(key=lambda m: m["start_date"].strip())

events = []
_ev_path = os.path.join(ROOT, "data", "events.csv")
if os.path.exists(_ev_path):
    with open(_ev_path, encoding="utf-8-sig") as f:
        events = list(csv.DictReader(f))
    events.sort(key=lambda e: e["start_date"].strip())

codes = [g["group_code"] for g in groups]
payload = {
    "season": SEASON,
    "built": date.today().isoformat(),
    "groups": [{"code": g["group_code"], "name": g["display_name"],
                "pathway": g["pathway"]} for g in groups],
    "showMeets": {code: _shows(g, "meets")
                  for g, code in zip(groups, codes)},
    "showEvents": {code: _shows(g, "events")
                   for g, code in zip(groups, codes)},
    "eventTypes": {n: h for n, h, _ in EVENT_TYPES},
    "events": [{
        "id": e["event_id"].strip(),
        "name": e["event_name"].strip(),
        "type": e["event_type"].strip(),
        "start": e["start_date"].strip(),
        "end": (e["end_date"] or e["start_date"]).strip(),
        "startTime": e["start_time"].strip(),
        "endTime": e["end_time"].strip(),
        "location": e["location"].strip(),
        "all": e["all_groups"].strip().lower() == "yes",
        "confirmBy": e["confirm_by"].strip(),
        "confirmCode": e.get("confirm_code", "").strip(),
        "confirmed": e["confirmed"].strip().lower() == "yes",
        "description": e["description"].strip(),
        "link": e["info_link"].strip(),
        "going": {cc: True for cc in codes if e.get(cc, "").strip()},
    } for e in events],
    "meets": [{
        "id": m["meet_id"].strip(),
        "name": m["meet_name"].strip(),
        "start": m["start_date"].strip(),
        "end": (m["end_date"] or m["start_date"]).strip(),
        "city": m["city"].strip(),
        "venue": m["venue"].strip(),
        "pool": m["pool"].strip(),
        "home": m["hosted_by_row"].strip().lower() == "yes",
        "confirmed": m["confirmed"].strip().lower() == "yes",
        "confirmBy": m["confirm_by"].strip(),
        "confirmCode": m.get("confirm_code", "").strip(),
        "eligibility": m["eligibility"].strip(),
        "link": m["info_link"].strip(),
        "notes": m["notes"].strip(),
        "going": {c: [t.strip() for t in m[c].replace(";", ",").split(",") if t.strip()]
                  for c in codes if m[c].strip()},
    } for m in meets],
}

TYPE_BG = {n: h for n, h, _ in MEET_TYPES}
TYPE_BG["Qualifiers Only"] = FLAG
TYPE_BG["Not confirmed"] = AMBER
TYPE_BG_JSON = json.dumps(TYPE_BG)
# Descriptions come from the Types sheet where given, and fall back to the Text
# sheet so the wording written earlier is not lost.
MEANING_JSON = json.dumps(
    [[n, d or TEXT.get(content.TAG_KEYS.get(n, ""), "")] for n, _, d in MEET_TYPES]
    + [[n, TEXT[content.TAG_KEYS[n]]] for n in ("Qualifiers Only", "Not confirmed")])
GROUPCARD_BODY = json.dumps(TEXT["groupcard_body"])
GROUPCARD_BUTTON = json.dumps(TEXT["groupcard_button"])
SCHEDULE_EMPTY = json.dumps(TEXT["schedule_empty"])
CONFIRM_URL_JSON = json.dumps(TEXT["confirm_url"])
CONFIRM_LABEL_JSON = json.dumps(TEXT["confirm_link_label"])
HELP_URL_JSON = json.dumps(TEXT["confirm_help_url"])
HELP_LABEL_JSON = json.dumps(TEXT["confirm_help_label"])
EVENT_MEANING_JSON = json.dumps([[n, h, d] for n, h, d in EVENT_TYPES])

html = f"""<!DOCTYPE html>
<html lang="en"><head><meta charset="utf-8">
<meta name="viewport" content="width=device-width,initial-scale=1">
<title>ROW {TEXT['schedule_title']} {SEASON}</title>
<style>
*{{box-sizing:border-box;}}
body{{margin:0;background:{FOAM};color:{INK};font-family:{BODY};line-height:1.6;}}
.wrap{{max-width:1000px;margin:0 auto;padding:0 18px 60px;}}
.hero{{background:{NAVY};color:{FOAM};padding:30px 0 26px;margin-bottom:0;}}
.hero .wrap{{padding-bottom:0;}}
.eyebrow{{font-family:{MONO};font-weight:700;font-size:11px;letter-spacing:0.16em;
text-transform:uppercase;color:{CYAN};margin:0 0 8px;}}
h1{{font-family:{DISPLAY};text-transform:uppercase;letter-spacing:0.01em;font-size:40px;
margin:0 0 10px;line-height:1.05;}}
.sub{{font-size:16px;max-width:44em;opacity:0.92;margin:0;}}
.lanes{{height:6px;background:linear-gradient(90deg,{CYAN} 0 25%,{TEAL} 25% 50%,
{SAND} 50% 75%,{RED} 75% 100%);}}
h2{{font-family:{UI};font-weight:700;text-transform:uppercase;letter-spacing:0.06em;
color:{NAVY};font-size:17px;margin:34px 0 12px;}}
.bar{{position:sticky;top:0;z-index:5;background:{FOAM};border-bottom:1px solid {LINE};
padding:14px 0;margin-bottom:6px;}}
.bar .inner{{display:flex;gap:14px;align-items:center;flex-wrap:wrap;
max-width:1000px;margin:0 auto;padding:0 18px;}}
label{{font-family:{UI};font-weight:700;font-size:11px;letter-spacing:0.08em;
text-transform:uppercase;color:{INK_SOFT};}}
select{{font-family:{BODY};font-size:16px;padding:10px 12px;border:2px solid {NAVY};
border-radius:8px;background:{FOAM};color:{INK};min-width:230px;}}
.count{{font-size:14px;color:{INK_SOFT};margin-left:auto;}}
.btn{{display:inline-block;font-family:{UI};font-weight:700;text-transform:uppercase;
letter-spacing:0.06em;font-size:13px;background:{TEAL};color:{FOAM};padding:11px 18px;
border-radius:8px;text-decoration:none;border:0;cursor:pointer;white-space:nowrap;}}
.btn:hover{{background:{NAVY};}}
.btn.done{{background:{TIDE};}}
.calcard{{background:{ROW_ALT};border:2px solid {TEAL};border-radius:12px;
padding:18px 20px;margin:16px 0 0;display:flex;gap:16px;align-items:center;
flex-wrap:wrap;}}
.calcard .t{{font-family:{UI};font-weight:700;text-transform:uppercase;letter-spacing:0.05em;
color:{NAVY};font-size:14px;}}
.calcard .d{{font-size:14px;color:{INK_SOFT};flex:1;min-width:220px;}}
table{{border-collapse:collapse;width:100%;margin:14px 0 0;font-size:14px;}}
th{{background:{NAVY};color:{FOAM};text-align:left;padding:11px 12px;
font-family:{UI};font-weight:700;text-transform:uppercase;letter-spacing:0.08em;
font-size:11px;}}
td{{border-top:1px solid {LINE};padding:12px;vertical-align:top;}}
tbody tr:nth-child(even){{background:{ROW_ALT};}}
.date{{font-family:{MONO};font-weight:700;color:{NAVY};white-space:nowrap;}}
.name{{font-weight:700;color:{NAVY};}}
.name a{{color:{NAVY};}}
.muted{{color:{INK_SOFT};font-size:13px;}}
.tag{{display:inline-block;font-family:{UI};font-weight:700;font-size:10.5px;
letter-spacing:0.05em;text-transform:uppercase;color:{FOAM};border-radius:4px;
padding:3px 7px;margin:0 4px 3px 0;white-space:nowrap;}}
.legend td{{font-size:14px;}}
a.help{{display:inline-block;width:15px;height:15px;line-height:15px;text-align:center;
border-radius:50%;background:{FOAM};color:{NAVY};font-size:10px;font-weight:700;
text-decoration:none;vertical-align:middle;opacity:0.75;}}
a.help:hover{{opacity:1;}}
.legend td:first-child{{white-space:nowrap;}}
.empty{{padding:26px;text-align:center;color:{INK_SOFT};background:{ROW_ALT};
border:1px solid {LINE};border-radius:10px;margin-top:14px;}}
footer{{margin-top:40px;padding-top:16px;border-top:1px solid {LINE};
font-size:13px;color:{INK_SOFT};}}
/* Narrow screens: rows become stacked cards. This is the layout the pasted page
   cannot have, and the reason seven columns stop being a problem on a phone. */
@media (max-width:760px){{
  h1{{font-size:30px;}}
  thead{{position:absolute;left:-9999px;}}
  tbody tr{{display:block;border:1px solid {LINE};border-radius:10px;
  margin:0 0 12px;background:{FOAM};padding:4px 2px;}}
  tbody tr:nth-child(even){{background:{FOAM};}}
  td{{display:flex;gap:12px;border-top:0;padding:7px 12px;}}
  td::before{{content:attr(data-label);flex:none;width:96px;font-family:{UI};
  font-weight:700;font-size:10.5px;letter-spacing:0.05em;text-transform:uppercase;
  color:{INK_SOFT};padding-top:3px;}}
  td:first-child{{border-top:0;}}
  .count{{margin-left:0;}}
  select{{width:100%;}}
}}
</style></head><body>

<div class="hero"><div class="wrap">
  <div class="eyebrow">{TEXT['schedule_eyebrow']}</div>
  <h1>{TEXT['schedule_title']}</h1>
  <p class="sub">{TEXT['schedule_subtitle']}</p>
</div></div>
<div class="lanes"></div>

<div class="bar"><div class="inner">
  <label for="group">{TEXT['group_label']}</label>
  <select id="group"><option value="">{TEXT['group_all']}</option></select>
  <span class="count" id="count"></span>
</div></div>

<div class="wrap">
  <div id="calcard"></div>
  <h2 id="meetshead">{TEXT['meets_heading']}</h2>
  <div id="out"></div>
  <h2 id="eventshead">{TEXT['events_heading']}</h2>
  <div id="events"></div>

  <h2>{TEXT['legend_heading']}</h2>
  <table class="legend"><tbody id="legend"></tbody></table>

  <h2 id="eventlegendhead" style="display:none;">{TEXT['event_legend_heading']}</h2>
  <table class="legend" id="eventlegendtable" style="display:none;">
  <tbody id="eventlegend"></tbody></table>

  <footer>
    <p id="built"></p>
  </footer>
</div>

<script>
var FALLBACK = {json.dumps(payload)};
var CAL_BASE = 'https://row-gm.github.io/row-meets/calendars';
var CONFIRM_URL = {CONFIRM_URL_JSON};
var CONFIRM_LABEL = {CONFIRM_LABEL_JSON};
var HELP_URL = {HELP_URL_JSON};
var HELP_LABEL = {HELP_LABEL_JSON};
var TYPE_BG = {TYPE_BG_JSON};
var MEANING = {MEANING_JSON};
var EVENT_MEANING = {EVENT_MEANING_JSON};
var DASH = String.fromCharCode(8211), EMDASH = String.fromCharCode(8212);
var MON = ['Jan','Feb','Mar','Apr','May','Jun','Jul','Aug','Sep','Oct','Nov','Dec'];
var data = FALLBACK;

function esc(s) {{
  return String(s).replace(/&/g,'&amp;').replace(/</g,'&lt;').replace(/>/g,'&gt;');
}}
function tag(text, bg) {{
  return '<span class="tag" style="background:' + bg + '">' + esc(text) + '</span>';
}}
function d(iso) {{
  var p = iso.split('-');
  return {{ m: +p[1], day: +p[2], y: +p[0] }};
}}
function dateLabel(m) {{
  var a = d(m.start), b = d(m.end);
  if (m.start === m.end) return MON[a.m-1] + ' ' + a.day;
  if (a.m === b.m) return MON[a.m-1] + ' ' + a.day + '\\u2013' + b.day;
  return MON[a.m-1] + ' ' + a.day + ' \\u2013 ' + MON[b.m-1] + ' ' + b.day;
}}
function confirmLabel(m) {{
  if (!m.confirmBy) return '\\u2014';
  var c = d(m.confirmBy);
  return MON[c.m-1] + ' ' + c.day;
}}
function th(label) {{
  /* The one question this column reliably raises, answered where it is asked.
     Small, muted, and skipped entirely by anyone who already knows. */
  if (label === 'Confirm By' && HELP_URL) {{
    return '<th>' + label + ' <a class="help" href="' + esc(HELP_URL) +
      '" target="_blank" title="' + esc(HELP_LABEL) + '">?</a></th>';
  }}
  return '<th>' + label + '</th>';
}}

function typesFor(m, code) {{
  if (code && m.going[code]) return m.going[code];
  var all = {{}};
  for (var k in m.going) m.going[k].forEach(function (t) {{ all[t] = 1; }});
  return Object.keys(TYPE_BG).filter(function (t) {{ return all[t]; }});
}}

function render() {{
  // A missing key should degrade to an empty section, not stop the page.
  data.events = data.events || [];
  data.showMeets = data.showMeets || {{}};
  data.showEvents = data.showEvents || {{}};
  data.eventTypes = data.eventTypes || {{}};
  var code = document.getElementById('group').value;
  var list = data.meets.filter(function (m) {{ return !code || m.going[code]; }});
  var g = data.groups.filter(function (x) {{ return x.code === code; }})[0];

  document.getElementById('count').textContent =
    list.length + (list.length === 1 ? ' meet' : ' meets') + (g ? ' for ' + g.name : '');

  document.getElementById('calcard').innerHTML = !g ? '' :
    '<div class="calcard"><div class="t">' + esc(g.name) + '</div>' +
    '<div class="d">' + {GROUPCARD_BODY} + '</div>' +
    '<button class="btn" id="copycal" data-url="' + CAL_BASE + '/row-' +
    g.code.toLowerCase().replace(/ /g,'-') + '.ics">' + {GROUPCARD_BUTTON} +
    '</button></div>';

  var showM = !code || data.showMeets[code] !== false;
  var showE = !code || data.showEvents[code] !== false;
  if (!showM) {{
    document.getElementById('out').innerHTML = '';
  }} else if (!list.length) {{
    document.getElementById('out').innerHTML =
      '<div class="empty">' + {SCHEDULE_EMPTY} + '</div>';
  }} else {{
    var head = ['Meet Date','Confirm By','Meet Name','Location','Pool','Meet Type','Eligibility'];
    var h = '<table><thead><tr>' + head.map(th).join('') + '</tr></thead><tbody>';
    list.forEach(function (m) {{
      var name = m.link
        ? '<a href="' + esc(m.link) + '" target="_blank">' + esc(m.name) + '</a>'
        : esc(m.name);
      var extra = '';
      if (m.home) extra += '<div class="muted">At our pool. Officials needed.</div>';
      if (!m.confirmed) extra += '<div>' + tag('Not confirmed','{AMBER}') + '</div>';
      if (m.notes) extra += '<div class="muted">' + esc(m.notes) + '</div>';
      h += '<tr>' +
        '<td data-label="Date" class="date">' + dateLabel(m) + '</td>' +
        '<td data-label="Confirm by" class="date">' + confirmLabel(m) + '</td>' +
        '<td data-label="Meet"><span class="name">' + name + '</span>' + extra + '</td>' +
        '<td data-label="Where">' + esc(m.city) +
          '<div class="muted">' + esc(m.venue) + '</div></td>' +
        '<td data-label="Pool">' + esc(m.pool) + '</td>' +
        '<td data-label="Type">' + typesFor(m, code).map(function (t) {{
            return tag(t, TYPE_BG[t] || '{INK_SOFT}');
          }}).join('') + '</td>' +
        '<td data-label="Entry">' + (m.eligibility === 'Qualifiers Only'
          ? tag('Qualifiers Only','{FLAG}') : tag('All Welcome','{INK_SOFT}')) + '</td>' +
        '</tr>';
    }});
    document.getElementById('out').innerHTML = h + '</tbody></table>';
  }}
  document.getElementById('meetshead').style.display = showM ? '' : 'none';

  /* Events. Own table, own columns: an event has no pool, meet type or
     eligibility, so sharing the meets table would leave four columns empty on
     every row. */
  var evs = data.events.filter(function (e) {{
    return showE && (!code || e.all || e.going[code]);
  }});
  document.getElementById('eventshead').style.display = evs.length ? '' : 'none';
  if (!evs.length) {{
    document.getElementById('events').innerHTML = '';
  }} else {{
    var eh = '<table><thead><tr>' +
      ['Date','Time','Event','Location','Confirm By'].map(th).join('') +
      '</tr></thead><tbody>';
    evs.forEach(function (e) {{
      var nm = e.link
        ? '<a href="' + esc(e.link) + '" target="_blank">' + esc(e.name) + '</a>'
        : esc(e.name);
      var extra = '<div>' + tag(e.type, data.eventTypes[e.type] || '{INK_SOFT}') + '</div>';
      if (!e.confirmed) extra += '<div>' + tag('Not confirmed','{AMBER}') + '</div>';
      if (e.description) extra += '<div class="muted">' + esc(e.description) + '</div>';
      var time = (e.startTime && e.endTime)
        ? esc(e.startTime) + '&ndash;' + esc(e.endTime) : 'All day';
      eh += '<tr>' +
        '<td data-label="Date" class="date">' + dateLabel(e) + '</td>' +
        '<td data-label="Time" class="date">' + time + '</td>' +
        '<td data-label="Event"><span class="name">' + nm + '</span>' + extra + '</td>' +
        '<td data-label="Where">' + (e.location ? esc(e.location) : '&mdash;') + '</td>' +
        '<td data-label="Confirm by" class="date">' + confirmLabel(e) + '</td>' +
        '</tr>';
    }});
    document.getElementById('events').innerHTML = eh + '</tbody></table>';
  }}

  var b = document.getElementById('copycal');
  if (b) b.addEventListener('click', function () {{
    var url = b.dataset.url;
    function done() {{
      b.textContent = 'Copied'; b.classList.add('done');
      setTimeout(function () {{
        b.textContent = {GROUPCARD_BUTTON}; b.classList.remove('done');
      }}, 1800);
    }}
    if (navigator.clipboard && window.isSecureContext) {{
      navigator.clipboard.writeText(url).then(done, function () {{ window.prompt('Copy this link:', url); }});
    }} else {{ window.prompt('Copy this link:', url); }}
  }});
}}

function start() {{
  var sel = document.getElementById('group');
  data.groups.forEach(function (g) {{
    var o = document.createElement('option');
    o.value = g.code; o.textContent = g.name + ' (' + g.code + ')';
    sel.appendChild(o);
  }});
  sel.addEventListener('change', function () {{
    render();
    try {{ localStorage.setItem('rowGroup', sel.value); }} catch (e) {{}}
  }});
  try {{
    var saved = localStorage.getItem('rowGroup');
    if (saved) sel.value = saved;
  }} catch (e) {{}}
  document.getElementById('legend').innerHTML = MEANING.map(function (r) {{
    return '<tr><td>' + tag(r[0], TYPE_BG[r[0]]) + '</td><td>' + r[1] + '</td></tr>';
  }}).join('');
  // Only worth showing once there are events to explain.
  if (data.events && data.events.length) {{
    document.getElementById('eventlegendhead').style.display = '';
    document.getElementById('eventlegendtable').style.display = '';
    document.getElementById('eventlegend').innerHTML = EVENT_MEANING.map(function (r) {{
      return '<tr><td>' + tag(r[0], r[1]) + '</td><td>' + (r[2] || '') + '</td></tr>';
    }}).join('');
  }}
  document.getElementById('built').textContent = 'Schedule last updated ' + data.built + '.';
  render();
}}

/* A real CSV parser, because a group cell can hold "Performance, Team" and a
   naive split on commas would tear it in half. */
function parseCSV(text) {{
  var CR = String.fromCharCode(13), NL = String.fromCharCode(10);
  var rows = [], row = [], field = '', q = false, i = 0;
  text = text.split(CR + NL).join(NL).split(CR).join(NL);
  for (; i < text.length; i++) {{
    var ch = text[i];
    if (q) {{
      if (ch === '"') {{
        if (text[i+1] === '"') {{ field += '"'; i++; }} else {{ q = false; }}
      }} else {{ field += ch; }}
    }} else if (ch === '"') {{ q = true; }}
    else if (ch === ',') {{ row.push(field); field = ''; }}
    else if (ch === NL) {{ row.push(field); rows.push(row); row = []; field = ''; }}
    else {{ field += ch; }}
  }}
  if (field !== '' || row.length) {{ row.push(field); rows.push(row); }}
  var head = rows.shift().map(function (h) {{ return h.trim(); }});
  return rows.filter(function (r) {{ return r.join('').trim() !== ''; }})
    .map(function (r) {{
      var o = {{}};
      head.forEach(function (h, n) {{ o[h] = (r[n] || '').trim(); }});
      return o;
    }});
}}

function shows(g, kind) {{
  var v = g['show_' + kind];
  if (v === undefined || String(v).trim() === '') v = g.show_on_page;
  if (v === undefined || String(v).trim() === '') v = 'Yes';
  return /^(yes|y|true)$/i.test(String(v).trim());
}}

function build(meetRows, groupRows, eventRows) {{
  var gs = groupRows
    .filter(function (g) {{ return shows(g, 'meets') || shows(g, 'events'); }})
    .sort(function (a, b) {{ return (+a.sort_order) - (+b.sort_order); }})
    .map(function (g) {{
      return {{ code: g.group_code, name: g.display_name, pathway: g.pathway }};
    }});
  var codes = gs.map(function (g) {{ return g.code; }});
  var ms = meetRows.map(function (m) {{
    var going = {{}};
    codes.forEach(function (c) {{
      var v = (m[c] || '').trim();
      if (v) {{
        going[c] = v.replace(/;/g, ',').split(',')
          .map(function (t) {{ return t.trim(); }})
          .filter(Boolean);
      }}
    }});
    return {{
      id: m.meet_id, name: m.meet_name, start: m.start_date,
      end: m.end_date || m.start_date, city: m.city, venue: m.venue, pool: m.pool,
      home: /^yes$/i.test(m.hosted_by_row), confirmed: /^yes$/i.test(m.confirmed),
      confirmBy: m.confirm_by, confirmCode: (m.confirm_code || '').trim(),
      eligibility: m.eligibility, link: m.info_link,
      notes: m.notes, going: going
    }};
  }}).sort(function (a, b) {{ return a.start < b.start ? -1 : a.start > b.start ? 1 : 0; }});
  var showMeets = {{}}, showEvents = {{}};
  groupRows.forEach(function (g) {{
    showMeets[g.group_code] = shows(g, 'meets');
    showEvents[g.group_code] = shows(g, 'events');
  }});

  var es = (eventRows || []).map(function (e) {{
    var going = {{}};
    codes.forEach(function (cc) {{ if ((e[cc] || '').trim()) going[cc] = true; }});
    return {{
      id: e.event_id, name: e.event_name, type: e.event_type,
      start: e.start_date, end: e.end_date || e.start_date,
      startTime: e.start_time || '', endTime: e.end_time || '',
      location: e.location || '', all: /^yes$/i.test(e.all_groups || ''),
      confirmBy: e.confirm_by || '', confirmCode: (e.confirm_code || '').trim(),
      confirmed: /^yes$/i.test(e.confirmed || ''),
      description: e.description || '', link: e.info_link || '', going: going
    }};
  }}).sort(function (a, b) {{ return a.start < b.start ? -1 : a.start > b.start ? 1 : 0; }});

  // Every key the renderer reads must be here. Returning a partial object is
  // what broke this page: data.events was undefined and rendering stopped.
  return {{
    season: FALLBACK.season, built: FALLBACK.built,
    groups: gs, meets: ms, events: es,
    showMeets: showMeets, showEvents: showEvents,
    eventTypes: FALLBACK.eventTypes
  }};
}}

/* Live data when it is reachable, the built-in copy when it is not. Opening this
   file straight off disk hits the fallback, which is why the preview works. */
Promise.all([
  fetch('../data/meets.csv').then(function (r) {{ if (!r.ok) throw 0; return r.text(); }}),
  fetch('../data/groups.csv').then(function (r) {{ if (!r.ok) throw 0; return r.text(); }}),
  // Optional. No events.csv simply means no events.
  fetch('../data/events.csv').then(function (r) {{ return r.ok ? r.text() : ''; }})
    .catch(function () {{ return ''; }})
]).then(function (texts) {{
  var live = build(parseCSV(texts[0]), parseCSV(texts[1]),
                   texts[2] ? parseCSV(texts[2]) : []);
  if (!live.meets.length || !live.groups.length) throw 0;
  data = live;
  data.built = 'just now';
  start();
}}).catch(function () {{
  start();
}});
</script>
</body></html>"""

os.makedirs(OUT, exist_ok=True)
with open(os.path.join(OUT, "index.html"), "w", encoding="utf-8") as f:
    f.write(html)
print(f"wrote {os.path.join(OUT, 'index.html')} {len(html):,} chars")
print(f"{len(payload['meets'])} meets, {len(payload['groups'])} groups")
