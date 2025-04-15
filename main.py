import sys
import random
from PyQt6.QtWidgets import QApplication, QWidget, QVBoxLayout
from PyQt6.QtGui import QPainter, QColor
from PyQt6.QtCore import Qt, QTimer

CELL_SIZE = 15
ROWS, COLS = 13, 13

class MazeWidget(QWidget):
    def __init__(self):
        super().__init__()
        self.setFixedSize(COLS * CELL_SIZE, ROWS * CELL_SIZE)
        self.maze = [[1 for _ in range(COLS)] for _ in range(ROWS)]
        self.generate_maze()
        self.add_imperfections(100)  # Number of walls to be removed

    def generate_maze(self):
        def carve(x, y):
            dirs = [(0, -2), (0, 2), (-2, 0), (2, 0)]
            random.shuffle(dirs)
            for dx, dy in dirs:
                nx, ny = x + dx, y + dy
                if 0 <= nx < ROWS and 0 <= ny < COLS and self.maze[nx][ny] == 1:
                    self.maze[nx][ny] = 0
                    self.maze[x + dx // 2][y + dy // 2] = 0
                    carve(nx, ny)

        self.maze[1][1] = 0
        carve(1, 1)

    def add_imperfections(self, count):
        attempts = 0
        added = 0
        max_attempts = count * 10

        while added < count and attempts < max_attempts:
            x = random.randrange(1, ROWS - 1)
            y = random.randrange(1, COLS - 1)
            if self.maze[x][y] == 1:
                if x % 2 == 1 and y % 2 == 0:
                    if self.maze[x][y - 1] == 0 and self.maze[x][y + 1] == 0:
                        self.maze[x][y] = 2
                        added += 1
                elif x % 2 == 0 and y % 2 == 1:
                    if self.maze[x - 1][y] == 0 and self.maze[x + 1][y] == 0:
                        self.maze[x][y] = 2
                        added += 1
            attempts += 1

    def paintEvent(self, event):
        painter = QPainter(self)
        for row in range(ROWS):
            for col in range(COLS):
                value = self.maze[row][col]
                if value == 0:
                    color = QColor(255, 255, 255)  # Way
                elif value == 1:
                    color = QColor(0, 0, 0)        # Wall
                elif value == 2:
                    color = QColor(0, 120, 255)    # Imperfection
                painter.fillRect(col * CELL_SIZE, row * CELL_SIZE, CELL_SIZE, CELL_SIZE, color)


class MazeWindow(QWidget):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("CastleMaze")
        layout = QVBoxLayout()
        self.maze_widget = MazeWidget()
        layout.addWidget(self.maze_widget)
        self.setLayout(layout)

if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = MazeWindow()
    window.show()
    sys.exit(app.exec())
