🧩 Queens Puzzle Game (Pygame)

A logic puzzle game built in Python using Pygame, where you place Queens on the board under specific rules.
The game automatically checks for a valid solution, tracks your time, and allows you to generate new puzzles dynamically.

📖 Game Rules

You must place exactly one Queen in every row, column, and region.

Click or drag to fill cells with X marks (your helper notes).

When you’re confident about a spot, click again to turn an X into a Queen.

The game automatically checks if your solution is correct:

✅ If you’ve placed all Queens correctly → you win! 🎉

⏱️ Your completion time is displayed.

🎮 Features

Dynamic grid size – choose the size of the board when starting the game (e.g. 7x7, 8x8).

Interactive controls:

Left click → Empty → X → Queen cycle

Hold + drag (left mouse) → Fill empty cells with Xs

Right click + drag → Clear Xs only

New puzzles – Press N to generate a brand-new puzzle board with one solution (animated).

Timer – A timer at the bottom of the screen tracks how long you’ve been solving. Resets on new boards.

Auto-win detection – No need for a “Check” button, the game verifies instantly when you’ve solved the puzzle.

🖼️ Screenshots
![Game window example](window%20example.png)

⌨️ Controls
Action	Mouse/Keyboard
Place/Change cell	Left click
Drag to add Xs	Hold + drag (LMB)
Remove Xs	Hold + drag (RMB)
New puzzle	N key
Quit	ESC or close window