# Docker Assets

The canonical runtime contract is:

- API: `/backend/Dockerfile` with repo-root build context
- Worker: `/backend/Dockerfile.worker` with repo-root build context
- Frontend: `/frontend/Dockerfile` with `frontend/` build context
- Demo backend: `/deploy/docker/demo.Dockerfile` with repo-root build context
- Demo frontend: `/deploy/docker/frontend.demo.Dockerfile` with repo-root build context

Railway production backend services should use config-as-code:

- API service -> `/railway.toml` -> `backend/Dockerfile` -> `sh /app/backend/start-api.sh` -> healthcheck `/ready`
- Worker service -> `/backend/railway.toml` -> `backend/Dockerfile.worker` -> `sh /app/backend/start-worker.sh` -> healthcheck `/ready`

Required backend envs for non-local deploys:

- `DATABASE_URL`
- `REDIS_URL`
- `JWT_SECRET`
- `REFRESH_SECRET_KEY`

Hosted demo backend envs:

- `APP_ENV=development`
- `DEMO_MODE=true`
- `AUTO_SEED_DEMO_DATA=true` on the API service
- `AUTO_SEED_DEMO_DATA=false` on the worker service

Worker note:

- the worker health app now binds to Railway's assigned `PORT` by default

Do not rely on:

- Dockerfile auto-detection
- custom Railway start commands
- demo Dockerfiles for production services

Legacy compatibility shims remain temporarily at:

- `/Dockerfile.production`
- `/Dockerfile.demo`
- `/frontend/Dockerfile.demo`
- `/deploy/docker/backend.Dockerfile`
- `/deploy/docker/worker.Dockerfile`
- `/deploy/docker/frontend.Dockerfile`

Use the canonical files listed at the top for all new production and demo work.
