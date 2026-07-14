#!/bin/bash
# MaterialBrowser — GitHub 上传脚本 (Mac/Linux)

echo "=========================================="
echo "  MaterialBrowser — GitHub 上传脚本"
echo "=========================================="
echo ""

# 检查 git
if ! command -v git &> /dev/null; then
    echo "❌ 未检测到 git，请先安装 Git: https://git-scm.com/download/mac"
    exit 1
fi

echo "请先去 GitHub 创建仓库："
echo "  1. 打开 https://github.com/new"
echo "  2. 仓库名字填: MaterialBrowser"
echo "  3. 不要勾选任何选项，点 Create repository"
echo "  4. 复制仓库 URL（类似 https://github.com/你的用户名/MaterialBrowser.git）"
echo ""
read -p "请粘贴仓库 URL: " REPO_URL

echo ""
echo "[1/3] 初始化 Git …"
git init
git add .
git commit -m "Initial commit: MaterialBrowser v1.0"

echo ""
echo "[2/3] 添加远程仓库 …"
git remote add origin "$REPO_URL"

echo ""
echo "[3/3] 推送代码 …"
git branch -M main
git push -u origin main

echo ""
echo "=========================================="
echo "  ✅ 完成！"
echo "  去 GitHub Actions 构建 exe："
echo "  1. 打开仓库 → Actions 标签"
echo "  2. 点 'Build Windows EXE'"
echo "  3. 点 'Run workflow'"
echo "  4. 等 5-8 分钟，Artifacts 下载"
echo "=========================================="
