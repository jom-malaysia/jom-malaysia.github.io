@echo off
chcp 65001 >nul
cd /d "%~dp0"
echo === サイトに反映（GitHub Pages 再デプロイ） ===
echo.
git add -A
git commit -m "サイト更新"
git push
echo.
echo 反映まで 1〜2 分ほどかかります。
echo.
pause
