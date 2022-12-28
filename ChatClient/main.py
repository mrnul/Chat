import os
import sys

from PySide6 import QtWidgets

import ChatUI

if __name__ == '__main__':
    app = QtWidgets.QApplication()
    app.setStyle('Fusion')

    # name is passed as a command line argument
    # if name is not found then get os.getlogin() as name
    chat_ui = ChatUI.ChatUI(sys.argv[1] if len(sys.argv) >= 2 else os.getlogin())

    try:
        # set style using style.qss file
        # use default styling if file not found
        with open('style.qss', mode='r') as f:
            chat_ui.setStyleSheet(f.read())
    except FileNotFoundError:
        pass

    chat_ui.show()
    app.exec()
