# -*- mode: python ; coding: utf-8 -*-

block_cipher = None


a = Analysis(['..\\main.py'],
             pathex=['C:\\Sources\\FalconVoucherChecker\\setup'],
             binaries=[('..\\driver', '.\\driver')],
             datas=[('..\\images', '.\\images')],
             hiddenimports=['wx', 'wx._xml'],
             hookspath=[],
             runtime_hooks=[],
             excludes=[],
             win_no_prefer_redirects=False,
             win_private_assemblies=False,
             cipher=block_cipher,
             noarchive=False)
pyz = PYZ(a.pure, a.zipped_data,
             cipher=block_cipher)
exe = EXE(pyz,
          a.scripts,
          a.binaries,
          a.zipfiles,
          a.datas,
          [],
          name='FalconVoucherChecker',
          debug=False,
          bootloader_ignore_signals=False,
          strip=False,
          upx=True,
          upx_exclude=[],
          runtime_tmpdir=None,
          console=False , icon='falcon_logo.ico')
