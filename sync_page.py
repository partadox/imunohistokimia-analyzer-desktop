from PyQt5.QtWidgets import QWidget, QVBoxLayout, QLabel, QPushButton

class SyncPage(QWidget):
    def __init__(self):
        super().__init__()
        self.setup_ui()

    def setup_ui(self):
        layout = QVBoxLayout()
        layout.addWidget(QLabel("Sync Page"))
        self.sync_status = QLabel("Sync Status: Not synced")
        layout.addWidget(self.sync_status)
        sync_button = QPushButton("Start Sync")
        sync_button.clicked.connect(self.start_sync)
        layout.addWidget(sync_button)
        self.setLayout(layout)

    def start_sync(self):
        # Implementasi sinkronisasi
        self.sync_status.setText("Sync Status: Syncing...")
        # Setelah sinkronisasi selesai:
        # self.sync_status.setText("Sync Status: Synced")