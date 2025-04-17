import random

class Generate:
    def __init__(self, rows, cols):
        self.logical_rows = rows
        self.logical_cols = cols
        self.physical_rows = rows * 3
        self.maze = [[1 for _ in range(cols)] for _ in range(rows)]
        self.render_maze = [[1 for _ in range(cols)] for _ in range(self.physical_rows)]

    def generate_maze(self):
        def carve(x, y):
            dirs = [(0, -2), (0, 2), (-2, 0), (2, 0)]
            random.shuffle(dirs)
            for dx, dy in dirs:
                nx, ny = x + dx, y + dy
                if 0 <= nx < self.logical_rows and 0 <= ny < self.logical_cols and self.maze[nx][ny] == 1:
                    self.maze[nx][ny] = 0
                    self.maze[(x + nx) // 2][(y + ny) // 2] = 0
                    carve(nx, ny)

        self.maze[1][1] = 0
        carve(1, 1)

    def generate_render_maze(self):
        self.render_maze = [[1 for _ in range(self.logical_cols)] for _ in range(self.physical_rows)]
        
        for y in range(self.logical_rows):
            for x in range(self.logical_cols):
                base_y = y * 3
                if self.maze[y][x] == 0:
                    self.render_maze[base_y + 1][x] = 0
                    
                    if y > 0 and self.maze[y-1][x] == 0:
                        self.render_maze[base_y][x] = 0
                    
                    if y < self.logical_rows - 1 and self.maze[y+1][x] == 0:
                        self.render_maze[base_y + 2][x] = 0
                    
                    if x > 0 and self.maze[y][x-1] == 0:
                        for i in range(3):
                            self.render_maze[base_y + i][x-1] = 0
                    
                    if x < self.logical_cols - 1 and self.maze[y][x+1] == 0:
                        for i in range(3):
                            self.render_maze[base_y + i][x+1] = 0

    def add_imperfections(self, count):
        added = 0
        attempts = 0
        max_attempts = count * 20
        
        while added < count and attempts < max_attempts:
            start_y = random.randrange(1, self.logical_rows - 1)
            start_x = random.randrange(1, self.logical_cols - 1)
            
            if self.maze[start_y][start_x] != 0:
                attempts += 1
                continue
            
            direction = random.choice(['horizontal', 'vertical'])
            
            if direction == 'horizontal':
                for x in range(start_x + 1, self.logical_cols):
                    if self.maze[start_y][x] == 0:
                        for tx in range(start_x + 1, x):
                            if self.maze[start_y][tx] == 1:
                                self.maze[start_y][tx] = 2
                                render_y = start_y * 3 + 1
                                self.render_maze[render_y][tx] = 2
                        added += 1
                        break
                    elif self.maze[start_y][x] == 1:
                        continue
                    else:
                        break
            
            else:
                for y in range(start_y + 1, self.logical_rows):
                    if self.maze[y][start_x] == 0:
                        for ty in range(start_y + 1, y):
                            if self.maze[ty][start_x] == 1:
                                self.maze[ty][start_x] = 2
                                base_render_y = ty * 3
                                for i in range(3):
                                    self.render_maze[base_render_y + i][start_x] = 2
                        added += 1
                        break
                    elif self.maze[y][start_x] == 1:
                        continue
                    else:
                        break
            
            attempts += 1