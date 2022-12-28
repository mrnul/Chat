import json

import PySide6
from PySide6 import QtWidgets, QtCore
from PySide6.QtCore import Slot

from Emoji import Emoji


class EmojiMenu(QtWidgets.QMenu):
    signal_emoji_selected = QtCore.Signal(bytes)

    emojis: dict = None
    tabbed_panel: QtWidgets.QTabWidget = None

    def __init__(self, parent):
        """
        Loads supported emojis from emojis.json, builds a tabbed menu to display them
        :param parent: parent widget
        """
        super().__init__(parent=parent)
        self.__load_json__()
        self.tabbed_panel = QtWidgets.QTabWidget(self)

        main_layout = QtWidgets.QGridLayout(self)

        for emoji_category in self.emojis:
            category_layout = QtWidgets.QGridLayout(self.tabbed_panel)
            category_layout.setSpacing(0)
            category_layout.setAlignment(PySide6.QtCore.Qt.AlignmentFlag.AlignTop)

            row, col = 0, 0
            for emoji_code_str in self.emojis[emoji_category]:
                emoji_code = int(emoji_code_str.replace('U+', '0x'), 16)
                emoji_button = \
                    Emoji(emoji_code.to_bytes(8, byteorder='little').decode(encoding='UTF-32'), self.tabbed_panel)
                emoji_button.signal_click.connect(self.__on_emoji_selected__)
                category_layout.addWidget(emoji_button, row, col)
                col += 1
                if col == 15:
                    row, col = row + 1, 0

            category_widget = QtWidgets.QWidget(self.tabbed_panel)
            category_widget.setLayout(category_layout)
            self.tabbed_panel.addTab(category_widget, emoji_category)
        main_layout.addWidget(self.tabbed_panel)
        self.setLayout(main_layout)

    @Slot(int)
    def __on_emoji_selected__(self, value: str):
        self.signal_emoji_selected.emit(value)

    def __load_json__(self):
        with open('emojis.json') as f:
            self.emojis = json.load(f)

    def closeEvent(self, event):
        event.accept()
        self.tabbed_panel.setCurrentIndex(0)
