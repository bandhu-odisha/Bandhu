reconstruct: ran 2026-10-29 sha=3974cc638c379fc2
acceptance: python manage.py test 2>err.log >/dev/null; tail -5 err.log  → must show "Ran 762 tests" and "OK (expected failures=10)", exit 0; plus chrome-devtools E2E asserts in spec.md B1–B3 (record in e2e.md)
baseline: da779713dac9adbc625fb75d1b315d13eae7417b
wave check: 1 unit (A1/B1-B3/C1 share ankurayan.html + ankurayan.css) → sequential
layout gate: Q1 previews were hand-built ASCII mocks, not real-app captures; user picked from them in planning. Not re-run; noted in report.
reconstruct: correction lane 2026-10-29 (Q2 arrows→match Gallery; B1,B3 rewritten; Gallery.jsx:128-151 quoted) sha=cc3e1a736f03a681
phase1: done HEAD=da77971 2026-10-29T14:29:21
phase2 r1: NEEDS_CHANGES (opus I1+M1-M5, fable I1+M1-M3)
phase2 r2: APPROVED; end fable APPROVED; acceptance worktree Ran 762 OK rc=0; phase5 done 2026-10-29T14:40:15
