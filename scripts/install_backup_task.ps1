param(
    [string]$ProjectDir = "C:\Users\PC\Desktop\AMEEK",
    [string]$TaskName = "AMEEK Backup",
    [string]$DailyAt = "03:00"
)

$ScriptPath = "$ProjectDir\scripts\scheduled_backup.ps1"
$Action = New-ScheduledTaskAction -Execute "PowerShell.exe" -Argument "-NoProfile -ExecutionPolicy Bypass -File `"$ScriptPath`" -ProjectDir `"$ProjectDir`""
$Trigger = New-ScheduledTaskTrigger -Daily -At $DailyAt
$Principal = New-ScheduledTaskPrincipal -UserId "SYSTEM" -LogonType ServiceAccount -RunLevel Highest
$Settings = New-ScheduledTaskSettingsSet -StartWhenAvailable -DontStopOnIdleEnd

Register-ScheduledTask -TaskName $TaskName -Action $Action -Trigger $Trigger -Principal $Principal -Settings $Settings -Force

Write-Host "Tâche planifiée '$TaskName' installée (exécution quotidienne à $DailyAt)."
Write-Host "Script : $ScriptPath"
