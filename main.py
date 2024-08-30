import sys
from PyQt5.QtWidgets import QApplication, QMainWindow, QPushButton, QVBoxLayout, QHBoxLayout, QWidget, QStackedWidget
from project_page import ProjectPage
from capture_page import CapturePage
from sync_page import SyncPage
from action_page import ActionPage

class MicroscopeApp(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Microscope Image Capture")
        self.setGeometry(100, 100, 1024, 768)
        self.setup_ui()

    def setup_ui(self):
        main_layout = QHBoxLayout()

        # Sidebar
        sidebar = QWidget()
        sidebar_layout = QVBoxLayout()
        
        self.project_btn = QPushButton("Project")
        capture_btn = QPushButton("Capture")
        sync_btn = QPushButton("Sync")
        
        sidebar_layout.addWidget(self.project_btn)
        sidebar_layout.addWidget(capture_btn)
        sidebar_layout.addWidget(sync_btn)
        sidebar_layout.addStretch()
        
        sidebar.setLayout(sidebar_layout)
        sidebar.setFixedWidth(200)

        # Main content area
        self.content_area = QStackedWidget()
        
        self.project_page = ProjectPage(self.content_area)
        self.capture_page = CapturePage()
        self.sync_page = SyncPage()

        self.content_area.addWidget(self.project_page)
        self.content_area.addWidget(self.capture_page)
        self.content_area.addWidget(self.sync_page)

        # Connect sidebar buttons
        self.project_btn.clicked.connect(lambda: self.change_page(0))
        capture_btn.clicked.connect(lambda: self.change_page(1))
        sync_btn.clicked.connect(lambda: self.change_page(2))

        # Connect the image_captured signal to update_project_display slot
        self.capture_page.image_captured.connect(self.project_page.update_project_display)

        # Connect project page to action page
        self.project_page.switch_to_action_page.connect(self.show_action_page)

        # Add sidebar and content area to main layout
        main_layout.addWidget(sidebar)
        main_layout.addWidget(self.content_area)

        central_widget = QWidget()
        central_widget.setLayout(main_layout)
        self.setCentralWidget(central_widget)

    def change_page(self, index):
        current_widget = self.content_area.currentWidget()
        if isinstance(current_widget, ActionPage):
            self.go_back_to_projects()
        
        self.content_area.setCurrentIndex(index)
        if index == 1:  # Capture page
            self.capture_page.update_project_list()
            self.capture_page.start_camera()
        else:
            self.capture_page.stop_camera()

    def show_action_page(self, project_name):
        action_page = ActionPage(project_name, self.project_page.projects_folder)
        action_page.go_back_signal.connect(self.go_back_to_projects)
        self.content_area.addWidget(action_page)
        self.content_area.setCurrentWidget(action_page)

    def go_back_to_projects(self):
        self.content_area.setCurrentWidget(self.project_page)
        # Remove the ActionPage widget
        for i in range(self.content_area.count()):
            if isinstance(self.content_area.widget(i), ActionPage):
                widget = self.content_area.widget(i)
                self.content_area.removeWidget(widget)
                widget.deleteLater()
                break
        self.project_page.update_project_display()

if __name__ == "__main__":
    app = QApplication(sys.argv)
    app.setStyleSheet("""
        QLabel {
            font-size: 10px;
        }
        QPushButton {
            font-size: 12px;
        }
    """)
    window = MicroscopeApp()
    window.show()
    sys.exit(app.exec_())