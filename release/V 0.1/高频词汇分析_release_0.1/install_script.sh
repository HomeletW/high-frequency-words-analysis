#!/bin/bash

SCRIPT_DIR=$(dirname "$0")

cd "$SCRIPT_DIR" || {
  echo "Failure"
  exit 1
}

echo "Working in $(pwd)"

echo "Installing Virtuelenv..."

# first install virtualenv

python3 -m pip install virtualenv

echo "Creating Virtuelenv enviroment..."

virtualenv hfwa_env

source hfwa_env/bin/activate

echo "Installing Dependencies..."

# now install all required pacakges in requirements.txt

hfwa_env/bin/python -m pip install -r requirements.txt

echo "Prepare to build App..."

# after install complete we build the app

rm -rf build dist

hfwa_env/bin/python setup.py py2app -A

deactivate

echo "Finnished!"

echo "安装结束！已在 dist 文件夹里创造 高频词汇分析.app"

open -R "dist/高频词汇分析.app"
