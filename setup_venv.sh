#!/bin/bash

# 创建虚拟环境的脚本
# 使用方法: bash setup_venv.sh

echo "正在创建虚拟环境..."

# 创建虚拟环境
python3 -m venv venv

# 激活虚拟环境
echo "正在激活虚拟环境..."
source venv/bin/activate

# 升级 pip
echo "正在升级 pip..."
pip install --upgrade pip

# 安装依赖
echo "正在安装项目依赖..."
pip install -r requirements.txt

echo ""
echo "✅ 虚拟环境设置完成！"
echo ""
echo "要激活虚拟环境，请运行："
echo "  source venv/bin/activate"
echo ""
echo "要退出虚拟环境，请运行："
echo "  deactivate"
echo ""

