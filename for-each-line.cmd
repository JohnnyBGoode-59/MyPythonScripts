@Echo off
Rem For each line in a file... do something.
Rem Use %l for that line of the file on the command line.
SetLocal
set cmdline=%*
for /F "tokens=1" %%l in (%temp%\new-files.lst) do (
	%cmdline%
	)