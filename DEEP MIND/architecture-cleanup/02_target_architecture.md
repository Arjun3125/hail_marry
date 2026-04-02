# Target Architecture

```text
backend/
  src/
    bootstrap/
    domains/
      */domain/
      */application/
    infrastructure/
    interfaces/
    shared/
```

## Current migration default

- keep bounded contexts
- add `application` services first
- migrate interfaces before deep domain/entity refactors
- keep `src.*` import root during cleanup

