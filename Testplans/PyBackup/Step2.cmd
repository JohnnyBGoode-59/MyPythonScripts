@echo off
@Rem Back up a folder with issues to an existing, very similar folder.
@SetLocal

@Rem The next lines delete files and folders created when this step is performed.
cd %temp%
if exist pybackup.step2.log.txt del pybackup.step2.log.txt
cd %temp%\pybackup
if exist step1 rd step1 /s /q
if exist step2 rd step2 /s /q
attrib -a /s

@Rem Make a few changes before copying step0 to step2.
cd %temp%\pybackup\step0
echo Step2 (in Step0): test an existing file changed in both source and destination>changed.txt
echo Step2 (in Step0): This is a new source file>new.txt

md NoCRC
echo Step2 (in Step0): This folder contains no CRC control file>NoCRC\ReadMe.txt

dir CorruptCRC>CorruptCRC\crc.csv

@Rem Create pybackup\step2 to be quite similar to pybackup\step0
cd %temp%\pybackup
xcopy /e /c /i /y step0\*.* step2

@Rem Make a few more source files changes in both source and destination
del %temp%\pybackup\step0\obsolete.txt
cd %temp%\pybackup\step2
echo Step2: test an existing file changed in both source and destination>changed.txt
echo Step2: This is a new destination file that will be replaced with a new source file>new.txt
echo Step2: This is a new destination file that will be be ignored>ignored.txt
del deleted.txt

Rem Review the differences between Step0 and Step2 before backing up Step0
"C:\Program Files\WinDiff\windiff.exe" %temp%\pybackup\step0 %temp%\pybackup\step2

@Rem Backup step0 to step2
cd %temp%\pybackup
@echo on
pybackup step0 step2
@echo off
ren %temp%\pybackup.log.txt pybackup.step2.log.txt
@Echo.

Rem See how the destination folder compares with the source.
"C:\Program Files\WinDiff\windiff.exe" %temp%\pybackup\step0 %temp%\pybackup\step2

Rem Review the errors that occurred
attrib %temp%\pybackup\*.* /s >>%temp%\pybackup.step2.log.txt
%temp%\pybackup.step2.log.txt
@exit /b
