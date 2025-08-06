REM Скомпилировать .mo из .po
chcp 65001
@echo off
cls

msgfmt common_tools/locale/ru/LC_MESSAGES/trig_fall.po -o common_tools/locale/ru/LC_MESSAGES/trig_fall.mo
echo ~
echo ~~
echo ~~~
echo i18n_compile done at %date% %time%
echo ~~~
echo ~~
echo ~

