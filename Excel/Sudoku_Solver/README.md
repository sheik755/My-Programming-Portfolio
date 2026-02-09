# 🧠 Logic-Based Sudoku Solver (Excel VBA)
A Sudoku solver that thinks like a human. Built entirely in Excel VBA.
Unlike standard solvers that use "Backtracking" (brute-force guessing), this tool attempts to solve puzzles using **logical deduction and heuristic strategies**—mimicking the way a real person plays.

## 🚀 Features
- **🚫 No Brute Force**: Does not rely on random guessing.
- **🧠 Human Logic**: Implements real-world solving techniques.
- **⚡ Instant Feedback**: Fills in cells as the logic confirms them.
- **📊 Excel Interface**: Easy-to-use grid input.

## ⚙️ Algorithms Implemented
This solver iteratively applies the following rules until the puzzle is solved or no further logical moves are possible:
1.  **Naked Singles**: Identifying cells where only one number is mathematically possible.
2.  **Hidden Singles**: Finding numbers that can only fit in one specific cell within a Row, Column, or 3x3 Block.
3.  **Candidate Checking**: Find all the possiblities on each cell and deduce logically if we have just one candidate and repeat the steps.
4.  **Doubles**: Finding pairs that fit in 2 cells within a box and remove those possibilities from other cells to get singles and repeat steps.

## 🛠️ How to Use
1.  Open `Sudoku.xlsm`.
2.  Type your puzzle into the grid.
3.  Click **Solve**.
4.  Watch it deduce the numbers within seconds!

## Available files
- README.md - this file
- Sudoku Solver Steps - Showing fews steps to solver the sudoku
- The original .xlsm file (with all the VB codes) is available upon request
- ![Demo](./sudoku_show.gif)
