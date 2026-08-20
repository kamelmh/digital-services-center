@echo off
echo ========================================
echo   DSC Desktop App Builder
echo ========================================
echo.

echo [1/3] Installing PyInstaller...
pip install pyinstaller

echo.
echo [2/3] Building DSC Desktop App...
pyinstaller dsc.spec

echo.
echo [3/3] Build complete!
echo.
echo Output: dist\DSC_Digital_Services_Center.exe
echo.
echo You can now:
echo   1. Run the .exe directly
echo   2. Copy to USB drive
echo   3. Send via WhatsApp/Email
echo   4. Upload to Google Drive
echo.
pause
