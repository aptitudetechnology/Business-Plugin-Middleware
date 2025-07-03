#!/bin/bash
# BigCapital Backup Script

set -e

BACKUP_DIR="./backups"
DATE=$(date +%Y%m%d_%H%M%S)

echo "💾 Starting BigCapital backup..."

# Create backup directory
mkdir -p "$BACKUP_DIR"

# Backup MySQL database
echo "📁 Backing up MySQL database..."
docker compose exec -T bigcapital-mariadb mysqldump \
    -u bigcapital \
    -pbigcapital_secure_password \
    --single-transaction \
    --routines \
    --triggers \
    bigcapital > "$BACKUP_DIR/bigcapital-mysql-$DATE.sql"

# Backup MongoDB
echo "📁 Backing up MongoDB..."
docker compose exec -T bigcapital-mongo mongodump \
    --uri="mongodb://bigcapital:bigcapital_mongo_password@localhost:27017/bigcapital" \
    --out="/tmp/backup-$DATE"

# Copy MongoDB backup from container
docker cp "bigcapital-mongo:/tmp/backup-$DATE" "$BACKUP_DIR/bigcapital-mongo-$DATE"

# Backup application volumes
echo "📁 Backing up application data..."
docker run --rm \
    -v bigcapital_uploads:/data/uploads \
    -v bigcapital_storage:/data/storage \
    -v "$(pwd)/$BACKUP_DIR:/backup" \
    alpine tar czf "/backup/bigcapital-volumes-$DATE.tar.gz" -C /data .

# Create backup manifest
echo "📝 Creating backup manifest..."
cat > "$BACKUP_DIR/bigcapital-backup-$DATE.manifest" << EOF
# BigCapital Backup Manifest
# Created: $(date)
# Files:
bigcapital-mysql-$DATE.sql
bigcapital-mongo-$DATE/
bigcapital-volumes-$DATE.tar.gz

# Restore Instructions:
# 1. Stop BigCapital: make down
# 2. Restore MySQL: docker compose exec -T bigcapital-mariadb mysql -u bigcapital -p < bigcapital-mysql-$DATE.sql
# 3. Restore MongoDB: docker compose exec bigcapital-mongo mongorestore --uri="mongodb://bigcapital:password@localhost:27017/bigcapital" bigcapital-mongo-$DATE/bigcapital/
# 4. Restore volumes: docker run --rm -v bigcapital_uploads:/data/uploads -v bigcapital_storage:/data/storage -v "$(pwd)/$BACKUP_DIR:/backup" alpine tar xzf /backup/bigcapital-volumes-$DATE.tar.gz -C /data
# 5. Start BigCapital: make up
EOF

# Cleanup old backups (keep last 7 days)
echo "🧹 Cleaning up old backups..."
find "$BACKUP_DIR" -name "bigcapital-*" -type f -mtime +7 -delete 2>/dev/null || true

echo "✅ Backup completed successfully!"
echo "📁 Backup files saved to: $BACKUP_DIR"
echo "🔍 Backup size: $(du -sh "$BACKUP_DIR/bigcapital-"*"$DATE"* | awk '{total+=$1} END {print total "B"}')"
