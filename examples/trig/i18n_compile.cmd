REM Скомпилировать .mo из .po
chcp 65001
@echo off

msgfmt common_tools/locale/ru/LC_MESSAGES/trig_fall.po -o common_tools/locale/ru/LC_MESSAGES/trig_fall.mo

echo i18n_compile done at %date% %time%
echo ~
