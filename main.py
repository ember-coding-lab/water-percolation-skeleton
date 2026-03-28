from nicegui import ui
from matplotlib import pyplot as plt
import numpy as np
import asyncio
import grid

#####################
# Variables
# each element in this array is a tuple with these variables
# (porosity, N, percolation proportion, closed contact count)
# porosity               : probability of opening a cell in an NxN grid. INPUT.
# N                      : grid side length. INPUT.
# percolation proprotion : proportion of grids that successfully percolated. OUTPUT.
# closed contact count   : the number of closed cells that were in contact with water, on average. OUTPUT.
results = []

#####################
# Helper functions
def draw_grid(g: list[list[int]]):
    # for a new grid, g:
    # create a row
    # draw the cells for that grid
    # create a column containing info and a step through button

    # TODO: bind grid to state?

    def draw_cells():
        colors = {0: "black", 1: "white", 2: "blue"}
        for i in range(N):
            for j in range(N):
                cell_style = f'background-color: {colors[g[i][j]]}; border-radius: 0px'
                ui.card().style(cell_style)

    def update_text():
        percolates_label.text = f'Percolates? {grid.percolates(g)}'
        closed_count_label.text = f'Closed cell in contact with water: {grid.count_closed_contact(g)}'

    def step():
        grid.step(g)
        display_grid.clear()
        with display_grid:
            draw_cells()
        update_text()

    center_style = 'display: flex; justify-content: center; align-items: center; width: 100%;'
    with ui.row().style(center_style):
        N = len(g)
        display_grid = ui.grid(rows=N, columns=N).style('gap: 0')
        with display_grid:
            draw_cells()
        
        with ui.column():
            percolates_label = ui.label()
            closed_count_label = ui.label()
            step_button = ui.button('step', on_click=step)
            update_text()

def clear_plot(plot):
    with plot:
        lines = plt.gca().lines
        num_removed = 0
        while len(lines) > 0:
            lines[0].remove()
            num_removed += 1
    return num_removed

def clear_experiments():
    global results
    results = []
    clear_plot(percolation_plot)
    clear_plot(closed_count_plot)

def plot_simulation():
    # use global vars to plot
    global results
    sorted_array = np.array( sorted(results, key=lambda t: t[0]) ).reshape((-1, 4))
    x = sorted_array[:, 0]

    with percolation_plot:
        y_percolate = sorted_array[:, 2]
        clear_plot(percolation_plot)
        fig = plt.gcf()
        fig.tight_layout()
        plt.plot(x, y_percolate, 'o-')

    with closed_count_plot:
        y_closed_count = sorted_array[:, 3]
        clear_plot(closed_count_plot)
        fig = plt.gcf()
        fig.tight_layout()
        plt.plot(x, y_closed_count, 'o-')

async def simulate():
    # handle simulate button click event
    # perform experiment for different values of p
    global results
    min_p = porosity_range.value['min']
    max_p = porosity_range.value['max']

    step_size = 0.01
    plist = np.arange(min_p, max_p + step_size, step_size)
    i = 0
    async def work(p):
        # do the experiment
        nonlocal i
        await experiment(int(N_input.value), p, 40)
        i += 1

    simulate_button.disable()
    for p in plist:
        await work(p)
        simulate_button.text = f"Completed {i} / {len(plist)}"
        await asyncio.sleep(0)

    simulate_button.text = 'simulate'
    simulate_button.enable()
    # print("final results: ", results)
    plot_simulation()

async def experiment(N: int, p: float, t: int):
    # perform t iid trials of a NxN grid with porosity p
    percolates = []
    counts = []

    for i in range(t):
        g = grid.create_grid(N)
        grid.randomly_open(g, p)
        grid.step_all(g)

        percolates.append(grid.percolates(g))
        counts.append(grid.count_closed_contact(g))

    # update global results
    # (porosity, N, percolation prop., avg counts)
    percolate_prop = np.sum(percolates) / t
    avg_counts = np.sum(counts) / t
    result = (p, N, percolate_prop, avg_counts)
    results.append(result)

#####################
# Rendering
center_style = 'display: flex; justify-content: center; width: 100%;' # attaching this style to a row centers all of its contents
prange_low = .3
prange_high = .7

try:
    test_grid = grid.test_grid()
except:
    test_grid = grid.create_grid(20)
    grid.randomly_open(test_grid, .6)

draw_grid(test_grid)

ui.label() # padding
ui.separator()
ui.label() # padding

sim_params_width = '40%'
with ui.row().style('display: flex; justify-content: center; align-items: center; width: 100%;'):
    with ui.column().style(f'width: {sim_params_width}'):
        with ui.row().style('width: 100%;'):
            N_input = ui.number(label="Grid side length (N)", placeholder="N", value=20, min=1, max=50, precision=0, step=1).style('width: 20%')
            ui.label("N larger than 30 may crash and cause a refresh").style('color: gray; font-size: 12px;')
        prange_label = ui.label(f"Porosity range: ({prange_low}, {prange_high})")

ui.label() # padding

# porosity range   
with ui.row().style(center_style):
     
    porosity_range = ui.range(min=0, max=1, step=.01,
                              value={'min': prange_low, 'max': prange_high})\
                                .style(f'width: {sim_params_width}')\
                                .props('label-always')
    porosity_range.on_value_change(lambda: setattr(prange_label, 'text', f"Porosity range: ({porosity_range.value['min']}, {porosity_range.value['max']})"))

# simulation button
with ui.row().style(center_style):
    simulate_button = ui.button('simulate', on_click=simulate)

# plotting
with ui.row().style(center_style):
    width = 4
    height = 4
    percolation_plot = ui.pyplot(figsize=(width, height), close=False)
    closed_count_plot = ui.pyplot(figsize=(width, height), close=False)
    
    with percolation_plot:
        ax = plt.axes()
        ax.set_xlim(0, 1)
        ax.set_ylim(0, 1.1)
        ax.set_xlabel("Porosity")
        ax.set_ylabel("Percolation Probability")
        ax.set_title("Percolation Probability vs Porosity")

    with closed_count_plot:
        ax = plt.axes()
        ax.set_xlim(0, 1)
        ax.set_xlabel("Porosity")
        ax.set_ylabel("Watered Cells")
        ax.set_title("Watered Closed Cells Count vs Porosity")

with ui.row().style(center_style):
    ui.label("Each data point is the result of repeating T times: step through a given NxN grid and porosity until no new cells are filled").style('color: gray; font-size: 12px;')

# clear
with ui.row().style(center_style):
    # clearing
    clear_button = ui.button("clear", on_click=clear_experiments)

ui.run(show=False, favicon='./images/penguin-suit.png')