"""Build the Confirm or Decline page fragment for the CMS.

Class-based markup against the shared stylesheet. Two pastes: this HTML into the
content editor via Source, and the generated CSS into the page's CSS field.

Written to parents, not swimmers. Confirming is a parent's job, and the rest of
the meet pages speak to the swimmer, so mixing the two would blur who is being
asked to act.

Two things shape the copy:

  - The headline is "confirming is how your swimmer gets entered", not "silence
    means they are out". Both state the same rule, but one asks for an action and
    the other teaches people that ignoring the email works. The no-answer case is
    a plain factual answer among the questions, present for anyone who looks for
    it and never advertised.

  - Declining is presented as doing something, because it does: it keeps a
    swimmer out of the entry. A parent who thinks Decline is a courtesy has no
    reason to click it.

Nothing here quotes a cost. The mechanism, that the club pays for every swimmer
on a submitted entry, explains the deadline without putting a number on a public
page and without reading as blame.

Screenshots and click-by-click steps are left to SportsEngine's own article,
which they keep current. This page carries only what is true about ROW.

Output: row_confirm_or_decline_embed.html
        row_confirm_or_decline.css
"""

import os

import row_classes as R

HERE = os.path.dirname(os.path.abspath(__file__))
OUT_DIR = os.environ.get("ROW_MEETS_OUT", "/mnt/user-data/outputs")
SHARED_CSS = os.path.join(HERE, "row_stylesheet.css")

SCHEDULE_URL = "https://row-gm.github.io/row-meets/schedule/"
HELP_URL = ("https://motion-help.sportsengine.com/en/articles/"
            "8537937-how-to-commit-sign-up-for-a-meet-event")

answers = R.table(
    ["Your answer", "What it does"],
    [[R.pill("Confirm", R.TEAL), "Puts your swimmer in the entry for that meet."],
     [R.pill("Decline", R.INK_SOFT),
      "Keeps your swimmer out of it. This is a real answer that does a real thing: "
      "it closes that meet off, so nobody is entered by accident."]])

# The schedule links each meet straight to its own confirmation page, so hunting
# through a list is the fallback, not the method. Describing the manual route
# first made the page read as more work than it is.
steps = (R.step(1, "Tap the Confirm By date on the schedule",
                "It takes you straight to that meet's confirmation page. Sign in if "
                "you are asked to.")
         + R.step(2, "Choose Confirm or Decline for each swimmer",
                  "Families with more than one swimmer answer for each of them "
                  "separately.")
         + R.step(3, "Check it saved",
                  "Your answer shows against your swimmer's name. If it does not, it "
                  "did not save."))

questions = [
    ("Do we have to answer every meet on the list?",
     "Yes, either way. Nobody is expected at every meet, and a Decline is a perfectly "
     "good answer. What we cannot work with is no answer at all."),
    ("What happens if we do not answer?",
     "We build each entry from the swimmers who have confirmed, so a meet with no "
     "answer is not entered. Please answer either way. Declining takes a moment and it "
     "is the right answer when your swimmer cannot make it."),
    ("Can we change a Decline back to a Confirm?",
     "Yes, any time before the Confirm By date. Neither answer is locked in until "
     "then, so answer early and change it if you need to."),
    ("We missed the deadline. Can our swimmer still race?",
     "Ask your swimmer's coach. Sometimes a late entry is possible and sometimes it is "
     "not, and they will know quickly either way."),
    ("We confirmed and now cannot go. What should we do?",
     "Change it to Decline if the Confirm By date has not passed. After that date, tell "
     "your coach as soon as you know, so they can adjust relays and the meet sheet. The "
     "entry fee cannot be refunded."),
    ("A meet is marked " + R.pill("Coach Decision", "#5C6B2F") + ". What does that mean?",
     "Your coach chooses who is invited to that one. If it is on your swimmer's list, they "
     "have been invited, so confirm or decline exactly as you would for any other meet."),
    ("Our swimmer needs a qualifying time for a meet. Do we still answer?",
     "Yes. Confirm if you would like them to race and your coach will tell you whether "
     "they have the time. Meets that need one are marked "
     + R.pill("Qualifiers Only", R.FLAG) + " on the schedule."),
    ("We have two swimmers in different groups. Do we answer twice?",
     "Yes, once for each swimmer. Their groups may be going to different meets, so the "
     "lists will not always match."),
    ("We cannot get into our member account.",
     "Email the club office and we will sort it out. Do not let a sign-in problem run "
     "past a Confirm By date, and tell us before the deadline rather than after."),
]

page = R.wrap(
    R.hero("ROW Swim Club", "Confirm or Decline",
           "Every meet and event on your swimmer's list needs an answer. Here is what "
           "each answer does, and how to give one."),
    R.lanes(),

    R.h2("Confirming is how your swimmer gets entered"),
    R.p("We build every entry from the swimmers who have confirmed. So each meet and "
        "event needs one of two answers from you."),
    answers,
    R.note("<strong>Declining is not a letdown.</strong> It is the right answer when "
           "your swimmer cannot make a meet, it takes a moment, and it tells their "
           "coach what to plan for."),

    R.h2("You can change your mind, until the deadline"),
    R.card(
        R.p("Either answer can be changed as often as you like <strong>up to the "
            "Confirm By date</strong>. Confirmed and then something came up? Change it "
            "to Decline. Declined and the weekend freed up? Change it to Confirm.")
        + R.p("On the Confirm By date the confirmation page closes. After that we "
              "submit the entry, and the club pays for every swimmer on it. That is "
              "why a change after the deadline cannot be undone or refunded.")),
    R.callout("<strong>Where to find the deadline.</strong> Every meet and event on the "
              "schedule has a <strong>Confirm By</strong> date. Your group's calendar "
              "carries the same dates."),

    R.h2("How to answer"),
    R.p("Three taps from the schedule. You answer in your ROW member account, not by "
        "replying to an email."),
    R.card(steps),
    R.note("No link on the date? That meet has not been set up for confirming yet. "
           "Sign in to your member account, open it from the team events list, and "
           "answer there."),
    R.note("SportsEngine, who run our member accounts, keep a walkthrough with pictures "
           "of every screen. " + R.button("Step by step with pictures", HELP_URL,
                                          alt=True)),

    R.cta("See what needs an answer",
          "Your group's meets and events, each with its Confirm By date.",
          "Open the schedule", SCHEDULE_URL),

    R.h2("Questions"),
    R.faq(questions),
    R.callout("Not sure whether a meet suits your swimmer? Ask their coach on deck. For "
              "anything to do with your account, entries or payments, email the club "
              "office at <strong>office@rowswimming.ca</strong>."),
)

os.makedirs(OUT_DIR, exist_ok=True)
OUT = os.path.join(OUT_DIR, "row_confirm_or_decline_embed.html")
with open(OUT, "w", encoding="utf-8") as f:
    f.write(page)

CSS_OUT = os.path.join(OUT_DIR, "row_confirm_or_decline.css")
with open(CSS_OUT, "w", encoding="utf-8") as f:
    f.write(R.stylesheet(SHARED_CSS))

print(f"wrote {OUT} {len(page):,} chars")
print(f"wrote {CSS_OUT}")
