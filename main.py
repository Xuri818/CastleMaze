# main.py
import sys
from PyQt6.QtWidgets import (
    QApplication, QMainWindow, QPushButton, QVBoxLayout, QWidget, QLabel,
    QHBoxLayout, QMessageBox, QInputDialog
)
from PyQt6.QtGui import QPixmap, QPalette
from PyQt6.QtCore import *
from ui.game_window import MazeWindow  # Assuming your maze logic is here

class WelcomeWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowFlags(
            Qt.WindowType.FramelessWindowHint | 
            Qt.WindowType.WindowMinimizeButtonHint
        )
        self.setFixedSize(400, 300)
        self.setStyleSheet("background-color: #121212;")  # Dark background

        # Layout
        layout = QVBoxLayout()
        label = QLabel("Welcome to Castle Maze!")
        label.setStyleSheet("color: #FFFFFF; font-size: 18px; font-weight: bold;")
        label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        layout.addWidget(label)

        image = QLabel()  # Add your image here
        pixmap = QPixmap("assets\logo.png").scaled(200, 100, Qt.AspectRatioMode.KeepAspectRatio)
        image.setPixmap(pixmap)
        image.setAlignment(Qt.AlignmentFlag.AlignCenter)
        layout.addWidget(image)

        play_button = QPushButton("Play")
        play_button.setStyleSheet("background-color: #1E90FF; color: white; font-size: 16px;")
        play_button.clicked.connect(self.go_to_mode_selection)
        layout.addWidget(play_button)

        close_button = QPushButton("Shut Down")
        close_button.setStyleSheet("background-color: #1E90FF; color: white; font-size: 16px;")
        close_button.clicked.connect(self.close)
        layout.addWidget(close_button)

        container = QWidget()
        container.setLayout(layout)
        self.setCentralWidget(container)

    def closeEvent(self, event):
        self.close()
        
    def go_to_mode_selection(self):
        self.mode_window = ModeSelectionWindow()
        self.mode_window.show()
        self.close()

class ModeSelectionWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowFlags(Qt.WindowType.FramelessWindowHint)
        self.setFixedSize(400, 300)
        self.setStyleSheet("background-color: #121212;")

        layout = QVBoxLayout()
        label = QLabel("Select a Mode:")
        label.setStyleSheet("color: #FFFFFF; font-size: 18px; font-weight: bold;")
        label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        layout.addWidget(label)

        game_button = QPushButton("Game Mode")
        game_button.setStyleSheet("background-color: #1E90FF; color: white; font-size: 16px;")
        game_button.clicked.connect(lambda: self.go_to_size_selection("Game"))
        layout.addWidget(game_button)

        no_game_button = QPushButton("No-Game Mode")
        no_game_button.setStyleSheet("background-color: #1E90FF; color: white; font-size: 16px;")
        no_game_button.clicked.connect(lambda: self.go_to_size_selection("No-Game"))
        layout.addWidget(no_game_button)

        return_button = QPushButton("Return 🢀 ")
        return_button.setStyleSheet("background-color: #1E90FF; color: white; font-size: 16px;")
        return_button.clicked.connect(lambda: self.go_to_welcome())
        layout.addWidget(return_button)

        container = QWidget()
        container.setLayout(layout)
        self.setCentralWidget(container)

    def go_to_welcome(self):
        self.welcome_window = WelcomeWindow()
        self.welcome_window.show()
        self.close()

    def go_to_size_selection(self, mode):
        self.size_window = MazeSizeWindow(mode)
        self.size_window.show()
        self.close()

class MazeSizeWindow(QMainWindow):
    def __init__(self, mode):
        super().__init__()
        self.mode = mode
        self.setWindowFlags(Qt.WindowType.FramelessWindowHint)
        self.setFixedSize(400, 300)
        self.setStyleSheet("background-color: #121212;")

        layout = QVBoxLayout()
        label = QLabel(f"Select a Maze Size ({self.mode}):")
        label.setStyleSheet("color: #FFFFFF; font-size: 18px; font-weight: bold;")
        label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        layout.addWidget(label)

        for size in [10, 15, 20, 25, 30, 35]:
            btn = QPushButton(f"{size}x{size}")
            btn.setStyleSheet("background-color: #1E90FF; color: white; font-size: 16px;")
            btn.clicked.connect(lambda _, m = mode, s=size: self.start_maze(s,m))
            layout.addWidget(btn)

        return_button = QPushButton("Return 🢀 ")
        return_button.setStyleSheet("background-color: #1E90FF; color: white; font-size: 16px;")
        return_button.clicked.connect(lambda: self.go_to_mode_selection())
        layout.addWidget(return_button)

        container = QWidget()
        container.setLayout(layout)
        self.setCentralWidget(container)

    def go_to_mode_selection(self):
        self.mode_window = ModeSelectionWindow()
        self.mode_window.show()
        self.close()
        
    def start_maze(self, size, mode):
        self.maze_window = MazeWindow(size, size, mode)
        self.maze_window.show()
        self.close()

if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = WelcomeWindow()
    window.show()
    sys.exit(app.exec())
