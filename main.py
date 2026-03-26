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
def tween_color(color1, color2, t):
    # color1 and color2 are in hex format, e.g. "#RRGGBB"
    # t is a number between 0 and 1 that determines how much of each color to use
    c1 = np.array([int(color1[i:i+2], 16) for i in (1, 3, 5)])
    c2 = np.array([int(color2[i:i+2], 16) for i in (1, 3, 5)])
    ct = (1 - t) * c1 + t * c2
    return '#' + ''.join(f'{int(x):02x}' for x in ct)

def draw_grid(g: list[list[int]]):
    # for a new grid, g:
    # create a row
    # draw the cells for that grid
    # create a column containing info and a step through button

    # TODO: bind grid to state?

    def draw_cells():
        colors = {grid.CLOSED: "#000000", # black
                  grid.CONTAINED: "#FFF538", # yellow
                  grid.OPEN: "#FFFFFF", # white
                  grid.MAX_TDS: "#964B00", # brown
                  0: "#ADD8E6"} # lightblue
        for i in range(N):
            for j in range(N):
                cell = g[i][j]
                if cell <= grid.OPEN:
                    color = colors[cell]
                else:
                    prop_tds = cell / grid.MAX_TDS
                    color = tween_color(colors[0], colors[grid.MAX_TDS], prop_tds)
                cell_style = f'background-color: {color}; border-radius: 0px'
                ui.card().style(cell_style)

    def update_text():
        percolates_label.text = f'{grid.percolates(g)}'
        salt_captured_label.text = f'{grid.count_contact(g)}'
        tds_label.text = f'{int(grid.current_tds * 100) / 100} / {grid.MAX_TDS}'
        steps_label.text = f'{steps}'

    steps = 0
    def step():
        nonlocal steps
        steps += 1
        grid.step(g, capture_salts=capture_salts.value)
        display_grid.clear()
        with display_grid:
            draw_cells()
        update_text()

    def update_selectivity():
        grid.SELECTIVITY = selectivity.value

    center_style = 'display: flex; justify-content: center; width: 100%;'
    grid_row = ui.row().style(center_style)
    with grid_row:
        N = len(g)
        display_grid = ui.grid(rows=N, columns=N).style('gap: 0')
        with display_grid:
            draw_cells()
        
        with ui.column().style('width: 20%;'):
            with ui.row().style('width: 100%;'):
                ui.label('Percolates?').style('width:50%;')
                percolates_label = ui.label()
            with ui.row().style('width: 100%;'):
                ui.label('Contact area:').style('width:50%;')
                salt_captured_label = ui.label()
            with ui.row().style('width: 100%;'):
                ui.label('TDS:').style('width:50%;')
                tds_label = ui.label()
            with ui.row().style('width: 100%;'):
                ui.label('Steps:').style('width:50%;')
                steps_label = ui.label()

            step_button = ui.button('step', on_click=step)
            capture_salts = ui.checkbox("Capture salts?", value=True)
            selectivity = ui.number(label="Selectivity (TDS removed if captured)", placeholder="Selectivity", value=grid.SELECTIVITY, min=0, max=grid.MAX_TDS, step=.1, on_change=update_selectivity).style('width: 100%;')
            update_text()

    return grid_row

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
        await experiment(int(N_input.value), p, 40, capture_salts=True)
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

async def experiment(N: int, p: float, t: int, capture_salts: bool=False):
    # perform t iid trials of a NxN grid with porosity p
    percolates = []
    counts = []

    for i in range(t):
        g = grid.create_grid(N)
        grid.randomly_open(g, p)
        grid.step_all(g, capture_salts=capture_salts)

        percolates.append(grid.percolates(g))
        counts.append(grid.count_contact(g))

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

with ui.row().style(center_style):
    def new_grid(N=None, p=None):
        if N is None:
            N = new_N.value
        if p is None:
            p = new_p.value

        grid.current_tds = grid.MAX_TDS
        g = grid.create_grid(int(N))
        grid.randomly_open(g, p)
        grid_column.clear()
        with grid_column:
            draw_grid(g)
            with ui.row().style(center_style):
                ui.label(f"New grid with N={N} and p={p}").style('color: gray; font-size: 12px;')

    grid_column = ui.column().style('width: 80%;')
    with grid_column:
        try:
            test_grid = grid.test_grid()
            draw_grid(test_grid)
        except:
            grid_column.clear()
            new_grid(20, .65)

    with ui.column().style('width: 80%;'):
        with ui.row().style(center_style):
            new_grid_button = ui.button('new grid', on_click=new_grid)

        with ui.row().style(center_style):
            new_N = ui.number(label="Grid side length (N)", placeholder="N", value=20, min=1, max=50, precision=0, step=1).style('width: 12%')
            new_p = ui.number(label="Porosity (p)", placeholder="p", value=0.65, min=0, max=1, step=0.01).style('width: 8%')


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
        ax.set_ylabel("Contact Area")
        ax.set_title("Contact Area vs Porosity")

with ui.row().style(center_style):
    ui.label("Each data point is the result of repeating T times: step through a given NxN grid and porosity until no new cells are filled and stepping one final time").style('color: gray; font-size: 12px;')

# clear
with ui.row().style(center_style):
    # clearing
    clear_button = ui.button("clear", on_click=clear_experiments)

ui.run(show=False, favicon='./images/penguin-suit.png')