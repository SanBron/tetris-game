from tkinter import *
from tkinter import messagebox
from random import choice, randrange
from copy import deepcopy
import time
import socket

class TetrisGame:
    def __init__(self, conn):
        self.conn = conn
        self.current_matrix = []
        self.W, self.H = 10, 20
        self.TILE = 45
        self.GAME_RES = self.W * self.TILE, self.H * self.TILE
        self.RES = 750, 940
        self.FPS = 60

        self.tk = Tk()
        self.app_running = True
        self.tk.protocol("WM_DELETE_WINDOW", self.on_closing)
        self.tk.title("Tetris")
        self.tk.resizable(0, 0)
        self.tk.wm_attributes("-topmost", 1)

        self.sc = Canvas(self.tk, width=self.RES[0], height=self.RES[1], bg="red", highlightthickness=0)
        self.sc.pack()

        self.game_sc = Canvas(self.tk, width=self.W * self.TILE + 1, height=self.H * self.TILE + 1, bg="yellow", highlightthickness=0)
        self.game_sc.place(x=20, y=20, anchor=NW)

        self.img_obj1 = PhotoImage(file="img/bg.png")
        self.sc.create_image(0, 0, anchor=NW, image=self.img_obj1)

        self.img_obj2 = PhotoImage(file="img/bg2.png")
        self.game_sc.create_image(0, 0, anchor=NW, image=self.img_obj2)

        self.grid = [self.game_sc.create_rectangle(x * self.TILE, y * self.TILE, x * self.TILE + self.TILE, y * self.TILE + self.TILE) for x in range(self.W) for y in range(self.H)]

        self.figures_pos = [[(-1, 0), (-2, 0), (0, 0), (1, 0)],
                            [(0, -1), (-1, -1), (-1, 0), (0, 0)],
                            [(-1, 0), (-1, 1), (0, 0), (0, -1)],
                            [(0, 0), (-1, 0), (0, 1), (-1, -1)],
                            [(0, 0), (0, -1), (0, 1), (-1, -1)],
                            [(0, 0), (0, -1), (0, 1), (1, -1)],
                            [(0, 0), (0, -1), (0, 1), (-1, 0)]]

        self.figures = [[[x + self.W // 2, y + 1, 1, 1] for x, y in fig_pos] for fig_pos in self.figures_pos]
        self.field = [[0 for i in range(self.W)] for j in range(self.H)]

        self.anim_count, self.anim_speed, self.anim_limit = 0, 60, 2000

        self.score, self.lines = 0, 0
        self.scores = {0: 0, 1: 100, 2: 300, 3: 700, 4: 1500}
        self.record = "0"
        self.sc.create_text(505, 30, text="TETRIS", font=("WiGuru 2", 50), fill="red", anchor=NW)
        self.sc.create_text(535, 780, text="score:", font=("WiGuru 2", 35), fill="black", anchor=NW)
        self._score = self.sc.create_text(550, 840, text=str(self.score), font=("WiGuru 2", 35), fill="black", anchor=NW)
        self.sc.create_text(525, 650, text="record:", font=("WiGuru 2", 35), fill="black", anchor=NW)
        self._record = self.sc.create_text(550, 710, text=self.record, font=("WiGuru 2", 35), fill="black", anchor=NW)

        self.get_color = lambda: (randrange(30, 256), randrange(30, 256), randrange(30, 256))

        self.figure, self.next_figure = deepcopy(choice(self.figures)), deepcopy(choice(self.figures))
        self.color, self.next_color = self.get_color(), self.get_color()

        self.dx, self.rotate = 0, False

        self.total_matrix = []
        self.key = 5

    def rgb_to_hex(self, rgb):
        return '#%02x%02x%02x' % rgb

    def check_borders(self):
        for i in range(4):
            if self.figure[i][0] < 0 or self.figure[i][0] > self.W - 1:
                return False
            elif self.figure[i][1] > self.H - 1 or self.field[self.figure[i][1]][self.figure[i][0]]:
                return False
        return True

    def move_obj(self):
        localkey = int(self.key)
        if localkey == 1:
            self.rotate = True
        elif localkey == 2:
            self.anim_limit = 100
        elif localkey == 3:
            print('dqsadqwdqd')
            self.dx = -1
        elif localkey == 4:
            self.dx = 1

    def on_closing(self):
        if messagebox.askokcancel("Выход из приложения", "Хотите выйти из приложения?"):
            self.app_running = False

    def get_record(self):
        try:
            with open('record') as f:
                return f.readline()
        except FileNotFoundError:
            with open('record', 'w') as f:
                f.write('0')
            return "0"

    def set_record(self, record, score):
        rec = max(int(record), score)
        with open('record', 'w') as f:
            f.write(str(rec))

    def run(self):
        while self.app_running:
            if self.app_running:
                self.current_matrix = [[0 for i in range(self.W)] for j in range(self.H)]
                self.record = self.get_record()
                self.move_obj()

                # move x
                figure_old = deepcopy(self.figure)
                for i in range(4):
                    self.figure[i][0] += self.dx
                    if not self.check_borders():
                        self.figure = deepcopy(figure_old)
                        break

                # move y
                self.anim_count += self.anim_speed
                if self.anim_count > self.anim_limit:
                    self.anim_count = 0
                    figure_old = deepcopy(self.figure)
                    for i in range(4):
                        self.figure[i][1] += 1
                        if not self.check_borders():
                            for i in range(4):
                                self.field[figure_old[i][1]][figure_old[i][0]] = self.color
                            self.figure, self.color = self.next_figure, self.next_color
                            self.next_figure, self.next_color = deepcopy(choice(self.figures)), self.get_color()
                            self.anim_limit = 2000
                            break

                # rotate
                center = self.figure[0]
                figure_old = deepcopy(self.figure)
                if self.rotate:
                    for i in range(4):
                        x = self.figure[i][1] - center[1]
                        y = self.figure[i][0] - center[0]
                        self.figure[i][0] = center[0] - x
                        self.figure[i][1] = center[1] + y
                        if not self.check_borders():
                            self.figure = deepcopy(figure_old)
                            break

                for row in range(self.H):
                    for col in range(self.W):
                        self.current_matrix[row][col] = self.field[row][col]
                        if any((self.figure[i][0] == col and self.figure[i][1] == row) for i in range(4)):
                            self.current_matrix[row][col] = 1


                # Display the matrix in the console
                if self.current_matrix != self.total_matrix:
                    matrix_str = ' '
                    for row in self.current_matrix:
                        row_str = " ".join(map(lambda x: str(1 if x else 0), row))
                        matrix_str += row_str + "\n"
                    matrix_str = matrix_str.strip()
                    data = matrix_str + ';' + str(self.score) + ';' + '0'
                    msg = bytes(data, encoding='utf-8')
                    conn.send(msg)
                    self.key = conn.recv(1024).decode()

                self.total_matrix = self.current_matrix

                line, self.lines = self.H - 1, 0
                for row in range(self.H - 1, -1, -1):
                    count = 0
                    for i in range(self.W):
                        if self.field[row][i]:
                            count += 1
                        self.field[line][i] = self.field[row][i]
                    if count < self.W:
                        line -= 1
                    else:
                        self.anim_speed += 3
                        self.lines += 1

                # compute score
                self.score += self.scores[self.lines]
                fig = []

                # draw figure
                for i in range(4):
                    figure_rect_x = self.figure[i][0] * self.TILE
                    figure_rect_y = self.figure[i][1] * self.TILE
                    fig.append(
                        self.game_sc.create_rectangle(figure_rect_x, figure_rect_y, figure_rect_x + self.TILE,
                                                      figure_rect_y + self.TILE, fill=self.rgb_to_hex(self.color)))

                # draw field
                for y, raw in enumerate(self.field):
                    for x, col in enumerate(raw):
                        if col:
                            figure_rect_x, figure_rect_y = x * self.TILE, y * self.TILE
                            fig.append(self.game_sc.create_rectangle(figure_rect_x, figure_rect_y, figure_rect_x + self.TILE,
                                                                       figure_rect_y + self.TILE, fill=self.rgb_to_hex(col)))

                fig2 = []

                # draw next figure
                for i in range(4):
                    figure_rect_x = self.next_figure[i][0] * self.TILE + 380
                    figure_rect_y = self.next_figure[i][1] * self.TILE + 185
                    fig2.append(self.sc.create_rectangle(figure_rect_x, figure_rect_y, figure_rect_x + self.TILE,
                                                         figure_rect_y + self.TILE, fill=self.rgb_to_hex(self.next_color)))

                # draw titles
                self.sc.itemconfigure(self._score, text=str(self.score))
                self.sc.itemconfigure(self._record, text=self.record)

                # game over
                for i in range(self.W):
                    if self.field[0][i]:
                        self.set_record(self.record, self.score)
                        self.field = [[0 for i in range(self.W)] for i in range(self.H)]
                        self.anim_count, self.anim_speed, self.anim_limit = 0, 60, 2000
                        self.score = 0
                        for item in self.grid:
                            self.game_sc.itemconfigure(item, fill=self.rgb_to_hex(self.get_color()))
                            time.sleep(0.005)
                            self.tk.update_idletasks()
                            self.tk.update()

                        for item in self.grid:
                            self.game_sc.itemconfigure(item, fill="")

                self.dx, self.rotate = 0, False
                self.tk.update_idletasks()
                self.tk.update()

                for id_fig in fig:
                    self.game_sc.delete(id_fig)

                for id_fig in fig2:
                    self.sc.delete(id_fig)

                time.sleep(0.005)

if __name__ == "__main__":
    port = 11000
    sock = socket.socket()
    sock.bind(('', port))
    sock.listen(1)
    conn, addr = sock.accept()
    game = TetrisGame(conn)
    game.run()

