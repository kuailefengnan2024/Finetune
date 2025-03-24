@echo off
echo 正在运行Python虚拟环境安装脚本...
echo.

:: 尝试用py启动器运行Python 3.10
py -3.10 Train_Scripts\setup_venv.py %*
if %ERRORLEVEL% == 0 goto end

:: 如果失败，尝试用python命令
echo 尝试使用python命令...
python Train_Scripts\setup_venv.py %*
if %ERRORLEVEL% == 0 goto end

:: 如果还是失败，尝试直接用python3.10命令
echo 尝试使用python3.10命令...
python3.10 Train_Scripts\setup_venv.py %*
if %ERRORLEVEL% == 0 goto end

echo.
echo 安装失败！请确保已安装Python 3.10
pause

:end
echo.
echo 安装完成！
pause 