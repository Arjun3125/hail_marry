# Deployment Scripts

Canonical deployment scripts now live here.

- `run-demo.sh`: Unix demo launcher
- `run-demo.bat`: Windows demo launcher
- `deploy.sh`: canonical deploy entrypoint placeholder
- `rollback.sh`: canonical rollback entrypoint placeholder
- `smoke-check.sh`: basic smoke verification entrypoint

Legacy compatibility launchers still remain at the repo root:

- `/demo.sh`
- `/demo.bat`

Prefer `deploy/scripts/*` for new deployment and launch work.
