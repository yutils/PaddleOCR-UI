@echo off
chcp 65001 >nul 2>&1
setlocal

:: 配置项
set "PY_FILE=main.py"
set "VENV_DIR=.venv"
set "PYTHONW_EXE=%VENV_DIR%\Scripts\pythonw.exe"

:: 检查依赖（失败时才显示控制台提示）
if not exist "%PYTHONW_EXE%" (
    echo [错误] 虚拟环境的pythonw.exe不存在：%PYTHONW_EXE%
    echo 请先执行：python -m venv .venv
    pause
    exit /b 1
)
if not exist "%PY_FILE%" (
    echo [错误] 找不到main.py：%PY_FILE%
    pause
    exit /b 1
)

:: 关键：用 start /min /b 强制脱离批处理进程，且无窗口
:: "" 是必须的（start命令的窗口标题占位符），/min 确保即使有窗口也最小化，/b 后台运行
start "" /min /b "%PYTHONW_EXE%" "%PY_FILE%" >nul 2>&1
echo 正在启动...
:: 等待1秒
timeout /t 5 /nobreak >nul 2>&1
:: 强制批处理立即退出，不等待子进程
endlocal
:: 退出码0，且不返回控制台
exit /b 0
