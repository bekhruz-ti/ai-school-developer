document.addEventListener('DOMContentLoaded', function() {
  const grid = document.getElementById('game');
  const rows = 10;
  const cols = 10;
  const minesCount = 20;
  let cells = [];

  function init() {
    grid.innerHTML = '';
    cells = [];
    for (let i = 0; i < rows * cols; i++) {
      const cell = document.createElement('div');
      cell.className = 'cell';
      cell.addEventListener('click', function() { revealCell(i); });
      cell.addEventListener('contextmenu', function(e) {
        e.preventDefault();
        toggleFlag(i);
      });
      grid.appendChild(cell);
      cells.push(cell);
    }
    placeMines();
  }

  function placeMines() {
    let minesPlaced = 0;
    while (minesPlaced < minesCount) {
      const index = Math.floor(Math.random() * rows * cols);
      const cell = cells[index];
      if (!cell.classList.contains('mine')) {
        cell.classList.add('mine');
        minesPlaced++;
      }
    }
  }

  function revealCell(index) {
    const cell = cells[index];
    if (cell.classList.contains('mine')) {
      alert('Game Over!');
      init();
    }
  }

  function toggleFlag(index) {
    const cell = cells[index];
    cell.classList.toggle('flagged');
  }

  init();
});document.addEventListener('DOMContentLoaded', function () {
    const grid = document.querySelector('.grid');
    let width = 10;
    let squares = [];
    let mineArray = [];

    function createBoard() {
        // Create array of mines
        mineArray = Array(20).fill('mine').concat(Array(80).fill('valid'));
        mineArray.sort(() => Math.random() - 0.5);

        for (let i = 0; i < width * width; i++) {
            const square = document.createElement('div');
            square.setAttribute('id', i);
            square.classList.add(mineArray[i]);
            grid.appendChild(square);
            squares.push(square);

            square.addEventListener('click', function(e) {
                click(square);
            });
        }
        console.log(mineArray)
    }

    function click(square) {
        if (square.classList.contains('mine')) {
            alert('Game Over! You hit a mine.');
        } else {
            let total = 0;
            const isLeftEdge = (square.id % width === 0);
            const isRightEdge = (square.id % width === width - 1);

            if (square.id > 0 && !isLeftEdge && squares[parseInt(square.id) - 1].classList.contains('mine')) total++;
            if (square.id < 99 && !isRightEdge && squares[parseInt(square.id) + 1].classList.contains('mine')) total++;
            if (square.id > 9 && squares[parseInt(square.id) - width].classList.contains('mine')) total++;
            if (square.id < 90 && squares[parseInt(square.id) + width].classList.contains('mine')) total++;

            if (total === 0) {
                setTimeout(() => {
                    const newIds = [square.id - 1, square.id + 1, square.id - width, square.id + width].filter(id => id >= 0 && id < 100);
                    newIds.forEach(newId => {
                        const newSquare = squares[newId];
                        if (!newSquare.classList.contains('clicked')) {
                            newSquare.classList.add('clicked');
                            click(newSquare);
                        }
                    });
                }, 10);
            }
            square.innerHTML = total;
            square.classList.add('clicked');
        }
    }

    createBoard();
});
document.addEventListener('DOMContentLoaded', function() {
  const grid = document.getElementById('game');
  const rows = 10;
  const cols = 10;
  const minesCount = 20;
  let cells = [];

  function init() {
    grid.innerHTML = '';
    cells = [];
    for (let i = 0; i < rows * cols; i++) {
      const cell = document.createElement('div');
      cell.className = 'cell';
      cell.addEventListener('click', function() { revealCell(i); });
      cell.addEventListener('contextmenu', function(e) {
        e.preventDefault();
        toggleFlag(i);
      });
      grid.appendChild(cell);
      cells.push(cell);
    }
    placeMines();
  }

  function placeMines() {
    let mineLocations = [];
    let minesPlaced = 0;
    while (minesPlaced < minesCount) {
      const index = Math.floor(Math.random() * rows * cols);
      const cell = cells[index];
      if (!cell.classList.contains('mine')) {
        cell.classList.add('mine');
        minesPlaced++;
        mineLocations.push(index);
      }
    }
    console.log('Mines are placed at indices:', mineLocations);
  }

  function revealCell(index) {
    const cell = cells[index];
    if (cell.classList.contains('mine')) {
      alert('Game Over!');
      init();
    } else {
      // Check for neighboring mines and reveal cells recursively
      let total = 0;
      const isLeftEdge = (index % cols === 0);
      const isRightEdge = (index % cols === cols - 1);

      if (index > 0 && !isLeftEdge && cells[index - 1].classList.contains('mine')) total++;
      if (index < (rows * cols - 1) && !isRightEdge && cells[index + 1].classList.contains('mine')) total++;
      if (index >= cols && cells[index - cols].classList.contains('mine')) total++;
      if (index < (rows * cols - cols) && cells[index + cols].classList.contains('mine')) total++;

      if (total === 0) {
        setTimeout(() => {
          const newIds = [index - 1, index + 1, index - cols, index + cols].filter(id => id >= 0 && id < rows * cols);
          newIds.forEach(newId => {
            const newCell = cells[newId];
            if (!newCell.classList.contains('clicked')) {
              newCell.classList.add('clicked');
              revealCell(newId);
            }
          });
        }, 10);
      }
      cell.innerHTML = total;
      cell.classList.add('clicked');
    }
  }

  function toggleFlag(index) {
    const cell = cells[index];
    cell.classList.toggle('flagged');
  }

  init();
});document.addEventListener('DOMContentLoaded', function() {
  const grid = document.getElementById('game');
  const rows = 10;
  const cols = 10;
  const minesCount = 20;
  let cells = [];

  function init() {
    grid.innerHTML = '';
    cells = [];
    for (let i = 0; i < rows * cols; i++) {
      const cell = document.createElement('div');
      cell.className = 'cell';
      cell.addEventListener('click', function() { revealCell(i); });
      cell.addEventListener('contextmenu', function(e) {
        e.preventDefault();
        toggleFlag(i);
      });
      grid.appendChild(cell);
      cells.push(cell);
    }
    placeMines();
  }

  function placeMines() {
    let minesPlaced = 0;
    while (minesPlaced < minesCount) {
      const index = Math.floor(Math.random() * rows * cols);
      const cell = cells[index];
      if (!cell.classList.contains('mine')) {
        cell.classList.add('mine');
        minesPlaced++;
      }
    }
  }

  function revealCell(index) {
    const cell = cells[index];
    if (cell.classList.contains('mine')) {
      alert('Game Over!');
      init();
    } else {
      // Check for neighboring mines and reveal cells recursively
      let total = 0;
      const isLeftEdge = (index % cols === 0);
      const isRightEdge = (index % cols === cols - 1);

      if (index > 0 && !isLeftEdge && cells[index - 1].classList.contains('mine')) total++;
      if (index < (rows * cols - 1) && !isRightEdge && cells[index + 1].classList.contains('mine')) total++;
      if (index >= cols && cells[index - cols].classList.contains('mine')) total++;
      if (index < (rows * cols - cols) && cells[index + cols].classList.contains('mine')) total++;

      if (total === 0) {
        setTimeout(() => {
          const newIds = [index - 1, index + 1, index - cols, index + cols].filter(id => id >= 0 && id < rows * cols);
          newIds.forEach(newId => {
            const newCell = cells[newId];
            if (!newCell.classList.contains('clicked')) {
              newCell.classList.add('clicked');
              revealCell(newId);
            }
          });
        }, 10);
      }
      cell.innerHTML = total;
      cell.classList.add('clicked');
    }
  }

  function toggleFlag(index) {
    const cell = cells[index];
    cell.classList.toggle('flagged');
  }

  init();
});

// Add a check to display a win message when all non-miner cells are uncovered
function checkWin() {
    let allSafeCellsUncovered = true;
    for (let i = 0; i < grid.length; i++) {
        for (let j = 0; j < grid[i].length; j++) {
            if (!grid[i][j].isMine && !grid[i][j].isRevealed) {
                allSafeCellsUncovered = false;
                break;
            }
        }
        if (!allSafeCellsUncovered) break;
    }

    if (allSafeCellsUncovered) {
        alert('Congratulations! You have won the game!');
    }
}

// Call checkWin function whenever a cell is revealed
function revealCell(x, y) {
    if (!grid[x][y].isRevealed && !grid[x][y].isFlagged) {
        grid[x][y].isRevealed = true;
        if (grid[x][y].isMine) {
            alert('Game Over!');
        } else {
            checkWin(); // Check if the player has won after this reveal
        }
    }
}
