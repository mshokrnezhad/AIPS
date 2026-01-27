#!/bin/bash
# Remove AIPS scheduled jobs
# Usage: ./unschedule.sh [FOLDER_PATH]

AIPS_CMD="/home/masoud/.local/bin/aips"

echo "🗑️  Unscheduling AIPS"
echo "===================="
echo ""

if [ $# -eq 0 ]; then
    # Remove all AIPS cron jobs
    if crontab -l 2>/dev/null | grep -F "$AIPS_CMD" > /dev/null; then
        echo "Current AIPS scheduled jobs:"
        crontab -l | grep -F "$AIPS_CMD"
        echo ""
        read -p "Remove ALL AIPS scheduled jobs? (y/N) " -n 1 -r
        echo
        if [[ $REPLY =~ ^[Yy]$ ]]; then
            crontab -l | grep -vF "$AIPS_CMD" | crontab -
            echo "✅ All AIPS jobs removed"
        else
            echo "Cancelled"
        fi
    else
        echo "⚠️  No AIPS scheduled jobs found"
    fi
else
    # Remove specific folder's job
    FOLDER="$1"
    if crontab -l 2>/dev/null | grep -F "$FOLDER && $AIPS_CMD" > /dev/null; then
        echo "Found scheduled job for: $FOLDER"
        crontab -l | grep -F "$FOLDER && $AIPS_CMD"
        echo ""
        read -p "Remove this job? (y/N) " -n 1 -r
        echo
        if [[ $REPLY =~ ^[Yy]$ ]]; then
            crontab -l | grep -vF "$FOLDER && $AIPS_CMD" | crontab -
            echo "✅ Job removed"
        else
            echo "Cancelled"
        fi
    else
        echo "⚠️  No scheduled job found for: $FOLDER"
    fi
fi

echo ""
