import tkinter as tk
from tkinter import messagebox
from game_engine import Board
import time
import threading
import os
import csv
import datetime
import ai_agent
from ai_agent import red_minimax_ai, blue_minimax_ai, random_ai

CELL_WIDTH = 60
CELL_HEIGHT = 60
ROWS = 9
COLS = 6
GFILE = 'gamestate.txt'

class GameUI:
    def __init__(self, root, ai_vs_ai=False):
        self.root = root
        self.root.title("Chain Reaction")
        self.canvas = tk.Canvas(root, width=COLS * CELL_WIDTH, height=ROWS * CELL_HEIGHT)
        self.canvas.pack()
        self.hint_button = tk.Button(root, text="Let AI Play for Red", command=self.ai_play_red)
        self.hint_button.pack(pady=10)

        self.canvas.bind("<Button-1>", self.on_click)
        self.current_player = 'R'  
        self.board = Board()
        self.ai_vs_ai = ai_vs_ai
        self.write_state("Human Move:")  
        self.draw()

        # Human plays first, then after each human move, Blue AI plays 3 times

        if self.ai_vs_ai:
            self.ai_loop_thread = threading.Thread(target=self.ai_vs_ai_loop, daemon=True)
            self.ai_loop_thread.start()
        else:
            self.poll_thread = threading.Thread(target=self.poll_for_ai_move, daemon=True)
            self.poll_thread.start()

    def blue_ai_three_moves(self):
        # Blue AI plays 3 moves: horizontal mirror, vertical mirror, horizontal mirror of last human move
        if not hasattr(self, 'last_human_move') or self.last_human_move is None:
            # Fallback: just do 3 random moves if no human move is recorded
            for _ in range(3):
                if self.board.is_terminal():
                    self.show_winner()
                    return
                try:
                    move = blue_minimax_ai.choose_move(self.board, 'B')
                    if move is None:
                        print("Blue AI found no valid moves.")
                        return
                except Exception as e:
                    print(f"Blue AI error: {e} — using random move.")
                    move = random_ai(self.board, 'B')
                print(f"[AI] Blue AI playing at: {move}")
                self.board.apply_move('B', move)
                self.draw()
                if self.board.is_terminal():
                    self.show_winner()
                    return
            self.current_player = 'R'
            self.write_state("Human Move:")
            self.draw()
            return

        i, j = self.last_human_move
        moves = []
        # 1. Horizontal mirror
        moves.append((i, COLS - 1 - j))
        # 2. Vertical mirror
        moves.append((ROWS - 1 - i, j))
        # 3. Horizontal mirror again
        moves.append((i, COLS - 1 - j))

        for move in moves:
            if self.board.is_terminal():
                self.show_winner()
                return
            # Only play if legal
            legal = self.board.legal_moves('B')
            if move not in legal:
                # fallback to any legal move
                if legal:
                    move = legal[0]
                else:
                    print("Blue AI has no legal moves.")
                    return
            print(f"[AI] Blue AI playing at: {move}")
            self.board.apply_move('B', move)
            self.draw()
            if self.board.is_terminal():
                self.show_winner()
                return
        self.current_player = 'R'
        self.write_state("Human Move:")
        self.draw()

    def write_state(self, header):
        with open(GFILE, 'w') as f:
            f.write(f"{header}\n")
            f.write(str(self.board))

    def read_state(self):
        with open(GFILE, 'r') as f:
            lines = f.readlines()
        header = lines[0].strip()
        board_str = ''.join(lines[1:])
        self.board = Board.from_string(board_str)
        return header

    def on_click(self, event):
        if self.current_player != 'R':
            return  # wait for AI 

        j = event.x // CELL_WIDTH
        i = event.y // CELL_HEIGHT
        if not (0 <= i < ROWS and 0 <= j < COLS):
            return

        cell = self.board.grid[i][j]
        if cell.is_empty() or cell.color == 'R':
            self.board.apply_move('R', (i, j))
            self.last_human_move = (i, j)
            if self.board.is_terminal():
                self.draw()
                messagebox.showinfo("Game Over", "Red wins!")
                self.root.quit()
                return

            self.current_player = 'B'
            self.write_state("Human Move:")
            self.draw()
            # After human move, let Blue AI play 3 times
            self.root.after(200, self.blue_ai_three_moves)

    def draw(self):
        self.canvas.delete("all")
        radius = 10  

        for i in range(ROWS):
            for j in range(COLS):
                x0, y0 = j * CELL_WIDTH, i * CELL_HEIGHT
                x1, y1 = x0 + CELL_WIDTH, y0 + CELL_HEIGHT
                self.canvas.create_rectangle(x0, y0, x1, y1, outline="black")

                cell = self.board.grid[i][j]
                if cell.count > 0:
                    
                    color = 'red' if cell.color == 'R' else 'blue'  
                    
                    cx, cy = (x0 + x1) // 2, (y0 + y1) // 2

                    
                    if cell.count == 1:
                        self.canvas.create_oval(cx - radius, cy - radius, cx + radius, cy + radius, fill=color, outline="")
                    elif cell.count == 2:
                        self.canvas.create_oval(cx - radius - 8, cy - radius, cx + radius - 8, cy + radius, fill=color, outline="")
                        self.canvas.create_oval(cx - radius + 8, cy - radius, cx + radius + 8, cy + radius, fill=color, outline="")
                    elif cell.count == 3:
                        self.canvas.create_oval(cx - radius, cy - radius - 8, cx + radius, cy + radius - 8, fill=color, outline="")
                        self.canvas.create_oval(cx - radius - 8, cy - radius + 8, cx + radius - 8, cy + radius + 8, fill=color, outline="")
                        self.canvas.create_oval(cx - radius + 8, cy - radius + 8, cx + radius + 8, cy + radius + 8, fill=color, outline="")


    def show_winner(self):
        winner = self.board.winner()
        if winner == 'R':
            winner_str = "Red"
        elif winner == 'B':
            winner_str = "Blue"
        else:
            winner_str = "No one"

        messagebox.showinfo("Game Over", f"{winner_str} wins!")
        self.root.quit()

    def ai_play_red(self):
        if self.current_player != 'R':
            print("It's not Red's turn.")
            return

        try:
            # Let AI choose a move (you can use new_ai, random_ai, or red_minimax_ai)
            move = ai_agent.red_minimax_ai.choose_move(self.board, 'R')  # Or: ai_agent.new_ai(self.board, 'R')

            if move is None:
                print("Red AI found no valid moves.")
                return

            print(f"[Hint Button] Red AI playing at: {move}")
            self.board.apply_move('R', move)

            if self.board.is_terminal():
                self.draw()
                self.show_winner()
                return

            self.current_player = 'B'
            self.write_state("Human Move:")
            self.draw()

        except Exception as e:
            print("Error in Red AI button:", e)

    def ai_vs_ai_loop(self):
        start_time = time.time()
        move_count = 0

        while True:
            time.sleep(1)
            if self.board.is_terminal():
                break

            move = None
            move_start = time.time()

            try:
                if self.current_player == 'R':
                    move = red_minimax_ai.choose_move(self.board, 'R')
                else:
                    move = blue_minimax_ai.choose_move(self.board, 'B')

                if time.time() - move_start > 3 or move is None:
                    raise TimeoutError("Too slow or invalid")
            except Exception as e:
                print(f"{self.current_player} error: {e} — using random move.")
                move = random_ai(self.board, self.current_player)

            self.board.apply_move(self.current_player, move)
            move_count += 1
            self.current_player = 'B' if self.current_player == 'R' else 'R'

            self.write_state("AI Move:")
            self.draw()

        end_time = time.time()
        log_ai_vs_ai_stats(self.board.winner(), move_count, start_time, end_time)
        self.show_winner()


    def poll_for_ai_move(self):
        while True:
            time.sleep(1)
            try:
                header = self.read_state()

                if self.board.is_terminal():
                    self.draw()
                    self.show_winner()
                    return

                if header == "AI Move:":
                    self.current_player = 'R'
                    self.draw()

                elif header == "Human Move:" and self.current_player == 'B':
                    #  wait
                    continue

            except Exception as e:
                print("Error reading file:", e)



def log_ai_vs_ai_stats(winner, move_count, start_time, end_time):
    duration = round(end_time - start_time, 2)
    with open("ai_vs_ai_results.csv", "a", newline='') as file:
        writer = csv.writer(file)
        writer.writerow([winner, move_count, duration])


if __name__ == "__main__":
    if not os.path.exists("ai_vs_ai_results.csv"):
        with open("ai_vs_ai_results.csv", "w", newline='') as f:
            writer = csv.writer(f)
            writer.writerow(["Winner", "Move Count", "Duration (s)"])

    root = tk.Tk()
    game = GameUI(root, ai_vs_ai=False)
    root.mainloop()
