---
name: backup-sync
description: Automated backup and synchronization solutions for files, databases, and configurations. Use when setting up backup systems, syncing data across locations, or implementing disaster recovery.
---

# Backup & Synchronization

Automated backup and sync solutions for files, databases, and configurations.

## When to Use

- Automated file backups
- Database backups
- Cloud synchronization
- Disaster recovery planning
- Version control for configs
- Cross-device sync
- Offsite backup

## File Backup Solutions

### rsync (Local/Remote)

```bash
# Local backup
rsync -av --delete /source/ /backup/

# Remote backup (SSH)
rsync -avz --delete /source/ user@remote:/backup/

# With compression and progress
rsync -avzh --progress --delete /source/ /backup/

# Exclude patterns
rsync -av --exclude='*.tmp' --exclude='.git' /source/ /backup/
```

### Automated Backup Script

```bash
#!/bin/bash
# backup.sh

SOURCE="/Volumes/SharedData"
BACKUP_DIR="/Volumes/BackupDrive"
DATE=$(date +%Y-%m-%d_%H-%M-%S)

# Create backup
rsync -avzh --delete \
  --exclude='*.tmp' \
  --exclude='.DS_Store' \
  "$SOURCE/" \
  "$BACKUP_DIR/backup_$DATE/"

# Keep only last 7 backups
find "$BACKUP_DIR" -type d -name "backup_*" | \
  sort -r | \
  tail -n +8 | \
  xargs rm -rf

echo "Backup completed: backup_$DATE"
```

### Cron Job (Daily at 2 AM)

```bash
# Edit crontab
crontab -e

# Add line
0 2 * * * /path/to/backup.sh >> /var/log/backup.log 2>&1
```

## Cloud Backup

### rclone (Cloud Storage)

```bash
# Install
brew install rclone

# Configure
rclone config

# Sync to Google Drive
rclone sync /source remote:backup --progress

# Sync to S3
rclone sync /source s3:bucket/backup --progress

# Encrypted backup
rclone sync /source remote:encrypted \
  --crypt-remote remote:crypt \
  --crypt-password your_password
```

### Backblaze B2

```bash
# Install
pip install b2

# Authorize
b2 authorize_account APPLICATION_KEY_ID APPLICATION_KEY

# Create bucket
b2 create_bucket my-backup-bucket allPrivate

# Upload
b2 sync /source b2://my-backup-bucket/backup
```

## Database Backups

### PostgreSQL

```bash
# Full backup
pg_dump -U postgres mydb > backup_$(date +%Y%m%d).sql

# Compressed backup
pg_dump -U postgres mydb | gzip > backup_$(date +%Y%m%d).sql.gz

# Restore
psql -U postgres mydb < backup_20260305.sql

# Automated script
#!/bin/bash
DB_NAME="skillsdb"
BACKUP_DIR="/backups/postgres"
DATE=$(date +%Y%m%d_%H%M%S)

pg_dump -U postgres "$DB_NAME" | gzip > "$BACKUP_DIR/$DB_NAME_$DATE.sql.gz"

# Keep 30 days
find "$BACKUP_DIR" -name "*.sql.gz" -mtime +30 -delete
```

### SQLite

```bash
# Backup
cp database.db database_$(date +%Y%m%d).db.backup

# With compression
sqlite3 database.db ".backup 'backup_$(date +%Y%m%d).db'"
gzip backup_20260305.db
```

## Synchronization

### Bidirectional Sync (Syncthing)

```bash
# Install
brew install syncthing

# Start
syncthing

# Access web UI
open http://localhost:8384
```

### One-Way Sync (Unison)

```bash
# Install
brew install unison

# Sync
unison /source /destination -batch

# With profile
unison myprofile -batch
```

## Version Control Backups

### Git for Configs

```bash
# Initialize repo
cd ~/.openclaw/workspace
git init

# Add files
git add .

# Commit
git commit -m "Backup $(date)"

# Push to remote
git push origin main

# Automated commit script
#!/bin/bash
cd ~/.openclaw/workspace
git add .
git commit -m "Auto-backup $(date '+%Y-%m-%d %H:%M')"
git push origin main
```

## Disaster Recovery Plan

### Backup Strategy (3-2-1 Rule)

- **3** copies of data
- **2** different media types
- **1** offsite location

### Example Setup

```
Primary: /Volumes/SharedData (working files)
Local Backup 1: /Volumes/BackupDrive (rsync daily)
Local Backup 2: Time Machine (hourly)
Offsite: Backblaze B2 (sync daily)
```

### Recovery Testing

```bash
# Monthly test restore
#!/bin/bash
TEST_DIR="/tmp/restore_test"
mkdir -p "$TEST_DIR"

# Restore from backup
rsync -av /Volumes/BackupDrive/backup_latest/ "$TEST_DIR/"

# Verify
diff -r /Volumes/SharedData/important/ "$TEST_DIR/important/"

# Cleanup
rm -rf "$TEST_DIR"
```

## Monitoring

### Backup Health Check

```bash
#!/bin/bash
# check_backups.sh

# Check last backup time
LAST_BACKUP=$(ls -t /Volumes/BackupDrive/backup_* | head -1)
LAST_TIME=$(stat -f %m "$LAST_BACKUP")
NOW=$(date +%s)
AGE=$(( (NOW - LAST_TIME) / 86400 ))

if [ $AGE -gt 2 ]; then
  echo "WARNING: Last backup is $AGE days old"
  exit 1
else
  echo "OK: Last backup is $AGE days old"
  exit 0
fi
```

## Best Practices

1. **Automate everything** - Don't rely on manual backups
2. **Test restores** - Verify backups work
3. **Monitor backups** - Alert on failures
4. **Encrypt sensitive data** - Especially offsite
5. **Version control configs** - Track changes
6. **Document recovery** - Write runbooks
7. **Regular audits** - Check backup integrity

---

*Last Updated: 2026-03-05*  
*Version: 1.0.0*
