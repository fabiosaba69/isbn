
import PyInstaller.__main__
import sys
import os

PyInstaller.__main__.run([
    'main.py',
    '--onefile',
    '--windowed',
    '--add-data=templates;templates',
    '--add-data=static;static',
    '--icon=generated-icon.png',
    '--name=ISBN_Manager',
    '--hidden-import=flask',
    '--hidden-import=sqlalchemy',
    '--hidden-import=isbnlib',
    '--hidden-import=reportlab',
    '--hidden-import=barcode',
    '--hidden-import=pillow'
])
