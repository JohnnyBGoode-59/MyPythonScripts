call camera-backup.py
for /d %%d in (*) do (
	cd %%d
	call camera-backup.py
	cd ..
	rd %%d
	)
