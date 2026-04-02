# Docker Assets

Canonical Docker image definitions now live here.

- `backend.Dockerfile`: production backend image
- `worker.Dockerfile`: background worker image
- `frontend.Dockerfile`: production frontend image
- `demo.Dockerfile`: demo backend image
- `frontend.demo.Dockerfile`: demo frontend image

Legacy compatibility copies still remain at the repo root and in feature folders:

- `/Dockerfile.production`
- `/Dockerfile.demo`
- `/backend/Dockerfile.worker`
- `/frontend/Dockerfile`
- `/frontend/Dockerfile.demo`

Prefer the files in `deploy/docker/` for new deployment work.
