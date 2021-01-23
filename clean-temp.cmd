@echo off
del /q %temp%\*.*
for /d %%i in (%temp%) do (
	rd /s /q %%i
	)
