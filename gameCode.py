import tkinter as tk
import random
import copy
import time
from ctypes import windll
from pygame import mixer
import sqlite3
from _thread import *

windll.shcore.SetProcessDpiAwareness(1)

class Game2048:
    def __init__(self, root):
        self.root = root
        self.gameMatrix = []
        self.freePositions = []
        self.gameScore = 0
        self.bestScore = 0
        self.nDimension = 4
        self.timeScore = 0
        self.running = False
        self.newGame = False
        self.gameRunning = True
        self.initialize_ui()
    def initialize_ui(self):
        self.root.title("2048 Game")
        self.root.resizable(False, False)
        self.root.configure(background="#faf8ef")
        self.root.minsize(width=432, height=571)
        
        self.name_label = tk.Label(self.root, text="Enter Your Name:", font=("Arial", 16, "bold"), bg="#faf8ef", fg="#776E65")
        self.name_label.grid(row=0, column=0, columnspan=self.nDimension, pady=(200, 0))

        self.name_entry = tk.Entry(self.root, font=("Arial", 16), width=20, borderwidth=0, highlightthickness=2, fg="#776E65", bg="#faf8ef", justify="center")
        self.name_entry.grid(row=1, column=0, columnspan=self.nDimension, padx=100, pady=10)

        self.submit_button = tk.Button(self.root, text="Submit", font=("Arial", 16, "bold"), background="#776E65", fg="#FBF9EF", borderwidth=0, highlightthickness=0, activebackground="#faf8ef", activeforeground="#776E65", command=self.start_game_callback)
        self.submit_button.grid(row=2, column=0, columnspan=self.nDimension, pady=10)

        self.name_entry.focus()

        self.root.bind('<Left>', self.handle_key)
        self.root.bind('<Right>', self.handle_key)
        self.root.bind('<Up>', self.handle_key)
        self.root.bind('<Down>', self.handle_key)
    def initialize_game_board(self):
    
        self.labels = [[tk.Label(self.root, text="", width=4, height=2, font=("Arial", 24, "bold"), bg="#CCC0B4", fg="#776E65", borderwidth=0, relief="solid")
                        for j in range(self.nDimension)] for i in range(self.nDimension)]
        for i in range(self.nDimension):
            for j in range(self.nDimension):
                self.labels[i][j].grid(row=i + 4, column=j, padx=5, pady=5)

        self.update_board_ui()
    def setup_game_info_ui(self):
        tabScore = self.get_best_score()
        firstLine = "1. " + " ".join(map(str, tabScore[0][:2])) if len(tabScore) > 0 else "1. -"
        secondLine = "2. " + " ".join(map(str, tabScore[1][:2])) if len(tabScore) > 1 else "2. -"
        thirdLine = "3. " + " ".join(map(str, tabScore[2][:2])) if len(tabScore) > 2 else "3. -"

        self.title_label = tk.Label(root, text="2048", font=("Arial", 28, "bold"), background="#FBF9EF", fg = "#776E65", anchor="w")
        self.title_label.grid(row=0, column=0, columnspan=self.nDimension, sticky="ew")

        self.bestScore_label = tk.Label(self.root, text=f"Best:\n{firstLine}\n{secondLine}\n{thirdLine}",
                                        font=("Arial", 16, "bold"), background="#FBF9EF", fg="#776E65",
                                        anchor="w", justify="left", wraplength=self.root.winfo_width())
        self.bestScore_label.grid(row=1, column=0, columnspan=self.nDimension, sticky="ew")

        self.score_label = tk.Label(self.root, text=f"Score: {self.gameScore}",
                                    font=("Arial", 16, "bold"), background="#FBF9EF", fg="#776E65",
                                    anchor="w", wraplength=self.root.winfo_width())
        self.score_label.grid(row=2, column=0, columnspan=self.nDimension, sticky="ew")

        self.time_label = tk.Label(self.root, text=f"Time: {self.timeScore}",
                                font=("Arial", 16, "bold"), background="#FBF9EF", fg="#776E65",
                                anchor="e", wraplength=self.root.winfo_width())
        self.time_label.grid(row=2, column=0, columnspan=self.nDimension, sticky="e")

        self.setup_game_control_ui()
    def setup_game_control_ui(self):
        self.newGameButton = tk.Button(self.root, text="New Game", font=("Arial", 18, "bold"),
                                    background="#776E65", fg="#FBF9EF",
                                    command=self.reset_game,
                                    anchor="center", borderwidth=0,
                                    activebackground="#FBF9EF", activeforeground="#776E65")
        self.newGameButton.grid(row=0, column=0, columnspan=self.nDimension, sticky="e")
    
    def start_game_callback(self):
        playerName = self.name_entry.get()
        if playerName:
            self.start_game(playerName)
    def start_game(self, playerName):
        self.playerName = playerName
        self.running = True
        self.newGame = False
        self.gameRunning = True
        self.gameScore = 0
        self.timeScore = 0
        self.nDimension = 4
        self.gameMatrix = [[" " for _ in range(self.nDimension)] for _ in range(self.nDimension)]
        self.freePositions = []

        self.name_label.grid_remove()
        self.name_entry.grid_remove()
        self.submit_button.grid_remove()

        self.root.config(background="#BBADA0")

        self.setup_game_info_ui()
        start_new_thread(self.updateThread, ())
        self.initialize_game_board()
        self.add_new_number()
        self.add_new_number()

    def handle_key(self, event):
        if not self.gameRunning:
            return
        
        game_matrix_test = copy.deepcopy(self.gameMatrix)
        moved = False
        result = None

        if event.keysym == 'Left':
            result = self.move_left(game_matrix_test, self.gameScore)
            if self.gameMatrix != result[0]:
                self.gameMatrix = result[0]
                self.gameScore = result[1]
                moved = True
                
        elif event.keysym == 'Right':
            result = self.move_right(game_matrix_test, self.gameScore)
        elif event.keysym == 'Up':
            result = self.move_up(game_matrix_test, self.gameScore)
        elif event.keysym == 'Down':
            result = self.move_down(game_matrix_test, self.gameScore)
        if self.gameMatrix != result[0]:
            self.gameMatrix = result[0]
            self.gameScore = result[1]
            moved = True

        if moved:
            self.play_sound()
            self.add_new_number()
            self.update_board_ui()
            self.check_game_over()
    def move_left(self, game_matrix_test, game_score_test):
        for i in range(self.nDimension):
            pairSums = []
            rowElements = game_matrix_test[i].copy()
            while " " in rowElements:
                rowElements.remove(" ")
            index = 0
            while index <= len(rowElements) - 1:
                if len(rowElements) == 1:
                    pairSums.append(rowElements[0])
                    break
                else:
                    if index < len(rowElements) - 1:
                        if rowElements[index] == rowElements[index + 1]:
                            pairSums.append(rowElements[index] * 2)
                            game_score_test += rowElements[index] * 2
                            index += 2
                        else:
                            pairSums.append(rowElements[index])
                            index += 1
                    else:
                        pairSums.append(rowElements[index])
                        index += 1
           
            if len(pairSums) != self.nDimension:
                for j in range(self.nDimension - len(pairSums)):
                    pairSums.append(" ")
                game_matrix_test[i] = pairSums
        return [game_matrix_test,game_score_test]
    def move_right(self, game_matrix_test, game_score_test):
        for i in range(self.nDimension):
            pairSums = []
            rowElements = game_matrix_test[i].copy()
            while (" " in rowElements):
                rowElements.remove(" ")
            index = len(rowElements) - 1
            while index >= 0:
                if len(rowElements) == 1:
                    pairSums.append(rowElements[0])
                    break
                else:
                    if index > 0:
                        if rowElements[index] == rowElements[index - 1]:
                            pairSums.append(rowElements[index] * 2)
                            game_score_test += rowElements[index] * 2
                            index -= 2
                        else:
                            pairSums.append(rowElements[index])
                            index -= 1
                    else:
                        pairSums.append(rowElements[index])
                        index -= 1

            pairSums = pairSums[::-1]
            if len(pairSums) != self.nDimension:
                for j in range(self.nDimension - len(pairSums)):
                    pairSums.insert(0," ")
            game_matrix_test[i] = pairSums
        return [game_matrix_test, game_score_test]
    def move_up(self, game_matrix_test, game_score_test):
        for i in range(self.nDimension):
            pairSums = []
            columnElements = []
            for j in range(self.nDimension):
                columnElements.append(game_matrix_test[j][i])
            while (" " in columnElements):
                columnElements.remove(" ")
            index = 0
            while index <= len(columnElements) - 1:
                if len(columnElements) == 1:
                    pairSums.append(columnElements[0])
                    break
                else:
                    if index < len(columnElements) - 1:
                        if columnElements[index] == columnElements[index + 1]:
                            pairSums.append(columnElements[index] * 2)
                            game_score_test += columnElements[index] * 2
                            index += 2
                        else:
                            pairSums.append(columnElements[index])
                            index += 1
                    else:
                        pairSums.append(columnElements[index])
                        index += 1
            if len(pairSums) != self.nDimension:
                for k in range(self.nDimension - len(pairSums)):
                    pairSums.append(" ")

            for _ in range(self.nDimension):
                game_matrix_test[_][i] = pairSums[_]
        return [game_matrix_test,game_score_test]
    def move_down(self, game_matrix_test, game_score_test):
        for i in range(self.nDimension):
            pairSums = []
            columnElements = []
            for j in range(self.nDimension):
                columnElements.append(game_matrix_test[j][i])
            while (" " in columnElements):
                columnElements.remove(" ")
            index = len(columnElements) - 1
            while index >= 0:
                if len(columnElements) == 1:
                    pairSums.append(columnElements[0])
                    break
                else:
                    if index > 0:
                        if columnElements[index] == columnElements[index - 1]:
                            pairSums.append(columnElements[index] * 2)
                            game_score_test += columnElements[index] * 2
                            index -= 2
                        else:
                            pairSums.append(columnElements[index])
                            index -= 1
                    else:
                        pairSums.append(columnElements[index])
                        index -= 1
            pairSums = pairSums[::-1]
            if len(pairSums) != self.nDimension:
                for k in range(self.nDimension - len(pairSums)):
                    pairSums.insert(0," ")

            for _ in range(self.nDimension):
                game_matrix_test[_][i] = pairSums[_]
        return [game_matrix_test,game_score_test]
    
    def update_board_ui(self):
        for i in range(self.nDimension):
            for j in range(self.nDimension):
                cell_value = self.gameMatrix[i][j]
                if cell_value == " ":
                    self.labels[i][j].config(text="", bg="#CCC0B4")
                else:
                    self.labels[i][j].config(text=str(cell_value), bg=self.get_color(cell_value), fg="#FAF8EF" if int(cell_value) > 4 else "#776E65")

                if cell_value == 2048:
                    self.game_win()

        self.score_label.config(text=f"Score: {self.gameScore}")
        self.time_label.config(text=f"Time: {self.timeScore}")
    def add_new_number(self):
        self.freePositions = [(i,j) for i in range(self.nDimension) for j in range(self.nDimension) if self.gameMatrix[i][j] == " "]
        if self.freePositions:
            i,j = random.choice(self.freePositions)
            self.gameMatrix[i][j] = 2 if random.random() < 0.9 else 4
            #self.gameMatrix[i][j] = 1024
            self.freePositions.remove((i,j))
            self.update_board_ui()
    def get_color(self, value):
        colors = {
            "2": "#eee4da",
            "4": "#ede0c8",
            "8": "#f2b179",
            "16": "#f59563",
            "32": "#f67c5f",
            "64": "#f65e3b",
            "128": "#edcf72",
            "256": "#edcc61",
            "512": "#edc850",
            "1024": "#edc53f",
            "2048": "#edc22e",
        }
        return colors.get(str(value), "#CCC0B4")  # Default color
    
    def check_game_over(self):
        if any(" " in row for row in self.gameMatrix):
            return

        for row in self.gameMatrix:
            for i in range(self.nDimension - 1):
                if row[i] == row[i + 1]:
                    return

        for i in range(self.nDimension):
            for j in range(self.nDimension - 1):
                if self.gameMatrix[j][i] == self.gameMatrix[j + 1][i]:
                    return

        self.gameRunning = False
        self.running = False
        self.title_label.config(text="Fail!", fg="#776E65")
        self.play_over_sound()
        self.insert_stats_to_db()
    def game_win(self):
        self.gameRunning = False
        self.running = False

        win_message = "Win!"
        self.title_label.config(text=win_message)
        self.newGameButton.config(text="Next Level", command=self.next_level)
        self.play_win_sound()
    def play_sound(self):
        mixer.init()
        mixer.music.load('buttonClick.mp3')
        mixer.music.play()
    def play_win_sound(self):
        mixer.init()
        mixer.music.load('win.mp3')
        mixer.music.play()
    def play_over_sound(self):
        mixer.init()
        mixer.music.load('fail.mp3')
        mixer.music.play()

    def reset_game(self):

        self.gameMatrix = [[" " for _ in range(self.nDimension)] for _ in range(self.nDimension)]
        self.freePositions = [(i, j) for i in range(self.nDimension) for j in range(self.nDimension)]
        self.gameScore = 0
        self.timeScore = 0
        self.running = True
        self.newGame = True
        self.gameRunning = True

        self.setup_game_info_ui()

        self.initialize_game_board()
        self.add_new_number()
        self.add_new_number()
        self.update_board_ui()
    def next_level(self):
        self.nDimension += 1

        self.gameMatrix = [[" " for _ in range(self.nDimension)] for _ in range(self.nDimension)]
        self.freePositions = [(i, j) for i in range(self.nDimension) for j in range(self.nDimension)]
        self.gameScore = 0
        self.timeScore = 0
        self.running = True
        self.newGame = True
        self.gameRunning = True
        self.title_label.config(text="2048")
        self.newGameButton.config(text="New Game", command=self.reset_game)

        self.setup_game_info_ui()
        start_new_thread(self.updateThread,())
        self.initialize_game_board()
        self.add_new_number()
        self.add_new_number()
        self.update_board_ui()

    def updateThread(self):
        while self.running:
            time.sleep(1)
            self.timeScore += 1
            self.time_label.config(text=f"Time: {self.timeScore}")

        tabScore = self.get_best_score()
        firstLine = "1. " + " ".join(map(str, tabScore[0][:2])) if len(tabScore) > 0 else "1. -"
        secondLine = "2. " + " ".join(map(str, tabScore[1][:2])) if len(tabScore) > 1 else "2. -"
        thirdLine = "3. " + " ".join(map(str, tabScore[2][:2])) if len(tabScore) > 2 else "3. -"

        self.title_label = tk.Label(root, text="2048", font=("Arial", 28, "bold"), background="#FBF9EF", fg = "#776E65", anchor="w")
        self.title_label.grid(row=0, column=0, columnspan=self.nDimension, sticky="ew")

        self.bestScore_label = tk.Label(self.root, text=f"Best:\n{firstLine}\n{secondLine}\n{thirdLine}",
                                        font=("Arial", 16, "bold"), background="#FBF9EF", fg="#776E65",
                                        anchor="w", justify="left", wraplength=self.root.winfo_width())
        self.bestScore_label.grid(row=1, column=0, columnspan=self.nDimension, sticky="ew")

        self.score_label = tk.Label(self.root, text=f"Score: {self.gameScore}",
                                    font=("Arial", 16, "bold"), background="#FBF9EF", fg="#776E65",
                                    anchor="w", wraplength=self.root.winfo_width())
        self.score_label.grid(row=2, column=0, columnspan=self.nDimension, sticky="ew")

        self.time_label = tk.Label(self.root, text=f"Time: {self.timeScore}",
                                font=("Arial", 16, "bold"), background="#FBF9EF", fg="#776E65",
                                anchor="e", wraplength=self.root.winfo_width())
        self.time_label.grid(row=2, column=0, columnspan=self.nDimension, sticky="e")

        self.setup_game_control_ui()
    def get_best_score(self):
        conn = sqlite3.connect('database.db')
        cur = conn.cursor()

        cur.execute("""
                SELECT name, MAX(score), MIN(timeScore) FROM RECORDS
                GROUP BY name
                ORDER BY score DESC
        """)

        result = cur.fetchall()
        conn.close()

        return result
    def insert_stats_to_db(self):
        conn = sqlite3.connect('database.db')
        cur = conn.cursor()

        cur.execute("INSERT INTO RECORDS (name, score, timeScore) VALUES (?, ?, ?)",
                    (self.playerName, self.gameScore, self.timeScore))

        conn.commit()
        conn.close()
    
if __name__ == "__main__":
    root = tk.Tk()
    game = Game2048(root)
    root.mainloop()