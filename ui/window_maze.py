from PyQt6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QGraphicsOpacityEffect,
    QFrame, QLabel, QPushButton, QGraphicsView, QApplication,
    QGraphicsScene, QGraphicsPixmapItem, QMessageBox
)

from PyQt6.QtCore import *
from PyQt6.QtGui import QPixmap, QPalette, QTransform, QPainter, QKeyEvent
from config.game_config import GameConfig
from config.Generate import MazeGenerator
from config.atlas_loader import AtlasLoader
from config.solve import MazeSolver
import os
import json
from datetime import datetime
import random


class MazeWidget(QWidget):
    def __init__(self, parent=None, loaded_maze=None):
        """
        Initializes the MazeWidget with the given parent and loaded maze.
        If the loaded_maze parameter is None, a new maze is generated and rendered.
        If the loaded_maze parameter is not None, the given maze is rendered.
        Depending on the game mode, the player is set up or not.
        The window is set to accept keyboard focus.
        """
        
        super().__init__(parent)
        self._initialize_properties(parent, loaded_maze)
        self._setup_timers()
        self._setup_ui()
        
        if self.loaded_maze == None:
            self._generate_and_render_maze()
        else:
            self.create_and_render_maze()

        
        if self.game_mode == 'Classic':
            self._setup_player()
            self.setFocusPolicy(Qt.FocusPolicy.StrongFocus)


    # ==================== INITIALIZATION METHODS ====================
    def _initialize_properties(self, parent, loaded_maze):
        
        """
        Initializes the properties of the MazeWidget instance.

        This method sets the parent window, the loaded maze, the game mode, the maze size, and the atlas loader.
        It also initializes the cell size, scale factor, solutions, current solution index, solution items, and other
        properties related to animation and movement.

        Basically, this method sets up those "attributes" that will be used next in other functions, or that represents the maze.
        """

        self.parent_window = parent
        self.loaded_maze = loaded_maze

        
        self.game_mode = GameConfig.get_game_mode()
        
        self.maze_size = GameConfig.get_maze_size()

        self.atlas_loader = AtlasLoader()
        self.cell_size = 48
        self.scale_factor = 1.0
        self.solutions = []
        self.current_solution_index = -1
        self.solution_items = []
        self.is_showing_solution = False
        self.showing_backtracking_animation = False
        self.should_stop_animating = False
        self.is_moving = False
        self.animation_frame_index = 0
        self.current_frame = "down_standing"
        self.movement_frames = []
        self.goal_reached = False
        self.solved = False
        self.selecting_start_point = self.game_mode == "Solver"
        self.start_point = None
   
 
    def _setup_timers(self):
        
        """
        This method creates two timers: one for updating the animation frame
        and another for stopping the animation after a certain time.

        The animation timer is connected to the _update_animation_frame 
        and the stop animation timer is connected to the _complete_animation_cycle .

        The timeouts are set to 100ms and 500ms respectively.
        """
        self.animation_timer = QTimer()
        self.animation_timer.timeout.connect(self._update_animation_frame)
        self.stop_animation_timer = QTimer()
        self.stop_animation_timer.timeout.connect(self._complete_animation_cycle)

    # ==================== UI SETUP METHODS ====================
    def _setup_ui(self):

        """
    This method sets up the user interface for the maze window. It configures
    the background, sets a fixed size for the window, and arranges the layout.
    It adds and organizes the main components: the game area and the bottom
    panel in a vertical layout without spacing or margins.

        """

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
        
        """
        This method sets up the game area widget. It creates a frame
        with a translucent background and adds a graphics view to it.
        The graphics view is configured to render the graphics
        antialiased and to ignore the horizontal and vertical scroll
        bars. The graphics view is then added to a horizontal layout
        in the game area frame, which is centered.

        """

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
        
        """
        This method sets up the bottom panel widget. It creates a frame with a translucent dark gray
        background and adds a horizontal layout to it. The layout is configured to center its items
        horizontally. The method then creates buttons for common and specific actions depending on the
        game mode and adds them to the layout, centering them horizontally. The buttons are created using
        the _create_button method, which takes a text string, a function to connect to the button's
        clicked signal, and the layout to add the button to. The buttons are then added to the layout
        in the order they are created. The buttons are then added to the bottom panel frame, which is
        then added to the main layout of the window.

        The buttons are added in the following order:

        * View Solver
        * Next Solver
        * Save Map
        * Reset Start (only for game mode 'Solver')
        * Back to Menu

        The buttons are centered horizontally in the bottom panel and are evenly spaced. The bottom panel
        is then added to the main layout of the window at the bottom, with no spacing or margins.
        """

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
        
        """
    This method creates a styled QPushButton with the given text and callback, and adds it to the specified layout.

    The button is styled with a specific font size, background color, text color, border radius, and border color.
    It also has hover and pressed styles for visual feedback.
        """

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
        
        """
        This function generates a new maze using MazeGenerator and renders it on the QGraphicsScene.

        If the game mode is Classic, it sets a random start point and calculates all possible solutions.
        Then it clears the scene and renders each cell of the maze.
        If a start point is set, it renders the start point.
        Finally, it adjusts the view to fit the maze.
        """

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
    
    def create_and_render_maze(self):
        
        """
        This method renders the maze that was loaded from a file.

        Sets the maze attributes from the loaded maze and clears the scene.
        If the game mode is Classic, it sets a random start point and calculates all possible solutions.
        Then it renders each cell of the maze.
        If the game mode is solver, it sets the start point from the loaded maze data and renders it.
        Finally, it adjusts the view to fit the maze.
        """

        self.maze = self.loaded_maze['map']
        self.rows = self.loaded_maze['rows']
        self.cols = self.loaded_maze['cols']
        self.maze_width = self.cols * self.cell_size
        self.maze_height = self.rows * self.cell_size

        if self.game_mode == 'Classic':
            # Buscar la posición donde está el número 4 en self.maze
            for i in range(len(self.maze)):
                for j in range(len(self.maze[i])):
                    if self.maze[i][j] == 3:
                        self.maze[i][j] = 1  
                        break 
           
            self.start_point = (random.randint(1, len(self.maze) - 2), random.randint(1, len(self.maze[0]) - 2))
            self.maze[self.start_point[0]][self.start_point[1]] = 3  # Colocar el 4 en la nueva posición
            self._calculate_solutions()
            self.selecting_start_point = False
            self._render_start_point()


        self.scene.clear()
        for row in range(self.rows):
            for col in range(self.cols):
                self._render_cell(row, col)
        

        if self.game_mode == 'Solver':
            self.start_point = self.loaded_maze['start_point']
            self._render_start_point()
            self.selecting_start_point = False
            self._calculate_solutions()

        QTimer.singleShot(100, self._adjust_view)

    def _render_cell(self, row, col):
        
        """
        This method first checks if the cell value is in the sprites dictionary.
        If it is, it renders the corresponding sprite. If the sprite information
        is a tuple, it renders the floor first if necessary, and then renders the
        detail sprite. Otherwise, it renders the sprite directly.

        """
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
        
        """
        This method adds a sprite to the QGraphicsScene at the specified row and column coordinate.
        
        The sprite is added to the scene as a QGraphicsPixmapItem and is positioned at the
        specified row and column coordinate, which are multiplied by the cell size to get
        the actual position in pixels.
        """

        item = QGraphicsPixmapItem(sprite)
        item.setPos(col * self.cell_size, row * self.cell_size)
        self.scene.addItem(item)

    def _get_floor_sprite(self, row, col):
        
        """
        This function returns the sprite for the floor at the specified row and column coordinate.
        The sprite is chosen depending on the position, alternating between "floor1" and "floor2".
        """
       
        return self.atlas_loader.get_frame("maze", "floor1" if (row + col) % 2 == 0 else "floor2")
    
    def _get_wall_sprite(self, row, col):
        
        """
    This function returns the sprite for the wall at the specified row and column coordinate.
    
    The sprite is chosen depending on the sum of the row and column indices,
    alternating between "wall1" and "wall2".
        """

        return self.atlas_loader.get_frame("maze", "wall1" if (row + col) % 2 == 0 else "wall2")

    def _render_start_point(self):
        
        """
    This function renders the start point of the maze on the QGraphicsScene.

    If a start point is set, this method gets the sprite for the start 
    point from the atlas loader and adds it to the scene at the specified 
    row and column coordinate of the start point.

        """

        if self.start_point:
            row, col = self.start_point
            sprite = self.atlas_loader.get_frame("details", "stairs")
            if sprite and not sprite.isNull():
                self._add_sprite_to_scene(sprite, row, col)
            
    def _set_random_start_point(self):
        
        """
    This method sets a random start point in the maze.

    This method randomly selects a valid position inside the maze bounds
    and sets it as the start point. The selected cell is marked as the 
    start point by updating its value in the maze matrix.

        """

        import random
        self.start_point = (random.randint(1, self.rows - 2), random.randint(1, self.cols - 2))
        self.maze[self.start_point[0]][self.start_point[1]] = MazeGenerator.START

    def _adjust_view(self):
        
        """
        This method adjusts the view of the QGraphicsView to fit the maze inside the available
        space in the game area.

        It calculates the scale factor to fit the maze in the available width and height, and
        applies it to the view. The scale factor is multiplied by 0.95 to ensure there is a little
        margin around the maze.

        Then it sets the scene rectangle to the size of the maze and sets the size of the view
        to the scaled size of the maze.

        This method is called once the maze is rendered and the game area is resized.
        """

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
        
        """
        This method calculates all possible paths in the maze and stores them in the solutions attribute.

        It uses the MazeSolver class to find all paths in the maze, and then filters out duplicate paths
        by sorting the coordinates of each path and using a set to keep track of seen paths. The solutions
        are then sorted by length and number of steps, and the current solution index is reset to -1.

        This method is called when the maze is generated or loaded, and when the game mode is changed.
        """
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
        
        """
    This method displays the shortest solution for the current maze.

    If no solutions are available, it informs the user via a message box.
    In 'Classic' game mode, it initiates a backtracking animation.
    In other modes, it clears the current solution, resets the solution index,
    and displays the shortest solution path. Marks the maze as solved.
        """

        if not self.solutions:
            QMessageBox.information(self, "No Solutions", "No solutions found for this maze.")
            return

        if self.game_mode == 'Classic':
            self.showing_backtracking_animation = True
            self.show_backtracking_animation(self.maze)
            self.solved = True

        else:
            self._clear_solution()
            self.current_solution_index = 0
            self._display_solution(self.solutions[self.current_solution_index][0])
            self.solved = True


    def show_backtracking_animation(self, maze):
        
        """
        This method displays a backtracking animation of the maze solving process.

        It clears the current solution, makes a copy of the maze, and starts a backtracking
        search from the start point of the maze. The search is done recursively following
        the directions given in the 'directions' variable (up, left, down, right). The
        visited matrix is used to keep track of visited cells. For each cell visited, it
        marks it with an asterisk (*) and waits for 100ms before continuing with the
        search. When it reaches a dead end, it backtracks by popping the last element from
        the path and marking the cell with a dash (-). The animation is stopped when the
        backtracking search is finished.

        This method is called when the user clicks the "View Solver" button in the
        'Classic' game mode.
        """

        self._clear_solution()
        showmaze = [row[:] for row in maze]  # Copia del laberinto

        path_steps = []
        directions = [(-1, 0), (0, -1), (1, 0), (0, 1)] 
        
        visited = []
        for _ in range(self.rows):
            row = []
            for _ in range(self.cols):
                row.append(False)
            visited.append(row)

        def backtrack(x, y, path):

            
            """
            This is a recursive function that performs a backtracking search from the given cell (x, y) to the goal point.

            The search is done following the directions given in the 'directions' variable (up, left, down, right). The
            visited matrix is used to keep track of visited cells. For each cell visited, it marks it with an asterisk (*) and
            waits for 100ms before continuing with the search. When it reaches a dead end, it backtracks by deleting the last
            element from the path and marking the cell with a dash (-). The animation is stopped when the backtracking search
            is finished.

            This function is called from the show_backtracking_animation method and is used to display a backtracking animation
            of the maze solving process.

            """

            if (x, y) == self._get_goal_point():
                return

            for dx, dy in directions:
                nx, ny = x + dx, y + dy
                if 0 <= nx < self.rows and 0 <= ny < self.cols:
                    if showmaze[nx][ny] in [1, 2, 3, 4] and not visited[nx][ny]:
                        visited[nx][ny] = True
                        path.append((nx, ny))

                        # Marcar exploración
                        self.update_ui(nx, ny, "*")
                        QCoreApplication.processEvents()
                        QThread.msleep(100)  # Velocidad de la animación

                        backtrack(nx, ny, path)

                        # Retroceso
                        path.pop()
                        visited[nx][ny] = False

                        self.update_ui(nx, ny, "-")
                        QCoreApplication.processEvents()
                        QThread.msleep(100)

        sx, sy = self.start_point
        visited[sx][sy] = True
        backtrack(sx, sy, [(sx, sy)])
        self.showing_backtracking_animation = False

    def update_ui(self, x, y, status):
        
        """
        This method updates the UI by adding a visual representation of a cell in the maze with a given status.

        The status parameter can be one of the following values:

        - "*": Exploration
        - "-": Backtracking
        - 3: Start
        - 4: Goal

        This method creates a QGraphicsOpacityEffect to set the opacity of the cell, and adds it to the scene.
        If the status is "*" or "-", it sets the opacity to 0.6 to show the progression of the backtracking algorithm.
        """
        
        if status == "*":  # Exploración
            color = Qt.GlobalColor.blue
        elif status == "-":  # Retroceso
            color = Qt.GlobalColor.white
        elif status == 3:  # Inicio
            color = Qt.GlobalColor.green
        elif status == 4:  # Meta
            color = Qt.GlobalColor.red
        else:  # Muros o caminos normales
            color = Qt.GlobalColor.white

        # Crear el elemento visual de la celda
        cell_pixmap = QPixmap(self.cell_size, self.cell_size)
        cell_pixmap.fill(color)

        item = QGraphicsPixmapItem(cell_pixmap)
        opacity_effect = QGraphicsOpacityEffect()
        opacity_effect.setOpacity(0.6 if status in ("*", "-") else 1.0)  # Opacidad para progresión
        item.setGraphicsEffect(opacity_effect)

        #    Ajustar posición en el gráfico
        item.setPos(y * self.cell_size, x * self.cell_size)
        self.scene.addItem(item)

        # Añadir el item a una lista si necesitas limpiar después
        self.solution_items.append(item)

    def show_next_solution(self):
        
        """
    This method displays the next solution path in the maze.

    This method cycles through the list of available solutions and displays
    the next solution in sequence. If there are no solutions available,
    it informs the user via a message box. The method does nothing if a 
    backtracking animation is currently being shown. The current solution 
    is cleared before displaying the next one. The maze is marked as solved 
    once a solution is displayed.

        """

        if not self.solutions:
            QMessageBox.information(self, "No Solutions", "No solutions found for this maze.")
            return
        
        if self.showing_backtracking_animation == True:
            return

        self._clear_solution()
        self.solved = True
        self.current_solution_index = (self.current_solution_index + 1) % len(self.solutions)
        self._display_solution(self.solutions[self.current_solution_index][0])
        self.scene.update()

        QApplication.processEvents()

    def _display_solution(self, path):
        
        """
    This function displays a visual representation of a given solution path in the maze.

    This method takes a path, represented as a list of (row, col) tuples, and 
    renders it on the scene using colored pixmaps. The path must have more 
    than two points to be displayed. The color of the path varies based on 
    the current solution index: green for the optimal solution, red for the 
    worst solution, and dark blue for average solutions. Each cell in the 
    path is rendered with a semi-transparent pixmap. The method updates the 
    solution_items list with the rendered items and marks the solution as 
    currently being shown.
    
        """

        if not path or len(path) <= 2:
            return

        colors = [Qt.GlobalColor.green, Qt.GlobalColor.red, Qt.GlobalColor.darkBlue]
        if self.current_solution_index == 0:
            color = colors[0]
        elif self.current_solution_index == len(self.solutions) - 1:
            color = colors[1]
        else:
            color = colors[2]

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
        
        """
        This function clears the current solution path from the scene.

        This method removes all items in the solution_items list from the scene and
        clears the list. It also sets is_showing_solution to False, indicating that
        there is currently no solution being displayed.
        """
        
        for item in self.solution_items:
            self.scene.removeItem(item)
        self.solution_items.clear()
        self.is_showing_solution = False
    
    # ==================== SAVE MAP LOGIC ==================== #

    def save_map_solution(self, file_path=None):
        
        """
        This function saves the current maze and its solution to a file in JSON format.

        If no file path is provided, it saves the maze in the "savegames" folder
        with a default name in the format "Map_<game_mode>_<timestamp>.json".

        The saved data includes the maze matrix, game mode, start point, goal point, and
        the number of rows and columns in the maze.

        If the start point is not set, or if a backtracking animation is being shown,
        or if the maze has not been generated, this method does nothing and shows an
        error message.

        If the file could not be saved, it shows an error message with the exception
        details.
        """

        if not self.start_point:
            QMessageBox.warning(self, "Error", "No hay un punto de inicio para guardar.")
            return
        
        if self.showing_backtracking_animation == True:
            return
        
        if not self.maze:
            QMessageBox.warning(self, "Error", "No hay un laberinto generado para guardar.")
            return

    # Definir ruta por defecto si no se proporciona
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")  # Ejemplo: 20230428_093145
        file_name = f"Map_{self.game_mode}_{timestamp}.json"
        file_path = os.path.join(os.getcwd(), "savegames", file_name)

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
        """
        This function searches for the position of the goal point in the maze. Since there is not any variable to store the goal point,
        it iterates through the maze matrix to find the position of the GOAL character.
        """
        for r in range(self.rows):
            for c in range(self.cols):
                if self.maze[r][c] == MazeGenerator.GOAL:
                    return (r, c)
        return None
    
        
    

    # ==================== PLAYER METHODS ====================
    def _setup_player(self):
        
        """
        This method sets up the player properties and renders the player sprite on the scene.
        
        If the start point is not set, the method returns without doing anything.
        It sets the player's initial position and direction to the start point's coordinates and 'down' respectively.
        It then renders the player sprite based on the current frame.
        Finally, it adds the player item to the scene and loads the movement frames.
        """
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
        
        """
        This method loads the movement frames for the player sprite.

        It creates a dictionary with all directions as keys and a list of four frames as the value.
        The frames are: standing, movement 1, standing, movement 2 for each direction.

        The frames are loaded from the atlas and stored in the self.movement_frames property.
        The frames are then used in the _update_animation_frame method to animate the player movement.
        """

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
        
        """
        This method updates the player item's position based on the current player coordinates.
        
        The method multiplies the player's row and column coordinates by the cell size to get the
        actual position in pixels. It then sets the player item's position using the setPos method.
        The y-coordinate is adjusted by subtracting the pixmap's height minus the cell size to align
        the bottom of the pixmap with the bottom of the cell.
        """

        player_pixmap = self.player_item.pixmap()
        if player_pixmap and not player_pixmap.isNull():
            self.player_item.setPos(
                self.player['col'] * self.cell_size,
                self.player['row'] * self.cell_size - (player_pixmap.height() - self.cell_size)
            )

    def _update_animation_frame(self):
        
        """
        This method updates the animation frame of the player sprite when the player moves.

        The method first checks if the player is moving and if the player item exists. 
        If not, it stops the animation timer and resets the animation frame index to 0.
        
        It then gets the frames for the current direction of the player from the self.movement_frames dictionary. 
        If the frames exist and all of them are not None, 
        it increments the animation frame index and sets the pixmap of the player item to the next frame in the sequence.

        If the animation should be stopped and the animation frame index is 0, 
        it calls the _complete_animation_cycle method to stop the animation and reset the player pixmap to the standing frame.
        """

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
        
        """
        This method is called when the animation should be stopped.

        It stops the stop animation timer and the animation timer, and sets the is_moving flag to False.
        It then sets the pixmap of the player item to the standing frame for the current direction of the player.

        This method is called from the _update_animation_frame method when the animation should be stopped and the
        animation frame index is 0.
        """

        self.stop_animation_timer.stop()
        self.is_moving = False
        self.animation_timer.stop()
        
        standing_frame = f"{self.player['direction']}_standing"
        player_pixmap = self.atlas_loader.get_frame("pj", standing_frame)
        if player_pixmap and not player_pixmap.isNull():
            self.player_item.setPixmap(player_pixmap)

    # ==================== EVENT HANDLERS ====================
    def keyPressEvent(self, event: QKeyEvent):
        
        """
        This method handles the key press event for the player movement.

        It checks if the game is in 'Classic' mode, if the player exists, and if the goal has not been reached yet.
        If any of these conditions are not met, it returns without doing anything.

        It then checks if the animation should be stopped. If so, it stops the stop animation timer and sets the
        should_stop_animating flag to False.

        It then gets the key that was pressed and checks if it is a valid direction. If it is, it updates the player's
        direction and position accordingly.

        Finally, it calls the _handle_player_movement method to handle the player's movement.

        """
        
        if self.game_mode != 'Classic' or not self.player or self.goal_reached or self.solved or self.showing_backtracking_animation:
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
       
        """
        This method handles the player movement.

        It first checks if the player is inside the maze bounds. If not, it returns without doing anything.

        It then checks if the cell at the new position is a valid path, shortcut, goal or start. If not, it returns without doing anything.

        It then updates the player's row and column coordinates to the new position.

        If the player has reached the goal, it sets the goal_reached flag to True and shows a message box to the user.

        If the direction has changed, it renders the standing frame of the player sprite for the current direction.

        If the player is not moving, it sets the is_moving flag to True and starts the animation timer.

        Finally, it calls the _update_player_position method to update the player item's position on the scene.

        """
        
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
        
        """
    This method handles the key release event for the player movement.

    This method checks if the game is in 'Classic' mode, if the player exists, and if the goal has not been reached.
    If any of these conditions are not met, it returns without doing anything.

    If the released key corresponds to one of the movement keys (W, Up, S, Down, A, Left, D, Right),
    it sets the should_stop_animating flag to True and starts the stop animation timer.
        """

        if self.game_mode != 'Classic' or not self.player or self.goal_reached or self.solved or self.showing_backtracking_animation:
            return
            
        if event.key() in [Qt.Key.Key_W, Qt.Key.Key_Up, Qt.Key.Key_S, Qt.Key.Key_Down, 
                         Qt.Key.Key_A, Qt.Key.Key_Left, Qt.Key.Key_D, Qt.Key.Key_Right]:
            self.should_stop_animating = True
            self.stop_animation_timer.start(200)

    def mousePressEvent(self, event):

        """
        This method handles the mouse press event for selecting the start point of the maze in Solver mode.

        It first checks if the game mode is Solver and if the selecting_start_point flag is True.
        If not, it returns without doing anything.

        It then gets the position of the click in the view and scene coordinates.
        If the click is outside the maze area or bounds, it shows a warning message and returns.

        If the cell at the clicked position is not a path cell, it shows a warning message and returns.

        If a start point is already set, it clears the old start point and renders the new one.
        It then sets the start_point attribute to the new position, renders the start point, and sets selecting_start_point to False.
        Finally, it calculates the solutions for the new start point.
        """

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
        
        """
        This method handles the resize event of the MazeWidget.

        It first calls the parent's resize event method.
        If the MazeWidget has been initialized,
        it adjusts the view to fit the available space in the game area.
        """

        super().resizeEvent(event)
        if hasattr(self, 'scale_factor'):
            self._adjust_view()

    # ==================== UTILITY METHODS ====================
    def remove_start(self):
        
        """
        This method removes the start point from the maze.

        If the start point is None, it shows a message box warning the user.
        Otherwise, it resets the start point cell to a path cell, removes the
        start point, and recalculates the solutions.

        """
        
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
        
        """
        This method sets up the background for the maze widget. It tries to load
        the image bg_maze.png from the assets folder and manages it to fit the
        window size while maintaining its aspect. If the image is not found or
        an error occurs during loading, a solid dark gray color is used instead.
        The background is then sent to the back of the window.
        """

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
        
        """
    This method is connected to navigate back from the current maze widget to a
    previous screen. If a backtracking animation is running, it exits without
    performing any action. Otherwise, it resets the game configuration and
    attempts to call a cleanup handler in the parent window if it exists.
    It then sets the view to a specific index in the parent window. In case of
    an error during this process, it defaults to setting the view to the main
    menu index.
    
        """

        if self.showing_backtracking_animation == True:
            return
        
        if self.parent_window:
            try:
                GameConfig.reset()
                if hasattr(self.parent_window, 'handle_maze_widget_cleanup'):
                    self.parent_window.handle_maze_widget_cleanup()
                self.parent_window.setCurrentIndex(1)
            except Exception:
                self.parent_window.setCurrentIndex(0)