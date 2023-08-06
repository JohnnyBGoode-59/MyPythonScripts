@echo off
Rem Back up from a network drive to an existing local drive.
Rem Prerequisite: run step4
SetLocal

Rem The next lines delete files and folders created when this step is performed.
if exist %temp%\pybackup.step5.log.txt del %temp%\pybackup.step5.log.txt

Rem Rename Step3 data to Step5 and then copy over it using Step4 data
cd %temp%\pybackup
if not exist step5 ren step3 step5
attrib -a step5\*.* /s
attrib -a z:\pybackup\step4\*.* /s
@echo on
%2 pybackup z:\pybackup\step4 step5
@echo off
ren %temp%\pybackup.log.txt pybackup.step5.log.txt

Rem See how the destination folder compares with the source.
%Rem% "C:\Program Files\WinDiff\windiff.exe" z:\pybackup\step4 %temp%\pybackup\step5

Rem Review for errors
cd %temp%\pybackup\step5
attrib z:\pybackup\step4\*.* /s >>%temp%\pybackup.step5.log.txt
attrib *.* /s >>%temp%\pybackup.step5.log.txt
endlocal
fc %temp%\pybackup.step?.log.txt results\*.*
