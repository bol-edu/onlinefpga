#!/bin/sh
sshpass -p "hls01-passwd" scp -P 1100 -o StrictHostKeyChecking=no ./config.py hls01@192.168.1.11:/opt/labManageKit/
sshpass -p "hls01-passwd" scp -P 1100 -o StrictHostKeyChecking=no ./manage_user.py hls01@192.168.1.11:/opt/labManageKit/
sshpass -p "hls01-passwd" scp -P 1100 -o StrictHostKeyChecking=no ./job_grabber.py hls01@192.168.1.11:/opt/labManageKit/
sshpass -p "hls01-passwd" scp -P 1100 -o StrictHostKeyChecking=no ./u50_tenant_util.py hls01@192.168.1.11:/opt/labManageKit/

sshpass -p "hls02-passwd" scp -P 1200 -o StrictHostKeyChecking=no ./config.py hls02@192.168.1.12:/opt/labManageKit/
sshpass -p "hls02-passwd" scp -P 1200 -o StrictHostKeyChecking=no ./manage_user.py hls02@192.168.1.12:/opt/labManageKit/
sshpass -p "hls02-passwd" scp -P 1200 -o StrictHostKeyChecking=no ./job_grabber.py hls02@192.168.1.12:/opt/labManageKit/
sshpass -p "hls02-passwd" scp -P 1200 -o StrictHostKeyChecking=no ./u50_tenant_util.py hls02@192.168.1.12:/opt/labManageKit/

sshpass -p "hls03-passwd" scp -P 1300 -o StrictHostKeyChecking=no ./config.py hls03@192.168.1.13:/opt/labManageKit/
sshpass -p "hls03-passwd" scp -P 1300 -o StrictHostKeyChecking=no ./manage_user.py hls03@192.168.1.13:/opt/labManageKit/
sshpass -p "hls03-passwd" scp -P 1300 -o StrictHostKeyChecking=no ./job_grabber.py hls03@192.168.1.13:/opt/labManageKit/
sshpass -p "hls03-passwd" scp -P 1300 -o StrictHostKeyChecking=no ./u50_tenant_util.py hls03@192.168.1.13:/opt/labManageKit/

sshpass -p "hls04-passwd" scp -P 1400 -o StrictHostKeyChecking=no ./config.py hls04@192.168.1.14:/opt/labManageKit/
sshpass -p "hls04-passwd" scp -P 1400 -o StrictHostKeyChecking=no ./manage_user.py hls04@192.168.1.14:/opt/labManageKit/
sshpass -p "hls04-passwd" scp -P 1400 -o StrictHostKeyChecking=no ./job_grabber.py hls04@192.168.1.14:/opt/labManageKit/
sshpass -p "hls04-passwd" scp -P 1400 -o StrictHostKeyChecking=no ./u50_tenant_util.py hls04@192.168.1.14:/opt/labManageKit/

sshpass -p "hls05-passwd" scp -P 1500 -o StrictHostKeyChecking=no ./config.py hls05@192.168.1.15:/opt/labManageKit/
sshpass -p "hls05-passwd" scp -P 1500 -o StrictHostKeyChecking=no ./manage_user.py hls05@192.168.1.15:/opt/labManageKit/
sshpass -p "hls05-passwd" scp -P 1500 -o StrictHostKeyChecking=no ./job_grabber.py hls05@192.168.1.15:/opt/labManageKit/
sshpass -p "hls05-passwd" scp -P 1500 -o StrictHostKeyChecking=no ./u50_tenant_util.py hls05@192.168.1.15:/opt/labManageKit/

echo "synchronize config.py manage_user.py job_grabber.py u50_tenant_util.py to HLS01~HLS05 clients"

