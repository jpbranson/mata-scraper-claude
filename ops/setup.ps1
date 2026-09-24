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

# Prefer the `py` launcher (installed by python.org even without "Add to
# PATH"). A bare `python` may be the Microsoft Store placeholder, which
# prints an install prompt and exits non-zero, so verify it actually runs.
$python = $null
foreach ($candidate in "py", "python") {
    $cmd = Get-Command $candidate -ErrorAction SilentlyContinue
    if ($cmd -and (& $cmd.Source --version 2>$null) -match "^Python 3\.(1\d|[2-9]\d)") {
        $python = $cmd.Source; break
    }
}
if (-not $python) {
    throw "Python 3.10+ not found. Install it from https://www.python.org/downloads/ (tick 'Add python.exe to PATH'), open a new PowerShell, and re-run."
}

# On a re-run, stop the tasks first: their python.exe is locked while running,
# so `venv` can't refresh it. Stopping mata-poller also leaves the python
# under its cmd.exe wrapper alive, holding poller.log open so the new task
# exits 1 (same as in update.ps1); kill that too.
Get-ScheduledTask mata-* -ErrorAction SilentlyContinue | Stop-ScheduledTask
Get-CimInstance Win32_Process -Filter "Name='python.exe' AND CommandLine LIKE '%cadavl_to_gtfs_rt.py%'" |
    ForEach-Object { Stop-Process -Id $_.ProcessId -Force -ErrorAction SilentlyContinue }
Start-Sleep 1

& $python -m venv "$dir\.venv"
if (-not (Test-Path $py)) { throw "venv creation failed; see output above." }
& $py -m pip install -q -r "$dir\requirements.txt"
if ($LASTEXITCODE -ne 0) { throw "pip install failed; see output above." }
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
# By default only admins may start or stop the tasks; also give this account
# read + execute (GRGX, which covers start and stop) so update.ps1 can run from
# a normal, non-admin PowerShell.
$sid = [Security.Principal.WindowsIdentity]::GetCurrent().User.Value
$scheduler = New-Object -ComObject Schedule.Service
$scheduler.Connect()
foreach ($t in $tasks) {
    $action = New-ScheduledTaskAction -Execute $t.Exec -Argument $t.Args -WorkingDirectory $dir
    Register-ScheduledTask -TaskName $t.Name -Action $action -Trigger $trigger `
        -Settings $settings -Principal $principal -Force | Out-Null
    $scheduler.GetFolder("\").GetTask($t.Name).SetSecurityDescriptor(
        "D:(A;;FA;;;BA)(A;;FA;;;SY)(A;;GRGX;;;$sid)", 0)
    Start-ScheduledTask -TaskName $t.Name
}

# Let phones on the home LAN or on Tailscale (100.64.0.0/10) reach the map.
New-NetFirewallRule -DisplayName "mata-web" -Direction Inbound -Program $py `
    -Protocol TCP -LocalPort 8000 -RemoteAddress @("LocalSubnet", "100.64.0.0/10") `
    -Action Allow -ErrorAction SilentlyContinue | Out-Null

Start-Sleep 3
Get-ScheduledTask mata-* | Select-Object TaskName, State
"Map: http://localhost:8000/map.html   Log: $dir\data\poller.log"
