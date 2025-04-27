from PyQt6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, 
    QFrame, QLabel, QPushButton, QGraphicsView, 
    QGraphicsScene, QGraphicsPixmapItem, QMessageBox
)
from PyQt6.QtCore import Qt, QRectF, QTimer
from PyQt6.QtGui import QPixmap, QPalette, QTransform, QPainter
from config.game_config import GameConfig
from config.Generate import MazeGenerator
from config.atlas_loader import AtlasLoader

class MazeWidget(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.parent_window = parent
        self.game_mode = GameConfig.get_game_mode()
        self.maze_size = GameConfig.get_maze_size()
        self.atlas_loader = AtlasLoader()
        self.cell_size = 48  # Tamaño de cada celda en píxeles
        self.scale_factor = 1.0
        if GameConfig.get_game_mode() == "Solver":
            self.selecting_start_point = True
        else:
            self.selecting_start_point = False
        self.start_point = None
        
        self._setup_ui()
        self._generate_and_render_maze()

    def _setup_ui(self):
        # Configurar imagen de fondo
        self._set_background()
        self.setFixedSize(1000, 800)
        
        # Layout principal
        main_layout = QVBoxLayout(self)
        main_layout.setContentsMargins(0, 0, 0, 0)
        main_layout.setSpacing(0)
        
        # Área de juego (85% del espacio)
        self.game_area = QFrame(self)
        self.game_area.setStyleSheet("background-color: rgba(0, 0, 0, 0.3);")

        # Configurar QGraphicsView
        self.graphics_view = QGraphicsView(self.game_area)
        self.scene = QGraphicsScene()
        self.graphics_view.setScene(self.scene)
        self.graphics_view.setRenderHint(QPainter.RenderHint.Antialiasing)
        self.graphics_view.setHorizontalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAlwaysOff)
        self.graphics_view.setVerticalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAlwaysOff)
        self.graphics_view.setAlignment(Qt.AlignmentFlag.AlignCenter)

        # Layout para el área de juego
        game_layout = QHBoxLayout(self.game_area)
        game_layout.setContentsMargins(0, 0, 0, 0)
        game_layout.setAlignment(Qt.AlignmentFlag.AlignCenter)
        game_layout.addWidget(self.graphics_view)
        
        # Panel inferior (15% del espacio)
        self.bottom_panel = QFrame(self)
        self.bottom_panel.setStyleSheet("background-color: rgba(40, 40, 40, 0.7);")
        self.bottom_panel.setFixedHeight(120)
        self._setup_bottom_panel()
        
        # Añadir áreas al layout principal
        main_layout.addWidget(self.game_area)
        main_layout.addWidget(self.bottom_panel)

    def _generate_and_render_maze(self):
        self.maze = MazeGenerator.generate_maze()
        
        # Calcular dimensiones
        self.rows = len(self.maze)
        self.cols = len(self.maze[0]) if self.rows > 0 else 0
        self.maze_width = self.cols * self.cell_size
        self.maze_height = self.rows * self.cell_size
        
        # Establecer el punto de inicio según el modo de juego
        if self.game_mode == 'Classic':
            self._set_random_start_point()
        elif self.game_mode == 'Solver':
            self.start_point = None  # Sin punto de inicio por defecto en el modo Solver
        
        # Limpiar escena anterior
        self.scene.clear()
        
        # Renderizar cada celda
        for row in range(self.rows):
            for col in range(self.cols):
                self._render_cell(row, col)
        
        # Si hay un punto de inicio, renderizarlo
        if self.start_point:
            self._render_start_point()
        
        # Ajustar vista después de mostrar
        QTimer.singleShot(100, self._adjust_view)

    def _render_start_point(self):
        """Renderiza el punto de inicio en el laberinto"""
        if self.start_point:
            row, col = self.start_point
            sprite = self.atlas_loader.get_frame("details", "stairs")
            if sprite and not sprite.isNull():
                item = QGraphicsPixmapItem(sprite)
                item.setPos(col * self.cell_size, row * self.cell_size)
                self.scene.addItem(item)
            
    def _set_random_start_point(self):
        """Establece un punto de inicio aleatorio en el laberinto"""
        import random
        self.start_point = (random.randint(1, self.rows - 2), random.randint(1, self.cols - 2))  # Evita los bordes
        self.maze[self.start_point[0]][self.start_point[1]] = MazeGenerator.START
        sprite = self.atlas_loader.get_frame("details", "stairs")

    def _render_cell(self, row, col):
        cell_value = self.maze[row][col]
        sprite = None
        if cell_value == MazeGenerator.WALL:
            sprite = self._get_wall_sprite(row, col)
        elif cell_value == MazeGenerator.PATH:
            sprite = self._get_floor_sprite(row, col)
        elif cell_value == MazeGenerator.SHORTCUT:
            # Primero poner el piso
            floor_sprite = self._get_floor_sprite(row, col)
            if floor_sprite and not floor_sprite.isNull():
                item = QGraphicsPixmapItem(floor_sprite)
                item.setPos(col * self.cell_size, row * self.cell_size)
                self.scene.addItem(item)
            # Luego el objeto del atajo
            # sprite = self.atlas_loader.get_frame("details", "barrel")
        elif cell_value == MazeGenerator.GOAL:
            # Primero poner el piso
            floor_sprite = self._get_floor_sprite(row, col)
            if floor_sprite and not floor_sprite.isNull():
                item = QGraphicsPixmapItem(floor_sprite)
                item.setPos(col * self.cell_size, row * self.cell_size)
                self.scene.addItem(item)
            # Luego el objeto de la meta
            sprite = self.atlas_loader.get_frame("details", "chest1")
        elif cell_value == MazeGenerator.START:
            # Primero poner el piso
            floor_sprite = self._get_floor_sprite(row, col)
            if floor_sprite and not floor_sprite.isNull():
                item = QGraphicsPixmapItem(floor_sprite)
                item.setPos(col * self.cell_size, row * self.cell_size)
                self.scene.addItem(item)
            sprite = self.atlas_loader.get_frame("details", "stairs")
        if sprite and not sprite.isNull():
            item = QGraphicsPixmapItem(sprite)
            item.setPos(col * self.cell_size, row * self.cell_size)
            self.scene.addItem(item)

    def _get_floor_sprite(self, row, col):
        # Alternar entre pisos para variedad visual
        if (row + col) % 2 == 0:
            return self.atlas_loader.get_frame("maze", "floor1")
        return self.atlas_loader.get_frame("maze", "floor2")
    
    def _get_wall_sprite(self, row, col):
        # Alternar entre pisos para variedad visual
        if (row + col) % 2 == 0:
            return self.atlas_loader.get_frame("maze", "wall1")
        return self.atlas_loader.get_frame("maze", "wall2")

    def _adjust_view(self):
        """Ajusta la vista para que el laberinto ocupe el 85% del espacio"""
        available_width = self.game_area.width()
        available_height = self.game_area.height()
        
        scale_x = available_width / self.maze_width
        scale_y = available_height / self.maze_height
        self.scale_factor = min(scale_x, scale_y) * 0.95  # Pequeño margen
        
        transform = QTransform()
        transform.scale(self.scale_factor, self.scale_factor)
        self.graphics_view.setTransform(transform)
        
        self.graphics_view.setSceneRect(QRectF(0, 0, self.maze_width, self.maze_height))
        self.graphics_view.setFixedSize(
            int(self.maze_width * self.scale_factor), 
            int(self.maze_height * self.scale_factor)
        )

    def _setup_bottom_panel(self):
        """Configura el panel inferior con controles básicos"""
        layout = QHBoxLayout(self.bottom_panel)
        layout.setAlignment(Qt.AlignmentFlag.AlignCenter)

        # Botón de regreso
        self.back_button = QPushButton("Back to Menu", self.bottom_panel)
        self.back_button.setFixedSize(150, 50)
        self.back_button.setStyleSheet("""
            QPushButton {
                font-size: 16px;
                background-color: #5a5a5a;
                color: white;
                border-radius: 8px;
                border: 1px solid #7a7a7a;
                padding: 5px;
            }
            QPushButton:hover {
                background-color: #6a6a6a;
                border: 1px solid #8a8a8a;
            }
            QPushButton:pressed {
                background-color: #4a4a4a;
            }
        """)
        self.back_button.clicked.connect(self._go_back)
        layout.addWidget(self.back_button)

        # Botón para quitar la meta (modo Solver)
        if self.game_mode == 'Solver':
            self.remove_start_button = QPushButton("Reset Start", self.bottom_panel)
            self.remove_start_button.setFixedSize(150, 50)
            self.remove_start_button.setStyleSheet("""
                QPushButton {
                    font-size: 16px;
                    background-color: #5a5a5a;
                    color: white;
                    border-radius: 8px;
                    border: 1px solid #7a7a7a;
                    padding: 5px;
                }
                QPushButton:hover {
                    background-color: #6a6a6a;
                    border: 1px solid #8a8a8a;
                }
                QPushButton:pressed {
                    background-color: #4a4a4a;
                }
            """)
            self.remove_start_button.clicked.connect(self.remove_start)
            layout.addWidget(self.remove_start_button)

    def remove_start(self):
        if self.start_point is None:
            QMessageBox.information(self, "Oops!", "You haven't placed a start point yet!")
        else:
            row, col = self.start_point
            self.maze[row][col] = MazeGenerator.PATH  # Vuelve a ser camino
            self._render_cell(row, col)
            self.start_point = None
            self.selecting_start_point = True
  
    def _set_background(self):
        """Configura el fondo con bg_maze.png"""
        self.background = QLabel(self)
        try:
            pixmap = QPixmap("assets/bg_maze.png")
            if pixmap.isNull():
                raise FileNotFoundError
                
            pixmap = pixmap.scaled(
                1000, 800,
                Qt.AspectRatioMode.KeepAspectRatioByExpanding,
                Qt.TransformationMode.SmoothTransformation
            )
            self.background.setPixmap(pixmap)
            self.background.setGeometry(0, 0, 1000, 800)
            self.background.lower()
            
        except (FileNotFoundError, AttributeError):
            palette = self.palette()
            palette.setColor(QPalette.ColorRole.Window, Qt.GlobalColor.darkGray)
            self.setPalette(palette)

    def mousePressEvent(self, event):
        if GameConfig.get_game_mode() != "Solver" or not self.selecting_start_point:
            return

        # 1. Obtener posición del ratón respecto al widget
        mouse_pos = event.position().toPoint()
        
        # 2. Mapear a coordenadas de la vista gráfica
        view_pos = self.graphics_view.mapFromParent(mouse_pos)
        
        # 3. Verificar si el clic está dentro del área visible del laberinto
        if not self.graphics_view.viewport().rect().contains(view_pos):
            QMessageBox.warning(self, "Out of Bounds", "Clicked outside the maze area.")
            return
        
        # 4. Convertir a coordenadas de escena (considerando transformaciones)
        scene_pos = self.graphics_view.mapToScene(view_pos)
        
        # 5. Calcular posición relativa en el laberinto (sin escalado)
        x = scene_pos.x()
        y = scene_pos.y()
        
        # 6. Calcular fila y columna exactas
        col = int(x / self.cell_size)
        row = int(y / self.cell_size)
        
        # 8. Verificar límites y tipo de celda
        if 0 <= row < self.rows and 0 <= col < self.cols:
            if self.maze[row][col] == MazeGenerator.PATH:
                # Limpiar punto de inicio anterior si existe
                if self.start_point is not None:
                    old_row, old_col = self.start_point
                    self.maze[old_row][old_col] = MazeGenerator.PATH
                    self._render_cell(old_row, old_col)
                
                # Establecer nuevo punto de inicio
                self.start_point = (row, col)
                self.maze[row][col] = MazeGenerator.START
                self._render_cell(row, col)
                self.selecting_start_point = False
            else:
                QMessageBox.warning(self, "Invalid Cell", 
                                "Cannot place start on a wall or shortcut.")
        else:
            QMessageBox.warning(self, "Out of Bounds", 
                            "Clicked outside the maze bounds.")
    def resizeEvent(self, event):
        """Reajusta la vista al cambiar tamaño de ventana"""
        super().resizeEvent(event)
        if hasattr(self, 'scale_factor'):
            self._adjust_view()

    def _go_back(self):
        """Maneja el evento de volver al menú"""
        if self.parent_window:
            try:
                GameConfig.reset()
                if hasattr(self.parent_window, 'handle_maze_widget_cleanup'):
                    self.parent_window.handle_maze_widget_cleanup()
                self.parent_window.setCurrentIndex(1)
            except Exception as e:
                print(f"Error al volver atrás: {e}")
                self.parent_window.setCurrentIndex(0)