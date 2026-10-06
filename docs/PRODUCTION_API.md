# KhasiLex Production API Boundary

KhasiLex separates development/research evidence from authoritative public dictionary data.

## Runtime mode

Set:

```text
KHASILEX_ENV=production
```

for public production deployments.

In production mode:

- `/api/v1/words/{word}` returns only `verified` entries;
- `/api/v1/search` searches only `verified` entries;
- `/api/v1/reduplications` exposes only verified lexicalized reduplications;
- `/api/v1/corpus/entries` rejects requests for non-verified statuses;
- `/api/v2/resolve-to-khasi` refuses attempts to disable verified-only resolution;
- structural reduplication detection remains available, but pending lexical phrase matches are removed from analysis output.

The explicit authoritative endpoint remains available:

```text
/api/v1/authoritative/words/{word}
```

## Operational controls

Production middleware provides:

- per-request IDs;
- structured request logs;
- security headers;
- HSTS;
- declared request-body size enforcement;
- per-instance request-rate limiting;
- `/health` liveness;
- `/ready` lexicon-readiness checks.

Environment controls:

- `KHASILEX_MAX_BODY_BYTES` — default 65536, constrained to 1 KiB–1 MiB;
- `KHASILEX_RATE_LIMIT_PER_MINUTE` — default 120, constrained to 10–10000;
- `KHASILEX_ENABLE_DOCS` — enables API docs in production when explicitly set true.

## Deployment boundary

The in-process rate limiter is a safety backstop, not a substitute for an edge gateway. A horizontally scaled production deployment should also enforce rate limits, TLS, DDoS protection and request-size constraints at the platform/load-balancer layer.

The application never treats reviewed, historical-only, candidate, or AI-generated lexical material as authoritative merely because it exists in repository data.
