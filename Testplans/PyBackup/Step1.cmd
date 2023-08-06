@echo off
@Rem Create a set of folders used to test PyBackup.py.
@Rem Prerequisites: The folders used in this step must not be system protected.
@Rem PyBackup %test%\pybackup\step1 %test%\pybackup\step0

@Rem %1==Rem 		skips the WinDiff step(s)
@Rem %2==exit/b		aborts before running PyBackup
Set Rem=%1
SetLocal

Rem The next lines deletes all files and folders created during the test suite.
cd %temp%
if exist pybackup (
	icacls pybackup\*.* /t /inheritance:e /q >nul
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

Rem A filename cannot contain any I/O redirection characters or any of these: \ / : * ? "
Rem So let's  some strange filenames and folders as a test.
set strange="strange(~!@#$%^&+={2};',)named."
echo Step1: Strange filename test 1 >>%strange%file1.txt
md %strange%folder
echo Step1: Strange pathname test 2 >>%strange%folder\%strange%file2.txt"

Rem These test cases were known to fail in the past
set strange="[folder]"
md %strange%
echo Step1: Files found in a folder with square bracketts in the name>>%strange%\Known-issue.txt

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
%2 pybackup step1 step0
@echo off
ren %temp%\pybackup.log.txt pybackup.step1.log.txt
@Echo.

@Rem Compare the two new folders.
%1 "C:\Program Files\WinDiff\windiff.exe" %temp%\pybackup\step1 %temp%\pybackup\step0 

@Rem Review the logfile for this step
attrib %temp%\pybackup\*.* /s >>%temp%\pybackup.step1.log.txt
endlocal
fc %temp%\pybackup.step?.log.txt results\*.*
@exit /b
