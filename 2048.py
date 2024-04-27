import numpy as np
import random
import tkinter as tk
from tkinter import messagebox

class Game2048:
    def __init__(self, root, size=4):
        """initialize the game with a tkinter root window and board size""" # default 4x4 size and two tiles to start
        self.root = root
        self.size = size
        self.board = np.zeros((size, size), dtype=int)  # create a board filled with zeros
        self.score = 0  # initialize score to 0
        self.add_new_tile()  # add the first tile
        self.add_new_tile()  # add the second tile
        self.update_gui()  # update the GUI to reflect the initial board state

    def add_new_tile(self):
        """add a new tile (2 or 4) to a random empty spot on the board"""
        if np.any(self.board == 0):  # check if there is at least one empty spot
            i, j = random.choice([(i, j) for i in range(self.size) for j in range(self.size) if self.board[i, j] == 0])
            self.board[i, j] = 2 if random.random() < 0.9 else 4  # 90% chance to add a 2, 10% chance for a 4

    def compress(self, board):
        """compress the board by sliding all tiles to the left (used before merge)""" 
        # shifts all non-zero elements of each row to the left, ignores zeros
        new_board = np.zeros((self.size, self.size), dtype=int)
        for i in range(self.size):
            pos = 0  # position to insert the next non-zero tile
            for j in range(self.size):
                if board[i][j] != 0:
                    new_board[i][pos] = board[i][j] # move tile to the 'pos' index in the new board
                    pos += 1
        return new_board

    def merge(self, board):
        """merge tiles of the same value by doubling their value to the left"""
        #combines adjacent tiles of same value by doubling leftmost tile's value and set right tile to zero if they are the same
        score = 0
        for i in range(self.size):
            for j in range(self.size-1):
                if board[i][j] == board[i][j+1] and board[i][j] != 0:
                    board[i][j] *= 2
                    score += board[i][j]
                    board[i][j+1] = 0
        return board, score

    def reverse(self, board):
        """reverse each row of the board (used for right moves)"""
        new_board = np.zeros((self.size, self.size), dtype=int)
        for i in range(self.size):
            new_board[i] = board[i][::-1]
        return new_board

    def transpose(self, board):
        """transpose the board (used for up and down moves)"""
        return board.transpose()

    def move_left(self, board):
        """move tiles to the left and merge if possible"""
        board = self.compress(board)
        board, score = self.merge(board)
        board = self.compress(board)
        return board, score

    def move_right(self, board):
        """move tiles to the right and merge if possible"""
        board = self.reverse(board)
        board, score = self.move_left(board)
        board = self.reverse(board)
        return board, score

    def move_up(self, board):
        """move tiles up and merge if possible"""
        board = self.transpose(board)
        board, score = self.move_left(board)
        board = self.transpose(board)
        return board, score

    def move_down(self, board):
        """move tiles down and merge if possible"""
        board = self.transpose(board)
        board, score = self.move_right(board)
        board = self.transpose(board)
        return board, score

    def get_next_move(self):
        """determine the best next move by evaluating the potential score"""
        moves = ['Up', 'Down', 'Left', 'Right']
        best_score = -1
        best_move = None
        for move in moves:
            temp_board = np.copy(self.board)
            if move == 'Up':
                temp_board, score = self.move_up(temp_board)
            elif move == 'Down':
                temp_board, score = self.move_down(temp_board)
            elif move == 'Left':
                temp_board, score = self.move_left(temp_board)
            elif move == 'Right':
                temp_board, score = self.move_right(temp_board)

            # select the move that maximizes the score
            if not np.array_equal(self.board, temp_board) and score > best_score:
                best_move = move
                best_score = score

        return best_move

    def check_game_over(self):
        """check if there are no legal moves left"""
        if np.any(self.board == 0):
            return False  # there is at least one empty spot
        for move in ['Up', 'Down', 'Left', 'Right']:
            temp_board = np.copy(self.board)
            # check if any move changes the board
            if move == 'Up':
                temp_board, _ = self.move_up(temp_board)
            elif move == 'Down':
                temp_board, _ = self.move_down(temp_board)
            elif move == 'Left':
                temp_board, _ = self.move_left(temp_board)
            elif move == 'Right':
                temp_board, _ = self.move_right(temp_board)
            if not np.array_equal(self.board, temp_board):
                return False
        return True

    def play_move(self):
        """play the next move, update the score, and check for game over"""
        move = self.get_next_move()
        if move:
            if move == 'Up':
                self.board, score = self.move_up(self.board)
            elif move == 'Down':
                self.board, score = self.move_down(self.board)
            elif move == 'Left':
                self.board, score = self.move_left(self.board)
            elif move == 'Right':
                self.board, score = self.move_right(self.board)

            self.score += score
            self.add_new_tile()
            self.update_gui()

            if self.check_game_over():
                messagebox.showinfo("Game Over", f"Final Score: {self.score}")
                self.root.destroy()

    def update_gui(self):
        """update the GUI to reflect the current state of the board"""
        for widget in self.root.winfo_children():
            widget.destroy()

        color_scheme = {
            0: ("#cdc1b4", "#776e65"),
            2: ("#eee4da", "#776e65"),
            4: ("#ede0c8", "#776e65"),
            8: ("#f2b179", "#f9f6f2"),
            16: ("#f59563", "#f9f6f2"),
            32: ("#f67c5f", "#f9f6f2"),
            64: ("#f65e3b", "#f9f6f2"),
            128: ("#edcf72", "#f9f6f2"),
            256: ("#edcc61", "#f9f6f2"),
            512: ("#edc850", "#f9f6f2"),
            1024: ("#edc53f", "#f9f6f2"),
            2048: ("#edc22e", "#f9f6f2"),
        }

        for i in range(self.size):
            for j in range(self.size):
                val = self.board[i, j]
                bg_color, fg_color = color_scheme.get(val, ("#3c3a32", "#f9f6f2"))  # default color for tiles > 2048
                tile = tk.Label(self.root, text=str(val) if val != 0 else '', bg=bg_color,
                                fg=fg_color, font=("Helvetica", 24), width=4, height=2)
                tile.grid(row=i, column=j, padx=5, pady=5)

        self.root.after(500, self.play_move)  # automatically play the next move after 500ms

def main():
    root = tk.Tk()
    root.title("2048 Game AI")
    game = Game2048(root)  # create and start the game
    root.mainloop()

if __name__ == "__main__":
    main()


