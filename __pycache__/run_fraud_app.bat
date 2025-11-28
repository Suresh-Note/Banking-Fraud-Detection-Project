@echo off
echo Starting Fraud Detection System...
echo ------------------------------------

REM 1) Go to your project folder (VERY IMPORTANT)
cd /d "C:\Users\ksrsu\OneDrive\Desktop\SONY\ML\sql fraud detection"

REM 2) (Optional) activate environment if you use one
REM call env\Scripts\activate
REM call conda activate myenv

REM 3) Start FastAPI server in this folder
start cmd /k "uvicorn api:app --reload"

REM 4) Wait a bit for the server to start
timeout /t 3 > nul

REM 5) Open the UI in browser
start "" "http://127.0.0.1:8000/ui"

exit
