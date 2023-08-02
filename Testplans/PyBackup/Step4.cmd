@echo off
Rem Back up to an existing folder on a network drive.
Rem Prerequisite: run step3
SetLocal
set Rem=Rem 
if "%1"=="" set Rem=

Rem The next lines delete files and folders created when this step is performed.
if exist %temp%\pybackup.step4.log.txt del %temp%\pybackup.step4.log.txt

Rem Backup Step3 data to Step4 on a network drive
@echo on
if exist %temp%\pybackup\step0 rd /s /q %temp%\pybackup\step0
if exist z:\pybackup\step4 rd /s /q z:\pybackup\step4
attrib -a %temp%\pybackup\step3\*.* /s
pybackup %temp%\pybackup\step3 z:\pybackup\step4
@echo off
ren %temp%\pybackup.log.txt pybackup.step4.log.txt

Rem See how the destination folder compares with the source.
%Rem% "C:\Program Files\WinDiff\windiff.exe" %temp%\pybackup\step3 z:\pybackup\step4

Rem Review the errors that occurred
attrib %temp%\pybackup\step3\*.* /s>>%temp%\pybackup.step4.log.txt
attrib z:\pybackup\step4\*.* /s>>%temp%\pybackup.step4.log.txt
%Rem% %temp%\pybackup.step4.log.txt
