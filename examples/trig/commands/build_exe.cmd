ECHO off
CLS
ECHO Building Trig fall .exe ...

REM https://pyinstaller.org/en/stable/usage.html
REM pyinstaller 6.2.0
REM https://documentation.vkplay.ru/f2p_vkp/f2pc_distrib_vkp  Сборка билдов

cd %~dp0

set BUILD_EDITION=%1
set GAME_VERSION="1.2.2"

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
REM pyinstaller ставится в python, а не в venv
REM значёк на панели задач: заменить C:\python\venv\myproj311-32\Lib\site-packages\pygame\pygame_icon.bmp
ECHO ---
C:\python\venv\trig310\Scripts\pyinstaller ^
    --clean ^
    --onefile ^
    --noconfirm ^
    --noconsole ^
    --name "Trig fall %GAME_VERSION% %BUILD_EDITION%.exe" ^
    --add-data "../res:res" ^
    --add-data "../common_tools/locale/ru/LC_MESSAGES:common_tools/locale/ru/LC_MESSAGES" ^
    --splash "../_docs/_win_res/win_splash.png" ^
    --icon "../_docs/_win_res/game_icon.ico" ^
    ../main.py
ECHO ---
ECHO Build finished.

:end


REM pyinstallers:
REM C:\python\Python311-32\Scripts\pyinstaller
REM C:\python\venv\trig310\Scripts\pyinstaller