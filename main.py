from nicegui import ui
from matplotlib import pyplot as plt
import numpy as np
import asyncio
import csv
import grid

#####################
# Variables
# each element in this array is a tuple with these variables
# (porosity, N, percolation proportion, closed contact count)
# porosity               : probability of opening a cell in an NxN grid. INPUT.
# N                      : grid side length. INPUT.
# percolation proprotion : proportion of grids that successfully percolated. OUTPUT.
# closed contact count   : the number of closed cells that were in contact with water, on average. OUTPUT.
# TDS                    : the total dissolved solids remaining in the water after capture, on average. OUTPUT.
results = []
headers = ["Porosity", "Grid Size", "Percolation Proportion", "Average Contact Area", "Dissolved Solids"]

#####################
# Helper functions
def get_header_index(header_name: str) -> int:
    for i in range(len(headers)):
        if headers[i] == header_name:
            return i 

    print("can't find header")
    return -1 


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
        tds_label.text = f'{int(grid.get_current_tds(g) * 100) / 100} / {grid.MAX_TDS}'
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

def download_results():
    global results, headers
    def to_python(val):
        if isinstance(val, np.generic):  # catches all numpy scalar types
            return val.item()
        return val

    file_name = 'results.csv'
    with open(file_name, 'w', newline='') as f:
        writer = csv.writer(f)

        writer.writerow(headers)
        writer.writerows([[to_python(v) for v in row] for row in results])
    
    ui.download.file(file_name)

def clear_plot():
    # will this remember the above context?
    # yes, so have to call the right subplot before calling this function
    lines = plt.gca().lines
    num_removed = 0
    while len(lines) > 0:
        lines[0].remove()
        num_removed += 1
    return num_removed

def clear_experiments():
    global results
    results = []
    with plot_context:
        plt.subplot(1, 2, (1, 1))
        clear_plot()

        plt.subplot(1, 2, (2, 2))
        clear_plot()

def get_limits(header: int):
    # porosity and percolation proportion -> 0 to 1
    if header == 0 or header == 2:
        return (0, 1.1)
    
    # grid size
    # empty results -> 0 to 50
    # have results -> 0 to max resutls
    if header == 1:
        if not results:
            return (0, 50)

        grid_sizes = np.array(results)[:, header]
        return (0, np.max(grid_sizes))

    # average contact area
    if header == 3:
        if not results:
            return (0, 100)
        contact_areas = np.array(results)[:, header]
        return (0, np.max(contact_areas) * 1.1)

    # tds
    if header == 4:
        if not results:
            return (0, grid.MAX_TDS)
        tds = np.array(results)[:, header]
        return (0, np.max(tds) * 1.1)
    
    print("no header found")
    return (0, 1)

def plot_simulation(x_header: int, y_header: int, plot_index: int):
    # x_header: index of the header to use on the x axis
    # y_header: index of the header to use on the y aixs
    # plot_index: which subplot to draw the x and y header
    # use global vars to plot
    global results
    sorted_array = np.array( sorted(results, key=lambda t: t[x_header]) ).reshape((-1, len(headers)))
    x = sorted_array[:, x_header]
    y = sorted_array[:, y_header]

    with plot_context:
        plt.subplot(1, 2, plot_index)
        clear_plot()
        ax = plt.gca()
        x_lim = get_limits(x_header)
        y_lim = get_limits(y_header)
        ax.set_xlim(x_lim)
        ax.set_ylim(y_lim)
        ax.set_xlabel(headers[x_header])
        ax.set_ylabel(headers[y_header])
        ax.set_title(f'{headers[y_header]} vs {headers[x_header]}')
        plt.plot(x, y, 'o')

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
    x_header_left = get_header_index(x_left.value)
    y_header_left = get_header_index(y_left.value)
    plot_simulation(x_header_left, y_header_left, 1)

    x_header_right = get_header_index(x_right.value)
    y_header_right = get_header_index(y_right.value)
    plot_simulation(x_header_right, y_header_right, 2)

async def experiment(N: int, p: float, t: int, capture_salts: bool=False):
    # perform t iid trials of a NxN grid with porosity p
    percolates = []
    counts = []
    tdss = []

    for i in range(t):
        g = grid.create_grid(N)
        grid.randomly_open(g, p)
        grid.step_all(g, capture_salts=capture_salts)

        percolates.append(grid.percolates(g))
        counts.append(grid.count_contact(g))
        tdss.append(grid.lowest_bottom_tds(g))

    # update global results
    # (porosity, N, percolation prop., avg counts, avg tds)
    percolate_prop = np.sum(percolates) / t
    avg_counts = np.sum(counts) / t
    avg_tds = np.sum(tdss) / t
    result = (p, N, percolate_prop, avg_counts, avg_tds)
    results.append(result)

#####################
# Rendering
center_style = 'display: flex; justify-content: center; width: 100%;' # attaching this style to a row centers all of its contents
border_style = 'border: 1px solid black;'
prange_low = .3
prange_high = .7

# Grid drawing and interaction
with ui.row().style(center_style):
    def new_grid(N=None, p=None):
        if N is None:
            N = new_N.value
        if p is None:
            p = new_p.value

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

# Simulation and plotting
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
    def use_vars(plot_index: int):
        h = {
            1: (x_left.value, y_left.value),
            2: (x_right.value, y_right.value)
        }
        x_header = get_header_index(h[plot_index][0])
        y_header = get_header_index(h[plot_index][1])
        plot_simulation(x_header, y_header, plot_index)

    # variable dropdown for left graph
    with ui.column().style('min-width: 180px'):
        y_left = ui.select(label="Y, plot 1", options=headers, value=headers[2]).style('width: 100%; flex-shrink: 0; flex-grow: 1;')
        x_left = ui.select(label="X, plot 1", options=headers, value=headers[0]).style('width: 100%; flex-shrink: 0; flex-grow: 1;')
        y_left.on_value_change(lambda: use_vars(1))
        x_left.on_value_change(lambda: use_vars(1))

    width = 10
    height = 4
    plot_context = ui.pyplot(figsize=(width, height), close=False).style()

    with plot_context:
        plt.subplot(1, 2, (1, 1))
        plot_simulation(0, 2, 1)

        plt.subplot(1, 2, (2, 2))
        plot_simulation(0, 3, 2)

    # variable dropdown for right graph
    with ui.column().style('min-width: 180px'):
        y_right = ui.select(label="Y, plot 2", options=headers, value=headers[3]).style('width: 100%; flex-shrink: 0; flex-grow: 1;')
        x_right = ui.select(label="X, plot 2", options=headers, value=headers[0]).style('width: 100%; flex-shrink: 0; flex-grow: 1;')
        y_right.on_value_change(lambda: use_vars(2))
        x_right.on_value_change(lambda: use_vars(2))

with ui.row().style(center_style):
    ui.label("Each data point is the result of repeating T times: step through a given NxN grid and porosity until no new cells are filled and stepping one final time").style('color: gray; font-size: 12px;')

# clear
with ui.row().style(center_style):
    ui.element('div').style('flex: 1;') # padding
    clear_button = ui.button("clear", on_click=clear_experiments)

    with ui.element().style('flex: 1; display: flex; '):    
        download_button = ui.button("download results", on_click=download_results).style()

ui.run(show=False, favicon='./images/penguin-suit.png', title='Water Percolation')