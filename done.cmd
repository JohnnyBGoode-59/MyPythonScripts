@echo off
del *Thumbs.db *.jbf 2>nul
move *.* .. 2>nul
for %%i in (%cd%) do set CDIR=%%~ni
cd ..
rd "%CDIR%"
