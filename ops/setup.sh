#!/bin/sh -e
# One-shot install on a fresh Debian/Ubuntu host. Run as a user with sudo.
# Installs to /opt/mata-scraper-claude and starts both systemd units as you.
#
#   curl -fsSL https://raw.githubusercontent.com/jpbranson/mata-scraper-claude/main/ops/setup.sh | sh
#
# If the repo is private, clone it manually first; the script skips the clone
# when the directory already exists.

REPO=https://github.com/jpbranson/mata-scraper-claude
DIR=/opt/mata-scraper-claude

sudo apt-get update -q && sudo apt-get install -y -q git python3-venv
[ -d "$DIR" ] || sudo git clone "$REPO" "$DIR"
sudo chown -R "$USER" "$DIR"
cd "$DIR"
python3 -m venv .venv
.venv/bin/pip install -q -r requirements.txt

for unit in ops/*.service; do
    sed "s|^\[Service\]|[Service]\nUser=$USER|" "$unit" | sudo tee "/etc/systemd/system/$(basename "$unit")" > /dev/null
done
sudo systemctl daemon-reload
sudo systemctl enable --now mata-poller mata-web
systemctl --no-pager status mata-poller mata-web | grep -E "service|Active"
