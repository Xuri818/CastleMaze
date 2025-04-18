class MazeSolver:
    def __init__(self, maze):
        self.maze = [row[:] for row in maze] 
        self.rows = len(maze)
        self.cols = len(maze[0])
        self.goal = None
        self.start = None
        self.max_depth = 500
        self.visited = [[False for _ in range(self.cols)] for _ in range(self.rows)]
        self.shortest_path = None  # Track the shortest path
        self.directions = [(-1, 0), (0, -1), (1, 0), (0, 1)] # Up, Left, Down, Right

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

        # Mark the shortest path on the maze
        for x, y in self.shortest_path:
            if self.maze[x][y] != 4 and self.maze[x][y] != 3:  # start and goal
                self.maze[x][y] = 5

        return self.maze

    def _find_start_goal(self):
        for i in range(self.rows):
            for j in range(self.cols):
                if self.maze[i][j] == 4:  # Start point
                    self.start = (i, j)
                elif self.maze[i][j] == 3:  # Goal point
                    self.goal = (i, j)

    def _backtrack(self, x, y, path):

        # If we reach the goal, check if this path is the shortest
        if (x, y) == self.goal:
            if self.shortest_path is None or len(path) < len(self.shortest_path):
                self.shortest_path = list(path)  # Update the shortest path
            return

        #Manhattan Distance
        neighbors = []
        for dx, dy in self.directions:
            nx, ny = x + dx, y + dy
            if 0 <= nx < self.rows and 0 <= ny < self.cols:  # Stay within bounds
                if self.maze[nx][ny] in [0,2, 3] and not self.visited[nx][ny]:  # Valid path or goal
                    distance = abs(nx - self.goal[0]) + abs(ny - self.goal[1])
                    neighbors.append((distance, nx, ny))

        # Manhattan Distance
        neighbors.sort()

        # Explore neighbors in sorted order
        for _, nx, ny in neighbors:
            if self.shortest_path and len(path) >= len(self.shortest_path):  # Prune longer paths
                continue

            self.visited[nx][ny] = True
            path.append((nx, ny))  # Add this position to the current path
            self._backtrack(nx, ny, path)  # Recursively explore further
            path.pop()  # Backtrack 
            self.visited[nx][ny] = False









