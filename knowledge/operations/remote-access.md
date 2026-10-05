---
type: Runbook
title: Remote access
description: Reach the map away from home over Tailscale, with Tailscale terminating HTTPS so phone browsers can load it; never port-forward 8000.
tags: [ops, map]
generated: { by: claude-code/claude-opus-5-5, at: 2026-10-05T02:18:04Z }
sources:
  - id: design-md
    resource: https://github.com/jpbranson/mata-scraper-claude/blob/2a1b9ab/DESIGN.md
    title: DESIGN.md at 2a1b9ab
    last_modified: 2026-09-28T01:29:38Z
---

# Why Tailscale

Tailscale (free for personal use) on the machine and the phone makes a
private network between your own devices, with no router ports opened and
nothing exposed to the internet. `setup.ps1` already opens port 8000 to the
home LAN and Tailscale only ([running it](running-it.md)).

# HTTPS for phones

Phone browsers force `https://`, which plain `http.server` can't answer
(`ERR_SSL_PROTOCOL_ERROR`), so let Tailscale terminate HTTPS:

1. Enable MagicDNS and HTTPS in the Tailscale admin console (DNS page).
2. On the PC, run once: `tailscale serve --bg 8000`.
3. The map is then at `https://<pc-name>.<tailnet>.ts.net/map.html` from any
   signed-in device.

# Don't

Don't port-forward 8000 instead: `http.server` is not meant to face the
public internet.
