@echo off
@Rem Perform a update operation
@Rem Prerequisite: run step9
SetLocal
set Rem=Rem 
if "%1"=="" set Rem=

Rem The next lines delete files and folders that are no longer required
if exist %temp%\pybackup.step10.log.txt del %temp%\pybackup.step10.log.txt

SetLocal
@Rem Modify rename step9 to step10 and then make some simple changes
cd %temp%\pybackup
if not exist step10 ren step9 step10
cd step10
attrib -a *.* /s
echo Step 10: New files are ignored>also-ignored.txt
echo Step 10: A changed file>changed.txt
del deleted.txt

@echo on
cd %temp%\pybackup
pybackup -u step10
@echo off
@ren %temp%\pybackup.log.txt pybackup.step10.log.txt

Rem Review the errors that occurred
cd step10
attrib *.* /s>>%temp%\pybackup.step10.log.txt
%Rem% %temp%\pybackup.step8.log.txt
