# Schedule a one-time task to run schedule_followups.py --send in 48 hours
# Usage: run this script once. It will register a Scheduled Task named 'codex_followups_wave1'.

$projectRoot = 'C:\Users\Charles\Desktop\codex-operator'
$pythonExe = (Resolve-Path .venv\Scripts\python.exe -ErrorAction SilentlyContinue).Path
if (-not $pythonExe) { $pythonExe = 'python' }

$script = "cd '$projectRoot'; $pythonExe .\scripts\schedule_followups.py --send"

$runAt = (Get-Date).AddHours(48)
$trigger = New-ScheduledTaskTrigger -Once -At $runAt
$action = New-ScheduledTaskAction -Execute 'powershell.exe' -Argument "-NoProfile -WindowStyle Hidden -Command \"$script\""
# Register without requiring elevated RunLevel to avoid permission issues in non-admin contexts
Register-ScheduledTask -TaskName 'codex_followups_wave1' -Trigger $trigger -Action $action -Force

Write-Output "Scheduled task 'codex_followups_wave1' registered to run at: $runAt"
