@echo off
title Xoilac M3U8 Playlist Background Daemon + Local Server
cd /d "%~dp0"

echo ========================================================
echo   XOILAC M3U8 AUTO-REFRESH SERVICE + LOCAL HTTP SERVER
echo ========================================================
echo.
echo Mode: Auto-refresh setiap 5 menit + Server streaming lokal aktif.
echo Tekan Ctrl+C untuk menghentikan layanan.
echo.

python main.py --watch --serve --interval 300 --port 8080
pause
