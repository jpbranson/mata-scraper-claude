# Pull the latest code and restart both tasks. Run from an administrator
# PowerShell in the repo folder:
#
#   .\ops\update.ps1
$ErrorActionPreference = "Stop"
$dir = (Resolve-Path "$PSScriptRoot\..").Path

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
