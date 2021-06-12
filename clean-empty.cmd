@echo off
for /r /d %%i in (*.*) do (
	echo %%i
	if exist "%%i\thumbs.db" (
		attrib -h "%%i\thumbs.db"
		del "%%i\thumbs.db"
		)
	if exist "%%i\*" rd "%%i" 2>nul
	)
tree
