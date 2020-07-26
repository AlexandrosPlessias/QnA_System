@echo off
set file=%temp%\corenlp.shutdown
set key_var=0
for /f "tokens=*" %%A in (%file%) do (set key_var=%%A)
wget "localhost:9000/shutdown?key=%key_var%" -O -