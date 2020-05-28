#!/bin/bash

SCRIPT_DIR=$(dirname "$0")

cd "$SCRIPT_DIR" || {
  echo "Fail to cd to current dir"
  exit 1
}

echo "工作地址： $(pwd)"

# first install Homebrew

echo "正在安装 Homebrew..."

/usr/bin/ruby -e "$(curl -fsSL https://cdn.jsdelivr.net/gh/ineo6/homebrew-install/install)"

brew install git

echo "正在配置 Homebrew 使用 清华源..."

git -C "$(brew --repo)" remote set-url origin https://mirrors.tuna.tsinghua.edu.cn/git/homebrew/brew.git

git -C "$(brew --repo homebrew/core)" remote set-url origin https://mirrors.tuna.tsinghua.edu.cn/git/homebrew/homebrew-core.git

git -C "$(brew --repo homebrew/cask)" remote set-url origin https://mirrors.tuna.tsinghua.edu.cn/git/homebrew/homebrew-cask.git

git -C "$(brew --repo homebrew/cask-fonts)" remote set-url origin https://mirrors.tuna.tsinghua.edu.cn/git/homebrew/homebrew-cask-fonts.git

git -C "$(brew --repo homebrew/cask-drivers)" remote set-url origin https://mirrors.tuna.tsinghua.edu.cn/git/homebrew/homebrew-cask-drivers.git

brew update

echo "正在安装 poppler..."

brew install poppler

echo "正在安装 tesseract..."

brew install tesseract

echo "正在安装 Virtuelenv..."

echo "Using Mirror : https://pypi.tuna.tsinghua.edu.cn/simple"

# first install virtualenv

python3 -m pip install -i https://pypi.tuna.tsinghua.edu.cn/simple virtualenv

echo "正在配置 Virtuelenv 环境..."

virtualenv hfwa_env

source hfwa_env/bin/activate

echo "正在安装项目依赖..."

echo "Using Mirror : https://pypi.tuna.tsinghua.edu.cn/simple"

# now install all required pacakges in requirements.txt

hfwa_env/bin/python -m pip install -i https://pypi.tuna.tsinghua.edu.cn/simple -r requirements.txt

echo "开始编译程序..."

# after install complete we build the app

rm -rf build dist

hfwa_env/bin/python setup.py py2app -A

deactivate

echo "Finnished!"

echo "安装结束！已在 dist 文件夹里创造 高频词汇分析.app"

open -R "dist/高频词汇分析.app"
