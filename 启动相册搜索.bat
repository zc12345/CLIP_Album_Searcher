@echo off
chcp 65001 >nul
title CLIP相册搜索 - 一键启动

echo ====================================
echo     CLIP 智能相册搜索系统
echo ====================================
echo.

REM 检查Python是否安装
python --version >nul 2>&1
if %errorlevel% neq 0 (
    echo [错误] 未检测到Python，请先安装Python
    echo 下载地址：https://www.python.org/downloads/
    pause
    exit /b 1
)

REM 设置HuggingFace镜像
set HF_ENDPOINT=https://hf-mirror.com
set HF_HUB_ENABLE_HF_TRANSFER=1
echo [设置] 已设置HuggingFace镜像: %HF_ENDPOINT%

REM 检查依赖
echo [检查] 正在检查依赖包...
pip show open_clip_torch >nul 2>&1
if %errorlevel% neq 0 (
    echo [安装] 正在安装依赖包...
    pip install -r requirements.txt
    if %errorlevel% neq 0 (
        echo [错误] 依赖安装失败
        pause
        exit /b 1
    )
)

REM 创建默认配置文件
if not exist "config.json" (
    echo [配置] 创建默认配置文件...
    echo {"root_path": "D:\\documents\\images", "dump_path": "db.pt", "backup_path": "backup", "host": "localhost", "port": 8501} > config.json
)

REM 启动应用
echo.
echo [启动] 正在启动Web界面...
echo [提示] 浏览器将自动打开 http://localhost:8501
echo [提示] 按 Ctrl+C 停止服务
echo.

REM 启动Streamlit应用
streamlit run app.py -- --config config.json
pause