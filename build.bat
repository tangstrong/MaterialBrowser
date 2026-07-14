@echo off
chcp 65001 >nul
echo ========================================
echo   MaterialBrowser 构建脚本
echo ========================================
echo.

REM 检查 Python
python --version >nul 2>&1
if errorlevel 1 (
    echo [错误] 未检测到 Python，请先安装 Python 3.10+
    echo   下载地址: https://www.python.org/downloads/
    pause
    exit /b 1
)

REM 安装依赖
echo [1/3] 安装依赖…
pip install -r requirements.txt -q
echo [OK]

REM 构建
echo [2/3] PyInstaller 构建…
pyinstaller MaterialBrowser.spec --noconfirm
echo [OK]

echo.
echo ========================================
echo   构建完成！
echo   输出目录: dist\MaterialBrowser
echo   双击 MaterialBrowser.exe 运行
echo ========================================
pause
