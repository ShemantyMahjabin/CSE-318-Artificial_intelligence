#heuristic: Difference in total orb counts
def count_difference(board, player):
    opponent = 'B' if player == 'R' else 'R'
    my_count = 0
    opp_count = 0
    for row in board.grid:
        for cell in row:
            if cell.color == player:
                my_count += cell.count
            elif cell.color == opponent:
                opp_count += cell.count
    return my_count - opp_count

#Heuristic: Evaluate potential to convert opponent cells nearby explosion zones
def conversion_potential(board, player):
    opponent = 'B' if player == 'R' else 'R'
    score = 0

    for i in range(len(board.grid)):
        for j in range(len(board.grid[0])):
            cell = board.grid[i][j]
            crit = board.critical_mass(i, j)

            if cell.color == player and cell.count == crit - 1:
                # neighbors check korbo opponent's cells pai kina
                for di, dj in [(-1, 0), (1, 0), (0, -1), (0, 1)]:
                    ni, nj = i + di, j + dj
                    if board.in_bounds(ni, nj):
                        neighbor = board.grid[ni][nj]
                        if neighbor.color == opponent:
                            score += neighbor.count  
            elif cell.color == opponent and cell.count == crit - 1:
                for di, dj in [(-1, 0), (1, 0), (0, -1), (0, 1)]:
                    ni, nj = i + di, j + dj
                    if board.in_bounds(ni, nj):
                        neighbor = board.grid[ni][nj]
                        if neighbor.color == player:
                            score -= neighbor.count  
    return score

#Heuristic: Give more value to corner and edge cells (harder to explode)
def strategic_position(board, player):
    opponent = 'B' if player == 'R' else 'R'
    score = 0
    for i in range(len(board.grid)):
        for j in range(len(board.grid[0])):
            cell = board.grid[i][j]
            if (i == 0 or i == 8) and (j == 0 or j == 5):  # corners
                weight = 3
            elif (i == 0 or i == 8) or (j == 0 or j == 5):  # edges
                weight = 2
            else:  # inner
                weight = 1
            if cell.color == player:
                score += weight * cell.count
            elif cell.color == opponent:
                score -= weight * cell.count
    return score


#Heuristic: Favors near-explosion cells for AI, penalizes for opponent.
def potential_chain_reactions(board, player):
    opponent = 'B' if player == 'R' else 'R'
    score = 0
    for i in range(len(board.grid)):
        for j in range(len(board.grid[0])):
            cell = board.grid[i][j]
            crit = board.critical_mass(i, j)
            if cell.color == player:
                score += (cell.count / crit)
            elif cell.color == opponent:
                score -= (cell.count / crit)
    return score

#Heuristic: Count how many safe (legal) moves the player can make
def mobility(board, player):
    safe_moves = 0
    for i in range(len(board.grid)):
        for j in range(len(board.grid[0])):
            cell = board.grid[i][j]
            if cell.is_empty() or cell.color == player:
                safe_moves += 1
    return safe_moves



