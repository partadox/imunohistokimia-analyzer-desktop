import os
import json
from PyQt5.QtWidgets import (QWidget, QVBoxLayout, QHBoxLayout, QLabel, QPushButton,
                             QScrollArea, QGridLayout, QMessageBox, QFrame)
from PyQt5.QtGui import QPixmap
from PyQt5.QtCore import Qt, pyqtSignal
from image_viewer import ImageViewer

class ActionPage(QWidget):
    go_back_signal = pyqtSignal()

    def __init__(self, project_name, projects_folder):
        super().__init__()
        self.project_name = project_name
        self.projects_folder = projects_folder
        self.project_folder = os.path.join(projects_folder, project_name)
        self.selected_image = None
        self.image_containers = {}
        self.setup_ui()

    def setup_ui(self):
        layout = QVBoxLayout()

        # Project info
        info_layout = QVBoxLayout()
        info_layout.addWidget(QLabel(f"Project: {self.project_name}"))
        
        self.project_info = self.load_project_info()
        if self.project_info:
            self.total_data_label = QLabel(f"Total Data: {self.project_info.get('total_data', 'N/A')}")
            info_layout.addWidget(QLabel(f"Created: {self.project_info.get('timestamp_create', 'N/A')}"))
            info_layout.addWidget(self.total_data_label)
            info_layout.addWidget(QLabel(f"Description: {self.project_info.get('description', 'N/A')}"))
        else:
            info_layout.addWidget(QLabel("Project information not available"))
        
        layout.addLayout(info_layout)

        # Thumbnail grid
        scroll_area = QScrollArea()
        scroll_content = QWidget()
        self.grid_layout = QGridLayout(scroll_content)
        self.grid_layout.setSpacing(5)
        self.grid_layout.setContentsMargins(5, 5, 5, 5)
        scroll_area.setWidget(scroll_content)
        scroll_area.setWidgetResizable(True)
        scroll_area.setMinimumSize(650, 400)
        layout.addWidget(scroll_area)

        # Buttons
        button_layout = QHBoxLayout()
        delete_button = QPushButton("Delete Image")
        delete_button.clicked.connect(self.delete_image)
        button_layout.addWidget(delete_button)

        zoom_button = QPushButton("Zoom Image")
        zoom_button.clicked.connect(self.zoom_image)
        button_layout.addWidget(zoom_button)

        layout.addLayout(button_layout)

        self.setLayout(layout)
        self.load_images()

    def load_images(self):
        row = 0
        col = 0
        for filename in os.listdir(self.project_folder):
            if filename.lower().endswith(('.png', '.jpg', '.jpeg', '.bmp', '.gif')):
                image_path = os.path.join(self.project_folder, filename)
                pixmap = QPixmap(image_path)
                
                thumbnail = pixmap.scaled(150, 150, Qt.KeepAspectRatio, Qt.SmoothTransformation)
                
                container = QFrame()
                container.setFrameShape(QFrame.Box)
                container.setLineWidth(2)
                container.setStyleSheet("QFrame { border: 2px solid transparent; }")
                container_layout = QVBoxLayout(container)
                container_layout.setSpacing(2)
                container_layout.setContentsMargins(0, 0, 0, 0)
                
                thumbnail_label = QLabel()
                thumbnail_label.setPixmap(thumbnail)
                thumbnail_label.setAlignment(Qt.AlignCenter)
                thumbnail_label.setFixedSize(150, 150)
                thumbnail_label.mousePressEvent = lambda event, f=filename: self.select_image(f)
                container_layout.addWidget(thumbnail_label)
                
                filename_label = QLabel(filename)
                filename_label.setAlignment(Qt.AlignCenter)
                filename_label.setWordWrap(True)
                filename_label.setStyleSheet("font-size: 8px;")
                container_layout.addWidget(filename_label)
                
                self.grid_layout.addWidget(container, row, col)
                self.image_containers[filename] = container
                
                col += 1
                if col > 3:
                    col = 0
                    row += 1

    def load_project_info(self):
        projects_file = os.path.join(os.path.dirname(self.projects_folder), 'projects.json')
        if not os.path.exists(projects_file):
            print(f"File not found: {projects_file}")
            return {}
        
        with open(projects_file, 'r') as f:
            projects = json.load(f)
        for project in projects:
            if project['name'] == self.project_name:
                return project
        return {}

    def select_image(self, filename):
        if self.selected_image:
            self.image_containers[self.selected_image].setStyleSheet("QFrame { border: 2px solid transparent; }")
        self.selected_image = filename
        self.image_containers[filename].setStyleSheet("QFrame { border: 2px solid blue; }")
        print(f"Selected image: {filename}")

    def delete_image(self):
        if self.selected_image:
            reply = QMessageBox.question(self, 'Delete Image',
                                         f"Are you sure you want to delete '{self.selected_image}'?",
                                         QMessageBox.Yes | QMessageBox.No, QMessageBox.No)
            if reply == QMessageBox.Yes:
                image_path = os.path.join(self.project_folder, self.selected_image)
                os.remove(image_path)
                self.update_project_data()
                self.reload_images()
        else:
            QMessageBox.warning(self, "No Image Selected", "Please select an image to delete.")

    def zoom_image(self):
        if self.selected_image:
            image_path = os.path.join(self.project_folder, self.selected_image)
            self.image_viewer = ImageViewer(image_path)
            self.image_viewer.setWindowTitle(self.selected_image)
            self.image_viewer.resize(800, 600)
            self.image_viewer.show()
        else:
            QMessageBox.warning(self, "No Image Selected", "Please select an image to view.")

    def update_project_data(self):
        projects_file = os.path.join(os.path.dirname(self.projects_folder), 'projects.json')
        with open(projects_file, 'r') as f:
            projects = json.load(f)
        for project in projects:
            if project['name'] == self.project_name:
                project['total_data'] = len([name for name in os.listdir(self.project_folder)
                                             if os.path.isfile(os.path.join(self.project_folder, name))])
                self.project_info = project
                self.total_data_label.setText(f"Total Data: {project['total_data']}")
                break
        with open(projects_file, 'w') as f:
            json.dump(projects, f)

    def reload_images(self):
        for i in reversed(range(self.grid_layout.count())): 
            self.grid_layout.itemAt(i).widget().setParent(None)
        self.image_containers.clear()
        self.selected_image = None
        self.load_images()