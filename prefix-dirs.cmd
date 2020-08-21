@echo off
for /d %%i in (*) do (
	echo %%i
	cd %%i
	call \prefix
)
