from minimaxAI import MinimaxAI
from heuristics import count_difference,conversion_potential,strategic_position,potential_chain_reactions,mobility
import random


red_minimax_ai = MinimaxAI(max_depth=2, eval_fn=strategic_position)
blue_minimax_ai = MinimaxAI(max_depth=2, eval_fn=potential_chain_reactions)


def random_ai(board, player):
    moves = board.legal_moves(player)
    return random.choice(moves) if moves else None


def minimax_ai(board, player, depth=3, heuristic=count_difference):
    agent = MinimaxAI(max_depth=depth, eval_fn=heuristic)
    return agent.choose_move(board, player)

def new_ai(board,player):
    move=board.diagonal_move(player)
    print(f"[new_ai] Diagonal move chosen: {move}")
    return move
        

