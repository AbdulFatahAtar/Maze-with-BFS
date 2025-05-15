"""
The report 250 words
"""

from pyamaze import maze, agent, COLOR
from collections import deque
import random
import tkinter as tk
from tkinter import simpledialog, messagebox
import time

# this function use the BFS algorithm to find the shortest path in a maze
def BFS(m, start=None):
    try:
        # use if condition to pick a random corner of the maze
        if start is None:
            corners = [(1, m.cols), (m.rows, 1), (m.rows, m.cols)]
            start = random.choice(corners)

        frontier = deque([start])
        bfsPath, explored, bSearch = {}, [start], []
        # use while loop to explore the cells until we find the goal point
        while frontier:
            curr = frontier.popleft()
            if curr == m._goal:
                break

            # use for loop to check each direction and add valid the near cells
            for d in 'ESNW':
                if m.maze_map[curr][d]:
                    child = {'E': (curr[0], curr[1]+1),
                             'W': (curr[0], curr[1]-1),
                             'S': (curr[0]+1, curr[1]),
                             'N': (curr[0]-1, curr[1])}[d]

                    # use if condition for checking if the child cell is already explored
                    if child in explored:
                        continue
                    # add the child cell to the frontier and explored list
                    frontier.append(child)
                    explored.append(child)
                    bfsPath[child] = curr
                    bSearch.append(child)

        if m._goal not in bfsPath and start != m._goal:
            raise ValueError("No path found from {} to {}".format(start, m._goal))

        # create a dictionary for backtrack and use while loop to find the way from goal to start point
        fwdPath = {}
        cell = m._goal
        while cell != start:
            parent = bfsPath[cell]
            fwdPath[parent] = cell
            cell = parent

        return bSearch, bfsPath, fwdPath
    except Exception as e:
        messagebox.showerror("BFS Error", str(e))
        return [], {}, {}

# this class creates a maze application with a GUI and it allows the user to set the maze size, difficulty and theme
class MazeApp:
    # this function is the main function that set up and start the maze
    def __init__(self):
        self.setup()
        self.root = tk.Tk()
        self.build_maze()
        self.create_dashboard()
        self.reset()
        self.root.mainloop()

    # this function sets up the maze size, difficulty and theme it uses tkinter user input
    def setup(self):
        dlg = tk.Tk(); dlg.withdraw()
        # use while loop to check the rows and cols within limits 10-30 and if condition to check if the user input is valid
        while True:
            try:
                rows = int(simpledialog.askstring("Maze Size", "Enter number of rows (10-30):", parent=dlg))
                cols = int(simpledialog.askstring("Maze Size", "Enter number of columns (10-30):", parent=dlg))
                if 10 <= rows <= 30 and 10 <= cols <= 30:
                    self.rows, self.cols = rows, cols
                    break
                else:
                    messagebox.showwarning("Invalid Size", "Rows and columns must be between 10 and 30.")
            except (TypeError, ValueError):
                messagebox.showwarning("Invalid Input", "Please enter integer values for size.")

        # use while loop to check the difficulty and if condition to check if the user input is valid
        self.loop_map = {'easy': 5, 'medium': 50, 'hard': 100}
        while True:
            lvl = simpledialog.askstring("Difficulty", "Choose difficulty (easy, medium, hard):", parent=dlg)
            if lvl and lvl.lower() in self.loop_map:
                self.level = lvl.lower()
                self.loopPercent = self.loop_map[self.level]
                break
            else:
                messagebox.showwarning("Invalid Difficulty", "Please choose from easy, medium, hard.")

        # use while loop to check the them and if condition to check if the user input is valid
        while True:
            th = simpledialog.askstring("Theme", "Choose theme (light or dark):", parent=dlg)
            if th and th.lower() in ('light', 'dark'):
                self.theme = th.lower()
                break
            else:
                messagebox.showwarning("Invalid Theme", "Please choose 'light' or 'dark'.")

        self.delay = 50
        dlg.destroy()

    # this function uses the pyamaze library to create the maze and the agents
    def build_maze(self):
        try:
            for w in list(self.root.children.values()):
                if isinstance(w, tk.Canvas):
                    w.destroy()

            self.m = maze(self.rows, self.cols)
            self.m.CreateMaze(loopPercent=self.loopPercent, theme=self.theme)
            self.start = random.choice([(1, self.cols), (self.rows, 1), (self.rows, self.cols)])
            self.bSearch, self.bfsPath, self.fwdPath = BFS(self.m, self.start)

            # create three agents with different, bule to find the goal, red to find the shorter way from the goal to the start point and yellow to use the short way from start point to the goal
            self.a = agent(self.m, *self.start, footprints=True, color=COLOR.blue, shape='square', filled=True)
            self.b = agent(self.m, *self.start, footprints=True, color=COLOR.yellow, shape='square', filled=False)
            self.c = agent(self.m, 1, 1, footprints=True, color=COLOR.red, shape='square', filled=True, goal=(self.rows, self.cols))
        except Exception as e:
            messagebox.showerror("Build Maze Error", str(e))

    # this function create a dashboard with two buttom and display 6 more information
    def create_dashboard(self):
        try:
            # create two buttom to close or replay
            self.canvas = next(w for w in self.root.children.values() if isinstance(w, tk.Canvas))
            self.frame = tk.Frame(self.root, bg='#222222', width=200)
            self.frame.place(relx=1.0, rely=0.0, anchor='ne')
            btn_kwargs = {'font':('Arial',12,'bold'),'bd':2,'relief':'ridge','width':12,'padx':6,'pady':4}
            tk.Button(self.frame, text="close", bg='#b22222', fg='black', **btn_kwargs, command=self.root.destroy).pack(pady=5)
            tk.Button(self.frame, text="Replay", bg='#228B22', fg='black', **btn_kwargs, command=self.reset).pack(pady=5)

            # create labels using for loop for display the moves, time, speed, them, goal, grid sizq
            self.labels = {}
            for key in ["Moves","Time (s)","Speed (ms)","Theme","Goal","Grid Size"]:
                lbl = tk.Label(self.frame, text=f"{key}: ", font=('Arial',12), fg='white', bg='#222222')
                lbl.pack(pady=3)
                self.labels[key] = lbl

            self.root.update()
            w, h = self.canvas.winfo_reqwidth(), self.canvas.winfo_reqheight()
            self.root.geometry(f"{w+200}x{h+60}")
        except Exception as e:
            messagebox.showerror("Dashboard Error", str(e))

    # this function reset the maze and the agents when the user click the replay button
    def reset(self):
        try:
            self.move_count = 0
            self.start_time = None

            # the blue agent explores in BFS order using while loop
            blue_cells = list(self.bSearch)

            # the red agent follows path back from goal to start using while loop
            red_cells = []
            cell = self.m._goal
            while True:
                red_cells.append(cell)
                if cell == self.start:
                    break
                cell = self.bfsPath[cell]

            # the yellow agent follows path from start to goal using while loop
            yellow_cells = []
            cell = self.start
            while cell != self.m._goal:
                next_cell = self.fwdPath[cell]
                yellow_cells.append(next_cell)
                cell = next_cell

            # use for loops to make all steps into one list
            self.steps = deque()
            for cell in blue_cells:
                self.steps.append((self.a, cell))
            for cell in red_cells:
                self.steps.append((self.c, cell))
            for cell in yellow_cells:
                self.steps.append((self.b, cell))

            self.a.position = self.start
            self.b.position = self.start
            self.c.position = (1,1)
            self.start_time = time.time()
            self.animate_step()
        except Exception as e:
            messagebox.showerror("Reset Error", str(e))

    # this function animate the agents step by step with delay
    def animate_step(self):
        try:
            # use if codition to make agents move step by step with delay
            if self.steps:
                agent_obj, cell = self.steps.popleft()
                agent_obj.position = cell
                self.move_count += 1
                self.update_dashboard()
                self.root.after(self.delay, self.animate_step)
            else:
                self.update_dashboard(final=True)
        except Exception as e:
            messagebox.showerror("Animation Error", str(e))

    # this function update the dashboard with the moves, time, speed, theme, goal and grid size 
    def update_dashboard(self, final=False):
        try:
            elapsed = time.time() - self.start_time if self.start_time else 0
            self.labels["Moves"].config(text=f"Moves: {self.move_count}")
            self.labels["Time (s)"].config(text=f"Time (s): {elapsed:.2f}")
            self.labels["Speed (ms)"].config(text=f"Speed (ms): {self.delay}")
            self.labels["Theme"].config(text=f"Theme: {self.theme.title()}")
            self.labels["Goal"].config(text=f"Goal: {self.m._goal}")
            self.labels["Grid Size"].config(text=f"Grid Size: {self.rows}x{self.cols}")
        except Exception as e:
            messagebox.showerror("Dashboard Update Error", str(e))

# this function is the main function that run the maze application using the MazeApp class
if __name__ == '__main__':
    MazeApp()
