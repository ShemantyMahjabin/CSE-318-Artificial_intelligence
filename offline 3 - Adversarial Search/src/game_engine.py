import copy

ROWS = 9
COLS = 6

class Cell:
    def __init__(self,count=0,color=None,last_row=0,last_col=0):
        self.count = count #orbs
        self.color=color #R/B
        self.last_row=last_row
        self.last_col=last_col
    def is_empty(self):
        return self.count == 0
    def clone(self): #board copy
        return Cell(self.count,self.color)
    
class Board:
    def __init__(self,last_row=0,last_col=0,start=0):
        self.grid = [[Cell() for _ in range(COLS)] for _ in range(ROWS)]
        self.last_row=last_row
        self.last_col=last_col
        self.start=0

    def critical_mass(self,i,j):
        if(i==0 or i==ROWS-1) and (j==0 or j==COLS-1):
            return 2
        elif i==0 or i==ROWS-1 or j==0 or j==COLS-1:
            return 3
        return 4
    
    def in_bounds(self,i,j):
        return 0<=i<ROWS and 0<=j<COLS
    
    def legal_moves(self,player):
        moves=[]
        for i in range(ROWS):
            for j in range(COLS):
                cell = self.grid[i][j]
                if cell.is_empty() or cell.color == player:
                    moves.append((i,j))
                # Limit to first 10 moves for performance(report generation r jonne)
                # if len(moves) >= 10:
                #     return moves
        return moves
    def diagonal_move(self, player):
        # Improved diagonal move logic: moves from (0,0) to (5,5) diagonally, wraps, and always returns a legal move
        if self.start == 0:
            self.last_row = 0
            self.last_col = 0
            self.start = 1
            if self.grid[0][0].is_empty() or self.grid[0][0].color == player:
                return (0, 0)

        for _ in range(ROWS * COLS):
            cell = self.grid[self.last_row][self.last_col]
            if cell.is_empty() or cell.color == player:
                move = (self.last_row, self.last_col)
                # Advance diagonally down-right, wrap if needed
                if self.last_row < ROWS - 1 and self.last_col < COLS - 1:
                    self.last_row += 1
                    self.last_col += 1
                else:
                    self.last_row = 0
                    self.last_col = 0
                return move
            # If not legal, advance diagonally down-right, wrap if needed
            if self.last_row < ROWS - 1 and self.last_col < COLS - 1:
                self.last_row += 1
                self.last_col += 1
            else:
                self.last_row = 0
                self.last_col = 0

        # Fallback: return any legal move
        legal_moves = self.legal_moves(player)
        if legal_moves:
            self.last_row, self.last_col = legal_moves[0]
            return legal_moves[0]
        return None
        
    
    def apply_move(self,player,move):
        i,j=move
        if not self.in_bounds(i,j):
            return
        cell = self.grid[i][j]
        if cell.is_empty():
            cell.color=player
        cell.count += 1
        if self.is_terminal():
            return  
        self._explode(player)
    
    def _explode(self, current_player, max_iterations=150):
        changed = True
        iteration = 0
        
        while changed and iteration < max_iterations:
            changed = False
            iteration += 1
            to_explode = []
            
            for i in range(ROWS):
                for j in range(COLS):
                    if self.grid[i][j].count >= self.critical_mass(i,j):
                        to_explode.append((i,j))
            
            if to_explode:
                changed = True
                for i,j in to_explode:
                    self._trigger_explosion(i,j,current_player)
            
            
            if iteration >= max_iterations and changed:
                print(f" Explosion chain reached maximum iterations ({max_iterations})")
                break
    
    def _trigger_explosion(self,i,j,current_player):
        count_to_distribute = self.critical_mass(i,j)
        self.grid[i][j].count-=count_to_distribute #otogula orbs exploding cell theke minus
        if self.grid[i][j].count == 0:
            self.grid[i][j].color = None #exploding cell empty hole color clear
        for dx,dy in [(-1,0),(1,0),(0,-1),(0,1)]: #4 ta orthogonal direction 
            ni,nj = i + dx,j + dy #neighbor coordinate
            if self.in_bounds(ni,nj):
                neighbor = self.grid[ni][nj]
                if(neighbor.is_empty()):
                    neighbor.color = current_player
                elif neighbor.color != current_player:
                    neighbor.color = current_player #When a red cell explodes and there are blue cells around, the blue cells are converted to red
                neighbor.count += 1 #add an orb to neighbor
    
    def clone(self):#board copy
        new_board = Board()
        for i in range(ROWS):
            for j in range(COLS):
                new_board.grid[i][j] = self.grid[i][j].clone()
        return new_board
    
    def is_terminal(self):
        red_count, blue_count = 0, 0
        total_orbs = 0
        for row in self.grid:
            for cell in row:
                if cell.color == 'R':
                    red_count += cell.count
                elif cell.color == 'B':
                    blue_count += cell.count
                total_orbs += cell.count
        #jeno 1 jon 1st move dile na vabe game sesh 
        if total_orbs <= 1:
            return False
        if (red_count == 0 and blue_count > 1) or (blue_count == 0 and red_count > 1): #jeno 0 move e na vabe game sesh
            return True
        return False

    def winner(self):
        if not self.is_terminal():
            return None
        red_count,blue_count = 0,0
        for row in self.grid:
            for cell in row:
                if cell.color == 'R':
                    red_count += cell.count
                elif cell.color == 'B':
                    blue_count += cell.count
        if red_count > 0:
            return 'R'
        elif blue_count > 0:
            return 'B'
        return None
    
    def __str__(self):
        lines = []
        for row in self.grid:
            line = []
            for cell in row:
                if cell.count == 0:
                    line.append('0')
                else:
                    line.append(f"{cell.count}{cell.color}")
            lines.append(" ".join(line))
        return "\n".join(lines)
    
    @staticmethod
    def from_string(s):
        board = Board()
        rows = s.strip().split('\n')
        for i, line in enumerate(rows):
            cells = line.strip().split()
            for j, val in enumerate(cells):
                if val == '0':
                    board.grid[i][j] = Cell()
                else:
                    count = int(val[0])
                    color = val[1]
                    board.grid[i][j] = Cell(count, color)
        return board