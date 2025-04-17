import json
import random
from PyQt6.QtWidgets import (QWidget, QVBoxLayout, QMessageBox, 
                            QLabel, QHBoxLayout)
from PyQt6.QtGui import (QPainter, QColor, QKeyEvent, 
                        QImage, QPixmap, QPalette)
from PyQt6.QtCore import Qt
from maze.generate import Generate
from maze.player import Player

# Configuracion de la ventana
MAZE_SIZE = 9
WINDOW_WIDTH = 800
WINDOW_HEIGHT = 800
CONTROL_PANEL_HEIGHT = 100
BACKGROUND_COLOR = QColor(45, 45, 48)
MAZE_BACKGROUND_COLOR = QColor(60, 60, 60)
PANEL_COLOR = QColor(100, 100, 100)
BORDER_COLOR = QColor(80, 80, 80)

class MazeWidget(QWidget):
    def __init__(self, rows, cols, parent=None):
        super().__init__(parent)
        self.logical_rows = rows
        self.logical_cols = cols
        self.physical_rows = rows * 3
        self.calculate_cell_size()
        
        self.generator = Generate(rows, cols)
        self.player = Player(self)
        self.textures = {}
        
        self.goal_set = False
        self.start_set = False
        self.setFocusPolicy(Qt.FocusPolicy.StrongFocus)
        
        self.load_textures()
        self.generate_maze()

    def calculate_cell_size(self):
        """Calcula el tamaño de celda para ajustarse al área disponible"""
        available_width = WINDOW_WIDTH - 20
        available_height = WINDOW_HEIGHT - CONTROL_PANEL_HEIGHT - 20
        
        width_based = available_width // self.logical_cols
        height_based = available_height // self.physical_rows
        
        self.cell_size = min(width_based, height_based)
        self.cell_size = max(8, min(48, self.cell_size))

    def determine_floor_texture(self, row, col):
        """Determina qué textura de piso usar basado en muros adyacentes"""
        has_wall = {
            'u': row > 0 and self.generator.render_maze[row-1][col] == 1,
            'r': col < self.logical_cols-1 and self.generator.render_maze[row][col+1] == 1,
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
        self.generator.add_imperfections(100)
        self.render_maze = self.generator.render_maze

    def paintEvent(self, event):
        painter = QPainter(self)
        painter.fillRect(0, 0, self.width(), self.height(), BACKGROUND_COLOR)
        
        total_width = self.logical_cols * self.cell_size
        total_height = self.physical_rows * self.cell_size
        x_offset = (self.width() - total_width) // 2
        y_offset = 10  # Margen superior
        
        # Dibujar pisos y atajos
        for row in range(self.physical_rows):
            for col in range(self.logical_cols):
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

        # Dibujar muros
        for row in range(self.physical_rows):
            for col in range(self.logical_cols):
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
        
        total_width = self.logical_cols * self.cell_size
        total_height = self.physical_rows * self.cell_size
        MARGIN_TOP = 10
        MARGIN_SIDES = 10
        MARGIN_BOTTOM = 20
        
        lab_x_start = (self.width() - total_width) // 2
        lab_x_start = max(MARGIN_SIDES, lab_x_start)
        
        available_height = self.height() - MARGIN_TOP - MARGIN_BOTTOM
        lab_y_start = MARGIN_TOP + (available_height - total_height) // 2 if total_height < available_height else MARGIN_TOP
        
        if not (lab_x_start <= mouse_x < lab_x_start + total_width and
                lab_y_start <= mouse_y < lab_y_start + total_height):
            return
        
        col = int((mouse_x - lab_x_start) // self.cell_size)
        row = int((mouse_y - lab_y_start) // self.cell_size)
        
        col = max(0, min(self.logical_cols - 1, col))
        row = max(0, min(self.physical_rows - 1, row))
        
        if self.render_maze[row][col] in [1, 3, 4]:
            return
        
        if not self.goal_set:
            self.render_maze[row][col] = 3
            self.goal_set = True
        elif not self.start_set:
            self.render_maze[row][col] = 4
            self.start_set = True
            self.player.set_position(row, col)
        
        self.update()

    def keyPressEvent(self, event: QKeyEvent):
        if not self.player.position:
            return
            
        dir_map = {
            Qt.Key.Key_W: (-1, 0),
            Qt.Key.Key_S: (1, 0),
            Qt.Key.Key_A: (0, -1),
            Qt.Key.Key_D: (0, 1),
        }
        
        if event.key() in dir_map:
            dx, dy = dir_map[event.key()]
            if self.player.move(dx, dy):
                self.update()
                x, y = self.player.position
                if self.render_maze[x][y] == 3:
                    QMessageBox.information(self, "¡Victoria!", "¡Llegaste a la meta!")

class MazeWindow(QWidget):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("CastleMaze")
        self.setFixedSize(WINDOW_WIDTH, WINDOW_HEIGHT)
        
        palette = self.palette()
        palette.setColor(self.backgroundRole(), BACKGROUND_COLOR)
        self.setPalette(palette)
        
        layout = QVBoxLayout()
        layout.setContentsMargins(10, 10, 10, 10)
        layout.setSpacing(15)
        
        self.maze_widget = MazeWidget(MAZE_SIZE, MAZE_SIZE * 3)
        layout.addWidget(self.maze_widget)
        
        self.control_panel = QWidget()
        self.control_panel.setFixedHeight(CONTROL_PANEL_HEIGHT)
        self.control_panel.setAutoFillBackground(True)
        
        panel_palette = self.control_panel.palette()
        panel_palette.setColor(self.control_panel.backgroundRole(), PANEL_COLOR)
        self.control_panel.setPalette(panel_palette)
        self.control_panel.setStyleSheet(f"border-top: 2px solid {BORDER_COLOR.name()};")
        
        panel_layout = QHBoxLayout(self.control_panel)
        panel_layout.addWidget(QLabel("Panel de control"))
        
        layout.addWidget(self.control_panel)
        self.setLayout(layout)