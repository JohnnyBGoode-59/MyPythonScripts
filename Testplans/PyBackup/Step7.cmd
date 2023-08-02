@echo off
@Rem See what happens when destination files cannot be accessed
@Rem Prerequisite: run step6
SetLocal
set Rem=Rem 
if "%1"=="" set Rem=

Rem The next lines delete files and folders that are no longer required
if exist %temp%\pybackup.step7.log.txt del %temp%\pybackup.step7.log.txt

SetLocal
@Rem Modify rename step5 to step7 and then protectsome files
cd %temp%\pybackup
if not exist step7 ren step5 step7
echo Step 6 (via 7): The folder will be used to test Inaccessible files>step6\Inaccessible\ReadMe.txt
cd step7
attrib -a *.* /s
echo Step 7: The folder will be used to test Inaccessible files>Inaccessible\ReadMe.txt
Rem Protect the files in the folder named Inaccessible	
icacls Inaccessible\*.* /inheritance:d /q
icacls Inaccessible\*.* /remove %USERNAME% /q

@echo on
cd %temp%\pybackup
pybackup step6 step7
@echo off
@ren %temp%\pybackup.log.txt pybackup.step7.log.txt

Rem Before running doing anything else, restore permissions
Rem that will keep Windiff from bogging down
icacls step7\Inaccessible\*.* /inheritance:e /q

Rem See how the destination folder compares with the source.
%Rem% "C:\Program Files\WinDiff\windiff.exe" %temp%\pybackup\step6 %temp%\pybackup\step7

Rem Review the errors that occurred
attrib *.* /s>>%temp%\pybackup.step7.log.txt
%Rem% %temp%\pybackup.step7.log.txt
