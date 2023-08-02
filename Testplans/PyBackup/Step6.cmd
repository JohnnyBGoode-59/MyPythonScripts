@echo off
@Rem See what happens when source files cannot be accessed
@Rem Prerequisite: run step5
SetLocal
set Rem=Rem 
if "%1"=="" set Rem=

Rem The next lines delete files and folders that are no longer required
if exist %temp%\pybackup.step6.log.txt del %temp%\pybackup.step6.log.txt
if exist z:\pybackup rd /s /q z:\pybackup

SetLocal
@Rem Modify step5 data by protecting some files
cd %temp%\pybackup\step5
attrib -a *.* /s

Rem Protect the files in the folder named Inaccessible	
icacls Inaccessible\*.* /inheritance:d /q
icacls Inaccessible\*.* /remove %USERNAME% /q
Echo Step 5: Both crc.csv and ReadMe.Txt are now inaccessible.>Inaccessible\acl.txt
 

cd %temp%\pybackup
@echo on
pybackup step5 step6
@echo off
ren %temp%\pybackup.log.txt pybackup.step6.log.txt

Rem Before running doing anything else, restore permissions
Rem that will keep Windiff from bogging down
icacls step5\Inaccessible\*.* /inheritance:e /q

Rem See how the destination folder compares with the source.
%Rem% "C:\Program Files\WinDiff\windiff.exe" %temp%\pybackup\step5 %temp%\pybackup\step6

Rem Review the errors that occurred
attrib *.* /s>>%temp%\pybackup.step6.log.txt
%Rem% %temp%\pybackup.step6.log.txt
