@echo off
chcp 65001 >nul
echo ============================================
echo    Ngrok 内网穿透 启动器
echo ============================================
echo.

:: 检查ngrok是否安装
ngrok --version >nul 2>&1
if errorlevel 1 (
    echo [错误] 未检测到ngrok
    echo.
    echo 请先下载并配置ngrok:
    echo.
    echo 步骤1: 访问 https://ngrok.com/download
    echo 步骤2: 下载Windows版本的ngrok
    echo 步骤3: 解压得到ngrok.exe
    echo 步骤4: 把ngrok.exe放到这个文件夹里
    echo.
    echo 或者你可以复制下面的命令在PowerShell中运行:
    echo.
    echo Invoke-WebRequest -Uri "https://bin.equinox.io/c/bNyj1mQVY4c/ngrok-v3-stable-windows-amd64.zip" -OutFile "ngrok.zip"
    echo.
    pause
    exit /b 1
)

echo [提示] 确认MCP服务器已经启动了吗？
echo 如果还没启动，请先运行 "启动http.bat"
echo.
echo 正在启动ngrok穿透服务...
echo.

ngrok http 8000

pause
