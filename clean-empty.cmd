@echo off
for /r /d %%i in (*.*) do (
	echo %%i
	rd "%%i"
	)
tree
