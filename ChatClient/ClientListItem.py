from PySide6 import QtWidgets


class ClientListItem(QtWidgets.QListWidgetItem):
    client_id: int = None
    client_name: str = None

    def __init__(self, cid: int, cname: str):
        """
        Items that are used in client list
        :param cid: client id
        :param cname: client name
        """
        super().__init__()
        self.client_id = cid
        self.update_client_name(cname)

    def update_client_name(self, cname: str):
        self.client_name = cname
        self.setText(self.client_name)

    def get_client_id(self):
        return self.client_id

    def get_client_name(self):
        return self.client_name
