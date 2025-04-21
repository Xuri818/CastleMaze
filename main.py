# main.py
import sys
from PyQt6.QtWidgets import QApplication, QMainWindow, QPushButton, QVBoxLayout, QWidget
from ui.game_window import MazeWindow  # Assuming your maze logic is here

class MainMenu(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Maze Size Selector")
        self.setFixedSize(400, 300)

        layout = QVBoxLayout()
        sizes = [5, 10, 15, 20, 25]

        for size in sizes:
            btn = QPushButton(f"{size}x{size}")
            btn.clicked.connect(lambda _, s=size: self.start_maze(s))
            layout.addWidget(btn)

        container = QWidget()
        container.setLayout(layout)
        self.setCentralWidget(container)

    def start_maze(self, size):
        self.maze_window = MazeWindow(rows=size, cols=size)
        self.maze_window.show()
        self.close()

if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = MainMenu()
    window.show()
    sys.exit(app.exec())
