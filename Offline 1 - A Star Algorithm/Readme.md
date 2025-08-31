# CSE-318: Artificial Intelligence – Offline 1  
## N-Puzzle Solver using A* Search (C++)

### 📌 Project Overview
This project implements an **N-Puzzle Solver** using the **A\*** search algorithm.  
The N-Puzzle (e.g., 8-puzzle, 15-puzzle) is a sliding tile puzzle where the objective is to arrange the tiles in order by making the least number of moves.  

The solver can handle arbitrary board sizes (k × k) and supports multiple heuristic functions.

---

### 🎯 Objectives
- Implement the A\* algorithm for solving the N-Puzzle:contentReference[oaicite:0]{index=0}.
- Allow switching between different heuristics:
  - Hamming Distance
  - Manhattan Distance
  - Euclidean Distance
  - Linear Conflict
- Detect unsolvable puzzles based on inversion count and blank position.
- Output:
  - Minimum number of moves (optimal solution).
  - Step-by-step board configurations from start to goal.
  - Number of nodes explored and expanded.

---

### 🛠️ Technologies Used
- **Language:** C++ 
- **Data Structures:** Priority Queue (min-heap)
- **Algorithm:** A\* Search with multiple heuristics



