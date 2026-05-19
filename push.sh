#!/bin/bash

# Network Agent 项目 - GitHub 推送脚本
# 使用方法: bash push_to_github.sh <GITHUB_TOKEN>

TOKEN=${1:-$GITHUB_TOKEN}

if [ -z "$TOKEN" ]; then
    echo "错误: 需要 GitHub Personal Access Token"
    echo "请访问 https://github.com/settings/tokens 生成 token"
    echo "然后运行: bash push_to_github.sh YOUR_TOKEN"
    exit 1
fi

REPO="toneliu/nethealer"
BRANCH="main"

echo "正在推送代码到 GitHub..."

git remote add origin https://github.com/$REPO.git 2>/dev/null || true

git push https://$TOKEN@github.com/$REPO.git $BRANCH

if [ $? -eq 0 ]; then
    echo "✅ 推送成功!"
    echo "📦 仓库地址: https://github.com/$REPO"
else
    echo "❌ 推送失败，请检查 token 权限"
fi
