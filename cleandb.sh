#!/bin/bash
KEEP_BACKUPS=28

BACKUP_DIRS=(
    "/opt/labManageKit/backupdb"
    "/mnt/HLSNAS/backupdb"
)

for BACKUP_PATH in "${BACKUP_DIRS[@]}"; do
    if [ -d "$BACKUP_PATH" ]; then
        cd "$BACKUP_PATH" || exit 1
        dirs=$(ls -1d [0-9]* | sort | head -n -$((KEEP_BACKUPS - 1)))
        if [ -n "$dirs" ]; then
            for dir in $dirs; do
                echo "正在刪除 $BACKUP_PATH/$dir"
                echo boleduhls00 | sudo -S rm -rf "$dir"
            done
        else
            echo "$BACKUP_PATH 無需刪除的備份"
        fi
    else
        echo "目錄 $BACKUP_PATH 不存在，跳過..."
    fi
done

