import threading

import PySide6
from PySide6 import QtWidgets, QtCore
from PySide6.QtCore import Slot
from PySide6.QtGui import QIcon

import ChatClient
from ChatPanel import ChatPanel
from ClientListItem import ClientListItem


class ChatUI(QtWidgets.QWidget):
    client_list_widget: QtWidgets.QListWidget = None
    chats_tabbed_panel: QtWidgets.QTabWidget = None
    client_id_name_map: dict = None

    chat_client: ChatClient.ChatClient = None
    name: str = None

    def __init__(self, name):
        """
        Initializes the UI, starts client thread and sets everything up
        :param name: Name to use in chatting
        """
        super().__init__()
        self.name = name
        self.client_id_name_map = {}
        self.chat_client = ChatClient.ChatClient()
        self.chat_client.signal_new_client_list.connect(self.__on_new_client_list__)
        self.chat_client.signal_update_client.connect(self.__on_client_update__)
        self.chat_client.signal_incoming_message.connect(self.__on_incoming_message__)
        self.chat_client.signal_connection.connect(self.__on_connection_update__)
        threading.Thread(target=self.chat_client.start_chat, args=('127.0.0.1', 4550)).start()

        self.client_list_widget = QtWidgets.QListWidget(parent=self)
        self.client_list_widget.itemDoubleClicked.connect(self.__on_client_double_click__)
        self.client_list_widget.itemClicked.connect(self.__on_client_double_click__)

        self.chats_tabbed_panel = QtWidgets.QTabWidget(parent=self)
        self.chats_tabbed_panel.setTabsClosable(True)
        self.chats_tabbed_panel.setElideMode(PySide6.QtCore.Qt.TextElideMode.ElideRight)
        self.chats_tabbed_panel.tabCloseRequested.connect(self.__on_tab_close__)
        self.chats_tabbed_panel.currentChanged.connect(self.__on_tab_changed__)

        main_layout = QtWidgets.QHBoxLayout()
        main_layout.setSpacing(0)
        main_layout.setContentsMargins(0, 0, 0, 0)
        main_layout.addWidget(self.client_list_widget, stretch=1)
        main_layout.addWidget(self.chats_tabbed_panel, stretch=3)

        if isinstance(self, QtWidgets.QMainWindow):
            w = QtWidgets.QWidget()
            w.setLayout(main_layout)
            self.setCentralWidget(w)
        else:
            self.setLayout(main_layout)
        self.resize(500, 500)

    def get_chat_panel_from_client_id(self, cid: int) -> ChatPanel | None:
        """
        Searches through all chat panels inside the chats tabbed panel and finds the one with client id = cid
        :param cid: client id to find
        :return: returns the chat panel or None
        """
        for i in range(self.chats_tabbed_panel.count()):
            panel = self.chats_tabbed_panel.widget(i)
            if isinstance(panel, ChatPanel):
                if panel.get_client_id() == cid:
                    return panel
        return None

    def get_tab_index_from_client_id(self, cid: int) -> int | None:
        """
        Searches through all chat panels inside the chats tabbed panel and finds the one with client id = cid
        :param cid: client id to find
        :return: returns the index of the tab or None
        """
        for i in range(self.chats_tabbed_panel.count()):
            panel = self.chats_tabbed_panel.widget(i)
            if isinstance(panel, ChatPanel):
                if panel.get_client_id() == cid:
                    return i
        return None

    @Slot(dict)
    def __on_send_message__(self, data: dict):
        self.chat_client.send_data(data)

    def __on_tab_changed__(self, index):
        """
        When user clicks on a tab selects the appropriate item from the client list
        """
        chat_panel = self.chats_tabbed_panel.widget(index)
        if not isinstance(chat_panel, ChatPanel):
            self.client_list_widget.clearSelection()
            return

        item = self.__find_client_list_item__(chat_panel.get_client_id())
        if not isinstance(item, ClientListItem):
            self.client_list_widget.clearSelection()
            return

        self.client_list_widget.setCurrentItem(item)

    def __on_tab_close__(self, index):
        self.chats_tabbed_panel.removeTab(index)

    def __on_client_double_click__(self, item):
        """
        When user double-clicks an item from the client list -> select the appropriate tab OR create a new tab
        if it does not already exist
        """
        chat_panel = self.get_chat_panel_from_client_id(item.get_client_id())
        if chat_panel is None:
            chat_panel = ChatPanel(item.get_client_id(), item.get_client_name(),
                                   self.__on_send_message__, self.__find_and_update_client__, self.chats_tabbed_panel)
            self.chats_tabbed_panel.addTab(chat_panel, str(item.get_client_name()))
        self.chats_tabbed_panel.setCurrentWidget(chat_panel)

    def __find_client_list_item__(self, cid: int) -> ClientListItem | None:
        """
        Searches through all items inside client list and finds the one with client id = cid
        :param cid: client id to find
        :return: returns the item or None
        """
        for i in range(self.client_list_widget.count()):
            item = self.client_list_widget.item(i)
            if isinstance(item, ClientListItem) and item.get_client_id() == cid:
                return item
        return None

    def __get_proper_text_for_list_and_tab__(self, cid: int, chat_panel: ChatPanel | None):
        """
        Builds text that is appropriate for display in a tab or in the client list

        This text includes "Self - " if item is our client, "(+) " if client has unread messages, name of the client
        :param cid: client id to build the text for
        :param chat_panel: chat panel of that client
        :return: text or None. If None is returned then client id could not be found and this id should be cleared
        """
        if cid not in self.client_id_name_map:
            return None

        if not isinstance(chat_panel, ChatPanel):
            return f'{"Self - " if cid == self.chat_client.get_id() else ""}' \
                   f'{self.client_id_name_map[cid]}'

        return f'{"Self - " if cid == self.chat_client.get_id() else ""}' \
               f'{"(+) " if chat_panel.has_unread_messages() else ""}' \
               f'{self.client_id_name_map[cid]}'

    @Slot(object)
    def __find_and_update_client__(self, cid: int):
        """
        Finds client specified by cid and updates displayed tab text / list item text

        if cid is not found then items are removed
        """
        chat_panel = None
        index = self.get_tab_index_from_client_id(cid)
        if index is not None:
            chat_panel = self.chats_tabbed_panel.widget(index)
            self.__update_tab__(index)

        item = self.__find_client_list_item__(cid)
        text = self.__get_proper_text_for_list_and_tab__(cid, chat_panel)
        if text is None:
            self.client_list_widget.removeItemWidget(item)
            self.client_list_widget.takeItem(self.client_list_widget.row(item))
            return

        if item is not None:
            item.update_client_name(text)
        else:
            item = ClientListItem(cid, text)
            self.client_list_widget.addItem(item)

    def __repopulate_client_list_widget__(self):
        self.client_list_widget.clear()
        for client in self.client_id_name_map:
            text = self.__get_proper_text_for_list_and_tab__(client, None)
            if text is not None:
                item = ClientListItem(client, self.__get_proper_text_for_list_and_tab__(client, None))
                self.client_list_widget.addItem(item)

    def __update_tab__(self, index: int):
        if index not in range(self.chats_tabbed_panel.count()):
            return

        chat_panel = self.chats_tabbed_panel.widget(index)
        if isinstance(chat_panel, ChatPanel):
            tab_text = self.__get_proper_text_for_list_and_tab__(chat_panel.get_client_id(), chat_panel)
            if tab_text is None:
                self.chats_tabbed_panel.removeTab(index)
            else:
                self.chats_tabbed_panel.setTabText(index, tab_text)

    def __update_opened_tabs__(self):
        for i in range(self.chats_tabbed_panel.count()):
            self.__update_tab__(i)

    @Slot(bool)
    def __on_connection_update__(self, data: dict):
        if not data.get('connected', False):
            self.setWindowIcon(QIcon('red_64.ico'))
            self.client_id_name_map.clear()
            self.client_list_widget.clear()
            self.chats_tabbed_panel.clear()
        else:
            self.setWindowIcon(QIcon('green_64.ico'))
            self.chat_client.send_name(self.name)
        self.setWindowTitle(data.get("text", ""))

    @Slot(dict)
    def __on_incoming_message__(self, data: dict):
        client_id = data.get('from')
        if client_id is None:
            return

        client_name = self.client_id_name_map.get(client_id)
        text = data.get('text', None)
        chat_panel = self.get_chat_panel_from_client_id(client_id)

        if chat_panel is None:
            chat_panel = ChatPanel(client_id, client_name,
                                   self.__on_send_message__, self.__find_and_update_client__, self.chats_tabbed_panel)
            self.chats_tabbed_panel.addTab(chat_panel, client_name)
        if text is not None:
            chat_panel.insert_message(text, True)
        self.__find_and_update_client__(client_id)

    @Slot(dict)
    def __on_new_client_list__(self, data: dict):
        self.client_id_name_map.clear()
        for clients in data.values():
            for client in clients:
                self.client_id_name_map[client['id']] = client['name']
        self.__repopulate_client_list_widget__()
        self.__update_opened_tabs__()

    @Slot(dict)
    def __on_client_update__(self, data: dict):
        client_id = data['update']['id']
        client_name = data['update']['name']
        info = data['update']['info']

        if info.casefold() == 'update':
            self.client_id_name_map[client_id] = client_name
        elif info.casefold() == 'add':
            self.client_id_name_map[client_id] = client_name
        elif info.casefold() == 'delete':
            self.client_id_name_map.pop(client_id)

        self.setWindowTitle(f'{self.client_id_name_map.get(self.chat_client.get_id())}')
        self.__find_and_update_client__(client_id)

    def closeEvent(self, event):
        event.accept()
        self.chat_client.shutdown()

    def hide_all_content(self):
        for i in range(self.chats_tabbed_panel.count()):
            chat_panel = self.chats_tabbed_panel.widget(i)
            if isinstance(chat_panel, ChatPanel):
                chat_panel.hide_content()

    def changeEvent(self, event):
        """
        In case that window is minimized OR not active -> hide all content
        """
        if event.type() == PySide6.QtCore.QEvent.Type.WindowStateChange:
            if self.windowState() & PySide6.QtCore.Qt.WindowState.WindowMinimized:
                self.hide_all_content()
        elif event.type() == PySide6.QtCore.QEvent.Type.ActivationChange:
            if not self.isActiveWindow():
                self.hide_all_content()
