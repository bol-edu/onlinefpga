#!/bin/bash
echo hls00-passwd | sudo -S rm -rf "/opt/labManageKit/backupdb/$(date +"%Y-%m-%d")"
echo hls00-passwd | sudo -S mkdir "/opt/labManageKit/backupdb/$(date +"%Y-%m-%d")"
echo hls00-passwd | sudo -S cp -rf /mnt/LabData/hls00/boledudb "/opt/labManageKit/backupdb/$(date +"%Y-%m-%d")"
sleep 10
docker rm -f boledudb
docker run -v /mnt/LabData/hls00/boledudb/:/data/db --name boledudb -d mongo
