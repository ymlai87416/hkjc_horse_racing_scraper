@echo off
REM 创建虚拟环境的脚本 (Windows)
REM 使用方法: setup_venv.bat

echo 正在创建虚拟环境...

REM 创建虚拟环境
python -m venv venv

REM 激活虚拟环境
echo 正在激活虚拟环境...
call venv\Scripts\activate.bat

REM 升级 pip
echo 正在升级 pip...
python -m pip install --upgrade pip

REM 安装依赖
echo 正在安装项目依赖...
pip install -r requirements.txt

echo.
echo ✅ 虚拟环境设置完成！
echo.
echo 要激活虚拟环境，请运行：
echo   venv\Scripts\activate
echo.
echo 要退出虚拟环境，请运行：
echo   deactivate
echo.

pause

