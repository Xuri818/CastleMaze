import json
import random
from PyQt6.QtGui import (QPainter, QColor, QKeyEvent, 
                        QImage, QPixmap, QPalette)
from PyQt6.QtCore import *
from PyQt6.QtWidgets import (
    QApplication, QMainWindow, QPushButton, QVBoxLayout, QWidget, QLabel,
    QHBoxLayout, QMessageBox, QInputDialog
)
from maze.generate import Generate
from maze.player import Player
from maze.solve import MazeSolver


# Configuracion de la ventana
WINDOW_WIDTH = 800
WINDOW_HEIGHT = 800
CONTROL_PANEL_HEIGHT = 100
BACKGROUND_COLOR = QColor(18, 18, 18)
MAZE_BACKGROUND_COLOR = QColor(18, 18, 18)
PANEL_COLOR = QColor(100, 100, 100)
BORDER_COLOR = QColor(80, 80, 80)

class MazeWidget(QWidget):
    def __init__(self, rows, cols, mode, parent=None):
        super().__init__(parent)
        self.physical_rows = rows 
        self.physical_cols = cols 
        self.gamemode = mode
        self.solved = False
        self.calculate_cell_size()
        
        self.generator = Generate(rows, cols)
        self.player = Player(self)
        self.textures = {}
        
        self.goal_set = False
        self.start_set = False

        self.setFocusPolicy(Qt.FocusPolicy.StrongFocus)
        self.setStyleSheet("background-color: #121212;")  # Dark background


        self.load_textures()
        self.generate_maze()

    def calculate_cell_size(self):
        """Calcula el tamaño de celda para ajustarse al área disponible"""
        available_width = WINDOW_WIDTH - 150
        available_height = WINDOW_HEIGHT - CONTROL_PANEL_HEIGHT - 150
        
        width_based = available_width // self.physical_cols
        height_based = available_height // self.physical_rows
        
        self.cell_size = min(width_based, height_based)
        self.cell_size = max(8, min(48, self.cell_size))

    def determine_floor_texture(self, row, col):
        """Determina qué textura de piso usar basado en muros adyacentes"""
        has_wall = {
            'u': row > 0 and self.generator.render_maze[row-1][col] == 1,
            'r': col < self.physical_cols-1 and self.generator.render_maze[row][col+1] == 1,
            'd': row < self.physical_rows-1 and self.generator.render_maze[row+1][col] == 1,
            'l': col > 0 and self.generator.render_maze[row][col-1] == 1
        }
        
        if not any(has_wall.values()):
            return 'ce'
        elif has_wall['u'] and has_wall['l']:
            return 'ul'
        elif has_wall['u'] and has_wall['r']:
            return 'ur'
        elif has_wall['d'] and has_wall['l']:
            return 'dl'
        elif has_wall['d'] and has_wall['r']:
            return 'dr'
        else:
            return 'ad'

    def load_textures(self):
        """Carga las texturas con manejo robusto de errores"""
        try:
            with open('assets/textures_config.json', 'r') as f:
                config = json.load(f)
            
            # Cargar texturas de muros
            wall_config = config['walls']
            wall_atlas = QImage(f"assets/{wall_config['texture_atlas']}")
            if not wall_atlas.isNull():
                for name, region in wall_config['textures'].items():
                    texture = wall_atlas.copy(region['x'], region['y'], region['w'], region['h'])
                    if self.cell_size != region['w']:
                        texture = texture.scaled(self.cell_size, self.cell_size,
                                              Qt.AspectRatioMode.IgnoreAspectRatio,
                                              Qt.TransformationMode.SmoothTransformation)
                    self.textures[f"wall_{name}"] = QPixmap.fromImage(texture)
            
            # Cargar texturas de pisos
            floor_config = config['floors']
            floor_atlas = QImage(f"assets/{floor_config['texture_atlas']}")
            if not floor_atlas.isNull():
                for name, region in floor_config['textures'].items():
                    texture = floor_atlas.copy(region['x'], region['y'], region['w'], region['h'])
                    if self.cell_size != region['w']:
                        texture = texture.scaled(self.cell_size, self.cell_size,
                                              Qt.AspectRatioMode.IgnoreAspectRatio,
                                              Qt.TransformationMode.SmoothTransformation)
                    self.textures[f"floor_{name}"] = QPixmap.fromImage(texture)
                    
        except Exception as e:
            print(f"Error cargando texturas: {str(e)}")
            # Fallback a colores básicos
            self.textures = {
                'wall_top': QPixmap(self.cell_size, self.cell_size),
                'wall_mid': QPixmap(self.cell_size, self.cell_size),
                'wall_bottom': QPixmap(self.cell_size, self.cell_size)
            }
            self.textures['wall_top'].fill(QColor(100, 100, 100))
            self.textures['wall_mid'].fill(QColor(80, 80, 80))
            self.textures['wall_bottom'].fill(QColor(120, 120, 120))

    def generate_maze(self):
        """Genera el laberinto y configura el renderizado"""
        self.generator.generate_maze()
        self.generator.generate_render_maze()
        self.generator.add_imperfections(12)
        self.render_maze = self.generator.getRenderMaze()

        
        goal_row, goal_col = self.find_random_goal()
        self.render_maze[goal_row][goal_col] = 3
        self.goal_set = True
        self.goal_pos = (goal_row, goal_col)

        if self.gamemode == "Game":
            start_row, start_col = self.find_random_goal()
            self.render_maze[start_row][start_col] = 4
            self.start_set = True
            self.start_pos = (start_row, start_col)
            self.player.set_position(start_row, start_col)
            
    def paintEvent(self, event):
        painter = QPainter(self)
        painter.fillRect(0, 0, self.width(), self.height(), BACKGROUND_COLOR)
        
        
        total_width = self.physical_cols * self.cell_size
        total_height = self.physical_rows * self.cell_size
        x_offset = (self.width() - total_width) // 2
        y_offset = 10  # Margen superior
        

        # Dibujar pisos y atajos
        for row in range(self.physical_rows):
            for col in range(self.physical_cols):
                value = self.render_maze[row][col]
                x = x_offset + col * self.cell_size
                y = y_offset + row * self.cell_size
                
                if value in [0, 2]:
                    texture_key = self.determine_floor_texture(row, col)
                    full_key = f"floor_{texture_key}"
                    
                    if full_key in self.textures:
                        if value == 2:  # Atajo - aplicar tinte azul
                            texture_img = self.textures[full_key].toImage()
                            for tex_x in range(texture_img.width()):
                                for tex_y in range(texture_img.height()):
                                    color = texture_img.pixelColor(tex_x, tex_y)
                                    new_color = QColor(
                                        color.red(),
                                        color.green(),
                                        min(255, color.blue() + 15),
                                        color.alpha()
                                    )
                                    texture_img.setPixelColor(tex_x, tex_y, new_color)
                            painter.drawImage(x, y, texture_img)
                        else:
                            painter.drawPixmap(x, y, self.textures[full_key])
                    else:
                        color = QColor(0, 120, 255) if value == 2 else QColor(255, 255, 255)
                        painter.fillRect(x, y, self.cell_size, self.cell_size, color)
                
                elif value == 3:
                    painter.fillRect(x, y, self.cell_size, self.cell_size, QColor(0, 255, 0))
                elif value == 4:
                    painter.fillRect(x, y, self.cell_size, self.cell_size, QColor(255, 100, 100))
                elif value == 5:
                    painter.fillRect(x, y, self.cell_size, self.cell_size, QColor(100, 180, 255))  # Ruta óptima azul

        # Dibujar muros
        for row in range(self.physical_rows):
            for col in range(self.physical_cols):
                if self.render_maze[row][col] == 1:
                    x = x_offset + col * self.cell_size
                    y = y_offset + row * self.cell_size
                    
                    texture = 'wall_top'
                    if row == self.physical_rows - 1:
                        texture = 'wall_bottom'
                    elif row < self.physical_rows - 1 and self.render_maze[row+1][col] in [0, 2, 3, 4]:
                        texture = 'wall_bottom'
                    elif (row < self.physical_rows - 1 and 
                        self.render_maze[row+1][col] == 1 and
                        (row+1 == self.physical_rows - 1 or 
                        self.render_maze[row+2][col] in [0, 2, 3, 4])):
                        texture = 'wall_mid'
                    
                    if f"wall_{texture}" in self.textures:
                        painter.drawPixmap(x, y, self.textures[f"wall_{texture}"])
                    else:
                        painter.fillRect(x, y, self.cell_size, self.cell_size, QColor(0, 0, 0))

        # Dibujar jugador
        self.player.draw(painter, x_offset, y_offset, self.cell_size)

    def mousePressEvent(self, event):
        self.setFocus()
        mouse_pos = event.position()
        mouse_x = mouse_pos.x()
        mouse_y = mouse_pos.y()
        
        total_width = self.physical_cols * self.cell_size
        total_height = self.physical_rows * self.cell_size
        MARGIN_TOP = 10
        MARGIN_SIDES = 10
        MARGIN_BOTTOM = 20
        
        lab_x_start = (self.width() - total_width) // 2
        lab_x_start = max(MARGIN_SIDES, lab_x_start)
        
        available_height = self.height() - MARGIN_TOP - MARGIN_BOTTOM
        lab_y_start = 10
        
        if not (lab_x_start <= mouse_x < lab_x_start + total_width and
                lab_y_start <= mouse_y < lab_y_start + total_height):
            return
        
        col = int((mouse_x - lab_x_start) // self.cell_size)
        row = int((mouse_y - lab_y_start) // self.cell_size)
        
        col = max(0, min(self.physical_cols - 1, col))
        row = max(0, min(self.physical_rows - 1, row))
        
        if self.render_maze[row][col] in [1, 3, 4]:
            return
        
        if self.start_set == False:
            self.render_maze[row][col] = 4  # inicio
            self.start_set = True
            self.start_pos = (row, col)

    def solve_mazee(self):
        solver = MazeSolver(self.render_maze)
        self.render_maze= solver.solve()
        self.paths = solver.get_paths()
        self.update()
        self.solved = True
    
    def render_path(self, path):
        for i in range(self.physical_rows):
            for j in range(self.physical_cols):
                if self.render_maze[i][j] == 5:  # Reset marked path cells
                    self.render_maze[i][j] = 0

        
        for x, y in path:
            if self.render_maze[x][y] != 4 and self.render_maze[x][y] != 3:  # Exclude start/goal
                self.render_maze[x][y] = 5

        self.update()  # Redraw the maze

    def find_random_goal(self):

        valid_goals = [
            (r, c) for r in range(self.physical_rows)
                for c in range(self.physical_cols)
                if self.render_maze[r][c] == 0
        ]
    
        return random.choice(valid_goals) if valid_goals else (1, 1)



    def keyPressEvent(self, event: QKeyEvent):
        if not self.player.position:
            return
            
        dir_map = {
            Qt.Key.Key_W: (-1, 0),
            Qt.Key.Key_S: (1, 0),
            Qt.Key.Key_A: (0, -1),
            Qt.Key.Key_D: (0, 1),
        }
        if self.gamemode == "Game":
            if event.key() in dir_map:
                dx, dy = dir_map[event.key()]
                if self.player.move(dx, dy):
                    self.update()
                    x, y = self.player.position
                    if self.render_maze[x][y] == 3:
                        QMessageBox.information(self, "¡Victoria!", "¡Llegaste a la meta!")



class MazeWindow(QMainWindow):
    def __init__(self, rows, cols, mode):
        super().__init__()
        self.setWindowFlags(Qt.WindowType.FramelessWindowHint)
        self.showFullScreen()
        self.setStyleSheet("background-color: #121212;")

        self.mode = mode  # Store game mode

        # Main Horizontal Layout (Maze + Side Panel)
        main_layout = QHBoxLayout()

        # Left Side - Maze Layout
        maze_container = QVBoxLayout()

        # Logo Layout (Top Left)
        logo_layout = QHBoxLayout()
        self.logo = QLabel()
        pixmap = QPixmap("assets/logo.png").scaled(200, 200, Qt.AspectRatioMode.KeepAspectRatio)
        self.logo.setPixmap(pixmap)
        logo_layout.addWidget(self.logo, alignment=Qt.AlignmentFlag.AlignLeft)

        # Maze Layout (Centered)
        self.maze_widget = MazeWidget(rows, cols, mode)
        self.maze_widget.setMinimumSize(600, 600)  # Ensure maze is visible
        maze_container.addLayout(logo_layout)  # Add logo at top
        maze_container.addStretch(1)  # Push maze into center
        maze_container.addWidget(self.maze_widget, alignment=Qt.AlignmentFlag.AlignCenter)
        maze_container.addStretch(1)  # Keep spacing consistent

        # Control Panel (Buttons at Bottom)
        self.control_panel = QWidget()
        self.control_panel.setFixedHeight(60)
        self.control_panel.setStyleSheet("background-color: #1A1A1A; border-top: 2px solid #87CEEB;")
        buttons_layout = QHBoxLayout()

        for text in ["Return", "Solve", "Save", "Upload"]:
            btn = QPushButton(text)
            btn.setStyleSheet("background-color: #1E90FF; color: white; font-size: 16px; padding: 8px; border-radius: 5px;")
            buttons_layout.addWidget(btn)

        self.control_panel.setLayout(buttons_layout)
        maze_container.addWidget(self.control_panel)  # Buttons go at the bottom

        # Right Side - Path Selection Panel
        self.path_panel = QWidget()
        self.path_panel.setFixedWidth(220)
        self.path_panel.setStyleSheet("background-color: #1A1A1A; border-left: 2px solid #87CEEB;")
        self.path_layout = QVBoxLayout()
        self.path_panel.setLayout(self.path_layout)

        # Add both sections to the main layout
        main_layout.addLayout(maze_container, stretch=3)  # Maze takes more space
        main_layout.addWidget(self.path_panel, stretch=1)  # Path selection panel

        # Set up main container
        container = QWidget()
        container.setLayout(main_layout)
        self.setCentralWidget(container)

        # Button actions
        buttons_layout.itemAt(0).widget().clicked.connect(self.return_to_menu)
        buttons_layout.itemAt(1).widget().clicked.connect(self.solve_maze)
        buttons_layout.itemAt(2).widget().clicked.connect(self.save_maze)
        buttons_layout.itemAt(3).widget().clicked.connect(self.upload_maze)

    def solve_maze(self):
        if self.maze_widget.solved == False:
            self.maze_widget.solve_mazee()
            all_paths = self.maze_widget.paths
            self.path_buttons(all_paths)

    def save_maze(self):
        print("Saving maze...")  # Placeholder for save logic

    def upload_maze(self):
        print("Uploading maze...")  # Placeholder for upload logic

    def return_to_menu(self):
        print("Returning to menu...")  # Placeholder for menu navigation

    def path_buttons(self, all_paths):
    # Clear previous buttons
        while self.path_layout.count():
            widget = self.path_layout.takeAt(0).widget()
            if widget:
                widget.deleteLater()

        for i in range(len(all_paths)):
            min_index = i
            for j in range(i + 1, len(all_paths)):
                if all_paths[j][1] < all_paths[min_index][1]:  # Compare step counts
                    min_index = j
            all_paths[i], all_paths[min_index] = all_paths[min_index], all_paths[i]
        
        xxx = 1
        for value, (path, steps) in enumerate(all_paths):
            if xxx == 1:
                btn = QPushButton(f" ⚡ Path {value + 1} ({steps} steps)")
                btn.setStyleSheet("background-color: #1E90FF; color: white; font-size: 14px;")
                btn.clicked.connect(lambda _, p=path: self.maze_widget.render_path(p))
                self.path_layout.addWidget(btn)
            else: 
                btn = QPushButton(f"Path {value + 1} ({steps} steps)")
                btn.setStyleSheet("background-color: #1E90FF; color: white; font-size: 14px;")
                btn.clicked.connect(lambda _, p=path: self.maze_widget.render_path(p))
                self.path_layout.addWidget(btn)
            xxx += 1
