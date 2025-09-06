@echo off
chcp 65001 >nul
title CLIP相册搜索系统

:: 设置窗口大小
mode con:cols=80 lines=25
color 0A

echo.
echo    ╔══════════════════════════════════════════════════════════════╗
echo    ║                                                              ║
echo    ║                CLIP 智能相册搜索系统                        ║
echo    ║                                                              ║
echo    ║                    一键启动 v1.0                             ║
echo    ║                                                              ║
echo    ╚══════════════════════════════════════════════════════════════╝
echo.

REM 设置HuggingFace镜像
set HF_ENDPOINT=https://hf-mirror.com
set HF_HUB_ENABLE_HF_TRANSFER=1
echo    [🌐] 已设置HuggingFace镜像: %HF_ENDPOINT%

REM 检查Python
python --version >nul 2>&1
if %errorlevel% neq 0 (
    echo    [❌] 错误：未检测到Python环境
    echo    [💡] 请先安装Python：https://www.python.org/downloads/
    echo    [💡] 安装时请勾选"Add Python to PATH"
    pause
    exit /b 1
)

echo    [✅] Python环境检查通过

REM 检查依赖
echo    [📦] 正在检查依赖包...
pip show open_clip_torch >nul 2>&1
if %errorlevel% neq 0 (
    echo    [⬇️]  正在安装依赖包，请稍候...
    pip install -r requirements.txt
    if %errorlevel% neq 0 (
        echo    [❌] 依赖安装失败
        pause
        exit /b 1
    )
    echo    [✅] 依赖安装完成
) else (
    echo    [✅] 依赖检查通过
)

REM 创建配置文件
if not exist "config.json" (
    echo    [⚙️]  创建默认配置文件...
    echo {    > config.json
    echo     "root_path": "D:\\documents\\images",    >> config.json
    echo     "dump_path": "db.pt",                   >> config.json
    echo     "backup_path": "backup",                >> config.json
    echo     "host": "localhost",                    >> config.json
    echo     "port": 8501,                           >> config.json
    echo     "model_name": "ViT-B-32",               >> config.json
    echo     "pretrained": "laion2b_s34b_b79k",      >> config.json
    echo     "max_results": 20,                      >> config.json
    echo     "default_threshold": 0.3,               >> config.json
    echo     "hf_endpoint": "https://hf-mirror.com", >> config.json
    echo     "hf_hub_enable_transfer": true           >> config.json
    echo }    >> config.json
    echo    [✅] 配置文件已创建
    echo    [💡] 请根据需要修改 config.json 中的路径设置
)

REM 检查图片目录
for /f "tokens=2 delims=:," %%a in ('findstr "root_path" config.json') do (
    set "img_path=%%~a"
)
set "img_path=%img_path:"=%"
set "img_path=%img_path: =%"

if not exist "%img_path%" (
    echo    [⚠️]  警告：图片目录不存在
    echo    [📁]  当前配置：%img_path%
    echo    [💡]  请修改 config.json 中的 root_path 为您的图片目录
    echo    [💡]  例如："root_path": "C:\\Users\\用户名\\Pictures"
)

echo.
echo    [🚀] 正在启动Web界面...
echo    [🌐] 浏览器将自动打开：http://localhost:8501
echo    [⏹️]  按 Ctrl+C 停止服务
echo.

REM 启动应用
streamlit run app.py -- --config config.json

pause