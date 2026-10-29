# Rough idea

## Original request (verbatim, 2026-10-29)
Let's apply same to the tiles in individual ankurayana pages like https://bandhuodisha.in/ankurayan/detail/2025/

check the image

(orchestrator note: the attached image was a capture of the live 2025 detail page; the logo card is square and the logo's sides are cut off.)

## Answers (recorded by the orchestrator; only A: lines are the user's words)
Q (orchestrator): On each Ankurayan detail page, the logo card will show the whole logo in its own shape (same as the home page). How should the gallery photo under the schedule handle photos of different shapes? See captures A and B.
Options (orchestrator), with real captures in scratch/detail-{before,A,B}-{1280,390}.png:
- A. Same box, whole photo (Recommended): box stays 4:3; each photo shows in full inside it with a soft tint; box doesn't change size when several photos rotate.
- B. Box takes photo's shape: box grows/shrinks per photo; no tint; box height changes each slide and the page below moves.
- Logo only: only fix the logo card; gallery keeps its 4:3 crop.
A: "A. Same box, whole photo (Recommended)"
Meaning (orchestrator): spec D2 = object-fit contain + tint in the existing 4:3 box; D1 logo natural shape.
