# Bug Log

Bugs found during development, how they were fixed, and the test that guards against regression.

| # | Found | Bug | Fix | Regression test |
|---|-------|-----|-----|-----------------|
| 1 | Phase 3 styling | Masked words of 8+ letters wrapped onto two lines (`word-break: break-all` on a spaced pattern). | `white-space: nowrap`, smaller responsive font size and letter spacing in `.pattern`. | `test_browser.py::test_long_word_stays_on_one_line_without_page_scroll` |
| 2 | Phase 3 styling | "Wrong letters" showed `NONE` (uppercase transform applied to the placeholder text). | Placeholder changed to "—". | Visual check |
| 3 | Phase 4 | Unexpected server exceptions returned Flask's HTML error page instead of JSON. | Catch-all error handler logs the traceback and returns `{"error": "internal server error"}` (500) for `/api/` routes. | `test_api.py::test_unexpected_error_returns_json_500` |
| 4 | Phase 4 | No limit on request body size. | `MAX_CONTENT_LENGTH` = 16 KB; oversized bodies get a JSON 413. | `test_api.py::test_oversized_body_rejected` |
| 5 | Phase 4 (test bug) | Browser test helper waited for a key to become disabled, but all keys are disabled while a request is in flight, so it returned too early (flaky). | Wait for the key's `correct`/`incorrect` class instead. | `test_browser.py` (ran 3× clean) |
