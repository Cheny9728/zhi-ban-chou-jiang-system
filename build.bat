@echo off
chcp 65001
echo 清理旧的构建文件...
rmdir /s /q build
rmdir /s /q dist

echo 安装必要依赖...
pip install --upgrade pip
pip install pyinstaller==5.13.2
pip install pillow
pip install pandas
pip install openpyxl
pip install numpy

echo 开始打包...
pyinstaller --clean ^
    --onefile ^
    --noconsole ^
    --upx-dir="upx" ^
    --add-data "Imgs\LOGO.png;Imgs" ^
    --icon "Imgs\值班抽奖系统.ico" ^
    --exclude-module matplotlib ^
    --exclude-module scipy ^
    --exclude-module PyQt5 ^
    --exclude-module PySide2 ^
    --exclude-module IPython ^
    --exclude-module jupyter ^
    --exclude-module notebook ^
    --exclude-module sphinx ^
    --exclude-module pytest ^
    --exclude-module PIL.ImageDraw ^
    --exclude-module PIL.ImageFont ^
    --exclude-module PIL.ImageFilter ^
    --exclude-module PIL.ImageEnhance ^
    --exclude-module PIL.ImageColor ^
    --exclude-module PIL.ImageGrab ^
    --exclude-module PIL.ImageOps ^
    --exclude-module PIL.ImageQt ^
    --exclude-module PIL.ImageWin ^
    --exclude-module PIL.ImageMath ^
    --exclude-module PIL.ImageShow ^
    --exclude-module PIL.ImagePath ^
    --exclude-module PIL.ImageMorph ^
    --exclude-module PIL.ImagePalette ^
    --exclude-module PIL.ImageSequence ^
    --exclude-module PIL.ImageStat ^
    --hidden-import numpy ^
    --hidden-import numpy.random ^
    --hidden-import pandas ^
    --hidden-import pandas.plotting ^
    --hidden-import pandas.core.frame ^
    --hidden-import pandas.core.series ^
    --hidden-import pandas.core.groupby ^
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