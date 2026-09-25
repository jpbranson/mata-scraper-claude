# Put route numbers on history rows recorded while routes.csv was stale, then
# rebuild replay frames and stop arrivals from the history, with the poller
# paused so it can't write into the files being rebuilt. Run from
# PowerShell in the repo folder (no admin needed):
#
#   .\ops\backfill.ps1              # every recorded day
#   .\ops\backfill.ps1 2026-09-24   # one day
param([string]$Day)
$ErrorActionPreference = "Stop"
$dir = (Resolve-Path "$PSScriptRoot\..").Path

Stop-ScheduledTask -TaskName mata-poller
# As in update.ps1: the python under the task's cmd.exe outlives the task.
Get-CimInstance Win32_Process -Filter "Name='python.exe' AND CommandLine LIKE '%cadavl_to_gtfs_rt.py%'" |
    ForEach-Object { Stop-Process -Id $_.ProcessId -Force -ErrorAction SilentlyContinue }
Start-Sleep 1

try {
    $dayArg = @(if ($Day) { $Day })
    # Every history file: they're named by UTC date, $Day is a local one.
    & "$dir\.venv\Scripts\python.exe" "$dir\backfill_routes.py"
    if ($LASTEXITCODE -ne 0) { Write-Warning "route backfill failed; see output above." }
    & "$dir\.venv\Scripts\python.exe" "$dir\backfill_replay.py" @dayArg
    if ($LASTEXITCODE -ne 0) { Write-Warning "backfill failed; see output above." }
} finally {
    # Restart the poller even if the backfill failed.
    Start-ScheduledTask -TaskName mata-poller
    Start-Sleep 3
    Get-ScheduledTask mata-poller | Select-Object TaskName, State
}
