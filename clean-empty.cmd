@echo off
for /r /d %%i in (*.*) do (
	echo %%i
	if exist "%%i\*" rd "%%i" 2>nul
	)
tree
