@echo off
title Xoilac M3U8 Playlist Generator
cd /d "%~dp0"

echo ========================================================
echo   XOILAC AUTOMATIC M3U8 PLAYLIST GENERATOR (100%% GRATIS)
echo ========================================================
echo.
echo Menjalankan update playlist...
python main.py

echo.
echo Selesai! File xoilac.m3u telah diperbarui.
pause
