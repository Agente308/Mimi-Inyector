import sys
import os
import ctypes
from ctypes import wintypes
from PyQt5.QtWidgets import (
    QApplication, QWidget, QPushButton, QLabel, QLineEdit,
    QFileDialog, QVBoxLayout, QHBoxLayout
)
from PyQt5.QtGui import QPixmap
from PyQt5.QtCore import Qt

def resource_path(relative_path):
    try:
        base_path = sys._MEIPASS
    except Exception:
        base_path = os.path.abspath(".")
    return os.path.join(base_path, relative_path)

class DLLInjectorUI(QWidget):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Mimi DLL Injector 3.0")
        self.setFixedSize(450, 450)
        self.setStyleSheet("background-color: white;")

        self.inject_button = QPushButton("Inyectar")
        self.inject_button.setFixedSize(200, 45)
        self.inject_button.setStyleSheet("""
            QPushButton {
                background-color: #0078D7;
                color: white;
                font-size: 15px;
                font-weight: bold;
                padding: 10px;
                border: none;
                border-radius: 10px;
            }
            QPushButton:hover {
                background-color: #005BB5;
            }
        """)
        self.inject_button.clicked.connect(self.inject_dll)

        self.dll_path_input = QLineEdit()
        self.dll_path_input.setPlaceholderText("Selecciona una DLL...")
        self.dll_path_input.setReadOnly(True)
        self.dll_path_input.setFixedSize(200, 38)
        self.dll_path_input.setStyleSheet("padding: 6px; font-size: 13px; border: 1px solid #ccc; border-radius: 8px;")

        self.browse_button = QPushButton("📁")
        self.browse_button.setFixedSize(40, 40)
        self.browse_button.clicked.connect(self.browse_dll)
        self.browse_button.setStyleSheet("border: 1px solid #ccc; border-radius: 8px; font-size: 20px;")

        left_panel = QVBoxLayout()
        left_panel.setAlignment(Qt.AlignCenter)
        left_panel.addWidget(self.inject_button)
        left_panel.addSpacing(15)
        left_panel.addWidget(self.dll_path_input, alignment=Qt.AlignCenter)
        left_panel.addSpacing(10)
        left_panel.addWidget(self.browse_button, alignment=Qt.AlignCenter)

        white_spacer = QLabel()
        white_spacer.setFixedWidth(10)
        white_spacer.setStyleSheet("background-color: white;")

        self.bg_image = QLabel()
        image_path = resource_path("img.jpg")
        self.bg_image.setPixmap(QPixmap(image_path).scaled(370, 370, Qt.KeepAspectRatio, Qt.SmoothTransformation))
        self.bg_image.setAlignment(Qt.AlignCenter)

        image_layout = QVBoxLayout()
        image_layout.addWidget(self.bg_image)
        image_layout.setAlignment(Qt.AlignCenter)

        main_layout = QHBoxLayout()
        main_layout.setSpacing(5)
        main_layout.setContentsMargins(20, 20, 20, 20)
        main_layout.addLayout(left_panel)
        main_layout.addWidget(white_spacer)
        main_layout.addLayout(image_layout)
        self.setLayout(main_layout)

    def browse_dll(self):
        dll_path, _ = QFileDialog.getOpenFileName(self, "Selecciona la DLL", "", "DLL Files (*.dll)")
        if dll_path:
            self.full_path = dll_path
            file_name = os.path.basename(dll_path)
            self.dll_path_input.setText(file_name)

    def inject_dll(self):
        if not hasattr(self, "full_path"):
            return

        dll_path = self.full_path
        process_name = "TuProceso.exe"

        if not os.path.isfile("Inyector.dll"):
            return

        try:
            dll = ctypes.WinDLL("Inyector.dll")
            dll.Inject.argtypes = [wintypes.LPCWSTR, wintypes.LPCWSTR]
            dll.Inject.restype = ctypes.c_bool
            dll.Inject(dll_path, process_name)
        except:
            pass

if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = DLLInjectorUI()
    window.show()
    sys.exit(app.exec_())
