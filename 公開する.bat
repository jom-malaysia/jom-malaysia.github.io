@echo off
chcp 65001 >nul
cd /d "%~dp0"
echo ============================================
echo  Jom! マレーシア！ アーカイブ  無料サイト公開
echo ============================================
echo.
echo GitHub の公開リポジトリを作成して、無料サイト(GitHub Pages)にします。
echo （GitHub CLI は認証済みです。アカウント作成などは不要）
echo.
pause
echo.

echo [1/3] 変更をコミット...
git add -A
git commit -m "サイト更新" 2>nul

echo [2/3] 公開リポジトリを作成してアップロード...
gh repo create mtown-jom-malaysia --public --source=. --remote=origin --push
if errorlevel 1 goto :err

echo [3/3] GitHub Pages を有効化...
for /f "delims=" %%u in ('gh api user --jq .login') do set GHUSER=%%u
gh api -X POST repos/%GHUSER%/mtown-jom-malaysia/pages -f "source[branch]=main" -f "source[path]=/" 2>nul

echo.
echo ============================================
echo  完了！ 1〜2分後に下記URLで公開されます：
echo.
echo    https://%GHUSER%.github.io/mtown-jom-malaysia/
echo.
echo  次回からの更新は「更新.bat」→「反映する.bat」だけです。
echo ============================================
echo.
pause
exit /b 0

:err
echo.
echo リポジトリ作成でエラーが出ました。すでに同名リポジトリがある場合は
echo GitHubで別名にするか、既存のものを削除してからやり直してください。
echo.
pause
exit /b 1
