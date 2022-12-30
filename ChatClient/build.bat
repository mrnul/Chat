set PYTHONPATH=../Common;%PYTHONPATH%
pyinstaller --noconsole --add-data "style.qss;." --add-data "green_64.ico;." --add-data "red_64.ico;." --add-data "emojis.json;." main.py