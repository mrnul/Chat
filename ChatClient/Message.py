import datetime

import PySide6
from PySide6 import QtWidgets, QtCore, QtGui


class Message(QtWidgets.QWidget):
    incoming: bool = None
    text: QtWidgets.QTextEdit = None

    def __init__(self, text, incoming):
        """
        Message is a widget that holds text and aligns it appropriately depending on value of incoming parameter
        :param text: message text
        :param incoming: true if this message represents an incoming message
        """
        super().__init__()
        self.incoming = incoming
        self.text = QtWidgets.QTextEdit()
        self.text.textChanged.connect(self.__on_text_change__)
        self.text.setReadOnly(True)
        self.text.setHorizontalScrollBarPolicy(PySide6.QtCore.Qt.ScrollBarPolicy.ScrollBarAlwaysOff)
        self.text.setAlignment(PySide6.QtCore.Qt.AlignmentFlag.AlignLeft
                               if self.incoming else
                               PySide6.QtCore.Qt.AlignmentFlag.AlignRight)
        self.insert_text(text)

        layout = QtWidgets.QHBoxLayout()
        layout.addWidget(self.text)
        layout.setContentsMargins(60 if not self.incoming else 0, 0, 60 if self.incoming else 0, 0)
        layout.setSpacing(0)

        self.setLayout(layout)
        self.setFixedHeight(120)

    def __on_text_change__(self):
        self.text.verticalScrollBar().setValue(self.text.verticalScrollBar().maximum())

    def __update_tooltip__(self):
        prev_tooltip = self.text.toolTip()
        if len(prev_tooltip) > 0:
            prev_tooltip += '\n'
            if len(prev_tooltip) > 60:
                prev_tooltip = ''
        self.text.setToolTip(f'{prev_tooltip}{datetime.datetime.now().strftime("%H:%M:%S")}')

    def __move_cursor_to_end__(self):
        cursor = self.text.textCursor()
        cursor.movePosition(PySide6.QtGui.QTextCursor.MoveOperation.End)
        self.text.setTextCursor(cursor)

    def insert_text(self, text: str):
        self.__move_cursor_to_end__()
        self.__update_tooltip__()
        self.text.insertPlainText(text)

    def insert_html(self, html: str):
        self.__move_cursor_to_end__()
        self.__update_tooltip__()
        self.text.insertHtml(html)
