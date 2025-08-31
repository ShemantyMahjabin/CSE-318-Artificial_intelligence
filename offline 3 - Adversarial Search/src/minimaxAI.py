import math
from game_engine import Board


class MinimaxAI:
    def __init__(self,max_depth=4,eval_fn=None):
        self.max_depth=max_depth
        self.eval_fn= eval_fn if eval_fn is not None else self.default_evaluation
    def choose_move(self, board:Board,player: str): #returns best move
        _,move=self._minimax(board,self.max_depth,-math.inf,math.inf,True,player)
        if not move:
            print(f" No legal moves for player {player}")
        
        return move   
    def _minimax(self,board,depth,alpha,beta,maximizing,player):
        opponent = 'B' if player == 'R' else 'R'
        if depth == 0 or board.is_terminal():
            return self.eval_fn(board,player),None
        legal_moves = board.legal_moves(player if maximizing else opponent)
        best_move = None
        if maximizing:
            max_eval = -math.inf
            for move in legal_moves:
                new_board = board.clone()
                new_board.apply_move(player,move)
                eval_score, _ =self._minimax(new_board,depth-1,alpha,beta,False,player)
                if eval_score > max_eval:
                    max_eval = eval_score
                    best_move = move
                alpha = max(alpha,eval_score)
                if beta <= alpha:
                    break
            return max_eval, best_move
        else:
            min_eval = math.inf
            for move in legal_moves:
                new_board = board.clone()
                new_board.apply_move(opponent, move)
                eval_score, _ = self._minimax(new_board, depth - 1, alpha, beta, True, player)
                if eval_score < min_eval:
                    min_eval = eval_score
                    best_move = move
                beta = min(beta, eval_score)
                if beta <= alpha:
                    break
            return min_eval, best_move
    def default_evaluation(self,board,player):  ##heuristic: Difference in total orb counts
        opponent = 'B' if player == 'R' else 'R'
        my_count = 0
        opp_count = 0
        for row in board.grid:
            for cell in row:
                if cell.color == player:
                    my_count += cell.count 
                elif cell.color == opponent:
                    opp_count +=cell.count
        return my_count - opp_count
    
    