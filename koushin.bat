@echo off
setlocal
cd /d "%~dp0"
echo === Convert new PDFs into site images (build.py) ===
echo.
python build.py
if errorlevel 1 (
  echo.
  echo  If it failed, run this once first:  pip install pymupdf pillow
)
echo.
pause
