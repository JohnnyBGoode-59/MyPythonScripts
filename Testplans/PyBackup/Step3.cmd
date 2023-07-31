@echo off
@Rem Validate the new backup folder.
@Rem Prerequisite: run step2
@SetLocal

@Rem The next lines delete files and folders created when this step is performed.
cd %temp%
if exist pybackup.step3.log.txt del pybackup.step3.log.txt
if exist pybackup\step3 rd /s /q pybackup\step3

Rem Simply validate the last folder created
cd pybackup
ren step2 step3
attrib -a step3\*.* /s
pybackup -v step3
@ren %temp%\pybackup.log.txt pybackup.step3.log.txt
attrib step3\*.* /s >>%temp%\pybackup.step3.log.txt
%temp%\pybackup.step3.log.txt
