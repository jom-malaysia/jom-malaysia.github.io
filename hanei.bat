@echo off
setlocal
cd /d "%~dp0"
echo === Push updates to the site (GitHub Pages redeploy) ===
echo.
git add -A
git commit -m "site update"
git push
echo.
echo  Live in about 1-2 minutes.
echo.
pause
