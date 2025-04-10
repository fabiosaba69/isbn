
import PyInstaller.__main__
import sys
import os

PyInstaller.__main__.run([
    'app.py',  # Changed from main.py since app.py contains the Flask application
    '--onefile',
    '--add-data=templates:templates',
    '--add-data=static:static',
    '--name=ISBN_Manager',
    '--hidden-import=flask',
    '--hidden-import=sqlalchemy',
    '--hidden-import=isbnlib',
    '--hidden-import=reportlab',
    '--hidden-import=barcode',
    '--hidden-import=pillow'
])
