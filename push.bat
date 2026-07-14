@echo off
chcp 65001 >nul
echo ==========================================
echo   MaterialBrowser — GitHub 上传脚本
echo ==========================================
echo.
echo 需要先做以下准备（只需做一次）：
echo.
echo   1. 打开 https://github.com/new
echo   2. 创建一个新仓库，名字叫: MaterialBrowser
echo   3. 不要勾选任何选项，直接点 Create repository
echo   4. 仓库创建后，复制仓库 URL（类似 https://github.com/你的用户名/MaterialBrowser.git）
echo   5. 回来这里运行脚本
echo.
set /p REPO_URL="请粘贴仓库 URL: "
echo.
echo [1/3] 初始化 Git …
git init
git add .
git commit -m "Initial commit: MaterialBrowser v1.0"

echo.
echo [2/3] 添加远程仓库 …
git remote add origin "%REPO_URL%"

echo.
echo [3/3] 推送代码 …
git branch -M main
git push -u origin main

echo.
echo ==========================================
echo   完成！接下来去 GitHub Actions 构建 exe：
echo   1. 打开你的仓库页面
echo   2. 点击 Actions 标签
echo   3. 点击 "Build Windows EXE"
echo   4. 点击右侧 "Run workflow"
echo   5. 等 5-8 分钟，在 Artifacts 下载
echo ==========================================
pause
