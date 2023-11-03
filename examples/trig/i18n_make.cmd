REM Пересобрать .po проекта
chcp 65001
@echo off

REM создать шаблон без переводов
xgettext -d trig_fall -s -L Python --no-wrap -o common_tools/locale/ru/LC_MESSAGES/trig_fall.pot common_tools/i18n.py

REM объединить старый перевод и новый шаблон - fuzzy
msgmerge -U common_tools/locale/ru/LC_MESSAGES/trig_fall.po common_tools/locale/ru/LC_MESSAGES/trig_fall.pot

REM удалить шаблон
del "common_tools\locale\ru\LC_MESSAGES\trig_fall.pot"

echo i18n_make done at %date% %time%
echo ~
