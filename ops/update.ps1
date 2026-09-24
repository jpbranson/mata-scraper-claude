# Pull the latest code and restart both tasks. Run from an administrator
# PowerShell in the repo folder:
#
#   .\ops\update.ps1
$ErrorActionPreference = "Stop"
$dir = (Resolve-Path "$PSScriptRoot\..").Path

git -C $dir pull --ff-only
& "$dir\.venv\Scripts\python.exe" -m pip install -q -r "$dir\requirements.txt"

foreach ($t in "mata-poller", "mata-web") {
    Stop-ScheduledTask -TaskName $t
    Start-ScheduledTask -TaskName $t
}
Start-Sleep 3
Get-ScheduledTask mata-* | Select-Object TaskName, State
