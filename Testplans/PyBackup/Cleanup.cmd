@echo off
Rem This file cleans up all files created and copies test results
Rem to a folder where git can be used to check for differences.
@SetLocal
if not exist Results goto :Exit
copy %temp%\pybackup*.txt Results /y
del %temp%\pybackup*.txt
if exist %temp%\pybackup rd /s /q %temp%\pybackup
if exist z:\pybackup rd /s /q z:\pybackup

:Exit