from random import random

def test_grid():
    # Draw your test grid here

    grid = create_grid(10)
    randomly_open(grid, .6)
    # grid = [[0, 0, 0, 1, 0, 0, 0],
    #         [0, 0, 0, 1, 0, 0, 0],
    #         [0, 0, 0, 1, 0, 0, 0],
    #         [0, 1, 1, 1, 1, 1, 0],
    #         [0, 1, 0, 1, 0, 1, 0],
    #         [0, 1, 0, 1, 0, 1, 0],
    #         [0, 1, 0, 1, 0, 1, 0]]
    
    return grid

def create_grid(n: int) -> list[list[int]]:
    grid = []
    for i in range(n):
        row = []
        # BEGIN TODO: build each row here. To add items to a list, use the .append() function: row.append(0).
        for j in range(n):
            row.append(0)
        # END TODO
        grid.append(row)
    
    return grid

def randomly_open(grid: list[list[int]], probability: float) -> int:
    # returns the number of cells opened
    cells_opened = 0
    n = len(grid)
    for i in range(n):
        for j in range(n):
            roll = random()
            if roll <= probability:
                grid[i][j] = 1
                cells_opened += 1

    return cells_opened

def step(grid: list[list[int]]) -> int:
    '''
    Take one time step to make every water cell in the grid fill the squares around them.

    0: closed
    1: open
    2: filled with water

    Returns the number of newly filled cells.
    '''
    # get all filled cells
    # if there are no filled cells, fill the top row.
    # otherwise, fill out the adjacent cells
    # returns the number of new cells opened

    currently_filled = []
    newly_filled = 0

    # get all water cells. a cell is represented with a row and column index
    n = len(grid)
    for i in range(n):
        for j in range(n):
            if grid[i][j] == 2:
                currently_filled.append([i, j])

    # fill the top layer with water if there are no watered cells. counts as a step
    if not currently_filled:
        for j in range(n):
            if grid[0][j] == 1:
                grid[0][j] = 2
                newly_filled += 1

        return newly_filled

    # For each filled cell, fill the ones next to it.
    for filled_cell in currently_filled:
        i = filled_cell[0]
        j = filled_cell[1]

        down = i + 1
        up = i - 1
        right = j + 1
        left = j - 1

        down_valid = down < n
        up_valid = up >= 0
        right_valid = right < n
        left_valid = left >= 0

        # EXAMPLE: down cell
        if down_valid:
            if grid[down][j] == 1:
                grid[down][j] = 2
                newly_filled += 1

            if grid[down][j] == 0:
                grid[down][j] = -1

        # BEGIN TODO: left cell
        # Check if there is a left cell and if it is open.
        # If yes, fill it and increase newly_filled by 1
        if left_valid:
            if grid[i][left] == 1:
                grid[i][left] = 2
                newly_filled += 1

            if grid[i][left] == 0:
                grid[i][left] = -1
        # END TODO

        # BEGIN TODO: right cell
        # Check if there is a right cell and if it is open.
        # If yes, fill it and increase newly_filled by 1
        if right_valid:
            if grid[i][right] == 1:
                grid[i][right] = 2
                newly_filled += 1
            
            if grid[i][right] == 0:
                grid[i][right] = -1
        # END TODO
        
        # BEGIN TODO: up cell
        # Check if there is a up cell and if it is open.
        # If yes, fill it and increase newly_filled by 1
        if up_valid:
            if grid[up][j] == 1:
                grid[up][j] = 2
                newly_filled += 1

            if grid[up][j] == 0:
                grid[up][j] = -1
        # END TODO

    return newly_filled

def step_all(grid: list[list[int]]):
    newly_filled = step(grid)
    while newly_filled > 0:
        newly_filled = step(grid)
    step(grid)

def percolates(grid: list[list[int]]) -> bool:
    # find a path from any of the top filled rows to the filled bottom row
    n = len(grid)
    visited = [[False]*n for _ in range(n)]
    
    # 4 directions: up, down, left, right
    directions = [(-1,0),(1,0),(0,-1),(0,1)]
    
    def dfs(r, c):
        if r == n-1:  # reached bottom row
            return True
        visited[r][c] = True
        for dr, dc in directions:
            nr, nc = r+dr, c+dc
            if 0 <= nr < n and 0 <= nc < n and not visited[nr][nc] and grid[nr][nc] == 2:
                if dfs(nr, nc):
                    return True
        return False

    # Start DFS from all top-row 1s
    for col in range(n):
        if grid[0][col] == 2 and not visited[0][col]:
            if dfs(0, col):
                return True

    return False

def count_contact(grid: list[list[int]]) -> int:
    # Count all cells with a -1
    n = len(grid)
    count = 0
    for i in range(n):
        for j in range(n):
            if grid[i][j] == -1:
                count += 1
    return count