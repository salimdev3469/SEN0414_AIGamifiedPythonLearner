@echo off
chcp 65001 >nul 2>&1
echo ============================================
echo Django Server Baslatiliyor (Portable Mode)
echo ============================================
echo.

REM [0/6] Check Python installation
echo [0/6] Python kontrol ediliyor...
python --version >nul 2>&1
if errorlevel 1 (
    echo [ERROR] Python bulunamadi!
    echo Lutfen Python 3.8+ yukleyin: https://www.python.org/downloads/
    echo.
    pause
    exit /b 1
)
python --version
echo [OK] Python bulundu.
echo.

REM [1/6] Create virtual environment if it doesn't exist
echo [1/6] Virtual environment kontrol ediliyor...
if not exist "venv\Scripts\activate.bat" (
    echo [INFO] Virtual environment bulunamadi, olusturuluyor...
    python -m venv venv
    if errorlevel 1 (
        echo [ERROR] Virtual environment olusturulamadi!
        pause
        exit /b 1
    )
    echo [OK] Virtual environment olusturuldu.
) else (
    echo [OK] Virtual environment mevcut.
)
echo.

REM [2/6] Activate virtual environment
echo [2/6] Virtual environment aktif ediliyor...
call venv\Scripts\activate.bat
if errorlevel 1 (
    echo [ERROR] Virtual environment aktif edilemedi!
    pause
    exit /b 1
)
echo [OK] Virtual environment aktif.
echo.

REM [3/6] Upgrade pip
echo [3/6] pip guncelleniyor...
python -m pip install --upgrade pip --quiet
if errorlevel 1 (
    echo [WARNING] pip guncellenemedi, devam ediliyor...
)
echo [OK] pip hazir.
echo.

REM [4/6] Check and install requirements
echo [4/6] Gereklilikler kontrol ediliyor...
if not exist "requirements.txt" (
    echo [WARNING] requirements.txt bulunamadi!
    echo Gereklilikler kontrol edilemiyor.
    echo.
) else (
    echo requirements.txt bulundu, eksik paketler kontrol ediliyor...
    
    REM Check if check_and_install_requirements.py exists
    if exist "check_and_install_requirements.py" (
        python check_and_install_requirements.py
        if errorlevel 1 (
            echo [WARNING] Paket kontrolu sirasinda hata olustu, devam ediliyor...
        )
    ) else (
        echo [INFO] check_and_install_requirements.py bulunamadi, tum paketler yukleniyor...
        python -m pip install -r requirements.txt
        if errorlevel 1 (
            echo [WARNING] Paket yukleme sirasinda hata olustu, devam ediliyor...
        )
    )
    echo [OK] Gereklilikler hazir.
)
echo.

REM [5/6] Database migrations
echo [5/6] Database migration'lari kontrol ediliyor...
python manage.py makemigrations --no-input >nul 2>&1
python manage.py migrate --no-input
if errorlevel 1 (
    echo [WARNING] Migration sirasinda hata olustu!
    echo Devam ediliyor...
)
echo [OK] Database hazir.
echo.

REM [6/6] Database info
echo [6/6] Database bilgisi:
if defined DATABASE_URL (
    echo [INFO] PostgreSQL kullaniliyor (DATABASE_URL mevcut)
) else (
    echo [INFO] SQLite kullaniliyor (db.sqlite3)
    if not exist "db.sqlite3" (
        echo [INFO] Database dosyasi henuz olusturulmadi, ilk calistirmada olusturulacak.
    )
)
echo.

echo ============================================
echo [Hazir] Server baslatiliyor...
echo ============================================
echo.
echo Server adresi: http://127.0.0.1:8000
echo Admin paneli: http://127.0.0.1:8000/admin/
echo Durdurmak icin: Ctrl+C
echo.
echo ============================================
echo.

python manage.py runserver
if errorlevel 1 (
    echo.
    echo [ERROR] Server baslatilirken hata olustu!
    echo.
    echo Hata detaylari icin yukaridaki mesajlari kontrol edin.
    echo.
    pause
    exit /b 1
)
