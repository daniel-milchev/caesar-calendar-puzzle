# 🎲 Caesar's Calendar Game  

A digital twist on the legendary **Caesar's Calendar puzzle**!  
Fit funky-shaped blocks onto the board and reveal the correct **month, day, and weekday**.  
It's like Tetris met a calendar. 🤸  

---

## 🕹️ How to Play
1. Play daily.  
2. Use the puzzle pieces to cover all the other numbers.  
3. If you've arranged them right — your chosen date will shine through.  

Sounds easy? …Try it. 😏  

---

## ✨ Features
- 🧩 Classic tangram-style mechanics  
- 📅 Every date of the year can be solved  
- 🎨 Minimal but addictive gameplay
- 🤖 Auto-solve feature with DLX algorithm
- 🎨 Three beautiful themes (Nord, Wood, Solarized)

---

## 📁 Project Structure
```
caesar-calendar-puzzle/
├── src/                      # Source code
│   └── caldendar_puzzle.py   # Main game file
├── docs/                     # Documentation
│   ├── HELPER_FUNCTIONS.md   # Helper function documentation
│   └── REFACTORING_SUMMARY.md # Refactoring details
├── tests/                    # Test files
│   └── test_refactoring.py   # Verification tests
├── requirements.txt          # Python dependencies
└── README.md                 # This file
```

---

## 🚀 Getting Started

### Prerequisites
- Python 3.8+
- pygame

### Installation
1. Clone the repo:  
   ```bash
   git clone https://github.com/daniel-milchev/caesar-calendar-puzzle.git
   cd caesar-calendar-puzzle
   ```

2. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```

3. Run the game:  
   ```bash
   python src/caldendar_puzzle.py
   ```

### Running Tests
```bash
python tests/test_refactoring.py
```

---

## 🎮 Controls
- **Left Mouse**: Drag and place pieces
- **Right Mouse**: Reset individual piece to palette
- **R**: Rotate selected piece
- **F**: Flip selected piece
- **T**: Change theme
- **ESC**: Deselect piece / Exit win screen
- **←/→**: Browse auto-solve solutions

---

## 📖 A Bit of History
The **Caesar's Calendar** is a mechanical brain-teaser where wooden blocks can be placed on a grid to mark any date of the year.  
This project brings the puzzle to your screen — no lost pieces, no Roman emperors judging you… just pure puzzle vibes.  

---

## 📚 Documentation
- [Helper Functions](docs/HELPER_FUNCTIONS.md) - Detailed documentation of all helper functions
- [Refactoring Summary](docs/REFACTORING_SUMMARY.md) - Code refactoring details and improvements

---

## 🎯 Coming Soon (maybe)
- 🏆 High score / speedrun mode (with a slight possibility of multiplayer rank-list 🤫)
- 🎨 Custom themes (go full Colosseum or cyberpunk) 

---

⚡ *"Veni, Vidi, Vici."* …except you'll spend more time on this calendar than Caesar spent conquering Gaul.
