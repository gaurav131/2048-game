from tkinter import Frame, Label, CENTER,Tk
from random import randint
import time
import numpy as np
import statistics
from game_2048 import GameDesigning

no_of_games = 3 #no of iteration you need it to run
best_tile_values = []
delay = 5 #waiting time in sec
a_moves = 2 #available moves for comparision

class Expectimax():
    # gives the next best move
    def next_step(self, board): 
        optimal_step, _ = self.optimize(board)
        return optimal_step
    # evaluate the tiles values
    def evaluation_board(self, board, n_empty): 
        grid = board.grid

        utility = 0
        smoothness = 0

        big_t = np.sum(np.power(grid, 2))
        s_grid = np.sqrt(grid)
        smoothness -= np.sum(np.abs(s_grid[::,0] - s_grid[::,1]))
        smoothness -= np.sum(np.abs(s_grid[::,1] - s_grid[::,2]))
        smoothness -= np.sum(np.abs(s_grid[::,2] - s_grid[::,3]))
        smoothness -= np.sum(np.abs(s_grid[0,::] - s_grid[1,::]))
        smoothness -= np.sum(np.abs(s_grid[1,::] - s_grid[2,::]))
        smoothness -= np.sum(np.abs(s_grid[2,::] - s_grid[3,::]))
        
        empty_w = 100000
        smoothness_w = 3

        empty_u = n_empty * empty_w
        smooth_u = smoothness ** smoothness_w
        big_t_u = big_t

        utility += big_t
        utility += empty_u
        utility += smooth_u

        return (utility, empty_u, smooth_u, big_t_u)
    # maximize
    def optimize(self, board, depth = 0):
        moves = board.get_available_moves()
        moves_boards = []

        for m in moves:
            m_board = board.clone()
            m_board.move(m)
            moves_boards.append((m, m_board))

        max_utility = (float('-inf'),0,0,0)
        best_direction = None

        for mb in moves_boards:
            utility = self.probabilty_node(mb[1], depth + 1)

            if utility[0] >= max_utility[0]:
                max_utility = utility
                best_direction = mb[0]

        return best_direction, max_utility
    # choice/probality node
    def probabilty_node(self, board, depth = 0):
        empty_cells = board.get_available_cells()
        n_empty = len(empty_cells)

        if n_empty >= 6 and depth >= 3:
            return self.evaluation_board(board, n_empty)

        if n_empty >= 0 and depth >= 5:
            return self.evaluation_board(board, n_empty)

        if n_empty == 0:
            _, utility = self.optimize(board, depth + 1)
            return utility

        possible_tiles = []

        chance_2 = (.9 * (1 / n_empty))
        chance_4 = (.1 * (1 / n_empty))
        
        for empty_cell in empty_cells:
            possible_tiles.append((empty_cell, 2, chance_2))
            possible_tiles.append((empty_cell, 4, chance_4))

        utility_sum = [0, 0, 0, 0]

        for t in possible_tiles:
            t_board = board.clone()
            t_board.insert_tile(t[0], t[1])
            _, utility = self.optimize(t_board, depth + 1)

            for i in range(4):
                utility_sum[i] += utility[i] * t[2]

        return tuple(utility_sum)

# game gui configurations
SIZE , GRID_LEN, GRID_PADDING= 500, 4, 10

BACKGROUND_COLOR_GAME = "#92877d"
BACKGROUND_COLOR_CELL_EMPTY = "#9e948a"
BACKGROUND_COLOR_DICT = {   2:"#eee4da", 4:"#ede0c8", 8:"#f2b179", 16:"#f59563", \
                            32:"#f67c5f", 64:"#f65e3b", 128:"#edcf72", 256:"#edcc61", \
                            512:"#edc850", 1024:"#edc53f", 2048:"#edc22e" }
CELL_COLOR_DICT = { 2:"#776e65", 4:"#776e65", 8:"#f9f6f2", 16:"#f9f6f2", \
                    32:"#f9f6f2", 64:"#f9f6f2", 128:"#f9f6f2", 256:"#f9f6f2", \
                    512:"#f9f6f2", 1024:"#f9f6f2", 2048:"#f9f6f2" }
FONT = ("Arial", 40, "bold")




# Creating GUI for the game
class GuiFrame(Frame):
    def __init__(self):
        Frame.__init__(self)

        self.grid()
        self.master.title('Yash AI')
        self.grid_cells = []

        self.init_grid()
        self.init_matrix()
        self.update_grid_cells()
        self.Expectimax = Expectimax()

        self.run_game()
        self.mainloop()
    # running the game
    def run_game(self):
        while True:
            self.board.move(self.Expectimax.next_step(self.board))
            self.update_grid_cells()
            self.add_init_tiles()
            self.update_grid_cells()

            if len(self.board.get_available_moves()) == a_moves:
                tile_values = list(map(int, reversed(sorted(list(self.board.grid.flatten())))))
                best_tile_values.append(tile_values[0])
                print("Score: -",tile_values[0])
                time.sleep(delay)
                self.master.destroy()
                break

            self.update()
        

    def init_grid(self):
        background = Frame(self, bg=BACKGROUND_COLOR_GAME, width=SIZE, height=SIZE)
        background.grid()

        for i in range(GRID_LEN):
            grid_row = []

            for j in range(GRID_LEN):

                cell = Frame(background, bg=BACKGROUND_COLOR_CELL_EMPTY, width=SIZE/GRID_LEN, height=SIZE/GRID_LEN)
                cell.grid(row=i, column=j, padx=GRID_PADDING, pady=GRID_PADDING)
                t = Label(master=cell, text="", bg=BACKGROUND_COLOR_CELL_EMPTY, justify=CENTER, font=FONT, width=4, height=2)
                t.grid()
                grid_row.append(t)

            self.grid_cells.append(grid_row)

    def gen(self):
        return randint(0, GRID_LEN - 1)

    def init_matrix(self):
        self.board = GameDesigning()
        self.add_init_tiles()
        self.add_init_tiles()

    def update_grid_cells(self):
        for i in range(GRID_LEN):
            for j in range(GRID_LEN):
                new_number = int(self.board.grid[i][j])
                if new_number == 0:
                    self.grid_cells[i][j].configure(text="", bg=BACKGROUND_COLOR_CELL_EMPTY)
                else:
                    n = new_number
                    if new_number > 2048:
                        c = 2048
                    else:
                        c = new_number

                    self.grid_cells[i][j].configure(text=str(n), bg=BACKGROUND_COLOR_DICT[c], fg=CELL_COLOR_DICT[c])
        self.update_idletasks()
        
    def add_init_tiles(self):
        if randint(0,99) < 100 * 0.9:
            value = 2
        else:
            value = 4

        cells = self.board.get_available_cells()
        pos = cells[randint(0, len(cells) - 1)] if cells else None

        if pos is None:
            return None
        else:
            self.board.insert_tile(pos, value)
            return pos

for i in range(no_of_games):
    print("--------------------------------")
    print("this is",i+1,"time game is running")
    GuiFrame()
    print("--------------------------------")
print("maximum output: -", max(best_tile_values), "in", best_tile_values.index(max(best_tile_values)), "attempt")
print("minimum output: -", min(best_tile_values), "in", best_tile_values.index(min(best_tile_values)), "attempt")
print("Arithmetic mean: -", round(statistics.mean(best_tile_values),2))