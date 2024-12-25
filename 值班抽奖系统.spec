# -*- mode: python ; coding: utf-8 -*-


a = Analysis(
    ['值班抽奖系统.py'],
    pathex=[],
    binaries=[],
    datas=[('Imgs\\LOGO.png', 'Imgs')],
    hiddenimports=[
        'numpy', 
        'numpy.random', 
        'pandas',
        'pandas.plotting',
        'pandas.core.frame',
        'pandas.core.series',
        'pandas.core.groupby'
    ],
    hookspath=[],
    hooksconfig={},
    runtime_hooks=[],
    excludes=[
        'matplotlib', 'scipy', 'PyQt5', 'PySide2', 'IPython', 
        'jupyter', 'notebook', 'sphinx', 'pytest',
        'PIL.ImageDraw', 'PIL.ImageFont', 'PIL.ImageFilter',
        'PIL.ImageEnhance', 'PIL.ImageColor', 'PIL.ImageGrab',
        'PIL.ImageOps', 'PIL.ImageQt', 'PIL.ImageWin',
        'PIL.ImageMath', 'PIL.ImageShow', 'PIL.ImagePath',
        'PIL.ImageMorph', 'PIL.ImagePalette', 'PIL.ImageSequence',
        'PIL.ImageStat'
    ],
    noarchive=False,
)
pyz = PYZ(a.pure)

exe = EXE(
    pyz,
    a.scripts,
    a.binaries,
    a.datas,
    [],
    name='值班抽奖系统',
    debug=False,
    bootloader_ignore_signals=False,
    strip=False,
    upx=True,
    upx_exclude=[],
    runtime_tmpdir=None,
    console=False,
    disable_windowed_traceback=False,
    argv_emulation=False,
    target_arch=None,
    codesign_identity=None,
    entitlements_file=None,
    icon=['Imgs\\值班抽奖系统.ico'],
)
