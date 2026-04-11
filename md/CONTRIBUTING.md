# Contributing to VidyaOS

Thanks for your interest in contributing. This repo is early-stage and evolving quickly, so we keep the process lightweight.

## Basics
- Use small, focused PRs.
- Match the existing code style in each file.
- Keep changes scoped to the problem you are solving.

## Local Setup (TL;DR)
```bash
cp .env.example .env
docker compose up -d postgres redis
cd backend && pip install -r requirements.txt
cd frontend && npm install
```

## Testing
- Backend: `cd backend && python -m pytest -q`
- Frontend lint: `cd frontend && npm run lint`
- Frontend build: `cd frontend && npm run build`

## What to Include in a PR
- Clear description of the problem and solution.
- Tests when practical.
- Any doc updates needed to keep status accurate.

## Security
If you find a security issue, do **not** open a public issue. Share details privately with the repo owner.
