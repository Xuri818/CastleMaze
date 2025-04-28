class MazeSolver:
    def __init__(self, maze):
        self.maze = [row[:] for row in maze]  # Copia del laberinto
        self.rows = len(maze)
        self.cols = len(maze[0])
        self.goal = None
        self.start = None
        self.all_paths = []
        self.visited = [[False for _ in range(self.cols)] for _ in range(self.rows)]
        self.shortest_path = None
        self.directions = [(-1, 0), (0, -1), (1, 0), (0, 1)]  # Arriba, izquierda, abajo, derecha

    def solve(self):
        self._find_start_goal()
        if not self.start or not self.goal:
            print("Start or goal not found.")
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
        return self.all_paths

    def _find_start_goal(self):
        """Encuentra inicio (3) y meta (4) en el laberinto"""
        for i in range(self.rows):
            for j in range(self.cols):
                if self.maze[i][j] == 3:  # Punto de inicio
                    self.start = (i, j)
                elif self.maze[i][j] == 4:  # Punto de meta
                    self.goal = (i, j)

    def _backtrack(self, x, y, path):
        """Algoritmo de backtracking mejorado para encontrar todas las rutas posibles"""
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