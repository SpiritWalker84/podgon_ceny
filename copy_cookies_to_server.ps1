# Скрипт для копирования cookies на сервер
# Использование: .\copy_cookies_to_server.ps1

$server = "rinat@sevvinrcqf"
$remotePath = "~/podgon_ceny/"
$localDir = "C:\projects\wbB\podgon_ceny"
$pscp = "C:\Program Files\PuTTY\pscp.exe"

Write-Host "Копирование cookies на сервер..." -ForegroundColor Green

# Переходим в директорию проекта
Push-Location $localDir

# Проверяем наличие файлов
$files = @(
    "wb_cookies.pkl",
    "wb_cookies.pkl.storage.json",
    "wb_cookies.json"
)

$foundFiles = @()
foreach ($file in $files) {
    if (Test-Path $file) {
        $foundFiles += $file
        Write-Host "✓ Найден: $file" -ForegroundColor Green
    }
}

if ($foundFiles.Count -eq 0) {
    Write-Host "ОШИБКА: Файлы cookies не найдены в $localDir" -ForegroundColor Red
    Write-Host "Убедитесь что вы запустили скрипт локально и авторизовались" -ForegroundColor Yellow
    Pop-Location
    exit 1
}

# Копируем файлы
foreach ($file in $foundFiles) {
    Write-Host "Копирование $file..." -ForegroundColor Yellow
    try {
        & $pscp $file "${server}:${remotePath}"
        if ($LASTEXITCODE -eq 0) {
            Write-Host "✓ $file успешно скопирован" -ForegroundColor Green
        } else {
            Write-Host "✗ Ошибка при копировании $file (код: $LASTEXITCODE)" -ForegroundColor Red
            Write-Host "Возможные причины:" -ForegroundColor Yellow
            Write-Host "  1. Сервер недоступен или имя хоста неверное"
            Write-Host "  2. Нет SSH подключения к серверу"
            Write-Host "  3. Нужно использовать полный адрес (например: rinat@server.example.com)"
        }
    } catch {
        Write-Host "✗ Ошибка: $_" -ForegroundColor Red
    }
}

Pop-Location

Write-Host "`nГотово! Проверьте на сервере:" -ForegroundColor Green
Write-Host "  ls -la ~/podgon_ceny/wb_cookies.*" -ForegroundColor Cyan
Write-Host "  chmod 600 ~/podgon_ceny/wb_cookies.pkl" -ForegroundColor Cyan

