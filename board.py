from __future__ import annotations
from enum import Enum
from copy import copy, deepcopy

name_map = "ABCDEFGH"

class Tile(Enum):
    NONE = 0
    WHITE = 1
    BLACK = 2

    def invert(self) -> Tile:
        return Tile.NONE if self == Tile.NONE else Tile.BLACK if self == self.WHITE else Tile.WHITE

class IllegalMoveException(Exception):
    ...

def tile_name_to_coord(name: str, board_size: int = 8) -> tuple[int, int]:
    # Quick and dirty validation
    if len(name) != 2:
        raise ValueError(f"Invalid tile name {name!r}.")
    
    # Split string into two
    l, n = name[0].upper(), name[1]
    
    if l not in name_map:
        raise ValueError(f"Invalid row {l!r}.")
    x = name_map.index(l)

    try:
        y = int(n) - 1
    except Exception:
        raise ValueError(f"{n} is not a valid column.")
    if not (0 <= y < board_size):
        raise ValueError(f"{y} is not a valid column (out of range.)")

    return x, y

class StaticBoard:

    def __init__(self, size: int = 8):
        self.size: int = size
        self.tiles: list[list[Tile]] = []

    def __deepcopy__(self):
        return self.__copy__()
    
    def __copy__(self):
        new = StaticBoard(self.size)
        new.tiles = deepcopy(self.tiles)
        return new
    
    @classmethod
    def reset(cls):
        board = cls()
        board.tiles = [[Tile.NONE] * board.size for _ in range(board.size)]
        h = board.size // 2
        board.tiles[h-1][h-1] = Tile.WHITE
        board.tiles[h][h] = Tile.WHITE
        board.tiles[h-1][h] = Tile.BLACK
        board.tiles[h][h-1] = Tile.BLACK

        return board
    
    @classmethod
    def from_data(cls, size, data):
        new = cls(size)
        new.tiles = deepcopy(data)
        return new
    
    def print(self):
        print(f" ABCDEFGH")
        for row in range(self.size):
            print(row+1,end='')
            for col in range(self.size):
                y = self.tiles[col][row]
                print("_" if y == Tile.NONE else "O" if y == Tile.WHITE else "X", end="")
            print("\n", end="")

    def update(self, tile: Tile, coord: tuple[int, int], bookends: list[list[tuple[int, int]]] = []) -> Board:
        new = copy(self)
        new[coord[0]][coord[1]] = tile
        for line in bookends:
            for flip in line:
                new[flip[0]][flip[1]] = tile
        return new
    
    def get_bookends(self, coord: tuple[int, int], tile: Tile) -> list[list[tuple[int, int]]]:
        if self.tiles[coord[0]][coord[1]] != Tile.NONE:
            return []

        lines = [[] for _ in range(self.size)]
        finished = [False] * self.size
        t_x, t_y = coord
        tiles = self.tiles
        op = tile.invert()
        size = self.size
        def bookend(i, x, y):
            if finished[i]:
                return
            
            if not (0 <= x < size and 0 <= y < size):
                lines[i] = []
                finished[i] = True
                return

            t = tiles[x][y]
            if t == op:
                lines[i].append((x, y))
            elif t == Tile.NONE:
                # DISCONNECTED
                lines[i] = []
                finished[i] = True
            else:
                # Bookended
                finished[i] = True

        for idx in range(1, self.size):
            bookend(0, t_x - idx, t_y)
            bookend(1, t_x + idx, t_y)
            bookend(2, t_x, t_y - idx)
            bookend(3, t_x, t_y + idx)
            bookend(4, t_x - idx, t_y - idx)
            bookend(5, t_x - idx, t_y + idx)
            bookend(6, t_x + idx, t_y - idx)
            bookend(7, t_x + idx, t_y + idx)
        return [l for l in lines if l]

    def get_available_moves(self, tile: Tile):
        open_tiles = ((col, row) for row in range(self.size) for col in range(self.size) if self.tiles[col][row] == Tile.NONE)
        bookends = ((coord, self.get_bookends(coord, tile)) for coord in open_tiles)
        return {c: b for c, b in bookends if b}

def evaluation(board: StaticBoard, tile: Tile):
    moves = board.get_available_moves(tile)
    if not moves:
        raise IllegalMoveException(f'{tile.name} cannot make a move')
    evaluations = {coord: sum(len(bookend) for bookend in move) for coord, move in moves.items()}
    best = max((e, c) for c, e in evaluations.items())[1]
    return best