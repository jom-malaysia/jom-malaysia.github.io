@echo off
setlocal
cd /d "%~dp0"
echo ==========================================================
echo  Jom! Malaysia archive  --  update ^& publish (one click)
echo ==========================================================
echo.

echo [1/3] Converting new PDFs into images...
python build.py
if errorlevel 1 (
  echo.
  echo  Conversion failed. Run this once, then try again:
  echo      pip install pymupdf pillow
  echo.
  pause
  exit /b 1
)

echo.
echo [2/3] Saving changes...
git add -A
git commit -m "site update"

echo.
echo [3/3] Publishing...
git push
if errorlevel 1 (
  echo.
  echo  Publish failed. Check your internet connection and try again.
  echo.
  pause
  exit /b 1
)

echo.
echo ==========================================================
echo  DONE. The site will update in 1-2 minutes:
echo      https://jom-malaysia.github.io/
echo ==========================================================
echo.
pause
