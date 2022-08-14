#!/bin/bash
source hfwa_env/bin/activate || {
    echo "无法启动高频词汇分析，请运行 ./install_script.sh"
    exit 1
}

hfwa_env/bin/python launcher.py
deactivate