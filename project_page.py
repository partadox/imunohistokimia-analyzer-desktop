import json
import os
from PyQt5.QtWidgets import (QWidget, QStackedWidget, QVBoxLayout, QHBoxLayout, QLabel, QTableWidget, QTableWidgetItem,
                             QPushButton, QLineEdit, QTextEdit, QMessageBox, QDialog, QHeaderView)
from PyQt5.QtCore import Qt, QDateTime, pyqtSignal
from PyQt5.QtGui import QColor
from action_page import ActionPage

class CreateProjectDialog(QDialog):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle("Create New Project")
        self.setup_ui()

    def setup_ui(self):
        layout = QVBoxLayout()
        
        self.name_input = QLineEdit()
        self.description_input = QTextEdit()
        
        layout.addWidget(QLabel("Project Name:"))
        layout.addWidget(self.name_input)
        layout.addWidget(QLabel("Description:"))
        layout.addWidget(self.description_input)
        
        buttons = QHBoxLayout()
        create_button = QPushButton("Create")
        create_button.clicked.connect(self.accept)
        cancel_button = QPushButton("Cancel")
        cancel_button.clicked.connect(self.reject)
        buttons.addWidget(create_button)
        buttons.addWidget(cancel_button)
        
        layout.addLayout(buttons)
        self.setLayout(layout)

class ProjectPage(QWidget):
    switch_to_action_page = pyqtSignal(str)

    def __init__(self, stacked_widget):
        super().__init__()
        self.stacked_widget = stacked_widget
        self.projects_file = 'projects.json'
        self.projects_folder = 'projects'
        self.setup_storage()
        self.setup_ui()

    def setup_storage(self):
        if not os.path.exists(self.projects_file):
            with open(self.projects_file, 'w') as f:
                json.dump([], f)
        if not os.path.exists(self.projects_folder):
            os.makedirs(self.projects_folder)

    def update_project_display(self, project_name=None):
        projects = self.load_projects()
        self.projects_table.setRowCount(len(projects))
        for row, project in enumerate(projects):
            self.projects_table.setItem(row, 0, QTableWidgetItem(project['name']))
            self.projects_table.setItem(row, 1, QTableWidgetItem(project['timestamp_create']))
            self.projects_table.setItem(row, 2, QTableWidgetItem(str(project['total_data'])))
            self.projects_table.setItem(row, 3, QTableWidgetItem(project['sync_status']))
            
            view_button = QPushButton("View")
            view_button.setStyleSheet("background-color: lightblue;")
            view_button.clicked.connect(lambda _, n=project['name']: self.view_project(n))
            self.projects_table.setCellWidget(row, 4, view_button)
            
            delete_button = QPushButton("Delete")
            delete_button.setStyleSheet("background-color: red; color: white;")
            delete_button.clicked.connect(lambda _, n=project['name']: self.delete_project(n))
            self.projects_table.setCellWidget(row, 5, delete_button)

    def view_project(self, project_name):
        self.switch_to_action_page.emit(project_name)
        action_page = ActionPage(project_name, self.projects_folder)
        self.stacked_widget.addWidget(action_page)
        self.stacked_widget.setCurrentWidget(action_page)

    def setup_storage(self):
        if not os.path.exists(self.projects_file):
            with open(self.projects_file, 'w') as f:
                json.dump([], f)
        if not os.path.exists(self.projects_folder):
            os.makedirs(self.projects_folder)

    def setup_ui(self):
        layout = QVBoxLayout()

        # Projects Table
        self.projects_table = QTableWidget()
        self.projects_table.setColumnCount(6)
        self.projects_table.setHorizontalHeaderLabels(["Name", "Created", "Data", "Status", "View", "Delete"])
        self.projects_table.horizontalHeader().setSectionResizeMode(QHeaderView.Stretch)
        layout.addWidget(self.projects_table)

        # New Project Button
        new_project_button = QPushButton("+ New Project")
        new_project_button.clicked.connect(self.show_create_project_dialog)
        layout.addWidget(new_project_button)

        self.setLayout(layout)
        self.update_project_list()

    def load_projects(self):
        with open(self.projects_file, 'r') as f:
            return json.load(f)

    def save_projects(self, projects):
        with open(self.projects_file, 'w') as f:
            json.dump(projects, f)

    def update_project_list(self):
        projects = self.load_projects()
        self.projects_table.setRowCount(len(projects))
        for row, project in enumerate(projects):
            self.projects_table.setItem(row, 0, QTableWidgetItem(project['name']))
            self.projects_table.setItem(row, 1, QTableWidgetItem(project['timestamp_create']))
            self.projects_table.setItem(row, 2, QTableWidgetItem(str(project['total_data'])))
            self.projects_table.setItem(row, 3, QTableWidgetItem(project['sync_status']))
            
            view_button = QPushButton("View")
            view_button.setStyleSheet("background-color: lightblue;")
            view_button.clicked.connect(lambda _, n=project['name']: self.view_project(n))
            self.projects_table.setCellWidget(row, 4, view_button)
            
            delete_button = QPushButton("Delete")
            delete_button.setStyleSheet("background-color: red; color: white;")
            delete_button.clicked.connect(lambda _, n=project['name']: self.delete_project(n))
            self.projects_table.setCellWidget(row, 5, delete_button)

    def show_create_project_dialog(self):
        dialog = CreateProjectDialog(self)
        if dialog.exec_():
            name = dialog.name_input.text()
            description = dialog.description_input.toPlainText()
            self.create_project(name, description)

    def create_project(self, name, description):
        if name:
            timestamp = QDateTime.currentDateTime().toString("dd-MM-yyyy HH:mm:ss")
            new_project = {
                "name": name,
                "timestamp_create": timestamp,
                "total_data": 0,
                "sync_status": "Not Synced",
                "description": description
            }
            projects = self.load_projects()
            projects.append(new_project)
            self.save_projects(projects)
            
            # Create project subfolder
            project_folder = os.path.join(self.projects_folder, name)
            os.makedirs(project_folder, exist_ok=True)
            
            self.update_project_list()
            QMessageBox.information(self, "Success", f"Project '{name}' created successfully!")
        else:
            QMessageBox.warning(self, "Error", "Project name cannot be empty!")

    def delete_project(self, project_name):
        reply = QMessageBox.question(self, 'Delete Project', 
                                     f"Are you sure you want to delete '{project_name}'?",
                                     QMessageBox.Yes | QMessageBox.No, QMessageBox.No)
        if reply == QMessageBox.Yes:
            projects = self.load_projects()
            projects = [p for p in projects if p['name'] != project_name]
            self.save_projects(projects)
            
            # Remove project subfolder
            project_folder = os.path.join(self.projects_folder, project_name)
            if os.path.exists(project_folder):
                import shutil
                shutil.rmtree(project_folder)
            
            self.update_project_list()
            QMessageBox.information(self, "Success", f"Project '{project_name}' deleted successfully!")

    #def view_project(self, project_name):
        # Placeholder for view project functionality
        # QMessageBox.information(self, "View Project", f"Viewing project: {project_name}")
        # You can implement the actual view functionality here
    
    def update_project_display(self, project_name=None):
        projects = self.load_projects()
        self.projects_table.setRowCount(len(projects))
        for row, project in enumerate(projects):
            self.projects_table.setItem(row, 0, QTableWidgetItem(project['name']))
            self.projects_table.setItem(row, 1, QTableWidgetItem(project['timestamp_create']))
            self.projects_table.setItem(row, 2, QTableWidgetItem(str(project['total_data'])))
            self.projects_table.setItem(row, 3, QTableWidgetItem(project['sync_status']))
            
            view_button = QPushButton("View")
            view_button.setStyleSheet("background-color: lightblue;")
            view_button.clicked.connect(lambda _, n=project['name']: self.view_project(n))
            self.projects_table.setCellWidget(row, 4, view_button)
            
            delete_button = QPushButton("Delete")
            delete_button.setStyleSheet("background-color: red; color: white;")
            delete_button.clicked.connect(lambda _, n=project['name']: self.delete_project(n))
            self.projects_table.setCellWidget(row, 5, delete_button)

        if project_name:
            for row in range(self.projects_table.rowCount()):
                if self.projects_table.item(row, 0).text() == project_name:
                    self.projects_table.selectRow(row)
                    break 