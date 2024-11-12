#!/bin/bash


# 获取脚本的绝对路径
SCRIPT_DIR=$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)
PROCESS_NAME="python "$SCRIPT_DIR/ai_bot.py""

# 使用 pgrep 查找进程是否存在
if pgrep -f "$PROCESS_NAME" > /dev/null; then
    echo "进程 '$PROCESS_NAME' 已经在运行。"
else
    echo "进程不存在，启动新进程。"

    # 启动进程
    nohup python "$SCRIPT_DIR/ai_bot.py" "$TOKEN" "$YOUR_USER_ID" > /dev/null 2>&1 &
    sleep 2

    echo "进程 '$PROCESS_NAME' 已启动。"
fi

