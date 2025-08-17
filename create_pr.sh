#!/bin/bash

# 创建GitHub Pull Request的脚本

echo "=== 创建Pull Request ==="
echo ""

# 检查当前分支
CURRENT_BRANCH=$(git branch --show-current)
echo "当前分支: $CURRENT_BRANCH"

# 检查是否有未提交的修改
if [ -n "$(git status --porcelain)" ]; then
    echo "警告: 有未提交的修改"
    git status --short
    echo ""
    read -p "是否继续? (y/N): " -n 1 -r
    echo
    if [[ ! $REPLY =~ ^[Yy]$ ]]; then
        echo "取消操作"
        exit 1
    fi
fi

# 检查远程分支是否存在
if ! git ls-remote --heads origin $CURRENT_BRANCH | grep -q $CURRENT_BRANCH; then
    echo "错误: 远程分支 $CURRENT_BRANCH 不存在"
    echo "请先推送分支: git push origin $CURRENT_BRANCH"
    exit 1
fi

echo ""
echo "准备创建Pull Request..."
echo ""

# 读取PR描述
if [ -f "PR_DESCRIPTION.md" ]; then
    echo "找到PR描述文件: PR_DESCRIPTION.md"
    PR_BODY=$(cat PR_DESCRIPTION.md)
else
    echo "未找到PR描述文件，将使用默认描述"
    PR_BODY="修复专利撰写工作流并集成测试模式功能"
fi

# 构建PR标题
PR_TITLE="修复专利撰写工作流并集成测试模式"

echo "PR标题: $PR_TITLE"
echo ""

# 使用GitHub CLI创建PR（如果可用）
if command -v gh &> /dev/null; then
    echo "使用GitHub CLI创建Pull Request..."
    echo ""
    
    # 创建PR
    gh pr create \
        --title "$PR_TITLE" \
        --body "$PR_BODY" \
        --base main \
        --head $CURRENT_BRANCH
    
    if [ $? -eq 0 ]; then
        echo ""
        echo "✅ Pull Request创建成功!"
        echo ""
        echo "下一步操作:"
        echo "1. 访问GitHub查看PR详情"
        echo "2. 进行代码审查"
        echo "3. 运行CI/CD检查"
        echo "4. 合并到主分支"
    else
        echo "❌ Pull Request创建失败"
        exit 1
    fi
else
    echo "GitHub CLI未安装，请手动创建Pull Request"
    echo ""
    echo "请访问以下链接创建PR:"
    echo "https://github.com/valkryhx/patent_agents/compare/main...$CURRENT_BRANCH"
    echo ""
    echo "PR标题: $PR_TITLE"
    echo ""
    echo "PR描述:"
    echo "$PR_BODY"
    echo ""
    echo "或者安装GitHub CLI:"
    echo "https://cli.github.com/"
fi

echo ""
echo "=== 完成 ==="