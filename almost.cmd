@echo off
del *Thumbs.db *.jbf 2>nul
for %%i in (%cd%) do set CDIR=%%~ni
move %CDIR%*.* .. 2>nul
