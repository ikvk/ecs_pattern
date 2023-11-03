ECHO off
CLS
ECHO Building Trig fall .exe ...

REM https://pyinstaller.org/en/stable/usage.html
REM pyinstaller 6.0.0

cd %~dp0

set BUILD_EDITION=%1
set GAME_VERSION="1.0.3"

if "%BUILD_EDITION%" == "pay" (
    echo PACKAGE_EDITION = 'pay'> "../common_tools/build_flags.py"
    goto :build
) else if "%BUILD_EDITION%" == "free" (
    echo PACKAGE_EDITION = 'free'> "../common_tools/build_flags.py"
    goto :build
) else (
    echo ERROR: Firts argument BUILD_EDITION must be: free or pay, specified: "%BUILD_EDITION%"
    goto :end
)

:build
echo BUILD_EDITION = %BUILD_EDITION%
echo GAME_VERSION = %GAME_VERSION%
ECHO ---
C:\python\venv\trig310\Scripts\pyinstaller ^
    --clean ^
    --onefile ^
    --noconfirm ^
    --noconsole ^
    --name "Trig fall %GAME_VERSION% %BUILD_EDITION%.exe" ^
    --add-data "../res:res" ^
    --splash "../_docs/img win/win_splash.png" ^
    --icon "../_docs/img win/game_icon.ico" ^
    ../main.py
ECHO ---
ECHO Build finished.

:end
