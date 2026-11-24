# DunkAPI experimental qualification

Free account only: https://dunkapi.com/signup. Verify email and create a key. Never paste key into chat or source. Use GitHub Actions secret DUNKAPI_API_KEY for a future explicitly approved manual workflow. No live workflow is enabled and no account is created by this branch.

Run offline tests: python -m unittest discover -s experimental -v

The adapter reserves credits in a persistent SQLite database before each call, rolling 31-day cap 392. This is only a local safeguard, not an account balance check. Do not delete/reset the database or use multiple independent databases or clients. No wallet top-ups or paid subscriptions. Free allowance is replenished around signup anniversary after email verification; 500 is not guaranteed available at each call. No automatic retries. No odds endpoints. No scheduled requests. No raw data exports. Current adapter returns metadata only, not a usable player dataset.

Next: authenticated single global injury request (2 credits), inspect schema privately, confirm team and player ID mapping via reference lookups, verify data timing and provider rights. No injury publication timestamp is supplied; absence from list is unknown. Player profile response may include later games, so no historical pre-match integration until temporal filtering validated. BALLDONTLIE start-year season 2026 maps to DunkAPI end-year 2027. No automatic mapping of provider IDs. No engine access. No change to KRAFT.

Sources: https://dunkapi.com/docs ; https://dunkapi.com/docs/get-injuries ; https://dunkapi.com/docs/get-player ; https://dunkapi.com/docs/timing-and-rights ; https://dunkapi.com/pricing ; https://dunkapi.com/terms .

Status: adapter and 12 offline tests committed, CI execution pending, live qualification blocked on credentials and explicit manual invocation. No account costs authorized.
