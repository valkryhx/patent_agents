#!/bin/bash

echo "=== 工作流监控脚本启动 ==="
echo "每3分钟检查一次工作流状态"
echo "================================"

while true; do
    echo ""
    echo "=== $(date '+%Y-%m-%d %H:%M:%S') 工作流进度汇报 ==="
    echo ""
    
    # 检查整体进度
    echo "📊 整体进度:"
    if [ -d "output" ]; then
        doc_count=$(find output -name "*.md" 2>/dev/null | wc -l)
        echo "   已生成文档数量: $doc_count"
    else
        echo "   输出目录不存在"
    fi
    
    echo ""
    echo "🤖 智能体状态:"
    
    # 检查各个智能体状态
    agents=("coordinator" "planner" "searcher" "discusser" "writer" "reviewer" "rewriter")
    for agent in "${agents[@]}"; do
        echo "   $agent:"
        if [ -f "output/logs/${agent}_agent.log" ]; then
            tail -1 "output/logs/${agent}_agent.log" 2>/dev/null | sed 's/^/     /'
        else
            echo "     日志文件不存在"
        fi
    done
    
    echo ""
    echo "🔍 最新任务执行:"
    if [ -d "output/logs" ]; then
        grep -r "🎯\|✅.*任务执行\|❌" output/logs/ 2>/dev/null | tail -3 | sed 's/^/   /'
    else
        echo "   日志目录不存在"
    fi
    
    echo ""
    echo "⏰ 等待3分钟后再次检查..."
    echo "=========================================="
    sleep 180
done