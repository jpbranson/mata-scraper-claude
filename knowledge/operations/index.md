# Runbooks

* [Running it](running-it.md) - Install, update and backfill the always-on Windows home machine that runs the poller and the map server as two scheduled tasks.
* [Remote access](remote-access.md) - Reach the map away from home over Tailscale, with Tailscale terminating HTTPS so phone browsers can load it; never port-forward 8000.

# Playbooks

* [Failure modes](failure-modes.md) - What happens, and what to do, when the vendor, the machine, MATA's routes, the GTFS feed, the official feed or the detour endpoints misbehave, and how often each has since 2026-09-25.
* [Working with live data](working-with-live-data.md) - Rules for agents and people working on the repo while the poller runs - analyse a copy of data/, use the repo's .venv Python, test poller changes in a scratch copy, and leave restarting the poller to the human.
