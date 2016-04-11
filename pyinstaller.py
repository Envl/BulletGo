import  os

if __name__ == '__main__':
    from PyInstaller.__main__ import run
    opts=['main.py','--onefile','--windowed','--icon=tmpIcon.ico']
    run(opts)