@echo off
Rem Create a batch rename operation to rename a set of files in a similar way.
SetLocal
set tfile=%temp%\rn.cmd
if exist %tfile% del %tfile%
for %%f in (%*) do echo ren "%%f" "%%f" >>%tfile%.unsorted
sort <%tfile%.unsorted >%tfile%
del %tfile%.unsorted
"C:\Program Files (x86)\Notepad++\notepad++.exe" %tfile%
call %tfile%
rem del %tfile%
