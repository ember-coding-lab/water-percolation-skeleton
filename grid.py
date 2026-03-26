from random import random

CONTAINED = -3
CLOSED = -2
OPEN = -1 # no TDS

# > OPEN to talk about filled cells. "it's more than just opened, it's filled"
# TDS ranges from 0 to MAX_TDS.
MAX_TDS = 100
SELECTIVITY = 1 # how much TDS does a closed cell capture

# current_tds = MAX_TDS # any number greater than 0 is filled

def test_grid():
    # Draw your test grid here
    # grid = [[1, 0, 0, 0, 0],
    #         [1, 1, 1, 1, 1],
    #         [0, 0, 0, 0, 1],
    #         [1, 1, 1, 1, 1],
    #         [1, 0, 0, 0, 0]]

    return None

def create_grid(n: int) -> list[list[int]]:
    grid = []
    for i in range(n):
        row = []
        # BEGIN TODO: build each row here. To add items to a list, use the .append() function: row.append(0).
        for j in range(n):
            row.append(CLOSED)
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
                grid[i][j] = OPEN
                cells_opened += 1

    return cells_opened

def step(grid: list[list[int]], capture_salts: bool=False) -> int:
    '''
    Take one time step to make every water cell in the grid fill the squares around them.

    Returns the number of newly filled cells.
    '''
    # get all filled cells
    # if there are no filled cells, fill the top row.
    # otherwise, fill out the adjacent cells
    # returns the number of new cells opened

    # global current_tds
    current_tds = get_current_tds(grid)
    currently_filled = []
    newly_filled = 0

    # get all water cells. a cell is represented with a row and column index
    n = len(grid)
    for i in range(n):
        for j in range(n):
            if grid[i][j] > OPEN:
                currently_filled.append([i, j])

    # fill the top layer with water if there are no watered cells. counts as a step
    if not currently_filled:
        current_tds = MAX_TDS
        for j in range(n):
            if grid[0][j] == OPEN:
                grid[0][j] = current_tds
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

        # remove tds from total by ionic strength for each closed cell in contact with water that is not containing anything
        if down_valid and grid[down][j] == CLOSED:
            grid[down][j] = (capture_salts and CONTAINED) or CLOSED
            if capture_salts:
                current_tds = max(0, current_tds - SELECTIVITY)
        
        if left_valid and grid[i][left] == CLOSED:
            grid[i][left] = (capture_salts and CONTAINED) or CLOSED
            if capture_salts:
                current_tds = max(0, current_tds - SELECTIVITY)
        
        if right_valid and grid[i][right] == CLOSED:
            grid[i][right] = (capture_salts and CONTAINED) or CLOSED
            if capture_salts:
                current_tds = max(0, current_tds - SELECTIVITY)
        
        if up_valid and grid[up][j] == CLOSED:
            grid[up][j] = (capture_salts and CONTAINED) or CLOSED
            if capture_salts:
                current_tds = max(0, current_tds - SELECTIVITY)

        # then fill like normal
        # EXAMPLE: down cell
        if down_valid and grid[down][j] == OPEN:
            grid[down][j] = current_tds
            newly_filled += 1

        # BEGIN TODO: left cell
        # Check if there is a left cell and if it is open.
        # If yes, fill it and increase newly_filled by 1
        if left_valid and grid[i][left] == OPEN:
            grid[i][left] = current_tds
            newly_filled += 1
        # END TODO

        # BEGIN TODO: right cell
        # Check if there is a right cell and if it is open.
        # If yes, fill it and increase newly_filled by 1
        if right_valid and grid[i][right] == OPEN:
            grid[i][right] = current_tds
            newly_filled += 1
        # END TODO
        
        # BEGIN TODO: up cell
        # Check if there is a up cell and if it is open.
        # If yes, fill it and increase newly_filled by 1
        if up_valid and grid[up][j] == OPEN:
            grid[up][j] = current_tds
            newly_filled += 1
        # END TODO

    return newly_filled

def step_all(grid: list[list[int]], capture_salts: bool=False):
    newly_filled = step(grid, capture_salts)
    while newly_filled > 0:
        newly_filled = step(grid, capture_salts)
    step(grid, capture_salts)

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
            if 0 <= nr < n and 0 <= nc < n and not visited[nr][nc] and grid[nr][nc] > OPEN:
                if dfs(nr, nc):
                    return True
        return False

    # Start DFS from all top-row 1s
    for col in range(n):
        if grid[0][col] > OPEN and not visited[0][col]:
            if dfs(0, col):
                return True

    return False

def count_contact(grid: list[list[int]]) -> int:
    # Count all cells with a -1
    n = len(grid)
    count = 0
    for i in range(n):
        for j in range(n):
            if grid[i][j] == CONTAINED:
                count += 1
    return count

def lowest_bottom_tds(grid: list[list[int]]) -> float:
    n = len(grid)
    lowest = MAX_TDS
    for j in range(n):
        if grid[n-1][j] > OPEN and grid[n-1][j] < lowest:
            lowest = grid[n-1][j]
    return lowest

def get_current_tds(grid: list[list[int]]) -> float:
    n = len(grid)
    current_tds = MAX_TDS
    for i in range(n):
        for j in range(n):
            if grid[i][j] > OPEN and grid[i][j] < current_tds:
                current_tds = grid[i][j]
    return current_tds
