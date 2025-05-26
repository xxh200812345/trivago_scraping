@echo off
title watch info.log
:: %~dp0 表示当前 bat 所在的目录，即 res
:: 使用 ..\C\info.log 跳到 A\C\info.log
powershell -Command "Get-Content -Path '%~dp0..\\log\\info.log' -Encoding UTF8 -Wait"

pause
