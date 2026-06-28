import tkinter as tk
import random
import sqlite3
from tkinter import simpledialog, messagebox

DB_FILE = "leaderboard.db"

class RockPaperScissorsUI:
    def __init__(self, root):
        self.root = root
        self.root.title("Rock-Paper-Scissors")
        self.conn = sqlite3.connect(DB_FILE)
        self.create_table()
        self.setup_game()

    def create_table(self):
        cursor = self.conn.cursor()
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS leaderboard (
                id INTEGER PRIMARY KEY,
                player_name TEXT NOT NULL,
                wins INTEGER DEFAULT 0,
                losses INTEGER DEFAULT 0,
                ties INTEGER DEFAULT 0
            )
        """)
        self.conn.commit()

    def setup_game(self):
        # Ask for player name, rounds, difficulty
        self.player_name = simpledialog.askstring("Player", "Enter your name:")
        self.total_rounds = simpledialog.askinteger("Rounds", "Enter number of rounds (Best of N):", minvalue=1)
        self.current_round = 0
        self.difficulty = simpledialog.askstring("Difficulty", "Choose difficulty (easy, normal, hard):").lower()

        self.player_wins = 0
        self.computer_wins = 0
        self.ties = 0

        # Clear window before setting up new game
        for widget in self.root.winfo_children():
            widget.destroy()

        self.result_label = tk.Label(self.root, text="Choose your move!", font=("Arial", 14))
        self.result_label.pack(pady=20)

        self.score_label = tk.Label(self.root, text="Player: 0 | Computer: 0 | Ties: 0", font=("Arial", 12))
        self.score_label.pack()

        button_frame = tk.Frame(self.root)
        button_frame.pack(pady=20)

        tk.Button(button_frame, text="Rock", width=10, command=lambda: self.play("rock")).grid(row=0, column=0, padx=5)
        tk.Button(button_frame, text="Paper", width=10, command=lambda: self.play("paper")).grid(row=0, column=1, padx=5)
        tk.Button(button_frame, text="Scissors", width=10, command=lambda: self.play("scissors")).grid(row=0, column=2, padx=5)

        # Play Again button (hidden until game ends)
        self.play_again_button = tk.Button(self.root, text="Play Again", width=15, command=self.setup_game)
        self.play_again_button.pack(pady=10)
        self.play_again_button.pack_forget()

        # Leaderboard button
        self.leaderboard_button = tk.Button(self.root, text="View Leaderboard", width=15, command=self.show_leaderboard)
        self.leaderboard_button.pack(pady=5)

    def computer_move(self, player_move):
        moves = ["rock", "paper", "scissors"]
        if self.difficulty == "easy":
            if player_move == "rock": return random.choice(["scissors", "scissors", "paper"])
            elif player_move == "paper": return random.choice(["rock", "rock", "scissors"])
            else: return random.choice(["paper", "paper", "rock"])
        elif self.difficulty == "hard":
            if player_move == "rock": return random.choice(["paper", "paper", "scissors"])
            elif player_move == "paper": return random.choice(["scissors", "scissors", "rock"])
            else: return random.choice(["rock", "rock", "paper"])
        else:
            return random.choice(moves)

    def play(self, player_move):
        if self.current_round >= self.total_rounds:
            return

        comp_move = self.computer_move(player_move)

        if player_move == comp_move:
            result = f"Computer chose {comp_move}. It's a tie!"
            self.ties += 1
        elif (player_move == "rock" and comp_move == "scissors") or \
             (player_move == "scissors" and comp_move == "paper") or \
             (player_move == "paper" and comp_move == "rock"):
            result = f"Computer chose {comp_move}. You win!"
            self.player_wins += 1
        else:
            result = f"Computer chose {comp_move}. Computer wins!"
            self.computer_wins += 1

        self.current_round += 1
        self.result_label.config(text=f"Round {self.current_round}/{self.total_rounds}: {result}")
        self.score_label.config(text=f"Player: {self.player_wins} | Computer: {self.computer_wins} | Ties: {self.ties}")

        if self.current_round == self.total_rounds:
            if self.player_wins > self.computer_wins:
                winner = "🎉 You won the match!"
            elif self.computer_wins > self.player_wins:
                winner = "💻 Computer wins the match!"
            else:
                winner = "🤝 It's a tie overall!"

            # Save to SQL leaderboard
            cursor = self.conn.cursor()
            cursor.execute("INSERT INTO leaderboard (player_name, wins, losses, ties) VALUES (?, ?, ?, ?)",
                           (self.player_name, self.player_wins, self.computer_wins, self.ties))
            self.conn.commit()

            messagebox.showinfo("Final Result", winner)
            self.play_again_button.pack()

    def show_leaderboard(self):
        cursor = self.conn.cursor()
        cursor.execute("SELECT player_name, wins, losses, ties FROM leaderboard ORDER BY wins DESC LIMIT 10")
        rows = cursor.fetchall()

        leaderboard_text = "🏆 Leaderboard (Top 10)\n\n"
        for row in rows:
            leaderboard_text += f"{row[0]} - Wins: {row[1]}, Losses: {row[2]}, Ties: {row[3]}\n"

        messagebox.showinfo("Leaderboard", leaderboard_text)

if __name__ == "__main__":
    root = tk.Tk()
    app = RockPaperScissorsUI(root)
    root.mainloop()
