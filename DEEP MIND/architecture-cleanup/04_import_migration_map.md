# Import Migration Map

## Canonical import root during cleanup

- backend runtime code stays on `src.*`

## Migration sequence

1. bootstrap imports extracted from `backend/main.py`
2. route-to-route imports replaced by `application` helpers
3. scripts/tests/Alembic path hacks reduced incrementally
4. new code lands in `application`, `interfaces`, and `infrastructure` packages

