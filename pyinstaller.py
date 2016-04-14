import  os

if __name__ == '__main__':
    from PyInstaller.__main__ import run
    opts=['BulletGo.py','--onefile','--windowed','--icon=tmpIcon.ico','--upx-dir=FILE']
    run(opts)