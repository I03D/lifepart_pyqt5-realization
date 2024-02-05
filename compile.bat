REM pyinstaller --onefile LifePart.py
pyinstaller --onefile --hidden-import pywintypes Blinker5.pyw
REM pyinstaller --onefile --hidden-import pywintypes Blinker45.pyw
copy config.ini dist\config.ini
copy flower.png dist\flower.png
copy sun.png dist\sun.png
