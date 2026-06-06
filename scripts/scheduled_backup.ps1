param(
    [string]$ProjectDir = "C:\Users\PC\Desktop\AMEEK",
    [string]$BackupDir = "$ProjectDir\backup",
    [string]$PythonExe = "python"
)

$ErrorActionPreference = "Stop"
$timestamp = Get-Date -Format "yyyy-MM-dd HH:mm:ss"

Write-Host "[$timestamp] Début de la sauvegarde AMEEK..."

try {
    & $PythonExe "$ProjectDir\manage.py" backup_data --output "$BackupDir"
    Write-Host "[$timestamp] Sauvegarde terminée avec succès."

    # Supprimer les sauvegardes de plus de 30 jours
    $cutoff = (Get-Date).AddDays(-30)
    Get-ChildItem "$BackupDir\ameek_backup_*.zip" | Where-Object {
        $_.LastWriteTime -lt $cutoff
    } | ForEach-Object {
        Remove-Item $_.FullName
        Write-Host "  Supprimé : $($_.Name)"
    }
}
catch {
    Write-Host "[$timestamp] ERREUR : $_"
    exit 1
}
