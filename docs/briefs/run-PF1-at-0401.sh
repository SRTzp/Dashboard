#!/bin/bash
# Starts Claude Code on the PF1 brief at 04:01 local time (after the 04:00 usage reset).
# Run in Terminal:  bash ~/Documents/Dashboard/docs/briefs/run-PF1-at-0401.sh
# Keep the Mac plugged in, lid open, and this Terminal window open.
cd /Users/peach/Documents/Dashboard || { echo "Dashboard folder not found"; exit 1; }
now=$(date +%s)
target=$(date -v4H -v1M -v0S +%s)
[ "$target" -le "$now" ] && target=$((target + 86400))
echo "Claude Code will start at: $(date -r "$target")  (in $(( (target-now)/60 )) min). Leave this window open."
caffeinate -i -s sleep $((target - now))
exec caffeinate -i -s claude --permission-mode auto "$(cat docs/briefs/PF1-run-prompt.txt)"
