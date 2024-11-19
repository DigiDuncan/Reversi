from __future__ import annotations
from enum import Enum

name_map = "ABCDEFGH"

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
    y = name_map.index(l)

    try:
        x = int(n) - 1
    except Exception:
        raise ValueError(f"{n} is not a valid column.")
    if 0 > x > board_size - 1:
        raise ValueError(f"{x} is not a valid column (out of range.)")

    return x, y

class Tile(Enum):
    NONE = 0
    WHITE = 1
    BLACK = 2

    def invert(self) -> Tile:
        return Tile.NONE if self.name == "NONE" else Tile.BLACK if self.name == "WHITE" else Tile.BLACK

class Player:
    def __init__(self, color: Tile, score: int = 0) -> None:
        self.color = color
        self.score = score

class Board:
    def __init__(self, size: int = 8) -> None:
        self.size = size
        self.tiles: list[list[Tile]] = [[]]
        self.current_turn = Tile.WHITE

        self.reset()

    def get_player_score(self, color: Tile) -> int:
        s = 0
        for c in self.tiles:
            for r in c:
                if r == color:
                    s += 1
        return s

    def get_tile_by_name(self, name: str) -> Tile:
        x, y = tile_name_to_coord(name)
        return self.tiles[y][x]

    def set_tile_by_name(self, name: str, value: Tile):
        x, y = tile_name_to_coord(name)
        self.tiles[y][x] = value

    def reset(self):
        self.tiles = [[Tile.NONE * self.size] * self.size]
        h = self.size // 2
        self.tiles[h-1][h-1] = Tile.WHITE
        self.tiles[h][h] = Tile.WHITE
        self.tiles[h-1][h] = Tile.BLACK
        self.tiles[h][h-1] = Tile.BLACK

    def is_move_legal(self, tile_name: str) -> bool:
        # Check a 3x3 around the player
        tile_x, tile_y = tile_name_to_coord(tile_name)
        for cy in range(tile_y - 1, tile_y + 2):
            for cx in range(tile_x - 1, tile_x + 2):
                if 0 >= cy > self.size and 0 >= cx > self.size:  # Ignore OOB
                    if self.tiles[cy][cx] == self.current_turn.invert():
                        # Technically this checks our current tile too but it'll never be True so who cards
                        return True
        return False

    def do_move(self, tile_name: str):
        if not self.is_move_legal(self, self.current_turn, tile_name):
            raise IllegalMoveException(f"Move {tile_name} illegal for player {self.current_turn.name}.")
        # ARC :hepme:
        # Do the move
        self.current_turn = self.current_turn.invert()

    @property
    def game_over(self) -> bool:
        # check if all empty tiles have a legal possible move
        return False

    def print(self):
        for y in self.tiles:
            for x in y:
                print("_" if x == Tile.NONE else "O" if x == Tile.WHITE else "X", end="")
            print("\n", end="")

def interface():
    game = Board(8)
    while not game.game_over:
        game.print()
        legal = False
        while not legal:
            move = input(f"Player {game.current_turn}, make a move: ")
            try:
                legal = game.is_move_legal(move)
            except ValueError as e:
                print(e.args[0])
                continue
        game.do_move(move)
    print(f"Game over! W:{game.get_player_score(Tile.WHITE)} B:{game.get_player_score(Tile.BLACK)}")

def main():
    interface()

if __name__ == "__main__":
    main()