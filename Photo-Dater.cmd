@echo off
if not "%2"=="" goto Run
Echo This script will add a date prefix to a set of files.
Echo It will then run Photo-Renamer.py to add that date to the EXIF data for those files.
Echo Syntax: Photo-Dater {date} {files} [-r]
Echo To be safe the files that are specified should be in the current folder.
Echo A subfolder will be temporarily created during processing and removed upon completion.
Echo If the -r switch is supplied the EXIF dates will be reset
exit /b

:Run
SetLocal
Set Prefix=%1

:Again
set Folder=_Temp_%RANDOM%_
md %Folder%
for %%f in (%2) do (
	cd %Folder%
	move "..\%%f" . >nul
	echo ren "%%f" "%Prefix%_%%f"
	ren "%%f" "%Prefix%_%%f"
	cd ..
	)
cd %Folder%
call photo-renamer.py %3
move *.* .. >nul
cd ..
rd %Folder%
:Exit
