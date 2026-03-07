# Backup and Recovery Policy

**Project:** VidyaOS – AI Infrastructure for Educational Institutions  
**Version:** v0.1  
**Applies To:** ERP Database + AI Vector Store + Configuration

---

## 1. Backup Schedule

| Asset | Method | Frequency | Time |
|---|---|---|---|
| PostgreSQL database | `pg_dump` (compressed) | Daily | 02:00 IST |
| Vector DB (FAISS/Qdrant) | File snapshot | Every 24h | 03:00 IST |
| Configuration files | Git commit | On change | Continuous |
| Application logs | Log rotation | Daily | 00:00 IST |

---

## 2. Storage Locations

| Backup Type | Primary Storage | Offsite Storage |
|---|---|---|
| Database dumps | Local server `/backups/` | S3-compatible cloud (Backblaze B2 / AWS S3) |
| Vector DB snapshots | Secondary local drive | S3-compatible cloud |
| Config & infra files | Git repository | GitHub (private repo) |
| Log archives | Local log directory | S3 (optional) |

**Rule:** No backup exists in only one location. At least one copy must be offsite.

---

## 3. Retention Period

| Asset | Retention |
|---|---|
| Daily database dumps | 30 days |
| Vector DB snapshots | 14 days |
| Configuration history | Permanent (Git) |
| Log archives | 7 days (local), 30 days (offsite) |

Older backups auto-deleted by cleanup cron job.

---

## 4. Backup Encryption

- All offsite backups encrypted using `gpg` or `age` before upload
- Encryption keys stored separately from backups
- Key documented in secure password manager (not in repo)

---

## 5. Restore Procedure

### 5.1 PostgreSQL Restore

```bash
# 1. Stop the API service
sudo systemctl stop vidyaos-api

# 2. Drop and recreate database
psql -U postgres -c "DROP DATABASE vidyaos_prod;"
psql -U postgres -c "CREATE DATABASE vidyaos_prod;"

# 3. Restore from backup
gunzip -c /backups/vidyaos_2026-03-02.sql.gz | psql -U postgres -d vidyaos_prod

# 4. Restart API service
sudo systemctl start vidyaos-api

# 5. Verify data integrity
python scripts/verify_restore.py
```

### 5.2 Vector DB Restore

```bash
# 1. Stop AI service
sudo systemctl stop vidyaos-ai

# 2. Remove current vector data
rm -rf /data/vector_db/*

# 3. Restore from snapshot
cp -r /backups/vector_db_2026-03-02/* /data/vector_db/

# 4. Restart AI service
sudo systemctl start vidyaos-ai
```

---

## 6. Restore Testing

**Frequency:** Weekly (every Sunday at 04:00 IST)

**Process:**
1. Spin up isolated test database
2. Restore latest backup into test DB
3. Run data integrity checks (row counts, foreign key consistency)
4. Run sample API queries against restored data
5. Log results to restore test report

**Rule:** If restore test fails, alert team immediately. Do not wait.

---

## 7. Emergency Rollback Plan

If a deployment causes data issues:

1. **Identify** — detect the problem (monitoring alerts, user reports)
2. **Freeze** — stop all write operations (maintenance mode)
3. **Restore** — roll back database to pre-deployment backup
4. **Revert** — redeploy previous application version
5. **Validate** — run smoke tests against restored system
6. **Communicate** — notify affected tenants
7. **Post-mortem** — document what went wrong and prevention

**RTO (Recovery Time Objective):** < 1 hour  
**RPO (Recovery Point Objective):** < 24 hours (daily backup)

---

## 8. Responsibility Matrix

| Action | Owner |
|---|---|
| Backup automation setup | DevOps / Infrastructure |
| Weekly restore testing | DevOps |
| Encryption key management | Security Lead |
| Emergency rollback execution | On-call Engineer |
| Post-mortem documentation | Engineering Lead |
