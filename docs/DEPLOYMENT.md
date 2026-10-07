# Production Deployment

KhasiLex ships as an OCI-compatible container. The application itself is provider-neutral.

## Required runtime configuration

Set:

```text
KHASILEX_ENV=production
```

Recommended baseline:

```text
KHASILEX_RATE_LIMIT_PER_MINUTE=120
KHASILEX_MAX_BODY_BYTES=65536
```

Public production traffic must terminate through HTTPS. The platform or edge gateway should additionally provide DDoS protection, access logs, health monitoring and horizontally consistent rate limiting.

## Health endpoints

- `GET /health` — liveness
- `GET /ready` — lexicon readiness

## Container hardening

The production image:

- runs as an unprivileged `khasilex` user;
- has an image-level health check;
- defaults to `KHASILEX_ENV=production`;
- can be run read-only with all Linux capabilities dropped using `docker-compose.production.yml`.

## Container publication

The repository contains a gated workflow for publishing an image to GitHub Container Registry. Publication is blocked unless the requested lexical release target passes the release-readiness gate, including the explicit linguistic-data licence decision.

## Host selection

Actual production deployment remains a separate environment decision. Any host that can run the OCI image is suitable, including managed container services and Kubernetes.

Before declaring Gate 6 complete, record:

- production host/provider;
- service/project identifier;
- HTTPS domain;
- deployment identity/credentials mechanism;
- rollback procedure;
- external monitoring/alerting;
- backup/recovery policy.

No production credential should be committed to the repository.
