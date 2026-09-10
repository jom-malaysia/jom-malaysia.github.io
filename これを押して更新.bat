@echo off
setlocal
cd /d "%~dp0"
echo ==========================================================
echo  Jom! Malaysia archive  --  update ^& publish (one click)
echo ==========================================================
echo.

REM --- make sure git knows who you are (first run only) ---
git config user.name  >nul 2>&1 || git config --global user.name  "sugitani0713"
git config user.email >nul 2>&1 || git config --global user.email "sugitani0713@gmail.com"

echo [1/4] Converting new PDFs into images...
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
echo [2/4] Staging changes...
git add -A

echo.
echo [3/4] Saving...
git diff --cached --quiet
if not errorlevel 1 (
  echo  ^(no changes to publish - already up to date^)
  echo.
  pause
  exit /b 0
)
git commit -m "site update"
if errorlevel 1 (
  echo.
  echo  ERROR: could not save the changes ^(git commit failed^).
  echo  Take a screenshot of this window and send it.
  echo.
  pause
  exit /b 1
)

echo.
echo [4/4] Publishing...
git push
if errorlevel 1 (
  echo.
  echo  ERROR: could not publish ^(git push failed^).
  echo  Check your internet connection and try again.
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
