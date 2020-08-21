@echo off
for %%i in (%cd%) do set CDIR=%%~ni
cd z:\pictures\%CDIR%

for /d %%d in (*) do (
	cd %%d
	if not exist z:%%d md z:%%d
	@echo replace %CDIR%\%%d\*.* z:%%d /a
	replace *.* z:%%d /a
	cd ..
	)
