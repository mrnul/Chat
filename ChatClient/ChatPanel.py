import PySide6
from PySide6 import QtWidgets, QtCore

from EmojiMenu import EmojiMenu
from Message import Message


class ChatPanel(QtWidgets.QWidget):
    client_id: int = None
    client_name: str = None
    now_hidden: bool = None
    unread_messages: bool = None

    emojis_menu: EmojiMenu = None
    messages_scroll_area: QtWidgets.QScrollArea = None
    new_message: QtWidgets.QLineEdit = None
    show_button: QtWidgets.QPushButton = None
    emojis_button: QtWidgets.QPushButton = None

    signal_send_message = PySide6.QtCore.Signal(dict)
    signal_show_message = PySide6.QtCore.Signal(object)

    def has_unread_messages(self):
        return self.unread_messages

    def get_client_id(self):
        return self.client_id

    def get_client_name(self):
        return self.client_name

    def __init__(self, cid: int, cname: str, on_send_message, on_show_click, parent):
        """
        Builds the chat panel for a specified client
        :param cid: client id
        :param cname: client name
        :param on_send_message: method to run when sending a message
        :param on_show_click: method to run when show button is clicked
        :param parent: parent widget
        """
        super().__init__(parent=parent)
        self.client_id = cid
        self.client_name = cname

        self.signal_send_message.connect(on_send_message)
        self.signal_show_message.connect(on_show_click)

        self.emojis_menu = EmojiMenu(self)
        self.emojis_menu.setWindowModality(PySide6.QtCore.Qt.WindowModality.ApplicationModal)
        self.emojis_menu.signal_emoji_selected.connect(self.__on_emoji_selected__)

        self.messages_scroll_area = QtWidgets.QScrollArea()
        self.messages_scroll_area.setVerticalScrollBarPolicy(PySide6.QtCore.Qt.ScrollBarPolicy.ScrollBarAlwaysOn)
        self.messages_scroll_area.setHorizontalScrollBarPolicy(PySide6.QtCore.Qt.ScrollBarPolicy.ScrollBarAlwaysOff)

        scroll_layout = QtWidgets.QVBoxLayout()
        scroll_layout.setSpacing(0)
        scroll_layout.setContentsMargins(0, 0, 0, 0)
        scroll_layout.setAlignment(PySide6.QtCore.Qt.AlignmentFlag.AlignTop)

        scroll_widget = QtWidgets.QWidget()
        scroll_widget.setLayout(scroll_layout)
        self.messages_scroll_area.setWidget(scroll_widget)
        self.messages_scroll_area.setWidgetResizable(True)
        self.messages_scroll_area.verticalScrollBar().rangeChanged.connect(self.__on_scroll_range_change__)

        self.new_message = QtWidgets.QLineEdit(parent=self)
        self.new_message.returnPressed.connect(self.__on_return_press__)

        self.show_button = QtWidgets.QPushButton(f'Show {self.client_name}', parent=self)
        self.show_button.clicked.connect(self.__on_show_click__)

        self.emojis_button = QtWidgets.QPushButton('Add emoji \U0001F643', parent=self)
        self.emojis_button.clicked.connect(self.__on_emojis_click__)
        self.emojis_button.setFlat(True)

        main_layout = QtWidgets.QVBoxLayout()
        main_layout.setSpacing(0)
        main_layout.setContentsMargins(0, 0, 0, 0)
        main_layout.addWidget(self.messages_scroll_area)
        h_layout = QtWidgets.QHBoxLayout()
        h_layout.addWidget(self.new_message)
        h_layout.addWidget(self.show_button)
        h_layout.addWidget(self.emojis_button)
        main_layout.addLayout(h_layout)

        self.hide_content()
        self.setLayout(main_layout)

    def insert_message(self, text: str, incoming: bool):
        if self.now_hidden:
            self.unread_messages = True
        message = Message(text, incoming)
        last_message = None
        last_index = self.messages_scroll_area.widget().layout().count() - 1
        if last_index >= 0:
            last_widget = self.messages_scroll_area.widget().layout().itemAt(last_index)
            if last_widget is not None:
                last_message = last_widget.widget()

        if isinstance(last_message, Message) and last_message.incoming == message.incoming:
            last_message.insert_text(f'\n{text}')
        else:
            self.messages_scroll_area.widget().layout().addWidget(message)

    def hide_content(self):
        self.messages_scroll_area.hide()
        self.new_message.hide()
        self.emojis_button.hide()
        self.show_button.show()
        self.now_hidden = True

    def __on_return_press__(self):
        self.__on_send_click__()

    def __on_scroll_range_change__(self, minimum, maximum):
        if maximum != minimum:
            self.messages_scroll_area.verticalScrollBar().setValue(maximum)

    def __on_emojis_click__(self):
        self.emojis_menu.popup(QtCore.QPoint(0, 0))
        x, y = -self.emojis_menu.size().width() + self.emojis_button.size().width() - 1, \
            -self.emojis_menu.size().height() - 1
        self.emojis_menu.move(self.emojis_button.mapToGlobal(QtCore.QPoint(x, y)))

    def __on_show_click__(self):
        self.messages_scroll_area.show()
        self.new_message.show()
        self.emojis_button.show()
        self.show_button.hide()
        self.now_hidden = False
        self.unread_messages = False
        self.signal_show_message.emit(self.client_id)

    def __on_emoji_selected__(self, value: bytes):
        self.new_message.insert(f'{value}')
        self.new_message.setFocus()

    def __on_send_click__(self):
        if len(self.new_message.text()) == 0:
            return

        self.signal_send_message.emit({'recipients': [self.client_id], 'text': self.new_message.text()})
        self.insert_message(self.new_message.text(), False)
        self.new_message.clear()
