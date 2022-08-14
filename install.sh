#!/bin/bash
USE_TSINGHUA_SOURCE="true"
TSINGHUA_SOURCE_HOMEBREW_BREW="https://mirrors.tuna.tsinghua.edu.cn/git/homebrew/brew.git"
TSINGHUA_SOURCE_HOMEBREW_CORE="https://mirrors.tuna.tsinghua.edu.cn/git/homebrew/homebrew-core.git"

set -e

if ! brew --version ; then
	echo "正在安装 Homebrew..."
	if [ $USE_TSINGHUA_SOURCE == "true" ] ; then
		echo "正在配置 Homebrew 使用 清华源..."
		HOMEBREW_BREW_GIT_REMOTE="${TSINGHUA_SOURCE_HOMEBREW_BREW}" HOMEBREW_CORE_GIT_REMOTE="${TSINGHUA_SOURCE_HOMEBREW_CORE}" /bin/bash -c "$(curl -fsSL https://raw.githubusercontent.com/Homebrew/install/master/install.sh)"
	else
		/bin/bash -c "$(curl -fsSL https://raw.githubusercontent.com/Homebrew/install/master/install.sh)"
	fi
fi

brew update
echo "正在安装 poppler..."
brew install poppler
echo "正在安装 tesseract..."
brew install tesseract
echo "正在安装 virtuelenv..."
brew install virtualenv

echo "正在配置 Virtuelenv 环境..."
mkdir -p hfwa_env
virtualenv hfwa_env
source ./hfwa_env/bin/activate

echo "正在安装项目依赖..."
./hfwa_env/bin/python -m pip install  -r requirements.txt

deactivate
