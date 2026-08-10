# row-meets

Meet schedule, group calendars and meet packages for ROW Swim Club.

The schedule spreadsheet is the only place data is edited. Everything here is
generated from it.

## Publishing a change

1. Edit the schedule spreadsheet.
2. **ROW > Check for problems** if you want to look before you leap.
3. **ROW > Publish schedule.**
4. Wait a few minutes. Group calendars are now live for everyone subscribed.
5. Open the [page HTML](https://row-gm.github.io/row-meets/page/), press
   **Copy page HTML**, and paste it into `/page/events/meet-schedule` using the
   editor's **Source** button.

Step 5 is the only manual part, and only the website needs it. Calendars update
themselves because families subscribe to a URL rather than downloading a file.

Nothing publishes on a timer. There is a weekly job, but it rebuilds calendars
only and never touches the page, so the website cannot change without a person.

## If a publish fails

The workflow validates before it commits anything. Bad data stops the build and
GitHub emails whoever published. The message names the meet and the field, for
example:

```
ROW Fall First Try: confirm by is 379 days before the meet. Check the year on 2025-10-03.
```

Fix the spreadsheet and publish again. A failed publish changes nothing, so
there is no half-published state to clean up.

## What is in here

```
build/        the scripts. Not edited when the schedule changes.
data/         meets.csv and groups.csv, written by the spreadsheet.
packages/     meet package PDFs, named after the meet_id.
calendars/    generated .ics files and the subscribe page.
page/         generated page HTML with a copy button.
```

### Meet packages

Name the PDF after the `meet_id` and put it in `packages/`. The meet name
becomes a link on the page and on the calendar entry. Nothing to type in the
spreadsheet.

`info_link` in the spreadsheet overrides this, for meets hosted elsewhere.

Never point either at the ROW Hosted Meets page on the website. That page
promotes our meets to other clubs; it is not a members' resource.

## Setup, once

**GitHub Pages:** Settings > Pages > deploy from `main`, root folder.

**The repo is public**, which GitHub Pages requires. Nothing with swimmer names
belongs in here.

**Apps Script:** in the spreadsheet, Extensions > Apps Script, paste
`apps-script/Code.gs`, then Project Settings > Script Properties:

| Property | Value |
| --- | --- |
| `GITHUB_TOKEN` | fine-grained token, `row-meets` only, Contents: Read and write |
| `GITHUB_OWNER` | `row-gm` |
| `GITHUB_REPO` | `row-meets` |

The token lives in Script Properties, never in a cell. Anyone with edit access
to the spreadsheet can read a cell.

Set the token to **No expiration**. It can only write to one public repository
of meet dates, and an expiry landing mid-season would break publishing for
whoever happens to be doing it that week. If it ever leaks, delete it on GitHub
and update `GITHUB_TOKEN` here.

### Making the token

GitHub avatar > Settings > Developer settings > Personal access tokens >
Fine-grained tokens > Generate new token.

- **Resource owner:** `row-gm`. If this is left as a personal account the token
  cannot reach the club repo.
- **Repository access:** Only select repositories > `row-meets`
- **Permissions:** Repository permissions > Contents > **Read and write**

Copy the token before leaving the page. GitHub shows it once.

If `row-gm` is an organisation, an owner may need to approve the token.

### The first publish

Google will say it has not verified the app. That is what it says about any
script it has not reviewed, including your own. Advanced > Go to project
(unsafe) > Allow. Once only.

Try **ROW > Check for problems** first: it needs no token, so it confirms the
script is wired up before you hand it a password.

## Running the build by hand

```
ROW_MEETS_ROOT=$PWD \
ROW_MEETS_CAL_OUT=$PWD/calendars \
ROW_MEETS_PAGE_OUT=$PWD/page \
ROW_MEETS_OUT=/tmp/out \
python3 build/build_meet_schedule.py && python3 build/make_calendars.py
```

## Two things worth knowing

**Deleting a group deletes its calendar.** The build removes `.ics` files for
groups no longer shown and says so in the log. Anyone still subscribed sees
their calendar quietly stop updating, with no error. Think before retiring a
group mid-season.

**`GROUP_DETAIL` at the top of `build_meet_schedule.py`** switches the page
between one block per group and one per pathway. Pathway is roughly half the
size, which matters because the page is pasted into a CMS editor by hand.
