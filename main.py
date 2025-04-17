import sys
from PyQt6.QtWidgets import QApplication
from ui.game_window import MazeWindow

if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = MazeWindow()
    window.show()
    sys.exit(app.exec())