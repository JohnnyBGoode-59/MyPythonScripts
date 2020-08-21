@echo off
if "%1"=="" goto Root
if "%2"=="" goto Month

:Day
echo %1/%2
cd %2
for /d %%i in (*) do move %%i ..\..
cd ..
exit /b

:Month
echo %1
cd %1
for /d %%i in (*) do call %0 %1 %%i
cd ..
exit /b

:Root
for /d %%i in (*) do call %0 %%i


