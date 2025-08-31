import time
from game_engine import Board
from ai_agent import blue_minimax_ai, random_ai,new_ai

AI_COLOR = 'B'
GFILE = 'gamestate.txt'

def read_state():
    with open(GFILE, 'r') as f:
        lines = f.readlines()
    current = lines[0].strip()
    board_str = ''.join(lines[1:])
    return current, Board.from_string(board_str)

def write_state(board, header):
    with open(GFILE, 'w') as f:
        f.write(f"{header}\n")  # Must be "AI Move:" or "Human Move:"
        f.write(str(board))

def run_ai():
    while True:
        time.sleep(1)

        try:
            current, board = read_state()

            if board.is_terminal():
                print("Game Over. Exiting AI.")
                return

            if current != "Human Move:":
                continue  # Wait until human has moved

            print("AI (B) thinking...")
            move_start = time.time()
            try:
                #move = blue_minimax_ai.choose_move(board, AI_COLOR)
                move=new_ai(board,AI_COLOR)
                if time.time() - move_start > 3 or move is None:
                    raise TimeoutError("Too slow or invalid")
            except Exception as e:
                print("Blue AI error:", e)
                move = random_ai(board, AI_COLOR)

            board.apply_move(AI_COLOR, move)

            if board.is_terminal():
                print("AI played winning move.")
                write_state(board, "AI Move:")  # Final board update
                return

            write_state(board, "AI Move:")
            print("AI (B) played. Turn passed to Red.")

        except Exception as e:
            print("Error in AI:", e)

if __name__ == "__main__":
    run_ai()
