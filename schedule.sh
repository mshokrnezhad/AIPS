#!/bin/bash
# Schedule AIPS to run in a specific folder
# Usage: ./schedule.sh FOLDER_PATH HOUR MINUTE

if [ $# -ne 3 ]; then
    echo "Usage: ./schedule.sh FOLDER_PATH HOUR MINUTE"
    echo ""
    echo "Examples:"
    echo "  ./schedule.sh /home/masoud/Desktop/AIPS 9 0    # 9:00 AM daily"
    echo "  ./schedule.sh /home/masoud/project-a 14 30     # 2:30 PM daily"
    exit 1
fi

FOLDER="$1"
HOUR="$2"
MINUTE="$3"
AIPS_CMD="/home/masoud/.local/bin/aips"
LOG_FILE="$FOLDER/aips.log"

# Validate folder exists
if [ ! -d "$FOLDER" ]; then
    echo "❌ Error: Folder $FOLDER does not exist"
    exit 1
fi

# Validate hour (0-23)
if [ "$HOUR" -lt 0 ] || [ "$HOUR" -gt 23 ]; then
    echo "❌ Error: Hour must be between 0-23"
    exit 1
fi

# Validate minute (0-59)
if [ "$MINUTE" -lt 0 ] || [ "$MINUTE" -gt 59 ]; then
    echo "❌ Error: Minute must be between 0-59"
    exit 1
fi

# Create cron job entry
CRON_ENTRY="$MINUTE $HOUR * * * cd $FOLDER && $AIPS_CMD >> $LOG_FILE 2>&1"

echo "📅 Scheduling AIPS"
echo "=================="
echo "Folder: $FOLDER"
echo "Time: $HOUR:$(printf "%02d" $MINUTE) daily"
echo "Log: $LOG_FILE"
echo ""

# Check if this exact entry already exists
if crontab -l 2>/dev/null | grep -F "$FOLDER && $AIPS_CMD" > /dev/null; then
    echo "⚠️  A cron job for this folder already exists!"
    echo ""
    crontab -l | grep -F "$FOLDER && $AIPS_CMD"
    echo ""
    read -p "Replace it? (y/N) " -n 1 -r
    echo
    if [[ ! $REPLY =~ ^[Yy]$ ]]; then
        exit 1
    fi
    # Remove old entry
    crontab -l | grep -vF "$FOLDER && $AIPS_CMD" | crontab -
fi

# Add new cron job
(crontab -l 2>/dev/null; echo "$CRON_ENTRY") | crontab -

echo "✅ Scheduled successfully!"
echo ""
echo "Cron entry:"
echo "  $CRON_ENTRY"
echo ""
echo "View all scheduled jobs:"
echo "  crontab -l"
echo ""
echo "View logs:"
echo "  tail -f $LOG_FILE"
echo ""
