import tkinter as tk
import random
import time
import socket
import keyboard

class MatrixDrawer:
    def __init__(self, master, matrix, max_score, score):
        self.master = master
        self.matrix = matrix
        self.max_score = max_score
        self.score = score
        self.cell_size = 20
        self.colors = ['white', 'red', 'blue', 'green']

        self.score_label = tk.Label(master, text=f"Score: {self.score}")
        self.score_label.pack()

        self.max_score_label = tk.Label(master, text=f"Max Score: {self.max_score}")
        self.max_score_label.pack()

        self.canvas = tk.Canvas(master, width=len(matrix[0]) * self.cell_size, height=len(matrix) * self.cell_size)
        self.canvas.pack()

        self.draw_matrix()
        self.calculate_score()

    def set_matrix(self, new_matrix, new_max_score, new_score):
        self.matrix = new_matrix
        self.max_score = new_max_score
        self.score = new_score
        self.draw_matrix()
        self.calculate_score()

    def calculate_score(self):
        self.score_label.config(text=f"Score: {self.score}")
        self.max_score_label.config(text=f"Max Score: {self.max_score}")

    def draw_matrix(self):
        self.canvas.delete("all")
        for i, row in enumerate(self.matrix):
            for j, value in enumerate(row):
                x1, y1 = j * self.cell_size, i * self.cell_size
                x2, y2 = x1 + self.cell_size, y1 + self.cell_size

                color = self.colors[value]
                self.canvas.create_rectangle(x1, y1, x2, y2, fill=color, outline='black')


def string_to_matrix(matrix_str):
    """
    Преобразует строку в двумерный массив matrix.
    Каждая строка строки представляет собой строку чисел, разделенных пробелами.
    Строки разделены символом новой строки.
    """
    rows = matrix_str.strip().split("\n")
    matrix = [list(map(int, row.split())) for row in rows]
    return matrix


def check_arrow_key_pressed():
    if keyboard.is_pressed('up'):
        return '1'
    elif keyboard.is_pressed('down'):
        return '2'
    elif keyboard.is_pressed('left'):
        return '3'
    elif keyboard.is_pressed('right'):
        return '4'
    else:
        return "5"

def recv_splitter(recv_string):
    splited_string = recv_string.split(';')
    return splited_string[0], splited_string[1], splited_string[2]


def start_game_screen():
    # Создаем окно
    start_root = tk.Tk()
    start_root.title("Game Start")

    # Переменная, которая будет установлена в True при начале игры
    game_started = False

    # Функция, вызываемая при нажатии на кнопку "Start"
    def start_game():
        nonlocal game_started
        game_started = True
        start_root.destroy()  # Закрываем окно старта

    # Создаем кнопку "Start"
    button_start = tk.Button(start_root, text="Start", command=start_game)
    button_start.pack()

    # Запускаем цикл обработки событий Tkinter
    start_root.wait_window()

    return game_started

def endgame(root, score, maxscore):
    for widget in root.winfo_children():
        widget.destroy()
    root.title("Game Over")

    label_score = tk.Label(root, text=f"Score: {score}")
    label_score.pack()

    label_max_score = tk.Label(root, text=f"Max Score: {maxscore}")
    label_max_score.pack()

    def exit_program():
        root.destroy()

    button_exit = tk.Button(root, text="Exit", command=exit_program)
    button_exit.pack()

    root.mainloop()

if __name__ == "__main__":
    myIp = '172.20.10.2'

    port = 11012
    sock = socket.socket()
    sock.connect((myIp, port))
    print("Connected")
    start_game_screen()
    root = tk.Tk()
    matrix_size = (20, 10)
    data = sock.recv(1024).decode()
    matrix, score, max_score = recv_splitter(data)
    matrix = string_to_matrix(matrix)
    print(matrix)
    sock.send(bytes("1", encoding='utf-8'))
    app = MatrixDrawer(root, matrix, max_score, score)
    game_alive = True

    # Start the Tkinter main loop
    while game_alive == True:
        data = sock.recv(1024).decode()
        if data == "101":
            endgame(root, score, max_score)
            game_alive = False
        else:
            matrix, score, max_score = recv_splitter(data)
            matrix = string_to_matrix(matrix)
            print(matrix)
            app.set_matrix(matrix, score, max_score)

            # Обновление главного окна Tkinter
            root.update_idletasks()
            root.update()
            sended = check_arrow_key_pressed()
            sock.send(bytes(sended, encoding='utf-8'))

