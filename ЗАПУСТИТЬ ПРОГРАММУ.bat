@echo off
cd /d "%~dp0"
python -c "import pymupdf" >nul 2>&1
if errorlevel 1 goto missing
python -X utf8 "%~dp0app.py"
if errorlevel 1 goto failed
exit /b 0
:missing
echo Python or PyMuPDF is missing. Run: python -m pip install pymupdf
pause
exit /b 1
:failed
echo Application failed. See the error above.
pause
exit /b 1
