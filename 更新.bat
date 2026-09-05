@echo off
chcp 65001 >nul
cd /d "%~dp0"
echo === Mtown 連載マンガ アーカイブ  ビルド ===
python build.py
if errorlevel 1 (
  echo.
  echo うまくいかない場合:  pip install pymupdf pillow  を実行してから もう一度お試しください。
)
echo.
pause
