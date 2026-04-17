#!/bin/bash
# 自动部署脚本 - 拉取最新代码并重启 Streamlit

cd /Users/admin/.openclaw/workspace_bot2/weekly-dashboard

# 拉取最新代码
echo "📥 拉取最新代码..."
git pull origin main

# 停止旧的 streamlit 进程
echo "🛑 停止旧进程..."
pkill -f "streamlit run.*sky/app.py" 2>/dev/null || true
sleep 2

# 启动新的 streamlit
echo "🚀 启动 Streamlit..."
cd /Users/admin/.openclaw/workspace_bot2/weekly-dashboard/sky
nohup python3 -m streamlit run app.py --server.headless true --server.port 8501 > /tmp/streamlit.log 2>&1 &

# 等待启动
sleep 3

# 检查是否启动成功
if pgrep -f "streamlit run.*sky/app.py" > /dev/null; then
    echo "✅ Streamlit 启动成功"
    echo "📍 访问地址: http://localhost:8501"
else
    echo "❌ Streamlit 启动失败"
    tail -20 /tmp/streamlit.log
    exit 1
fi
