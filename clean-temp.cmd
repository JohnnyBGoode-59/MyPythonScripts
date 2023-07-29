@echo off
Rem Remove all files in the temp folder
del /q %temp%\*.*
for /d %%i in (%temp%) do (
	rd /s /q %%i
	)
