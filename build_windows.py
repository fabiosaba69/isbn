
import PyInstaller.__main__
import os

PyInstaller.__main__.run([
    'app.py',
    '--onefile',
    '--name=ISBN_Manager',
    '--add-data=templates:templates',
    '--add-data=static:static',
    '--hidden-import=flask',
    '--hidden-import=flask_sqlalchemy',
    '--hidden-import=sqlalchemy',
    '--hidden-import=isbnlib',
    '--hidden-import=reportlab',
    '--hidden-import=barcode',
    '--hidden-import=pillow',
    '--hidden-import=email_validator'
])
