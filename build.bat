@echo off
chcp 65001

echo 清理旧的构建文件...
rmdir /s /q build
rmdir /s /q dist
del /f /q 值班抽奖系统.spec

echo 安装必要依赖...
pip install --upgrade pip
pip install pyinstaller==5.13.2
pip install pillow
pip install pandas
pip install openpyxl
pip install numpy

echo 开始打包...
pyinstaller ^
    --noconfirm ^
    --onefile ^
    --windowed ^
    --add-data "Imgs/LOGO.png;Imgs" ^
    --icon "Imgs/值班抽奖系统.ico" ^
    --hidden-import pandas ^
    --hidden-import numpy ^
    --hidden-import PIL ^
    --name "值班抽奖系统" ^
    "值班抽奖系统.py"

if errorlevel 1 (
    echo 打包失败，请检查错误信息
    pause
    exit /b 1
)

echo 打包完成！
echo 可执行文件位于 dist 文件夹中
pause