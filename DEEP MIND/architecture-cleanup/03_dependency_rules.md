# Dependency Rules

## Mandatory direction

- `interfaces -> application -> domain`
- `bootstrap -> interfaces + infrastructure`
- `infrastructure` is accessed through orchestrators/adapters, not from pure domain code

## Forbidden patterns

- route-to-route imports
- route imports inside services
- FastAPI imports inside future `domain/` packages
- provider SDK imports inside future `domain/` packages
- new `sys.path` hacks in app code

