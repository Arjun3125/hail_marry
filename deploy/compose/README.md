# Compose Assets

Canonical compose files now live here.

- `production.yml`: full stack production-style compose topology
- `demo.yml`: lightweight Class 11 CBSE showcase stack
- `local.yml`: compatibility include for local development
- `staging.yml`: compatibility include for staging rollout work

Current demo deployment contract:

- `APP_ENV=development`
- `DEMO_MODE=true`
- `AUTO_SEED_DEMO_DATA=true` on the API service
- strong and different `JWT_SECRET` and `REFRESH_SECRET_KEY`
- real `DATABASE_URL` and `REDIS_URL` values for hosted environments

Legacy compatibility copies remain at the repo root:

- `/docker-compose.yml`
- `/docker-compose.demo.yml`

Prefer `deploy/compose/*.yml` for new deployment work.
