@echo off
for %%n in (01 02 03 04 05 06 07 08 09 10 11 12) do (
	echo %%n
	for /d %%d in (20??-%%n* 20??_%%n*) do (
		echo %%d
		md %%n
		move %%d\*.* %%n
		)
	)
ren 01 01Jan
ren 02 02Feb
ren 03 03Mar
ren 04 04Apr
ren 05 05May
ren 06 06Jun
ren 07 07Jul
ren 08 08Aug
ren 09 09Sep
ren 10 10Oct
ren 11 11Nov
ren 12 12Dec
call clean-empty
