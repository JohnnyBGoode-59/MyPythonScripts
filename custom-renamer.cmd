@echo off
SetLocal
set tfile=%temp%\rn.cmd
if exist %tfile% del %tfile%
for %%f in (%*) do echo ren "%%f" "%%f" >>%tfile%.unsorted
sort <%tfile%.unsorted >%tfile%
del %tfile%.unsorted
"C:\Program Files (x86)\Notepad++\notepad++.exe" %tfile%
call %tfile%
del %tfile%
