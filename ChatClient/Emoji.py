from PySide6 import QtWidgets, QtCore


class Emoji(QtWidgets.QPushButton):
    signal_click = QtCore.Signal(str)

    def __init__(self, text, parent):
        """
        Emoji is simply a button
        :param text: emoji unicode
        :param parent: parent widget
        """
        super().__init__(text=text, parent=parent)
        self.clicked.connect(self.__on_emoji_click__)
        self.setFlat(True)
        self.setStyleSheet("background-color: transparent;"
                           "border: 10px;")

    def __on_emoji_click__(self):
        self.signal_click.emit(self.text())
