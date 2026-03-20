#!/bin/bash

pushd /opt/labManageKit/

current_time=$(date +%H:%M)
if [[ "$current_time" > "06:00" ]] && [[ "$current_time" < "07:00" ]]; then
     python3 active_monitord.py run_startup &
else
     python3 active_monitord.py run_routine &  
fi

python3 monitord.py
