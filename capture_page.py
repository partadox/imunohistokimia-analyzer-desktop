import cv2
import os
import json
from datetime import datetime
from PyQt5.QtWidgets import (QWidget, QVBoxLayout, QHBoxLayout, QLabel, QPushButton, 
                             QComboBox, QMessageBox)
from PyQt5.QtGui import QImage, QPixmap
from PyQt5.QtCore import QTimer, Qt, pyqtSignal

class CapturePage(QWidget):
    image_captured = pyqtSignal(str)
    
    def __init__(self):
        super().__init__()
        self.camera = None
        self.projects_file = 'projects.json'
        self.projects_folder = 'projects'
        self.setup_ui()

    def setup_ui(self):
        layout = QVBoxLayout()
        
        # Project selection
        project_layout = QHBoxLayout()
        project_layout.addWidget(QLabel("Select Project:"))
        self.project_dropdown = QComboBox()
        self.update_project_list()
        project_layout.addWidget(self.project_dropdown)
        layout.addLayout(project_layout)

        # Device selection
        device_layout = QHBoxLayout()
        self.device_dropdown = QComboBox()
        self.update_camera_list()
        device_layout.addWidget(self.device_dropdown)
        
        self.connect_button = QPushButton("Connect")
        self.connect_button.clicked.connect(self.connect_camera)
        device_layout.addWidget(self.connect_button)
        
        layout.addLayout(device_layout)
        
        self.image_label = QLabel()
        self.image_label.setMinimumSize(800, 600)
        layout.addWidget(self.image_label)

        capture_button = QPushButton("Capture Image")
        capture_button.clicked.connect(self.capture_image)
        layout.addWidget(capture_button)

        self.setLayout(layout)

        # Timer for camera preview update
        self.timer = QTimer(self)
        self.timer.timeout.connect(self.update_frame)

    def update_project_list(self):
        self.project_dropdown.clear()
        projects = self.load_projects()
        for project in projects:
            self.project_dropdown.addItem(project['name'])

    def load_projects(self):
        with open(self.projects_file, 'r') as f:
            return json.load(f)

    def save_projects(self, projects):
        with open(self.projects_file, 'w') as f:
            json.dump(projects, f)

    def update_camera_list(self):
        self.device_dropdown.clear()
        for i in range(10):  # Check first 10 camera indices
            cap = cv2.VideoCapture(i)
            if cap.isOpened():
                self.device_dropdown.addItem(f"Camera {i}")
                cap.release()

    def connect_camera(self):
        if self.camera:
            self.camera.release()
        camera_index = self.device_dropdown.currentIndex()
        self.camera = cv2.VideoCapture(camera_index)
        if not self.camera.isOpened():
            QMessageBox.warning(self, "Error", f"Failed to open camera {camera_index}")
        else:
            self.timer.start(30)

    def update_frame(self):
        if self.camera and self.camera.isOpened():
            ret, frame = self.camera.read()
            if ret:
                frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
                h, w, ch = frame.shape
                bytes_per_line = ch * w
                q_image = QImage(frame.data, w, h, bytes_per_line, QImage.Format_RGB888)
                self.image_label.setPixmap(QPixmap.fromImage(q_image).scaled(
                    self.image_label.size(), Qt.KeepAspectRatio, Qt.SmoothTransformation))

    def capture_image(self):
        if not self.camera or not self.camera.isOpened():
            QMessageBox.warning(self, "Error", "Camera is not connected")
            return

        selected_project = self.project_dropdown.currentText()
        if not selected_project:
            QMessageBox.warning(self, "Error", "Please select a project")
            return

        ret, frame = self.camera.read()
        if ret:
            project_folder = os.path.join(self.projects_folder, selected_project)
            if not os.path.exists(project_folder):
                os.makedirs(project_folder)

            # Generate filename
            timestamp = datetime.now().strftime("%Y%m%d-%H%M%S")
            file_count = len([name for name in os.listdir(project_folder) if os.path.isfile(os.path.join(project_folder, name))])
            filename = f"{timestamp}-{file_count+1:05d}.jpg"
            
            file_path = os.path.join(project_folder, filename)
            cv2.imwrite(file_path, frame)

            # Update project data
            projects = self.load_projects()
            for project in projects:
                if project['name'] == selected_project:
                    project['total_data'] += 1
                    break
            self.save_projects(projects)

            QMessageBox.information(self, "Success", f"Image captured: {filename}")

            # Emit signal that an image was captured
            self.image_captured.emit(selected_project)
        else:
            QMessageBox.warning(self, "Error", "Failed to capture image")

    def showEvent(self, event):
        super().showEvent(event)
        self.update_project_list() 

    def update_project_list(self):
        current_project = self.project_dropdown.currentText()
        self.project_dropdown.clear()
        projects = self.load_projects()
        for project in projects:
            self.project_dropdown.addItem(project['name'])
        
        # Restore the previously selected project if it still exists
        index = self.project_dropdown.findText(current_project)
        if index >= 0:
            self.project_dropdown.setCurrentIndex(index)

    def start_camera(self):
        if self.camera is None:
            camera_index = self.device_dropdown.currentIndex()
            self.camera = cv2.VideoCapture(camera_index)
        if self.camera.isOpened():
            self.timer.start(30)
        else:
            QMessageBox.warning(self, "Error", "Failed to start camera")

    def stop_camera(self):
        if self.camera:
            self.timer.stop()
            self.camera.release()
            self.camera = None
        self.image_label.clear()

    def closeEvent(self, event):
        if self.camera:
            self.camera.release()
        super().closeEvent(event)