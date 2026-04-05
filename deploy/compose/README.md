# Compose Assets

Canonical compose files now live here.

- `production.yml`: full stack production-style compose topology
- `demo.yml`: lightweight Class 11 CBSE showcase stack
- `local.yml`: compatibility include for local development
- `staging.yml`: compatibility include for staging rollout work

Legacy compatibility copies remain at the repo root:

- `/docker-compose.yml`
- `/docker-compose.demo.yml`

Prefer `deploy/compose/*.yml` for new deployment work.
