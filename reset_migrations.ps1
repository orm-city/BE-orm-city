# PowerShell script for resetting Django migrations
# 오류가 있는 것 같아서 수정해야 합니다. 잠시만 기다려주세요.
# 실행 명령어 : .\reset_migrations.ps1
# 권한 오류 발생 시 : Set-ExecutionPolicy -Scope Process -ExecutionPolicy Bypass

$PROJECT_ROOT = Get-Location

Write-Host "주의: 이 스크립트는 모든 마이그레이션 파일과 데이터베이스를 삭제합니다." -ForegroundColor Red
$confirmation = Read-Host "계속하시겠습니까? (Y/N)"
if ($confirmation -ne "Y") {
    Write-Host "작업이 취소되었습니다."
    exit
}

# 마이그레이션 파일 삭제 (__init__.py 제외)
Get-ChildItem -Recurse -Filter "*.py" -Exclude "__init__.py" |
    Where-Object { $_.FullName -notmatch "venv|site-packages" -and $_.FullName -match "migrations" } |
    Remove-Item -Verbose

# 컴파일된 마이그레이션 파일 삭제
Get-ChildItem -Recurse -Filter "*.pyc" |
    Where-Object { $_.FullName -notmatch "venv|site-packages" -and $_.FullName -match "migrations" } |
    Remove-Item -Verbose

# db.sqlite3 파일 삭제
Remove-Item "$PROJECT_ROOT\db.sqlite3" -ErrorAction SilentlyContinue -Verbose

# 가상 환경 활성화 (경로는 프로젝트에 맞게 수정 필요)
# & "$PROJECT_ROOT\venv\Scripts\Activate.ps1"

# makemigrations 및 migrate 실행
try {
    & pdm run python src/manage.py makemigrations
    if ($LASTEXITCODE -ne 0) { throw "makemigrations 실행 중 오류 발생" }

    & pdm run python src/manage.py migrate
    if ($LASTEXITCODE -ne 0) { throw "migrate 실행 중 오류 발생" }

    Write-Host "프로젝트 초기화 완료" -ForegroundColor Green

    # 서버 실행 (필요하지 않다면 이 줄을 제거하거나 주석 처리하세요)
    # & python manage.py runserver
}
catch {
    Write-Host "오류 발생: $_" -ForegroundColor Red
    exit 1
}
