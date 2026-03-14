#!/bin/bash
# Update landing page numbers from ClickHouse and push to GitHub.
# Designed for 3-hour cron on 9975WX.
#
# Usage: publish_landing.sh
# Cron:  50 */3 * * * SSH_AUTH_SOCK=/run/user/1000/ssh-agent.sock /mnt/ai-stack/ionis-ai/ionis-docs/scripts/publish_landing.sh 2>&1 | logger -t landing-update

set -euo pipefail

REPO_DIR="/mnt/ai-stack/ionis-ai/ionis-docs"
VENV="/mnt/ai-stack/ionis-ai/.venv/bin/python"
SCRIPT="${REPO_DIR}/scripts/update_landing.py"

cd "$REPO_DIR"

# Pull latest (in case Watson pushed changes)
git pull --quiet

# Update numbers from ClickHouse
"$VENV" "$SCRIPT"

# Only commit+push if there are actual changes
if git diff --quiet overrides/home.html; then
    echo "No changes to landing page."
    exit 0
fi

git add overrides/home.html
git commit --quiet -m "Auto-update landing page numbers $(date -u +'%Y-%m-%d %H:%MZ')"
git push --quiet

echo "Landing page updated and pushed."
