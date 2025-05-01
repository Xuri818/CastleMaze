class MazeSolver:
    def __init__(self, maze):
        """
    Initializes the MazeSolver with the provided maze.

    This init sets up the maze structure and initializes various attributes 
    required for solving the maze. It creates a  copy of the maze for internal use 
    and initializes the start and goal positions as None. The all_paths list will store 
    all potential paths found, while the visited matrix keeps track of visited cells. 
    The shortest_path will store the shortest path found. Directions for movement are 
    representing moves in four  directions: up, left, down, and right.
        """

        self.maze = [row[:] for row in maze]  # Copia del laberinto
        self.rows = len(maze)
        self.cols = len(maze[0])
        self.goal = None
        self.start = None
        self.all_paths = []
        self.visited = []
        for _ in range(self.rows):
            row = []
            for _ in range(self.cols):
                row.append(False)
            self.visited.append(row)
        self.shortest_path = None
        self.directions = [(-1, 0), (0, -1), (1, 0), (0, 1)]  # Arriba, izquierda, abajo, derecha

    def solve(self):
        """
    Solves the maze by finding and recording all possible paths.

    This function first locates the start and goal positions of the maze. 
    If either position is missing, it returns the maze as it is. Using a backtracking 
    algorithm, it explores all paths from the start to the goal, it uses the visited matrix to keep and control the cells it is visiting or has already visited. 
    If no path is found, it prints a message and returns the maze, if not, it returns the maze with all potential paths evaluated.
        """

        self._find_start_goal()
        if not self.start or not self.goal:
            return self.maze

        # Inicializar búsqueda
        sx, sy = self.start
        self.visited[sx][sy] = True
        self._backtrack(sx, sy, [(sx, sy)])

        if not self.shortest_path:
            print("No path found.")
            return self.maze

        return self.maze

    def get_paths(self):
        """
    Returns the list of all  paths found.

    This function returns the list of all paths found during the maze solving process.
        """

        return self.all_paths

    def _find_start_goal(self):
        
        """
        Finds the start and goal positions in the maze.
        This method iterates through the maze matrix to find the start and goal points.
        If the start or goal positions are not found, the attributes will remain None.
        This function is use in the backtracking for finding all possible paths, and for that is necessary to find the start and goal positions.
        """
        for i in range(self.rows):
            for j in range(self.cols):
                if self.maze[i][j] == 3:  # Punto de inicio
                    self.start = (i, j)
                elif self.maze[i][j] == 4:  # Punto de meta
                    self.goal = (i, j)

    def _backtrack(self, x, y, path):
        
        """
    This function is the important part of the solver. It uses a recursive backtracking search to find all possible paths in the maze.

    This method explores paths recursively from the current position (x, y) to 
    the goal position. It uses the visited matrix to keep track of visited cells, so it only explores unvisited cells and those cells that are path, shortcut, start or goal. Both conditions
    are necessary to avoid infinite loops and to avoid other problems. It backtracks
    when a dead end is reached. Valid paths are added to the list of all paths, and 
    the shortest path is updated if a shorter path is found.
        """

        if (x, y) == self.goal:
            # Solo añadir si es una ruta nueva y válida
            if path not in [p[0] for p in self.all_paths]:
                self.all_paths.append((list(path), len(path)))
                
                if self.shortest_path is None or len(path) < len(self.shortest_path):
                    self.shortest_path = list(path)
            return

        # Explorar todas las direcciones posibles
        for dx, dy in self.directions:
            nx, ny = x + dx, y + dy
            if 0 <= nx < self.rows and 0 <= ny < self.cols: 
                # Celdas por las que se puede pasar: camino (1), atajo (2), inicio (3) o meta (4)
                if self.maze[nx][ny] in [1, 2, 3, 4] and not self.visited[nx][ny]:
                    self.visited[nx][ny] = True
                    path.append((nx, ny))
                    self._backtrack(nx, ny, path)
                    path.pop()
                    self.visited[nx][ny] = False