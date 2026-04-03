import tkinter as tk
from tkinter import messagebox, ttk
import openai
from PIL import Image, ImageTk
import random
import json
import re

# Set your OpenAI API key here (get free credits from openai.com)
openai.api_key = "YOUR_OPENAI_API_KEY_HERE"  # Replace with your key!

class TicTacToeGenAI:
    def __init__(self):
        self.root = tk.Tk()
        self.root.title("Tic Tac Toe with GenAI 🤖")
        self.root.geometry("500x700")
        self.root.configure(bg='#2c3e50')
        
        # Game state
        self.board = [''] * 9
        self.current_player = 'X'  # X = Human, O = AI
        self.game_active = True
        self.scores = {'X': 0, 'O': 0, 'Draw': 0}
        
        self.setup_ui()
        self.ai_move()  # AI starts first
        
    def setup_ui(self):
        # Title
        title = tk.Label(self.root, text="🎮 Tic Tac Toe with GenAI", 
                        font=('Arial', 24, 'bold'), fg='#ecf0f1', bg='#2c3e50')
        title.pack(pady=20)
        
        # Score frame
        score_frame = tk.Frame(self.root, bg='#2c3e50')
        score_frame.pack(pady=10)
        
        tk.Label(score_frame, text="Score:", font=('Arial', 12, 'bold'), 
                fg='#ecf0f1', bg='#2c3e50').pack(side=tk.LEFT)
        
        self.score_label = tk.Label(score_frame, text="X:0 | O:0 | Draw:0", 
                                   font=('Arial', 12), fg='#bdc3c7', bg='#2c3e50')
        self.score_label.pack(side=tk.LEFT, padx=20)
        
        # Game board frame
        board_frame = tk.Frame(self.root, bg='#2c3e50')
        board_frame.pack(pady=20)
        
        # Create 3x3 buttons
        self.buttons = []
        for i in range(3):
            row = []
            for j in range(3):
                btn = tk.Button(board_frame, width=5, height=3, font=('Arial', 24, 'bold'),
                               bg='#34495e', fg='#ecf0f1', activebackground='#3498db',
                               command=lambda idx=i*3+j: self.make_move(idx))
                btn.grid(row=i, column=j, padx=5, pady=5)
                row.append(btn)
            self.buttons.extend(row)
        
        # Control buttons
        ctrl_frame = tk.Frame(self.root, bg='#2c3e50')
        ctrl_frame.pack(pady=20)
        
        tk.Button(ctrl_frame, text="🔄 Reset Game", font=('Arial', 12),
                 bg='#e74c3c', fg='white', command=self.reset_game,
                 width=12, height=1).pack(side=tk.LEFT, padx=10)
        
        tk.Button(ctrl_frame, text="📊 AI Analysis", font=('Arial', 12),
                 bg='#9b59b6', fg='white', command=self.ai_analysis,
                 width=12, height=1).pack(side=tk.LEFT, padx=10)
        
        # Status label
        self.status_label = tk.Label(self.root, text="🤖 AI's turn (O)", 
                                   font=('Arial', 14, 'bold'), fg='#f39c12', bg='#2c3e50')
        self.status_label.pack(pady=10)
        
        # AI thinking label
        self.ai_thinking = tk.Label(self.root, text="", font=('Arial', 10),
                                   fg='#3498db', bg='#2c3e50')
        self.ai_thinking.pack()
    
    def make_move(self, position):
        if self.board[position] == '' and self.game_active and self.current_player == 'X':
            self.board[position] = 'X'
            self.buttons[position].config(text='X', state='disabled', bg='#27ae60')
            
            if self.check_winner('X'):
                self.end_game('X wins! 🎉')
                return
            elif '' not in self.board:
                self.end_game('Draw! 🤝')
                return
            
            self.current_player = 'O'
            self.status_label.config(text="🤖 AI is thinking...")
            self.root.update()
            self.ai_move()
    
    def ai_move(self):
        if not self.game_active:
            return
            
        self.ai_thinking.config(text="🧠 GenAI calculating best move...")
        self.root.update()
        
        # Get AI move using OpenAI GPT
        ai_position = self.get_genai_move()
        
        # Fallback to random if AI fails
        if ai_position is None:
            available = [i for i, spot in enumerate(self.board) if spot == '']
            ai_position = random.choice(available)
        
        self.board[ai_position] = 'O'
        self.buttons[ai_position].config(text='O', state='disabled', bg='#e67e22')
        
        self.ai_thinking.config(text="")
        
        if self.check_winner('O'):
            self.end_game('AI wins! 🤖')
            return
        elif '' not in self.board:
            self.end_game('Draw! 🤝')
            return
        
        self.current_player = 'X'
        self.status_label.config(text="✋ Your turn (X)")
    
    def get_genai_move(self):
        try:
            # Current board state as string
            board_str = ''.join(self.board)
            
            prompt = f"""
            You are a Tic Tac Toe expert. Analyze this board position and suggest the BEST move (0-8) for player O.
            
            Board (empty='', X=human, O=AI):
            {board_str}
            
            Positions:
            0 1 2
            3 4 5
            6 7 8
            
            Rules:
            - Return ONLY a number 0-8 for empty position
            - Choose winning move if possible
            - Otherwise block opponent's win
            - Otherwise take center (4), then corners (0,2,6,8), then sides
            
            Response format: ONLY the number (e.g., "4")
            """
            
            response = openai.ChatCompletion.create(
                model="gpt-3.5-turbo",
                messages=[{"role": "user", "content": prompt}],
                max_tokens=10,
                temperature=0.1
            )
            
            move_text = response.choices[0].message.content.strip()
            move = int(re.search(r'\d+', move_text).group())
            
            # Validate move
            if 0 <= move <= 8 and self.board[move] == '':
                return move
                
        except Exception as e:
            print(f"AI Error: {e}")
            return None
        
        return None
    
    def check_winner(self, player):
        win_conditions = [
            [0,1,2], [3,4,5], [6,7,8],  # Rows
            [0,3,6], [1,4,7], [2,5,8],  # Columns
            [0,4,8], [2,4,6]             # Diagonals
        ]
        
        for condition in win_conditions:
            if all(self.board[i] == player for i in condition):
                return True
        return False
    
    def end_game(self, message):
        self.game_active = False
        self.status_label.config(text=message)
        
        if "X wins" in message:
            self.scores['X'] += 1
        elif "AI wins" in message:
            self.scores['O'] += 1
        else:
            self.scores['Draw'] += 1
            
        self.update_score()
    
    def update_score(self):
        self.score_label.config(
            text=f"X:{self.scores['X']} | O:{self.scores['O']} | Draw:{self.scores['Draw']}"
        )
    
    def reset_game(self):
        self.board = [''] * 9
        self.current_player = 'X'
        self.game_active = True
        
        for btn in self.buttons:
            btn.config(text='', state='normal', bg='#34495e')
        
        self.status_label.config(text="✋ Your turn (X)")
        self.ai_thinking.config(text="")
    
    def ai_analysis(self):
        board_str = ' '.join(self.board)
        messagebox.showinfo("AI Analysis", 
                           f"Current board: {board_str}\n\n"
                           f"GenAI will always choose optimal moves!\n"
                           f"Score: X={self.scores['X']} | AI={self.scores['O']}")
    
    def run(self):
        self.root.mainloop()

# Run the game!
if __name__ == "__main__":
    # ⚠️ IMPORTANT: Get your FREE OpenAI API key from https://platform.openai.com/api-keys
    print("🚀 Starting Tic Tac Toe with GenAI!")
    print("📝 Get your OpenAI API key and replace 'YOUR_OPENAI_API_KEY_HERE'")
    game = TicTacToeGenAI()
    game.run()