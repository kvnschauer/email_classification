@echo off
cd /d "C:\repos\email_classification"
"C:\Users\Kevin\AppData\Local\Programs\Python\Python313\python.exe" spam_collector_script.py >> "C:\repos\email_classification\spam_collector_log.txt" 2>&1

REM Now put the computer to sleep (this works on Windows 11)
powershell -Command "& {Add-Type -AssemblyName System.Windows.Forms; [System.Windows.Forms.Application]::SetSuspendState('Suspend', $false, $false)}"