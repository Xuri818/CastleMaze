# generate.py

import random
from maze.solve import MazeSolver
class Generate:
    def __init__(self, rows, cols):
        if rows % 2 == 0:
            rows += 1
        if cols % 2 == 0:
            cols += 1

        self.rows = rows
        self.cols = cols
        self.maze = [[1 for _ in range(cols)] for _ in range(rows)]
        self.render_maze = []

    def generate_maze(self):
        def carve(x, y):
            directions = [(0, -2), (0, 2), (-2, 0), (2, 0)]
            random.shuffle(directions)  # Randomize direction order for variability
            for dx, dy in directions:
                nx, ny = x + dx, y + dy
                if 0 < nx < self.rows and 0 < ny < self.cols and self.maze[nx][ny] == 1:
                    self.maze[nx][ny] = 0
                    self.maze[x + dx // 2][y + dy // 2] = 0  # Open the wall in between
                    carve(nx, ny)

        # Start carving from (1, 1)
        self.maze[1][1] = 0
        carve(1, 1)

    def generate_render_maze(self):
        # Copy maze for rendering
        self.render_maze = [row[:] for row in self.maze]

    def add_imperfections(self, count):
        """Introduce random shortcuts or imperfections to create multiple paths"""
        for _ in range(count):
            x = random.randrange(1, self.rows - 1)
            y = random.randrange(1, self.cols - 1)
            if self.maze[x][y] == 1:  # Ensure it's a wall
                self.maze[x][y] = 0  # Open this wall
                self.render_maze[x][y] = 2 # Reflect in render maze


        

    def getRenderMaze(self):
        return self.render_maze