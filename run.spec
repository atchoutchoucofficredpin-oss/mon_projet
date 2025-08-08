# -*- mode: python ; coding: utf-8 -*-

block_cipher = None

# Le chemin exact vers les paquets de votre environnement virtuel
full_site_packages_path = 'C:\\MON PROJET\\venv\\Lib\\site-packages'

a = Analysis(
    ['run.py'],
    pathex=['C:\\MON PROJET'],
    binaries=[],
    datas=[
        # Vos fichiers statiques et templates de projet
        ('staticfiles', 'staticfiles'),
        ('gestion_produits_stock/templates/gestion_produits_stock', 'gestion_produits_stock/templates/gestion_produits_stock'),
        # Les templates du thème Jazzmin
        (full_site_packages_path + '\\jazzmin\\templates', 'jazzmin\\templates'),
        # Les templates de l'admin de Django
        (full_site_packages_path + '\\django\\contrib\\admin\\templates', 'django\\contrib\\admin\\templates'),
        # Les fichiers statiques de Jazzmin et de l'admin de Django
        (full_site_packages_path + '\\jazzmin\\static', 'jazzmin\\static'),
        (full_site_packages_path + '\\django\\contrib\\admin\\static', 'django\\contrib\\admin\\static'),
    ],
    # Important : jazzmin doit être un "hidden import"
    hiddenimports=['jazzmin', 'whitenoise', 'whitenoise.middleware'],
    hookspath=[],
    hooksconfig={},
    runtime_hooks=[],
    excludes=[],
    noarchive=False,
    optimize=0,
)
pyz = PYZ(a.pure)

exe = EXE(
    pyz,
    a.scripts,
    a.binaries,
    a.datas,
    [],
    name='run',
    debug=False,
    bootloader_ignore_signals=False,
    strip=False,
    upx=True,
    upx_exclude=[],
    runtime_tmpdir=None,
    console=True,
    disable_windowed_traceback=False,
    argv_emulation=False,
    target_arch=None,
    codesign_identity=None,
    entitlements_file=None,
)