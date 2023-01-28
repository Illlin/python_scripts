import numpy as np
import pyray
import random
import math


def code_str_to_lists(code):
    code = code.split("/")
    births, survives = [int(x) for x in [*code][0][1:]], [int(y) for y in [*code][1][1:]]
    print(births, survives)
    return births, survives


def randomize_center(cells, radius):
    for y in range(math.floor(maze_height/2 - radius), math.floor(maze_height/2 + radius)):
        for x in range(math.floor(maze_width/2 - radius), math.floor(maze_width/2 + radius)):
            cells[y][x] = random.randint(0,1)


def sum_surrounding_cells(cells, x, y):
    return np.sum(cells[np.ix_([y-1,y,y+1],[x-1,x,x+1])]) - cells[y][x]


def lifelike_step(cells, birth, survive):
    newgrid = np.zeros((maze_height, maze_width))
    for y in range(1, maze_height-1):
        for x in range(1, maze_width-1):
            neighbours = sum_surrounding_cells(cells, x, y)
            if neighbours in birth and cells[y][x] == 0:
                newgrid[y][x] = 1
            elif neighbours in survive and cells[y][x] == 1:
                newgrid[y][x] = cells[y][x]
            else:
                newgrid[y][x] = 0
    return newgrid

def maze_to_cells(maze):
    vert_walls, horiz_walls = maze[0], maze[1]
    cells_height, cells_width = 2*len(vert_walls) + 1, 2*len(horiz_walls[0])+1
    cells = np.zeros((cells_height, cells_width))

    for y in range(1, cells_height-1):
        for x in range(1, cells_width-1):
            if x % 2 == 1 and y % 2 == 1:
                cells[y][x] = 1
    
            elif x % 2 == 1 and y % 2 == 0:
                cells[y][x] = horiz_walls[int((y-2)/2)][int((x-1)/2)]
            
            elif x % 2 == 0 and y % 2 == 1:
                cells[y][x] = vert_walls[int((y-1)/2)][int((x-2)/2)]

    return cells


def random_maze(width, height):
    horiz_walls = np.random.randint(0, 2, size=(height-1, width))
    vert_walls = np.random.randint(0, 2, size=(height, width-1))

    maze = [vert_walls, horiz_walls]
    return maze


def gen_recur_div_maze(width, height):
    horiz_walls = np.zeros((height-1, width))
    vert_walls = np.zeros((height, width-1))

    if width == 1 and height == 1:
        return vert_walls, horiz_walls
    elif width == 1:
        split_across = 1
    elif height == 1:
        split_across = 0
    else:
        split_across = (random.random() <= height/(width+height))

    if split_across:
        split = random.randint(0, height-2) # lock y value - horizontal line
        gap = random.randint(0, width-1)

        horiz_walls[split][gap] = 1

        # Top
        new_vert, new_horiz = gen_recur_div_maze(width, split+1)

        if (new_vert.shape[1] != 0):
            vert_walls[:new_vert.shape[0], -new_vert.shape[1]:] = new_vert
        if (new_horiz.shape[0] != 0):
            horiz_walls[:new_horiz.shape[0], -new_horiz.shape[1]:] = new_horiz

        # Bottom
        new_vert, new_horiz = gen_recur_div_maze(width, height-(split+1))

        if (new_vert.shape[1] != 0):
            vert_walls[-new_vert.shape[0]:, -new_vert.shape[1]:] = new_vert
        if (new_horiz.shape[0] != 0):
            horiz_walls[-new_horiz.shape[0]:, -new_horiz.shape[1]:] = new_horiz

    else:
        split = random.randint(0, width-2) # lock x value - vert line
        gap = random.randint(0, height-1)

        vert_walls[gap][split] = 1

        # Left
        new_vert, new_horiz = gen_recur_div_maze(split+1, height)

        if (new_vert.shape[1] != 0):
            vert_walls[:new_vert.shape[0], :new_vert.shape[1]] = new_vert
        if (new_horiz.shape[0] != 0):
            horiz_walls[:new_horiz.shape[0], :new_horiz.shape[1]] = new_horiz
        
        # Right
        new_vert, new_horiz = gen_recur_div_maze(width-(split+1), height)

        if (new_vert.shape[1] != 0):
            vert_walls[:new_vert.shape[0], -new_vert.shape[1]:] = new_vert
        if (new_horiz.shape[0] != 0):
            horiz_walls[:new_horiz.shape[0], -new_horiz.shape[1]:] = new_horiz

    return vert_walls, horiz_walls


def add_openings(cells):
    cells[0][1] = 1
    cells[-1][-2] = 1
    return cells


def automata_dead_end_solve_step(cells):
    hei, wid = len(cells), len(cells[0])
    newgrid = np.zeros((hei, wid))
    vects = [(1,0),(0,1),(-1,0),(0,-1)]

    for y in range(1, hei-1):
        for x in range(1, wid-1):

            if cells[y][x] == 1:
                neighbours = 0
                for vect in vects:
                    if cells[y+vect[0]][x+vect[1]] in [0,2]:
                        neighbours += 1
            
                if neighbours == 3:
                    newgrid[y][x] = 2
                else:
                    newgrid[y][x] = 1
            
            else:
                newgrid[y][x] = cells[y][x]

    newgrid[0][1] = 1
    newgrid[-1][-2] = 1
    return newgrid
            

cell_size = 10
maze_width, maze_height = 50, 50
tick_rate = 1/500
rule = "B3678/S34678"

colours = {
    0: pyray.Color(0,0,0,255),
    1: pyray.Color(255,255,255,255),
    2: pyray.Color(0,255,0,255)
}

def main():
    # Generate Maze
    maze = gen_recur_div_maze(maze_width, maze_height)
    cells = add_openings(maze_to_cells(maze))

    # Screen size
    screen_width, screen_height = len(cells[0]) * cell_size, len(cells) * cell_size
    screen_size = [screen_width,screen_height]
    grid_size = [len(cells[0]), len(cells)]

    # Init
    pyray.init_window(*screen_size, "Life-like automata")

    # Setup texture
    cell_img = pyray.gen_image_color(*grid_size, pyray.WHITE)
    cell_texture = pyray.load_texture_from_image(cell_img)
    pyray.unload_image(cell_img)
    pixels = pyray.ffi.new(f"Color [{grid_size[0]}][{grid_size[1]}]")

    pyray.set_target_fps(500)
    delta = 0

    while not pyray.window_should_close():
        # update cells
        delta += pyray.get_frame_time()
        if delta >= tick_rate:
            while delta >= tick_rate:
                cells = automata_dead_end_solve_step(cells)
                #delta -= tick_rate
                delta = 0 # Forces max 1 tick per frame

            for y in range(grid_size[1]):
                for x in range(grid_size[0]):
                    pixels[y][x] = colours[cells[y][x]]
                    

            pyray.update_texture(cell_texture,pyray.ffi.addressof(pixels))

        pyray.begin_drawing()

        # Draw texture
        pyray.clear_background(pyray.WHITE)
        source = pyray.Rectangle(0, 0, grid_size[0], -grid_size[1]) # Flip Y
        pyray.draw_texture_pro(cell_texture, source, pyray.Rectangle(0, 0, *screen_size), (0,0), 0, pyray.WHITE)

        pyray.draw_fps(10, 10)
    
        pyray.end_drawing()


if __name__ == "__main__":
    main()