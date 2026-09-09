#!/bin/bash
# Update landing page numbers from ClickHouse and push to GitHub.
# Runs on publish-1 (the rendering tier). CH_HOST selects the ClickHouse endpoint.
#
# Usage: publish_landing.sh
# Cron:  50 */3 * * * SSH_AUTH_SOCK=/run/user/1000/ssh-agent.sock /mnt/ai-stack/ionis-ai/ionis-docs/scripts/publish_landing.sh 2>&1 | logger -t landing-update

set -euo pipefail

REPO_DIR="${IONIS_REPO_DIR:-/mnt/ai-stack/ionis-ai/ionis-docs}"
VENV="${IONIS_VENV:-/mnt/ai-stack/ionis-ai/.venv/bin/python}"
SCRIPT="${REPO_DIR}/scripts/update_landing.py"

cd "$REPO_DIR"

# Pull latest (in case Watson pushed changes)
git pull --quiet

# Update numbers from ClickHouse
# --ch-host defaults to localhost in update_landing.py, which is only correct on the 9975
# where ClickHouse is local. From anywhere else that silently resolves to nothing listening.
# publish-1 reaches ClickHouse over the 10.60.2 DAC.
"$VENV" "$SCRIPT" --ch-host "${CH_HOST:-localhost}"

# Only commit+push if there are actual changes
if git diff --quiet overrides/home.html; then
    echo "No changes to landing page."
    exit 0
fi

git add overrides/home.html
git commit --quiet -m "Auto-update landing page numbers $(date -u +'%Y-%m-%d %H:%MZ')"
git push --quiet

echo "Landing page updated and pushed."
