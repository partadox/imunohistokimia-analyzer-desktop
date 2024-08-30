import cv2
import numpy as np
from PyQt5.QtWidgets import (QWidget, QVBoxLayout, QHBoxLayout, QLabel, QPushButton, 
                             QSlider, QFileDialog, QInputDialog, QScrollArea)
from PyQt5.QtGui import QImage, QPixmap, QPainter, QPen, QColor
from PyQt5.QtCore import Qt, QPoint

class ImageViewer(QWidget):
    def __init__(self, image_path):
        super().__init__()
        self.image_path = image_path
        self.original_image = cv2.imread(image_path)
        self.displayed_image = self.original_image.copy()
        self.zoom_factor = 1
        self.drawing = False
        self.last_point = QPoint()
        self.current_tool = None
        self.setup_ui()

    def setup_ui(self):
        main_layout = QVBoxLayout()

        # Scroll area for image
        scroll_area = QScrollArea()
        scroll_area.setWidgetResizable(True)
        main_layout.addWidget(scroll_area, 1)  # Add stretch factor

        # Container for image
        image_container = QWidget()
        scroll_area.setWidget(image_container)
        image_layout = QVBoxLayout(image_container)

        # Image display
        self.image_label = QLabel()
        self.image_label.setAlignment(Qt.AlignCenter)
        image_layout.addWidget(self.image_label)

        self.update_image()

        # Tools
        tools_layout = QHBoxLayout()
        
        zoom_in_btn = QPushButton("Zoom In")
        zoom_in_btn.clicked.connect(self.zoom_in)
        tools_layout.addWidget(zoom_in_btn)

        zoom_out_btn = QPushButton("Zoom Out")
        zoom_out_btn.clicked.connect(self.zoom_out)
        tools_layout.addWidget(zoom_out_btn)

        draw_btn = QPushButton("Draw")
        draw_btn.clicked.connect(lambda: self.set_tool("draw"))
        tools_layout.addWidget(draw_btn)

        crop_btn = QPushButton("Crop")
        crop_btn.clicked.connect(lambda: self.set_tool("crop"))
        tools_layout.addWidget(crop_btn)

        resize_btn = QPushButton("Resize")
        resize_btn.clicked.connect(self.resize_image)
        tools_layout.addWidget(resize_btn)

        save_btn = QPushButton("Save")
        save_btn.clicked.connect(self.save_image)
        tools_layout.addWidget(save_btn)

        main_layout.addLayout(tools_layout)

        self.setLayout(main_layout)
        self.resize(800, 600)  # Set initial size

        self.image_label.setMouseTracking(True)
        self.image_label.mousePressEvent = self.mouse_press_event
        self.image_label.mouseMoveEvent = self.mouse_move_event
        self.image_label.mouseReleaseEvent = self.mouse_release_event

    def update_image(self):
        height, width = self.displayed_image.shape[:2]
        bytes_per_line = 3 * width
        q_image = QImage(self.displayed_image.data, width, height, bytes_per_line, QImage.Format_RGB888).rgbSwapped()
        self.pixmap = QPixmap.fromImage(q_image)
        self.image_label.setPixmap(self.pixmap)
        self.image_label.adjustSize()

    def get_scaled_point(self, point):
        # Convert widget coordinates to image coordinates
        x = int(point.x() * (self.displayed_image.shape[1] / self.image_label.width()))
        y = int(point.y() * (self.displayed_image.shape[0] / self.image_label.height()))
        return QPoint(x, y)

    def mouse_press_event(self, event):
        if self.current_tool == "draw":
            self.drawing = True
            self.last_point = self.get_scaled_point(event.pos())

    def mouse_move_event(self, event):
        if self.current_tool == "draw" and self.drawing:
            current_point = self.get_scaled_point(event.pos())
            painter = QPainter(self.pixmap)
            painter.setPen(QPen(QColor(255, 0, 0), 3, Qt.SolidLine))
            painter.drawLine(self.last_point, current_point)
            self.image_label.setPixmap(self.pixmap)
            self.last_point = current_point

    def mouse_release_event(self, event):
        if self.current_tool == "draw":
            self.drawing = False
            # Update the displayed_image with the drawn content
            self.displayed_image = self.pixmap.toImage().convertToFormat(QImage.Format_RGB888)
            self.displayed_image = np.array(self.displayed_image.constBits()).reshape(self.displayed_image.height(), self.displayed_image.width(), 3)
        elif self.current_tool == "crop":
            end_point = self.get_scaled_point(event.pos())
            x1, y1 = self.last_point.x(), self.last_point.y()
            x2, y2 = end_point.x(), end_point.y()
            x1, x2 = min(x1, x2), max(x1, x2)
            y1, y2 = min(y1, y2), max(y1, y2)
            self.displayed_image = self.displayed_image[y1:y2, x1:x2]
            self.update_image()

    def zoom_in(self):
        self.zoom_factor *= 1.2
        self.apply_zoom()

    def zoom_out(self):
        self.zoom_factor /= 1.2
        self.apply_zoom()

    def apply_zoom(self):
        height, width = self.original_image.shape[:2]
        new_height, new_width = int(height * self.zoom_factor), int(width * self.zoom_factor)
        self.displayed_image = cv2.resize(self.original_image, (new_width, new_height))
        self.update_image()

    def set_tool(self, tool):
        self.current_tool = tool
        if tool == "crop":
            self.image_label.setCursor(Qt.CrossCursor)
        else:
            self.image_label.setCursor(Qt.ArrowCursor)

    def mousePressEvent(self, event):
        if self.current_tool == "draw":
            self.drawing = True
            self.last_point = event.pos()

    def mouseMoveEvent(self, event):
        if self.current_tool == "draw" and self.drawing:
            painter = QPainter(self.image_label.pixmap())
            painter.setPen(QPen(Qt.red, 3, Qt.SolidLine))
            painter.drawLine(self.last_point, event.pos())
            self.last_point = event.pos()
            self.image_label.update()

    def mouseReleaseEvent(self, event):
        if self.current_tool == "draw":
            self.drawing = False
        elif self.current_tool == "crop":
            x, y = self.last_point.x(), self.last_point.y()
            w, h = event.pos().x() - x, event.pos().y() - y
            self.displayed_image = self.displayed_image[y:y+h, x:x+w]
            self.update_image()

    def resize_image(self):
        new_width, ok = QInputDialog.getInt(self, "Resize Image", "Enter new width:", 
                                            self.displayed_image.shape[1], 1, 10000)
        if ok:
            aspect_ratio = self.displayed_image.shape[0] / self.displayed_image.shape[1]
            new_height = int(new_width * aspect_ratio)
            self.displayed_image = cv2.resize(self.displayed_image, (new_width, new_height))
            self.update_image()

    def save_image(self):
        file_name = self.image_path.split('/')[-1].split('.')[0]
        save_path, _ = QFileDialog.getSaveFileName(self, "Save Image", 
                                                   f"{file_name}-edited.jpg", 
                                                   "Images (*.png *.jpg *.bmp)")
        if save_path:
            cv2.imwrite(save_path, self.displayed_image)