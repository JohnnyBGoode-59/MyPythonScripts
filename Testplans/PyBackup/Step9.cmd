@echo on
@Rem Perform a backup operation with hard errors present, both source and destination
@Rem Prerequisite: run step7
@SetLocal

Rem The next lines delete files and folders that are no longer required
if exist %temp%\pybackup.step9.log.txt del %temp%\pybackup.step9.log.txt

SetLocal
@Rem Rename step6 to step9 and then protect some files
cd %temp%\pybackup
if not exist step9 ren step6 step9
cd step9
attrib -a *.* /s
cd Inaccessible
echo Step 9: This file cannot be replaced>CannotReplace.txt
icacls *.* /inheritance:d /q
icacls CannotReplace.txt /remove %USERNAME% /q

cd %temp%\pybackup\step8
attrib -a *.* /s
cd Inaccessible
echo Step 9 (in 8): This file cannot be copied>CannotCopy.txt
echo Step 9 (in 8): This file will not be replaced>CannotReplace.txt
icacls *.* /inheritance:d /q
icacls CannotCopy.txt /remove %USERNAME% /q

@echo on
cd %temp%\pybackup
pybackup step8 step9
@echo off
@ren %temp%\pybackup.log.txt pybackup.step9.log.txt

Rem Before running doing anything else, restore permissions
icacls step8\Inaccessible\*.* /inheritance:e /q
icacls step9\Inaccessible\*.* /inheritance:e /q

Rem Review the errors that occurred
cd %temp%\pybackup
attrib *.* /s>>%temp%\pybackup.step9.log.txt
%temp%\pybackup.step9.log.txt
