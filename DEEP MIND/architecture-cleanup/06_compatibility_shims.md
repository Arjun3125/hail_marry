# Compatibility Shims

## Temporary shims allowed

- `backend/config.py` remains public while loading from new root `config/`
- legacy route locations remain valid while new interface packages are introduced
- backend-local YAML files remain fallback sources during migration

## Removal conditions

- all runtime entrypoints load from new config root
- scripts/tests no longer depend on direct path hacks
- moved interfaces are imported only from cleaned package locations

