#!/bin/bash
DB_DIR=/mnt/LabData/hls00/boledudb
BACKUP_DIR="/opt/labManageKit/backupdb/$(date +"%Y-%m-%d")"

# after boot, wait up to 5 minutes for the NAS mount and the docker daemon
i=0
until mountpoint -q /mnt/LabData && docker info > /dev/null 2>&1; do
    i=$((i + 1))
    if [ "$i" -ge 60 ]; then
        echo "/mnt/LabData or docker is not ready, skip MongoDB backup and restart"
        exit 1
    fi
    sleep 5
done

echo hls00-passwd | sudo -S rm -rf "$BACKUP_DIR"
echo hls00-passwd | sudo -S mkdir "$BACKUP_DIR"
echo hls00-passwd | sudo -S cp -rf "$DB_DIR" "$BACKUP_DIR"
docker rm -f boledudb
docker run -v "$DB_DIR/":/data/db --name boledudb -d mongo:6.0.1
