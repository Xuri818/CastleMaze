# maze_generator.py

import random
from config.game_config import GameConfig

class MazeGenerator:
    WALL = 0
    PATH = 1
    SHORTCUT = 2
    START = 3
    GOAL = 4

    @classmethod
    def generate_maze(cls):
        """Genera un laberinto 2D usando Recursive Backtracking con imperfecciones."""
        size = GameConfig.get_maze_size()
        rows = size
        cols = size

        if rows % 2 == 0:
            rows += 1
        if cols % 2 == 0:
            cols += 1

        # Inicializar el laberinto completamente como muros
        maze = [[cls.WALL for _ in range(cols)] for _ in range(rows)]

        # Empezar en (1,1)
        maze[1][1] = cls.PATH
        cls._carve_passages(maze, 1, 1, rows, cols)

        # Asegurar bordes exteriores como muros
        for i in range(rows):
            maze[i][0] = maze[i][cols-1] = cls.WALL
        for j in range(cols):
            maze[0][j] = maze[rows-1][j] = cls.WALL

        # Asegurar que la esquina inferior izquierda no quede cerrada
        cls._fix_bottom_left_corner(maze, rows, cols)

        # Añadir imperfecciones (atajos)
        cls.add_imperfections(maze, rows, cols)

        # Agregamos la meta
        cls.place_random_goal(maze)
        return maze

    @classmethod
    def _carve_passages(cls, maze, x, y, rows, cols):
        """Carve passages recursively with randomized DFS."""
        directions = [(0, -2), (0, 2), (-2, 0), (2, 0)]
        random.shuffle(directions)

        for dx, dy in directions:
            nx, ny = x + dx, y + dy
            if 0 < nx < rows and 0 < ny < cols and maze[nx][ny] == cls.WALL:
                maze[nx][ny] = cls.PATH
                maze[x + dx // 2][y + dy // 2] = cls.PATH  # Abrir la pared entre las celdas
                cls._carve_passages(maze, nx, ny, rows, cols)

    @classmethod
    def _fix_bottom_left_corner(cls, maze, rows, cols):
        """Asegura que la esquina inferior izquierda no quede cerrada."""
        corner_row, corner_col = rows - 2, 1
        neighbors = [
            (corner_row-1, corner_col),
            (corner_row, corner_col+1),
            (corner_row+1, corner_col),
            (corner_row, corner_col-1)
        ]

        if maze[corner_row][corner_col] == cls.WALL:
            for r, c in neighbors:
                if 0 <= r < rows and 0 <= c < cols and maze[r][c] == cls.PATH:
                    maze[corner_row][corner_col] = cls.PATH
                    maze[corner_row][corner_col+1] = cls.PATH
                    break

    @classmethod
    def add_imperfections(cls, maze, rows, cols):
        """Añade atajos aleatorios para hacer el laberinto imperfecto."""
        num_shortcuts = max(1, rows // 3)
        added = 0
        attempts = 0
        max_attempts = 200  # Límite para evitar bucles infinitos

        while added < num_shortcuts and attempts < max_attempts:
            attempts += 1
            row = random.randint(1, rows-2)
            col = random.randint(1, cols-2)

            if (maze[row][col] == cls.WALL and cls._is_valid_shortcut(maze, row, col)):

                maze[row][col] = cls.SHORTCUT
                added += 1

    @classmethod
    def _is_valid_shortcut(cls, maze, row, col):
        """Verifica que el atajo conecta caminos opuestos y está bloqueado en las otras direcciones"""
        up = maze[row-1][col]
        down = maze[row+1][col]
        left = maze[row][col-1]
        right = maze[row][col+1]
        
        # Caso 1: Camino a izquierda y derecha, y muro arriba y abajo
        if (left in (cls.PATH, cls.SHORTCUT) and right in (cls.PATH, cls.SHORTCUT) and
            up == cls.WALL and down == cls.WALL):
            return True

        # Caso 2: Camino arriba y abajo, y muro a izquierda y derecha
        if (up in (cls.PATH, cls.SHORTCUT) and down in (cls.PATH, cls.SHORTCUT) and
            left == cls.WALL and right == cls.WALL):
            return True

        return False

    @classmethod
    def generate_render_maze(cls, logical_maze):
        """Para compatibilidad - devuelve el mismo laberinto."""
        return logical_maze

    @classmethod
    def set_custom_points(cls, maze, start_pos=None, end_pos=None):
        """Establece puntos de inicio y fin personalizados."""
        rows = len(maze)
        if rows == 0:
            return (None, None)
        cols = len(maze[0])
        default_start = (1, 1)
        default_end = (rows-2, cols-2)

        start_pos_used = default_start
        if start_pos is not None:
            s_row, s_col = start_pos
            if (0 <= s_row < rows and 0 <= s_col < cols and
                maze[s_row][s_col] in (cls.PATH, cls.SHORTCUT)):
                start_pos_used = (s_row, s_col)

        end_pos_used = default_end
        if end_pos is not None:
            e_row, e_col = end_pos
            if (0 <= e_row < rows and 0 <= e_col < cols and
                maze[e_row][e_col] in (cls.PATH, cls.SHORTCUT)):
                end_pos_used = (e_row, e_col)

        return (start_pos_used, end_pos_used)

    @classmethod
    def place_random_goal(cls, maze):
        """Coloca una meta (GOAL) en una posición aleatoria de camino."""
        rows = len(maze)
        cols = len(maze[0])

        path_cells = [(r, c) for r in range(1, rows-1) for c in range(1, cols-1) if maze[r][c] == cls.PATH]
        
        if not path_cells:
            return  # No hay caminos, raro pero seguridad extra

        goal_pos = random.choice(path_cells)
        r, c = goal_pos
        maze[r][c] = cls.GOAL

        # Opcional: podrías guardar la posición si quieres
        cls.goal_position = goal_pos  # ejemplo: cls.goal_position para referenciarla después
        
    @classmethod
    def print_maze(cls, maze):
        """Visualiza el laberinto en la consola."""
        for row in maze:
            print(' '.join('#' if cell == cls.WALL else 
                          '.' if cell == cls.PATH else 
                          '*' for cell in row))
        print()
