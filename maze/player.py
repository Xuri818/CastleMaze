from PyQt6.QtGui import QColor
from PyQt6.QtCore import Qt

class Player:
    def __init__(self, maze_widget):
        self.maze_widget = maze_widget
        self.position = None

    def set_position(self, row, col):
        self.position = (row, col)

    def move(self, dx, dy):
        if not self.position:
            return False
            
        x, y = self.position
        nx, ny = x + dx, y + dy
        
        if (0 <= nx < self.maze_widget.physical_rows and 
            0 <= ny < self.maze_widget.logical_cols and 
            self.maze_widget.render_maze[nx][ny] in [0, 2, 3]):
            self.position = (nx, ny)
            return True
        return False

    def draw(self, painter, x_offset, y_offset, cell_size):
        if not self.position:
            return
            
        x, y = self.position
        painter_x = x_offset + y * cell_size + 4
        painter_y = y_offset + x * cell_size + 4
        painter.setBrush(QColor(255, 0, 0))
        painter.drawEllipse(painter_x, painter_y, cell_size - 8, cell_size - 8)