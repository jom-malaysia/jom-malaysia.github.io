@echo off
setlocal
cd /d "%~dp0"

echo ==========================================================
echo  Publish : Jom! Malaysia archive  --^>  free GitHub Pages
echo ==========================================================
echo.
echo  Creates a PUBLIC GitHub repo "mtown-jom-malaysia",
echo  uploads this folder, and turns on GitHub Pages.
echo  (GitHub CLI is already logged in - no signup needed.)
echo.
pause
echo.

echo [1/4] commit local changes...
git add -A
git commit -m "site update" 1>nul 2>nul

echo [2/4] create public repo + push...
gh repo create mtown-jom-malaysia --public --source "." --remote origin --push
if errorlevel 1 goto ERR

echo [3/4] enable GitHub Pages...
gh api --method POST -H "Accept: application/vnd.github+json" repos/sugitani0713/mtown-jom-malaysia/pages -f "source[branch]=main" -f "source[path]=/" 1>nul 2>nul

echo [4/4] done.
echo.
echo ==========================================================
echo  DONE. The site will be live in 1-2 minutes at:
echo.
echo     https://sugitani0713.github.io/mtown-jom-malaysia/
echo.
echo  Weekly update from now on:
echo     1) double-click  koushin.bat   - convert new PDFs
echo     2) double-click  hanei.bat     - push updates to the site
echo ==========================================================
echo.
pause
exit /b 0

:ERR
echo.
echo  Could not create the repo.
echo  If a repo named "mtown-jom-malaysia" already exists on your
echo  GitHub, delete it (or rename) and run this again.
echo.
pause
exit /b 1
