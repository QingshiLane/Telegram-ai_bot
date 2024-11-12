#!/bin/bash

# 获取脚本的绝对路径
SCRIPT_DIR=$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)
PROCESS_NAME="python "$SCRIPT_DIR/ai_bot.py""

# 使用 pgrep 查找进程是否存在
if pgrep -f "$PROCESS_NAME" > /dev/null; then
    echo "进程 '$PROCESS_NAME' 在运行。"
    pkill -f "$PROCESS_NAME"
    echo "进程已终止，机器人停止运行。"
    sleep 1
else
    echo "进程不存在，机器人不在运行，无需停止。"

fi

