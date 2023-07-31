@echo off
@Rem Create a set of folders used to test PyBackup.py.
@Rem Prerequisites: The folders used in this step must not be system protected.
@Rem PyBackup %test%\pybackup\step1 %test%\pybackup\step0
SetLocal

Rem The next lines deletes all files and folders created during the test suite.
cd %temp%
if exist pybackup (
	icacls pybackup\*.* /t /inheritance:e
	rd pybackup /s /q
	)
if exist z:\pybackup rd z:\pybackup /s /q
if exist pybackup.*.txt del pybackup.*.txt

@Rem Create the initial set of test folders and files.
md pybackup
md pybackup\step1
cd pybackup\step1

echo Step1: This folder contains data files for common test cases>ReadMe.txt
echo Step1: This file will be deleted in a future backup, and then recreated>deleted.txt
echo Step1: This file will be deleted before a future backup>obsolete.txt
echo Step1: This file is read-only>readonly.txt
echo Step1: This file is hidden>hidden.txt
echo Step1: This file is a system file>system.txt

md CorruptCRC
echo Step1: This folder will be used to test a purposely corrupted CRC control file>CorruptCRC\ReadMe.txt

md Inaccessible
echo Step1: The folder will be used to test Inaccessible files>Inaccessible\ReadMe.txt

attrib -a *.* /s
attrib +r readonly.txt
attrib +h hidden.txt
attrib +s system.txt
attrib *.* /s >>ReadMe.txt
attrib -a *.* /s
echo Step1: a file that gets changed>changed.txt

@Rem Backup step1 data to step0, creating it in that process.
cd %temp%\pybackup
@echo on
pybackup step1 step0
@echo off
ren %temp%\pybackup.log.txt pybackup.step1.log.txt
@Echo.

@Rem Compare the two new folders.
"C:\Program Files\WinDiff\windiff.exe" %temp%\pybackup\step1 %temp%\pybackup\step0 

@Rem Review the logfile for this step
attrib %temp%\pybackup\*.* /s >>%temp%\pybackup.step1.log.txt
%temp%\pybackup.step1.log.txt
endlocal
@exit /b
