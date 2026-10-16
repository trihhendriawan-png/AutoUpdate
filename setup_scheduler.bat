@echo off
title Setup Windows Task Scheduler for Xoilac M3U
cd /d "%~dp0"

echo ========================================================
echo   MENDAFTARKAN TUGAS OTOMATIS KE WINDOWS TASK SCHEDULER
echo ========================================================
echo.
echo Script ini akan membuat Task otomatis di Windows yang
echo menjalankan pembaruan xoilac.m3u setiap 15 menit.
echo.

set TASKNAME="XoilacPlaylistAutoUpdate"
set PYTHON_EXE=python.exe
set SCRIPT_PATH="%~dp0main.py"

schtasks /create /tn %TASKNAME% /tr "\"%PYTHON_EXE%\" \"%SCRIPT_PATH%\"" /sc minute /mo 15 /f

if %ERRORLEVEL% EQU 0 (
    echo.
    echo [BERHASIL] Task '%TASKNAME%' berhasil didaftarkan!
    echo Windows akan otomatis memperbarui file xoilac.m3u setiap 15 menit di background.
) else (
    echo.
    echo [CATATAN] Jika gagal, pastikan Anda menjalankan file bat ini dengan 'Run as Administrator'.
)

echo.
pause
