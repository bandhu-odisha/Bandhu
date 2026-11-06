# Rough idea — Jan 2015 special Ankurayan

Original request (2026-11-06): a 2015 Ankurayan already exists (Dec 17–20, 2015). A special Jan 2015 Ankurayan must also show. Generate 5 approaches from smallest change to most maintainable with break risk, via /lateral, shown in Lavish.

## Questions I asked (recorded by the orchestrator; only `A:` lines are the user's words)

Q1a/Q1b (Lavish page `.lavish/ankurayan-jan2015.html`): Q1a "1. Which approach?" Options:
- A — section inside Dec 2015 (no code; admin click path)
- B — chip only (hand-made link in the year strip)
- C — second row, URL piece (slug) is the ID
- D ★ — C plus display label (own page, reads "Jan 2015")
- E — full rework (entries, not years)
Q1b "2. Also add the year-strip chip (B)?" (only matters with A)
A: "Ankurayan Jan 2015 pick: approach D; add year-strip chip (B): yes"
Meaning: build approach D. The chip comes from D's own year-strip entry (labelled via display_label); no hand-made link.

Q2a/Q2b (user, chat): "show me the mock before implementing" → mock page `.lavish/ankurayan-jan2015-mock.html` with real-site screenshots.
Question: Q2a "1. How should the old 2015 chip read?" Options: Option 2 ★ "Dec 2015" + "Jan 2015" (both rows get a label; Dec label is data set in /admin/); Option 1 "2015" + "Jan 2015" (old chip unchanged). Q2b "2. Go ahead and build it?" Options: build approach D as shown / change the mock first.
A: "Ankurayan Jan 2015 mock: chip labels = "Dec 2015" + "Jan 2015"; decision = build approach D"
A: "build using /dev-workflow"
Meaning: build D. The "Dec 2015" label is a data entry (label field on the existing 2015 row) done by the user in /admin/ after deploy; no data migration.

Q3 (user, chat): A: "Confirm there will be no regression to the existing website"
Meaning: acceptance adds a rendered-page regression check: with no label set on any row, every existing Ankurayan page (list + all detail pages, anonymous and admin) renders identical HTML before and after the change.

## Follow-ups (2026-11-06)
A: "build using /dev-workflow" → dev-workflow ran /re-construct DONE/planning/2026-11-06-ankurayan-jan-2015-special/plan.md (Reconstruct Gate).
