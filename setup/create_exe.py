import os
import PyInstaller.__main__


PyInstaller.__main__.run([
    '--name=%s' % "FalconVoucherChecker",
    '--onefile',
    '--windowed',
    '--hidden-import=%s' % 'wx',
    '--hidden-import=%s' % 'wx._xml',
    '--add-data=%s;%s' % (r'..\images', r'.\images'),
    '--add-binary=%s;%s' % (r'..\driver', r'.\driver'),
    '--icon=%s' % r"falcon_logo.ico",
    '--distpath=%s' % '.',
    os.path.join('..', 'main.py'),
])
