# -*- mode: python -*-
# coding=utf-8

import os

# Globals #####################################################################
backend_dir = os.path.abspath(os.path.join('..','backend'))
static_dir = os.path.abspath(os.path.join(backend_dir, 'static'))

# PyInstaller #################################################################
block_cipher = None
entry_point =  os.path.join(backend_dir, 'ctxdoing.py')
binary_name = 'ctxdoing'

a = Analysis([entry_point],
             pathex=[backend_dir],
             binaries=[],
             datas=[(static_dir,'static')],
             hiddenimports=[],
             hookspath=[],
             runtime_hooks=[],
             excludes=[],
             win_no_prefer_redirects=False,
             win_private_assemblies=False,
             cipher=block_cipher)

pyz = PYZ(a.pure, a.zipped_data,
             cipher=block_cipher)
exe = EXE(pyz,
          a.scripts,
          a.binaries,
          a.zipfiles,
          a.datas,
          name=binary_name,
          debug=False,
          strip=False,
          upx=True,
          console=True )
