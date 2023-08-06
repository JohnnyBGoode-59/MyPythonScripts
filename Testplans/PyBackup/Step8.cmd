@echo off
@Rem Perform a verify operation with hard errors present
@Rem Prerequisite: run step7
SetLocal

Rem The next lines delete files and folders that are no longer required
if exist %temp%\pybackup.step8.log.txt del %temp%\pybackup.step8.log.txt

SetLocal
@Rem Modify rename step5 to step7 and then protect some files
cd %temp%\pybackup
if not exist step8 ren step7 step8
cd step8
attrib -a *.* /s
echo Step 8: A new file>verifyme.txt
del deleted.txt
echo Step 8: A changed file>changed.txt
del NoCRC\crc.csv
dir >CorruptCRC\crc.csv
icacls Inaccessible\*.* /inheritance:d /q
icacls Inaccessible\*.* /remove %USERNAME% /q
type Inaccessible\readme.txt

@echo on
cd %temp%\pybackup
%2 pybackup -v step8
@echo off
@ren %temp%\pybackup.log.txt pybackup.step8.log.txt

Rem Before running doing anything else, restore permissions
cd step8
icacls Inaccessible\*.* /inheritance:e /q
cd ..

Rem Review the errors that occurred
attrib *.* /s>>%temp%\pybackup.step8.log.txt
endlocal
fc %temp%\pybackup.step?.log.txt results\*.*
