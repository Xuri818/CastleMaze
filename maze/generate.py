# generate.py

import random

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
            random.shuffle(directions)
            for dx, dy in directions:
                nx, ny = x + dx, y + dy
                if 0 < nx < self.rows and 0 < ny < self.cols and self.maze[nx][ny] == 1:
                    self.maze[nx][ny] = 0
                    self.maze[x + dx // 2][y + dy // 2] = 0
                    carve(nx, ny)

        # Start at (1,1)
        self.maze[1][1] = 0
        carve(1, 1)

    def generate_render_maze(self):
        self.render_maze = [row[:] for row in self.maze]

    def add_imperfections(self, count=0):
        #  Add few random shortcuts (defaults to 0)
        for _ in range(count):
            x = random.randrange(1, self.rows - 1, 2)
            y = random.randrange(1, self.cols - 1, 2)
            if self.render_maze[x][y] == 1 or self.render_maze[x][y] == 0:
                self.render_maze[x][y] = 2

    def getRenderMaze(self):
        return self.render_maze

