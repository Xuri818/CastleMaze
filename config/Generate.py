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
        """
        This method generates a maze with the specified size.

        The size is determined by GameConfig.get_maze_size().
        The maze is a 2D list of WALL, PATH, SHORTCUT, START, or GOAL values.

        return: A 2D list representing the maze
        """

        size = GameConfig.get_maze_size()
        rows = size
        cols = size

        if rows % 2 == 0:
            rows += 1
        if cols % 2 == 0:
            cols += 1

        maze = [[cls.WALL for _ in range(cols)] for _ in range(rows)]

        # Start carving passages from (1,1)
        maze[1][1] = cls.PATH
        cls._carve_passages(maze, 1, 1, rows, cols)

      
        for i in range(rows):
            maze[i][0] = maze[i][cols-1] = cls.WALL
        for j in range(cols):
            maze[0][j] = maze[rows-1][j] = cls.WALL


        cls._fix_bottom_left_corner(maze, rows, cols)

        cls.add_imperfections(maze, rows, cols)

        cls.place_random_goal(maze)
        
        return maze

    @classmethod
    def _carve_passages(cls, maze, x, y, rows, cols):
        """
        This method modifies the maze to create paths between cells.
        Starting from the given (x, y) position, it attempts to carve paths
        to adjacent cells in random directions, creating a perfect maze.
        """
        # left, right, up, down (two steps)
        directions = [(0, -2), (0, 2), (-2, 0), (2, 0)]
        random.shuffle(directions)  # Random directions 

        for dx, dy in directions:
            # Calculate new position
            nx, ny = x + dx, y + dy
            # Check if new position is in bounds and is a wall
            if 0 < nx < rows and 0 < ny < cols and maze[nx][ny] == cls.WALL:
                maze[nx][ny] = cls.PATH
             
                maze[x + dx // 2][y + dy // 2] = cls.PATH
                
                cls._carve_passages(maze, nx, ny, rows, cols)

    @classmethod
    def _fix_bottom_left_corner(cls, maze, rows, cols):
       
        """
        This method fixes the bottom left corner to not be a wall if it is surrounded by walls.

        If the bottom left corner cell is a wall, it is likely that the maze
        generation algorithm got stuck and couldn't find a way to carve a path
        to it. This method checks if the corner is surrounded by walls and
        if so, it creates a path to the left or up, whichever is available.

        This method  ensures that the maze is always solvable.
        """
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
        """
    This method adds imperfections to the maze by introducing shortcuts.

    This method randomly places shortcuts in the maze to make it less
    more challenging or less perfect as well. Shortcuts are added by replacing walls
    with paths in valid positions that do not compromise the maze's solvability.
    The number of shortcuts added is proportional to the maze size, ensuring
    at least one shortcut is always added. The process is limited by a maximum
    number of attempts to prevent infinite loops.

        """

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
        """
        This method determines if a given cell can be a valid shortcut.

        A cell can be a valid shortcut if it is a wall and is surrounded by
        paths in either the horizontal or vertical direction. This method
        checks these conditions and returns True if the cell is a valid
        shortcut, False if it not.

        The conditions are:

        Case 1: Path to the left and right, and wall above and below.
        Case 2: Path above and below, and wall to the left and right.

        If either of these conditions is met, the cell is a valid shortcut.
        """
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
    def set_custom_points(cls, maze, start_pos=None, end_pos=None):
    
        """
        This method sets custom start and end points for the maze.

        This method takes the maze and optional start and end points as the input.
        It checks if the points are valid (in the maze bounds and not a wall)
        and if is valid, sets the start and end points accordingly. If the points are
        invalid, the method returns the default points (1, 1) and (rows-2, cols-2)
        respectively.

        Returns:  A  (start_pos_used, end_pos_used) containing the used start and
            end points. If the input points are invalid, the default points are
            returned instead.
        """
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
        """
    This method places a random goal on a path cell in the maze bounds.

    This method iterates through the maze to identify all path cells,
    then randomly selects one of these cells to place the goal.
    If no path cells are available, the method returns without placing a goal.

        """

        rows = len(maze)
        cols = len(maze[0])

        for r in range (1, rows-1):
            for c in range (1, cols-1):
                if maze[r][c] == cls.PATH:
                    path_cells = [(r, c)]
        
        if not path_cells:
            return  # No hay caminos

        goal_pos = random.choice(path_cells)
        r, c = goal_pos
        maze[r][c] = cls.GOAL

        cls.goal_position = goal_pos  # ejemplo: cls.goal_position para referenciarla después
        
    @classmethod
    def print_maze(cls, maze):
        """
    Prints a visual representation of the maze to the console.

    This method iterates through each row of the provided maze and prints
    a string representation where each cell is denoted by specific characters:
    - '#' for walls (WALL)
    - '.' for paths (PATH)
    - '*' for other cell types (e.g., shortcuts, start, goal)
        """

        for row in maze:
            print(' '.join('#' if cell == cls.WALL else 
                          '.' if cell == cls.PATH else 
                          '*' for cell in row))
        print()
