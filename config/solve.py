class MazeSolver:
    def __init__(self, maze):
        self.maze = [row[:] for row in maze]  # Make a copy to avoid side effects
        self.rows = len(maze)
        self.cols = len(maze[0])
        self.goal = None
        self.start = None
        self.all_paths = []
        self.visited = [[False for _ in range(self.cols)] for _ in range(self.rows)]
        self.shortest_path = None  # Track the shortest path
        self.directions = [(-1, 0), (0, -1), (1, 0), (0, 1)]  # Up, left, down, right

    def solve(self):
        self._find_start_goal()
        if not self.start or not self.goal:
            print("Start or goal not found.")
            return self.maze

        # Initialize backtracking search
        sx, sy = self.start
        self.visited[sx][sy] = True
        self._backtrack(sx, sy, [(sx, sy)])  # Start the path with the start position

        if not self.shortest_path:
            print("No path found.")
            return self.maze

        
        for x, y in self.shortest_path:
            if self.maze[x][y] != 4 and self.maze[x][y] != 3:  #start and goal 
                self.maze[x][y] = 5

        return self.maze

    def get_paths(self):
        return self.all_paths

    def _find_start_goal(self):
        for i in range(self.rows):
            for j in range(self.cols):
                if self.maze[i][j] == 4:  # Start point
                    self.start = (i, j)
                elif self.maze[i][j] == 3:  # Goal point
                    self.goal = (i, j)

    def _backtrack(self, x, y, path):
        if (x, y) == self.goal:
            self.all_paths.append((list(path), len(path)))
            
            if self.shortest_path is None or len(path) < len(self.shortest_path):
                self.shortest_path = list(path)  # Update the shortest path
            return

        # Explore all possible directions
        for dx, dy in self.directions:
            nx, ny = x + dx, y + dy
            if 0 <= nx < self.rows and 0 <= ny < self.cols: 
                if self.maze[nx][ny] in [0, 2, 3] and not self.visited[nx][ny]:  # Valid path or goal
                    self.visited[nx][ny] = True
                    path.append((nx, ny))  # Add this position to the current path
                    self._backtrack(nx, ny, path)  # Recursively explore further
                    path.pop()  # Backtrack (remove the last position)
                    self.visited[nx][ny] = False









