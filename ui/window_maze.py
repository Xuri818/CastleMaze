from PyQt6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QGraphicsOpacityEffect,
    QFrame, QLabel, QPushButton, QGraphicsView, QApplication,
    QGraphicsScene, QGraphicsPixmapItem, QMessageBox
)
from PyQt6.QtCore import Qt, QRectF, QTimer, QPointF
from PyQt6.QtGui import QPixmap, QPalette, QTransform, QPainter, QKeyEvent
from config.game_config import GameConfig
from config.Generate import MazeGenerator
from config.atlas_loader import AtlasLoader
from config.solve import MazeSolver
import os
import json
from datetime import datetime


class MazeWidget(QWidget):
    def __init__(self, parent=None, loaded_maze=None):
        super().__init__(parent)
        self._initialize_properties(parent)
        
        # Si se proporciona un laberinto cargado, usaremos ese
        if loaded_maze is not None:
            self.maze = loaded_maze['map']
            self.rows = loaded_maze['rows']
            self.cols = loaded_maze['cols']
            self.start_point = loaded_maze['start_point']
            self.goal_point = loaded_maze['goal_point']
            self._setup_loaded_maze()
        else:
            self._generate_and_render_maze()
        
        if self.game_mode == 'Classic':
            self._setup_player()
            self.setFocusPolicy(Qt.FocusPolicy.StrongFocus)

    # ==================== INITIALIZATION METHODS ====================
    def _initialize_properties(self, parent):
        """Inicializa todas las propiedades de la clase"""
        self.parent_window = parent
        self.game_mode = GameConfig.get_game_mode()
        self.maze_size = GameConfig.get_maze_size()
        self.atlas_loader = AtlasLoader()
        self.cell_size = 48
        self.scale_factor = 1.0
        self.solutions = []
        self.current_solution_index = -1
        self.solution_items = []
        self.is_showing_solution = False
        self.should_stop_animating = False
        self.is_moving = False
        self.animation_frame_index = 0
        self.current_frame = "down_standing"
        self.movement_frames = []
        self.goal_reached = False
        self.solved = False
        self.selecting_start_point = self.game_mode == "Solver"
        self.start_point = None
   
    def _setup_loaded_maze(self):
        """Configura la vista usando un laberinto cargado"""
        self._setup_ui()
        self._render_full_maze()
        self.selecting_start_point = False
    def _render_full_maze(self):
        """Redibuja toda la matriz actual"""
        for row in range(self.rows):
            for col in range(self.cols):
                self._render_cell(row, col)

    def _setup_timers(self):
        """Configura los temporizadores necesarios"""
        self.animation_timer = QTimer()
        self.animation_timer.timeout.connect(self._update_animation_frame)
        self.stop_animation_timer = QTimer()
        self.stop_animation_timer.timeout.connect(self._complete_animation_cycle)

    # ==================== UI SETUP METHODS ====================
    def _setup_ui(self):
        """Configura la interfaz de usuario principal"""
        self._set_background()
        self.setFixedSize(1000, 800)
        
        main_layout = QVBoxLayout(self)
        main_layout.setContentsMargins(0, 0, 0, 0)
        main_layout.setSpacing(0)
        
        self._setup_game_area()
        self._setup_bottom_panel()
        
        main_layout.addWidget(self.game_area)
        main_layout.addWidget(self.bottom_panel)

    def _setup_game_area(self):
        """Configura el área de juego principal"""
        self.game_area = QFrame(self)
        self.game_area.setStyleSheet("background-color: rgba(0, 0, 0, 0.3);")
        
        self.graphics_view = QGraphicsView(self.game_area)
        self.scene = QGraphicsScene()
        self.graphics_view.setScene(self.scene)
        self.graphics_view.setRenderHint(QPainter.RenderHint.Antialiasing)
        self.graphics_view.setHorizontalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAlwaysOff)
        self.graphics_view.setVerticalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAlwaysOff)
        self.graphics_view.setAlignment(Qt.AlignmentFlag.AlignCenter)

        game_layout = QHBoxLayout(self.game_area)
        game_layout.setContentsMargins(0, 0, 0, 0)
        game_layout.setAlignment(Qt.AlignmentFlag.AlignCenter)
        game_layout.addWidget(self.graphics_view)

    def _setup_bottom_panel(self):
        """Configura el panel inferior con controles"""
        self.bottom_panel = QFrame(self)
        self.bottom_panel.setStyleSheet("background-color: rgba(40, 40, 40, 0.7);")
        self.bottom_panel.setFixedHeight(120)
        
        layout = QHBoxLayout(self.bottom_panel)
        layout.setAlignment(Qt.AlignmentFlag.AlignCenter)

        # Botones comunes
        self._create_button("View Solver", self.show_shortest_solution, layout)
        self._create_button("Next Solver", self.show_next_solution, layout)
        self._create_button("Save Map", lambda: self.save_map_solution(), layout)
        
        # Botón específico para modo Solver
        if self.game_mode == 'Solver':
            self._create_button("Reset Start", self.remove_start, layout)
            
        self._create_button("Back to Menu", self._go_back, layout)


    def _create_button(self, text, callback, layout):
        """Crea un botón estandarizado y lo añade al layout"""
        button = QPushButton(text, self.bottom_panel)
        button.setFixedSize(150, 50)
        button.setStyleSheet("""
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
        button.clicked.connect(callback)
        layout.addWidget(button)

    # ==================== MAZE RENDERING METHODS ====================
    def _generate_and_render_maze(self):
        """Genera y renderiza el laberinto completo"""
        self.maze = MazeGenerator.generate_maze()
        self.rows = len(self.maze)
        self.cols = len(self.maze[0]) if self.rows > 0 else 0
        self.maze_width = self.cols * self.cell_size
        self.maze_height = self.rows * self.cell_size
        
        if self.game_mode == 'Classic':
            self._set_random_start_point()
            self._calculate_solutions()
        
        self.scene.clear()
        
        for row in range(self.rows):
            for col in range(self.cols):
                self._render_cell(row, col)
        
        if self.start_point:
            self._render_start_point()
        
        QTimer.singleShot(100, self._adjust_view)

    def _render_cell(self, row, col):
        """Renderiza una celda individual del laberinto"""
        cell_value = self.maze[row][col]
        sprites = {
            MazeGenerator.WALL: self._get_wall_sprite(row, col),
            MazeGenerator.PATH: self._get_floor_sprite(row, col),
            MazeGenerator.SHORTCUT: ("barrel", True),
            MazeGenerator.GOAL: ("chest1", True),
            MazeGenerator.START: ("stairs", True)
        }
        
        if cell_value not in sprites:
            return
            
        sprite_info = sprites[cell_value]
        
        # Renderizar piso primero si es necesario
        if isinstance(sprite_info, tuple) and sprite_info[1]:
            floor_sprite = self._get_floor_sprite(row, col)
            if floor_sprite and not floor_sprite.isNull():
                self._add_sprite_to_scene(floor_sprite, row, col)
            
            detail_sprite = self.atlas_loader.get_frame("details", sprite_info[0])
            if detail_sprite and not detail_sprite.isNull():
                self._add_sprite_to_scene(detail_sprite, row, col)
        elif sprite_info and not sprite_info.isNull():
            self._add_sprite_to_scene(sprite_info, row, col)

    def _add_sprite_to_scene(self, sprite, row, col):
        """Añade un sprite a la escena en la posición especificada"""
        item = QGraphicsPixmapItem(sprite)
        item.setPos(col * self.cell_size, row * self.cell_size)
        self.scene.addItem(item)

    def _get_floor_sprite(self, row, col):
        """Obtiene el sprite de piso según la posición"""
        return self.atlas_loader.get_frame("maze", "floor1" if (row + col) % 2 == 0 else "floor2")
    
    def _get_wall_sprite(self, row, col):
        """Obtiene el sprite de pared según la posición"""
        return self.atlas_loader.get_frame("maze", "wall1" if (row + col) % 2 == 0 else "wall2")

    def _render_start_point(self):
        """Renderiza el punto de inicio en el laberinto"""
        if self.start_point:
            row, col = self.start_point
            sprite = self.atlas_loader.get_frame("details", "stairs")
            if sprite and not sprite.isNull():
                self._add_sprite_to_scene(sprite, row, col)
            
    def _set_random_start_point(self):
        """Establece un punto de inicio aleatorio en el laberinto"""
        import random
        self.start_point = (random.randint(1, self.rows - 2), random.randint(1, self.cols - 2))
        self.maze[self.start_point[0]][self.start_point[1]] = MazeGenerator.START

    def _adjust_view(self):
        """Ajusta la vista para que el laberinto ocupe el espacio adecuado"""
        available_width = self.game_area.width()
        available_height = self.game_area.height()
        
        self.scale_factor = min(
            available_width / self.maze_width,
            available_height / self.maze_height
        ) * 0.95
        
        transform = QTransform()
        transform.scale(self.scale_factor, self.scale_factor)
        self.graphics_view.setTransform(transform)
        
        self.graphics_view.setSceneRect(QRectF(0, 0, self.maze_width, self.maze_height))
        self.graphics_view.setFixedSize(
            int(self.maze_width * self.scale_factor), 
            int(self.maze_height * self.scale_factor)
        )

    # ==================== SOLUTION METHODS ====================
    def _calculate_solutions(self):
        """Calcula y prepara todas las soluciones únicas"""
        solver = MazeSolver(self.maze)
        solver.solve()
        
        unique_paths = []
        seen_paths = set()
        
        for path, length in solver.get_paths():
            path_key = tuple(sorted((x, y) for x, y in path))
            if path_key not in seen_paths:
                seen_paths.add(path_key)
                unique_paths.append((path, length))
        
        self.solutions = sorted(unique_paths, key=lambda x: (x[1], len(x[0])))
        self.current_solution_index = -1

    def show_shortest_solution(self):
        """Muestra la solución más corta"""
        if not self.solutions:
            QMessageBox.information(self, "No Solutions", "No solutions found for this maze.")
            return

        self._clear_solution()
        self.current_solution_index = 0
        self._display_solution(self.solutions[self.current_solution_index][0])
        self.solved = True

    def show_next_solution(self):
        """Muestra la siguiente solución única"""
        if not self.solutions:
            QMessageBox.information(self, "No Solutions", "No solutions found for this maze.")
            return

        self._clear_solution()
        self.solved = True
        self.current_solution_index = (self.current_solution_index + 1) % len(self.solutions)
        self._display_solution(self.solutions[self.current_solution_index][0])
        self.scene.update()

        QApplication.processEvents()

    def _display_solution(self, path):
        """Visualiza una solución en el laberinto"""
        if not path or len(path) <= 2:
            return

        colors = [Qt.GlobalColor.green, Qt.GlobalColor.red]
        color = colors[self.current_solution_index % len(colors)]

        for row, col in path[1:-1]:
            solution_pixmap = QPixmap(self.cell_size, self.cell_size)
            solution_pixmap.fill(color)
            
            item = QGraphicsPixmapItem(solution_pixmap)
            opacity_effect = QGraphicsOpacityEffect()
            opacity_effect.setOpacity(0.4)
            item.setGraphicsEffect(opacity_effect)
            item.setPos(col * self.cell_size, row * self.cell_size)
            self.scene.addItem(item)
            self.solution_items.append(item)
        self.is_showing_solution = True

    def _clear_solution(self):
        """Elimina la solución mostrada actualmente"""
        for item in self.solution_items:
            self.scene.removeItem(item)
        self.solution_items.clear()
        self.is_showing_solution = False
    
    # ==================== SAVE MAP LOGIC ==================== #

    def save_map_solution(self, file_path=None):
        """Guarda el mapa actual y datos relevantes en un archivo JSON."""
        if not self.start_point:
            QMessageBox.warning(self, "Error", "No hay un punto de inicio para guardar.")
            return
        if not self.maze:
            QMessageBox.warning(self, "Error", "No hay un laberinto generado para guardar.")
            return

    # Definir ruta por defecto si no se proporciona
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")  # Ejemplo: 20230428_093145
        file_name = f"saved_map_{timestamp}.json"
        file_path = os.path.join(os.getcwd(), "config", file_name)

        # Preparar los datos para guardar
        data_to_save = {
            "map": self.maze,  # La matriz del laberinto
            "game_mode": self.game_mode,
            "start_point": self.start_point,
            "goal_point": self._get_goal_point(),  # Buscar posición del GOAL
            "rows": self.rows,
            "cols": self.cols
        }


        try:
        # Guardar datos en formato JSON
            with open(file_path, "w") as file:
                json.dump(data_to_save, file, indent=4)
            QMessageBox.information(self, "Guardado exitoso", f"El laberinto se guardó en {file_path}.")
        except Exception as e:
            QMessageBox.critical(self, "Error", f"No se pudo guardar el archivo: {e}")

    def _get_goal_point(self):
        """Busca y retorna la posición de la meta (GOAL) en el laberinto."""
        for r in range(self.rows):
            for c in range(self.cols):
                if self.maze[r][c] == MazeGenerator.GOAL:
                    return (r, c)
        return None
    
    def get_maze_size(self):
        return self.rows, self.cols
        
    

    # ==================== PLAYER METHODS ====================
    def _setup_player(self):
        """Configura el personaje del jugador"""
        if not self.start_point:
            return
            
        self.player = {
            'row': self.start_point[0],
            'col': self.start_point[1],
            'direction': 'down'
        }
        
        self.current_frame = "down_standing"
        player_pixmap = self.atlas_loader.get_frame("pj", self.current_frame)
        if player_pixmap and not player_pixmap.isNull():
            self.player_item = QGraphicsPixmapItem(player_pixmap)
            self._update_player_position()
            self.scene.addItem(self.player_item)
            
        self._load_movement_frames()

    def _load_movement_frames(self):
        """Pre-carga los frames de animación para cada dirección"""
        directions = ['down', 'left', 'right', 'up']
        self.movement_frames = {
            dir: [
                self.atlas_loader.get_frame("pj", f"{dir}_standing"),
                self.atlas_loader.get_frame("pj", f"{dir}_movement_1"),
                self.atlas_loader.get_frame("pj", f"{dir}_standing"),
                self.atlas_loader.get_frame("pj", f"{dir}_movement_2")
            ] for dir in directions
        }

    def _update_player_position(self):
        """Actualiza la posición visual del jugador"""
        player_pixmap = self.player_item.pixmap()
        if player_pixmap and not player_pixmap.isNull():
            self.player_item.setPos(
                self.player['col'] * self.cell_size,
                self.player['row'] * self.cell_size - (player_pixmap.height() - self.cell_size)
            )

    def _update_animation_frame(self):
        """Actualiza el frame de animación durante el movimiento"""
        if not self.is_moving or not self.player_item:
            self.animation_timer.stop()
            self.animation_frame_index = 0
            return
            
        direction = self.player['direction']
        frames = self.movement_frames.get(direction, [])
        
        if frames and all(frame is not None for frame in frames):
            self.animation_frame_index = (self.animation_frame_index + 1) % len(frames)
            self.player_item.setPixmap(frames[self.animation_frame_index])
            
            if self.should_stop_animating and self.animation_frame_index == 0:
                self._complete_animation_cycle()

    def _complete_animation_cycle(self):
        """Completa el ciclo de animación antes de detenerse"""
        self.stop_animation_timer.stop()
        self.is_moving = False
        self.animation_timer.stop()
        
        standing_frame = f"{self.player['direction']}_standing"
        player_pixmap = self.atlas_loader.get_frame("pj", standing_frame)
        if player_pixmap and not player_pixmap.isNull():
            self.player_item.setPixmap(player_pixmap)

    # ==================== EVENT HANDLERS ====================
    def keyPressEvent(self, event: QKeyEvent):
        """Maneja el movimiento del jugador con teclado"""
        if self.game_mode != 'Classic' or not self.player or self.goal_reached or self.solved:
            return
            
        if self.should_stop_animating:
            self.should_stop_animating = False
            self.stop_animation_timer.stop()
            
        key = event.key()
        new_row, new_col = self.player['row'], self.player['col']
        direction_changed = False
        
        # Mapeo de teclas a direcciones
        direction_map = {
            Qt.Key.Key_W: ('up', -1, 0),
            Qt.Key.Key_Up: ('up', -1, 0),
            Qt.Key.Key_S: ('down', 1, 0),
            Qt.Key.Key_Down: ('down', 1, 0),
            Qt.Key.Key_A: ('left', 0, -1),
            Qt.Key.Key_Left: ('left', 0, -1),
            Qt.Key.Key_D: ('right', 0, 1),
            Qt.Key.Key_Right: ('right', 0, 1)
        }
        
        if key not in direction_map:
            return
            
        direction, row_diff, col_diff = direction_map[key]
        new_row += row_diff
        new_col += col_diff
        
        if self.player['direction'] != direction:
            self.player['direction'] = direction
            direction_changed = True
            
        self._handle_player_movement(new_row, new_col, direction_changed)

    def _handle_player_movement(self, new_row, new_col, direction_changed):
        """Maneja la lógica de movimiento del jugador"""
        if not (0 <= new_row < self.rows and 0 <= new_col < self.cols):
            return
            
        cell_value = self.maze[new_row][new_col]
        if cell_value not in [MazeGenerator.PATH, MazeGenerator.SHORTCUT, 
                            MazeGenerator.GOAL, MazeGenerator.START]:
            return
            
        self.player['row'], self.player['col'] = new_row, new_col
        
        if cell_value == MazeGenerator.GOAL:
            self.goal_reached = True
            QMessageBox.information(self, "¡Felicidades!", "¡Has llegado a la meta!")
            return
            
        if direction_changed:
            standing_frame = f"{self.player['direction']}_standing"
            player_pixmap = self.atlas_loader.get_frame("pj", standing_frame)
            if player_pixmap and not player_pixmap.isNull():
                self.player_item.setPixmap(player_pixmap)
        
        if not self.is_moving:
            self.is_moving = True
            self.animation_timer.start(100)
        
        self._update_player_position()

    def keyReleaseEvent(self, event: QKeyEvent):
        """Maneja la liberación de teclas de movimiento"""
        if self.game_mode != 'Classic' or not self.player or self.goal_reached:
            return
            
        if event.key() in [Qt.Key.Key_W, Qt.Key.Key_Up, Qt.Key.Key_S, Qt.Key.Key_Down, 
                         Qt.Key.Key_A, Qt.Key.Key_Left, Qt.Key.Key_D, Qt.Key.Key_Right]:
            self.should_stop_animating = True
            self.stop_animation_timer.start(200)

    def mousePressEvent(self, event):
        """Maneja la selección del punto de inicio en modo Solver"""
        if GameConfig.get_game_mode() != "Solver" or not self.selecting_start_point:
            return

        view_pos = self.graphics_view.mapFromParent(event.position().toPoint())
        if not self.graphics_view.viewport().rect().contains(view_pos):
            QMessageBox.warning(self, "Out of Bounds", "Clicked outside the maze area.")
            return
        
        scene_pos = self.graphics_view.mapToScene(view_pos)
        col = int(scene_pos.x() / self.cell_size)
        row = int(scene_pos.y() / self.cell_size)
        
        if not (0 <= row < self.rows and 0 <= col < self.cols):
            QMessageBox.warning(self, "Out of Bounds", "Clicked outside the maze bounds.")
            return
            
        if self.maze[row][col] != MazeGenerator.PATH:
            QMessageBox.warning(self, "Invalid Cell", "Cannot place start on a wall or shortcut.")
            return
            
        if self.start_point is not None:
            old_row, old_col = self.start_point
            self.maze[old_row][old_col] = MazeGenerator.PATH
            self._render_cell(old_row, old_col)
            
        self._clear_solution()
        self.start_point = (row, col)
        self.maze[row][col] = MazeGenerator.START
        self._render_cell(row, col)
        self.selecting_start_point = False
        self._calculate_solutions()

    def resizeEvent(self, event):
        """Reajusta la vista al cambiar tamaño de ventana"""
        super().resizeEvent(event)
        if hasattr(self, 'scale_factor'):
            self._adjust_view()

    # ==================== UTILITY METHODS ====================
    def remove_start(self):
        """Elimina el punto de inicio actual"""
        if self.start_point is None:
            QMessageBox.information(self, "Oops!", "You haven't placed a start point yet!")
        else:
            row, col = self.start_point
            self.maze[row][col] = MazeGenerator.PATH
            self._render_cell(row, col)
            self.start_point = None
            self.selecting_start_point = True
            self._clear_solution()
            self._calculate_solutions()

    def _set_background(self):
        """Configura la imagen de fondo"""
        self.background = QLabel(self)
        try:
            pixmap = QPixmap("assets/bg_maze.png")
            if not pixmap.isNull():
                pixmap = pixmap.scaled(
                    1000, 800,
                    Qt.AspectRatioMode.KeepAspectRatioByExpanding,
                    Qt.TransformationMode.SmoothTransformation
                )
                self.background.setPixmap(pixmap)
                self.background.setGeometry(0, 0, 1000, 800)
                self.background.lower()
                return
        except (FileNotFoundError, AttributeError):
            pass
            
        palette = self.palette()
        palette.setColor(QPalette.ColorRole.Window, Qt.GlobalColor.darkGray)
        self.setPalette(palette)

    def _go_back(self):
        """Maneja el evento de volver al menú"""
        if self.parent_window:
            try:
                GameConfig.reset()
                if hasattr(self.parent_window, 'handle_maze_widget_cleanup'):
                    self.parent_window.handle_maze_widget_cleanup()
                self.parent_window.setCurrentIndex(1)
            except Exception:
                self.parent_window.setCurrentIndex(0)