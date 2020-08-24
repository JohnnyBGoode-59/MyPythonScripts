@echo off
if exist 01Jan\*.* goto Start
if exist %1\*.jpg goto Start
Echo This batch file loops through a set of folders named by dates
Echo and renames and backs up those folders.
exit /b

:Start
for /d %%d in (*) do (
	cd %%d
	photo-renamer.py
	photo-backup.py
	cd ..
	rd %%d
	)