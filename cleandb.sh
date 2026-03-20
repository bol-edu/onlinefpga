#!/bin/bash
KEEP_BACKUPS=28

BACKUP_DIRS=(
    "/mnt/LabData/hls00/backupdb"
)

for BACKUP_PATH in "${BACKUP_DIRS[@]}"; do
    if [ -d "$BACKUP_PATH" ]; then
        cd "$BACKUP_PATH" || exit 1
        dirs=$(ls -1d [0-9]* | sort | head -n -$((KEEP_BACKUPS - 1)))
        if [ -n "$dirs" ]; then
            for dir in $dirs; do
                echo "Deleting $BACKUP_PATH/$dir"
                echo hls00-passwd | sudo -S rm -rf "$dir"
            done
        else
            echo "No backups to delete in $BACKUP_PATH"
        fi
    else
        echo "Directory $BACKUP_PATH not found, skipping..."
    fi
done
