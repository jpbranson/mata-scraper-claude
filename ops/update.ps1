# Pull the latest code and restart both tasks. Run from PowerShell in the repo
# folder (no admin needed; setup.ps1 lets your account start and stop them):
#
#   .\ops\update.ps1
$ErrorActionPreference = "Stop"
$dir = (Resolve-Path "$PSScriptRoot\..").Path

# The poller rebuilds routes.csv, stops.csv and network.geojson itself when
# MATA renumbers its lines. Drop those local copies so the pull can't
# conflict; if the pulled ones are stale, the poller rebuilds them again.
git -C $dir checkout -- routes.csv stops.csv network.geojson
git -C $dir pull --ff-only
& "$dir\.venv\Scripts\python.exe" -m pip install -q -r "$dir\requirements.txt"

foreach ($t in "mata-poller", "mata-web") { Stop-ScheduledTask -TaskName $t }
# Stopping mata-poller kills its cmd.exe wrapper but not the python under it,
# which keeps running the old code and holds poller.log open, so the restarted
# task can't redirect to it and exits 1. Kill the orphan before starting.
Get-CimInstance Win32_Process -Filter "Name='python.exe' AND CommandLine LIKE '%cadavl_to_gtfs_rt.py%'" |
    ForEach-Object { Stop-Process -Id $_.ProcessId -Force -ErrorAction SilentlyContinue }
Start-Sleep 1
foreach ($t in "mata-poller", "mata-web") { Start-ScheduledTask -TaskName $t }
Start-Sleep 3
Get-ScheduledTask mata-* | Select-Object TaskName, State
