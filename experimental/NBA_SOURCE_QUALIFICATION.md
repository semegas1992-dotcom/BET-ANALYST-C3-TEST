# C3.340–349 — NBA source qualification
Date: 2026-11-24
Scope: personal experimental analysis, zero paid API budget.

| Source | Decision | Evidence |
|---|---|---|
| BALLDONTLIE | Existing experimental collection; provider permission documented; third-party rights and external accuracy unresolved | https://www.balldontlie.io/terms.html (2026-10-20, sections 6,8,11); https://docs.balldontlie.io/ |
| DunkAPI | Candidate only; no authenticated test or account created | https://dunkapi.com/pricing ; https://dunkapi.com/terms ; https://dunkapi.com/ |
| NBA official injury report | Public reference; no automated ingestion approved | https://www.nba.com/players/injury-report ; https://www.nba.com/termsofuse |
| nba_api / NBA Stats | Do not integrate pending applicable permissions | https://github.com/swar/nba_api ; https://www.nba.com/termsofuse |
| Sports Reference | Manual reference candidate; automated use not qualified | https://www.sports-reference.com/data_use.html |
| Sportradar | Sustainable zero-cost access unconfirmed | https://developer.sportradar.com/basketball/docs/nba-ig-rosters |

DunkAPI published free allowance: 500 credits/month, injury request 2, player stats request 5. Example budget 60 injury calls + 60 player stats calls = 420 credits; reserve 80. This is planning only; actual query granularity and coverage untested. Daily refresh is insufficient for last-minute status. No odds endpoints required.

Gates: authenticate only after user creates a free account if necessary; verify endpoint schema, coverage, timestamps, identity mapping, missing-status behavior, quota and third-party terms; avoid raw export of DunkAPI datasets; no automatic promotion of any data. Unknown player availability must remain unknown. Keep engine_access=false and publication blocked. No KRAFT edits. No automated retrieval from NBA sites authorized by this memo.

Status: documentary qualification completed; runtime qualification and external verification pending. No charges or new credentials.
