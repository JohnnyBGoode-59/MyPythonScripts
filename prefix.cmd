@echo off
for %%i in (%cd%) do set CDIR=%%~ni
call \almost
@echo off
for %%i in (*) do (
	move "%%i" ..
	ren "..\%%i" "%CDIR%_%%i"
	)
cd ..
rd %CDIR%