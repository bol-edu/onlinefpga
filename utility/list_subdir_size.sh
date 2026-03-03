#!/bin/bash
echo Input parent dir of subdirs to calculate size :
read vardir
if [ -d "$vardir" ]; then
  sudo du -hDaxd1 $vardir | sort -h | tail -n15
else
  echo "Error: ${vardir} not found."
  exit 1
fi  
