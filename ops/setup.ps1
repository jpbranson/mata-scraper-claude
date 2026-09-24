# One-shot install on Windows. Needs Python 3.10+ on PATH (python.org
# installer, tick "Add to PATH"). Run once from an *administrator*
# PowerShell in the repo folder:
#
#   Set-ExecutionPolicy -Scope Process Bypass
#   .\ops\setup.ps1
#
# Creates the venv and registers two scheduled tasks, mata-poller and
# mata-web, that start at boot without anyone logged in and restart on
# failure. Poller output goes to data\poller.log.
#
# Manage them afterwards with Task Scheduler (taskschd.msc) or:
#   Get-ScheduledTask mata-* | Select TaskName, State
#   Stop-ScheduledTask mata-poller ; Start-ScheduledTask mata-poller

$ErrorActionPreference = "Stop"
$dir = (Resolve-Path "$PSScriptRoot\..").Path
$py  = "$dir\.venv\Scripts\python.exe"

python -m venv "$dir\.venv"
& $py -m pip install -q -r "$dir\requirements.txt"
New-Item -ItemType Directory -Force "$dir\data" | Out-Null

$settings = New-ScheduledTaskSettingsSet `
    -RestartCount 999 -RestartInterval (New-TimeSpan -Minutes 1) `
    -ExecutionTimeLimit ([TimeSpan]::Zero) -MultipleInstances IgnoreNew `
    -AllowStartIfOnBatteries -DontStopIfGoingOnBatteries -StartWhenAvailable
$trigger   = New-ScheduledTaskTrigger -AtStartup
$principal = New-ScheduledTaskPrincipal -UserId "$env:USERDOMAIN\$env:USERNAME" `
    -LogonType S4U -RunLevel Limited

$tasks = @(
    # -u: unbuffered stdout, so the log updates every poll instead of every few hours.
    @{ Name = "mata-poller"; Exec = "cmd.exe"
       Args = "/c `"`"$py`" -u cadavl_to_gtfs_rt.py >> data\poller.log 2>&1`"" },
    @{ Name = "mata-web";    Exec = $py; Args = "-m http.server 8000" }
)
foreach ($t in $tasks) {
    $action = New-ScheduledTaskAction -Execute $t.Exec -Argument $t.Args -WorkingDirectory $dir
    Register-ScheduledTask -TaskName $t.Name -Action $action -Trigger $trigger `
        -Settings $settings -Principal $principal -Force | Out-Null
    Start-ScheduledTask -TaskName $t.Name
}

# Let phones on the home LAN or on Tailscale (100.64.0.0/10) reach the map.
New-NetFirewallRule -DisplayName "mata-web" -Direction Inbound -Program $py `
    -Protocol TCP -LocalPort 8000 -RemoteAddress @("LocalSubnet", "100.64.0.0/10") `
    -Action Allow -ErrorAction SilentlyContinue | Out-Null

Start-Sleep 3
Get-ScheduledTask mata-* | Select-Object TaskName, State
"Map: http://localhost:8000/map.html   Log: $dir\data\poller.log"
