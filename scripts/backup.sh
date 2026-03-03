#!/bin/bash
# ─── AIaaS Backup Script ─────────────────────────────
# Daily automated backup for PostgreSQL + Vector DB
# Schedule: cron tab → 0 2 * * * /app/scripts/backup.sh
#
# Usage: ./scripts/backup.sh [--restore <backup_file>]

set -euo pipefail

# ─── Configuration ───────────────────────────
BACKUP_DIR="/backups"
DB_NAME="${POSTGRES_DB:-aiaas}"
DB_USER="${POSTGRES_USER:-postgres}"
VECTOR_DIR="/app/vector_data"
RETENTION_DAYS=30
DATE=$(date +%Y-%m-%d_%H%M)

mkdir -p "$BACKUP_DIR"

# ─── Colors ──────────────────────────────────
GREEN='\033[0;32m'
RED='\033[0;31m'
NC='\033[0m'

log() { echo -e "${GREEN}[BACKUP]${NC} $1"; }
err() { echo -e "${RED}[ERROR]${NC} $1" >&2; }

# ─── Restore Mode ────────────────────────────
if [ "${1:-}" = "--restore" ] && [ -n "${2:-}" ]; then
    RESTORE_FILE="$2"
    if [ ! -f "$RESTORE_FILE" ]; then
        err "Backup file not found: $RESTORE_FILE"
        exit 1
    fi
    log "Restoring database from: $RESTORE_FILE"
    gunzip -c "$RESTORE_FILE" | psql -U "$DB_USER" -d "$DB_NAME"
    log "Restore complete. Run verify_restore.py to validate."
    exit 0
fi

# ─── PostgreSQL Backup ───────────────────────
PG_BACKUP="$BACKUP_DIR/pg_${DB_NAME}_${DATE}.sql.gz"
log "Backing up PostgreSQL → $PG_BACKUP"
pg_dump -U "$DB_USER" "$DB_NAME" | gzip > "$PG_BACKUP"
log "PostgreSQL backup: $(du -h "$PG_BACKUP" | cut -f1)"

# ─── Vector DB Backup ────────────────────────
if [ -d "$VECTOR_DIR" ]; then
    VEC_BACKUP="$BACKUP_DIR/vectors_${DATE}.tar.gz"
    log "Backing up Vector DB → $VEC_BACKUP"
    tar -czf "$VEC_BACKUP" -C "$VECTOR_DIR" .
    log "Vector DB backup: $(du -h "$VEC_BACKUP" | cut -f1)"
else
    log "No vector data directory found, skipping."
fi

# ─── Cleanup Old Backups ─────────────────────
log "Cleaning backups older than ${RETENTION_DAYS} days..."
find "$BACKUP_DIR" -name "pg_*.sql.gz" -mtime +$RETENTION_DAYS -delete 2>/dev/null || true
find "$BACKUP_DIR" -name "vectors_*.tar.gz" -mtime +$RETENTION_DAYS -delete 2>/dev/null || true

# ─── Summary ─────────────────────────────────
BACKUP_COUNT=$(ls -1 "$BACKUP_DIR"/*.gz 2>/dev/null | wc -l)
BACKUP_SIZE=$(du -sh "$BACKUP_DIR" 2>/dev/null | cut -f1)
log "Done! Total backups: $BACKUP_COUNT ($BACKUP_SIZE)"
