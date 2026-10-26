#!/bin/bash
# usage: ./check_ssh_connection.sh [lines]   (default: last 500 lines of the auth log)
AUTH_LOG=${AUTH_LOG:-/var/log/auth.log}
LINES=${1:-500}
tail -n "$LINES" "$AUTH_LOG" | grep -E 'sshd(-session)?\[[0-9]+\]: (Accepted|Failed|Invalid user)|pam_unix\(sshd:session\)'
