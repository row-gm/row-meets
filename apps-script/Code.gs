/**
 * ROW Meet Schedule — publish to GitHub.
 *
 * Adds a "ROW" menu to the spreadsheet. Publish schedule reads the Meets and
 * Groups sheets and commits them to the row-meets repo as CSV. That commit
 * triggers the workflow, which validates the data, rebuilds the calendars and
 * rebuilds the page HTML.
 *
 * Nothing publishes on a timer. Nothing publishes until you click it.
 *
 * SETUP (once):
 *   1. Extensions > Apps Script, paste this in, save.
 *   2. Project Settings > Script Properties, add:
 *        GITHUB_TOKEN   a fine-grained token, row-meets only, Contents: Read and write
 *        GITHUB_OWNER   row-gm
 *        GITHUB_REPO    row-meets
 *   3. Reload the spreadsheet. The ROW menu appears.
 *
 * The token goes in Script Properties, never in a cell. Anyone with edit access
 * to the sheet can read a cell; Script Properties are not visible to them.
 *
 * "No expiration" is a reasonable choice for this token: it is scoped to one
 * public repository holding meet dates, and an expiry landing mid-season would
 * break publishing for whoever happens to be doing it. If it ever leaks, delete
 * it on GitHub and update GITHUB_TOKEN here.
 */

var SHEET_MEETS = 'Meets';
var SHEET_GROUPS = 'Groups';

// Row 1 is the header. Row 2 holds the grey hint text and is not data.
var FIRST_DATA_ROW = 3;

function onOpen() {
  SpreadsheetApp.getUi()
    .createMenu('ROW')
    .addItem('Publish schedule', 'publishSchedule')
    .addItem('Check for problems', 'checkOnly')
    .addToUi();
}

function checkOnly() {
  var problems = collectProblems();
  var ui = SpreadsheetApp.getUi();
  if (problems.length === 0) {
    ui.alert('No problems found', 'The schedule looks ready to publish.', ui.ButtonSet.OK);
  } else {
    ui.alert('Found ' + problems.length + ' problem(s)', problems.join('\n\n'), ui.ButtonSet.OK);
  }
}

function publishSchedule() {
  var ui = SpreadsheetApp.getUi();
  var problems = collectProblems();

  if (problems.length > 0) {
    ui.alert('Cannot publish yet', problems.join('\n\n'), ui.ButtonSet.OK);
    return;
  }

  var meets = readSheet(SHEET_MEETS);
  var answer = ui.alert(
    'Publish schedule?',
    meets.length + ' meets will be published.\n\n' +
    'Group calendars update on their own within a few minutes. ' +
    'The website page needs one paste afterwards.',
    ui.ButtonSet.OK_CANCEL);
  if (answer !== ui.Button.OK) return;

  try {
    var stamp = new Date().toISOString().slice(0, 16).replace('T', ' ');
    commitFile('data/meets.csv', toCsv(readSheet(SHEET_MEETS, true)), stamp);
    commitFile('data/groups.csv', toCsv(readSheet(SHEET_GROUPS, true, 2)), stamp);
    ui.alert('Published',
      'Sent to GitHub. Calendars rebuild in a few minutes.\n\n' +
      'When it is done, open the page HTML link and paste it into the website.',
      ui.ButtonSet.OK);
  } catch (e) {
    ui.alert('Publish failed', String(e), ui.ButtonSet.OK);
  }
}

/** Read a sheet into rows of strings, trimming trailing blank rows. */
function readSheet(name, withHeader, firstDataRow) {
  var sh = SpreadsheetApp.getActive().getSheetByName(name);
  if (!sh) throw new Error('Sheet not found: ' + name);
  var values = sh.getDataRange().getDisplayValues();
  var start = firstDataRow || FIRST_DATA_ROW;
  var header = values[0];
  var body = values.slice(start - 1).filter(function (r) {
    return r.join('').trim() !== '';
  });
  return withHeader ? [header].concat(body) : body;
}

function toCsv(rows) {
  return rows.map(function (r) {
    return r.map(function (cell) {
      var v = String(cell === null || cell === undefined ? '' : cell).trim();
      // A group cell can hold "Performance, Team", so quoting is not optional.
      if (v.indexOf('"') > -1) v = v.replace(/"/g, '""');
      return /[",\n]/.test(v) ? '"' + v + '"' : v;
    }).join(',');
  }).join('\n') + '\n';
}

/**
 * Checks that cost nothing here and save a failed build later. The Python build
 * validates properly; this catches the mistakes that are easiest to make in a
 * spreadsheet, while the person who made them is still looking at it.
 */
function collectProblems() {
  var problems = [];
  var rows = readSheet(SHEET_MEETS, true);
  var header = rows[0];
  var idx = {};
  header.forEach(function (h, i) { idx[String(h).trim()] = i; });

  ['meet_id', 'meet_name', 'start_date', 'confirm_by', 'pool',
   'confirmed', 'eligibility', 'hosted_by_row'].forEach(function (col) {
    if (!(col in idx)) problems.push('Missing column: ' + col);
  });
  if (problems.length) return problems;

  var seen = {};
  for (var r = 1; r < rows.length; r++) {
    var row = rows[r], line = 'Row ' + (r + FIRST_DATA_ROW - 1) + ' (' +
      (row[idx.meet_name] || 'no name') + '): ';

    var id = String(row[idx.meet_id]).trim();
    if (!id) problems.push(line + 'meet_id is blank.');
    else if (seen[id]) problems.push(line + 'meet_id "' + id + '" is used twice.');
    seen[id] = true;
    if (id && !/^[a-z0-9-]+$/.test(id)) {
      problems.push(line + 'meet_id must be lower case letters, numbers and hyphens.');
    }

    var start = parseDate(row[idx.start_date]);
    var conf = parseDate(row[idx.confirm_by]);
    if (!start) problems.push(line + 'start_date is not a date (use YYYY-MM-DD).');
    if (String(row[idx.confirm_by]).trim() && !conf) {
      problems.push(line + 'confirm_by is not a date (use YYYY-MM-DD).');
    }
    if (start && conf) {
      var days = Math.round((start - conf) / 86400000);
      if (days < 0) problems.push(line + 'confirm_by is after the meet.');
      // The season spans two calendar years, so a year typo is a real date that
      // sits before the meet and passes every other check.
      else if (days > 180) {
        problems.push(line + 'confirm_by is ' + days + ' days before the meet. ' +
          'Check the year.');
      }
    }

    if (['25m', '50m'].indexOf(String(row[idx.pool]).trim()) < 0) {
      problems.push(line + 'pool must be 25m or 50m.');
    }
    if (['Yes', 'No'].indexOf(String(row[idx.confirmed]).trim()) < 0) {
      problems.push(line + 'confirmed must be Yes or No.');
    }
    if (['Yes', 'No'].indexOf(String(row[idx.hosted_by_row]).trim()) < 0) {
      problems.push(line + 'hosted_by_row must be Yes or No.');
    }
    if (['All Welcome', 'Qualifiers Only'].indexOf(String(row[idx.eligibility]).trim()) < 0) {
      problems.push(line + 'eligibility must be All Welcome or Qualifiers Only.');
    }

    // Group columns start after the 13 meet fields. There is no meet-level type:
    // it is derived from these cells.
    var types = ['Peak', 'Performance', 'Pathway Skills', 'Team'];
    var racing = 0;
    for (var col = 13; col < header.length; col++) {
      var cell = String(row[col] || '').trim();
      if (!cell) continue;
      racing++;
      cell.split(',').forEach(function (t) {
        t = t.trim();
        if (t && types.indexOf(t) < 0) {
          problems.push(line + 'group ' + header[col] + ' has "' + t +
            '", which is not a meet type.');
        }
      });
    }
    if (racing === 0) problems.push(line + 'no group is racing this meet.');
  }
  return problems;
}

function parseDate(v) {
  var s = String(v).trim();
  if (!/^\d{4}-\d{2}-\d{2}$/.test(s)) return null;
  var d = new Date(s + 'T00:00:00Z');
  return isNaN(d.getTime()) ? null : d;
}

/** Create or update a file in the repo. */
function commitFile(path, content, stamp) {
  var props = PropertiesService.getScriptProperties();
  var token = props.getProperty('GITHUB_TOKEN');
  var owner = props.getProperty('GITHUB_OWNER');
  var repo = props.getProperty('GITHUB_REPO');
  if (!token || !owner || !repo) {
    throw new Error('Set GITHUB_TOKEN, GITHUB_OWNER and GITHUB_REPO in ' +
      'Project Settings > Script Properties.');
  }

  var url = 'https://api.github.com/repos/' + owner + '/' + repo + '/contents/' + path;

  /** Turn GitHub's status codes into something a club volunteer can act on. */
  function explain(code, body) {
    if (code === 401) {
      return 'GitHub rejected the token. It has probably been deleted or replaced. ' +
        'Make a new one and update GITHUB_TOKEN in Project Settings > Script Properties.';
    }
    if (code === 403) {
      return 'GitHub refused the request. The token may not have Contents: Read and write ' +
        'on ' + owner + '/' + repo + ', or an organisation owner may still need to approve it.';
    }
    if (code === 404) {
      return 'GitHub cannot find ' + owner + '/' + repo + '. Check GITHUB_OWNER and ' +
        'GITHUB_REPO in Project Settings, and that the token can see this repository.';
    }
    if (code === 409 || code === 422) {
      return 'GitHub could not apply the change. Someone may have edited the repository at ' +
        'the same moment. Wait a few seconds and publish again.';
    }
    return 'GitHub said ' + code + ': ' + body;
  }
  var headers = {
    Authorization: 'Bearer ' + token,
    Accept: 'application/vnd.github+json'
  };

  // The API needs the existing blob sha to replace a file.
  var sha = null;
  var probe = UrlFetchApp.fetch(url, {
    headers: headers, method: 'get', muteHttpExceptions: true
  });
  if (probe.getResponseCode() === 200) {
    sha = JSON.parse(probe.getContentText()).sha;
  } else if (probe.getResponseCode() !== 404) {
    throw new Error(explain(probe.getResponseCode(), probe.getContentText()));
  }

  var body = {
    message: 'Schedule published from the spreadsheet, ' + stamp,
    content: Utilities.base64Encode(content, Utilities.Charset.UTF_8)
  };
  if (sha) body.sha = sha;

  var res = UrlFetchApp.fetch(url, {
    method: 'put', headers: headers, contentType: 'application/json',
    payload: JSON.stringify(body), muteHttpExceptions: true
  });
  if (res.getResponseCode() >= 300) {
    throw new Error(explain(res.getResponseCode(), res.getContentText()));
  }
}
