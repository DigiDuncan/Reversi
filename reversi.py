from __future__ import annotations
from enum import Enum

from board import evaluation, StaticBoard, Tile, IllegalMoveException

name_map = "ABCDEFGH"


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

def coord_to_tile_name(coord) -> str:
    return f"{name_map[coord[0]]}{coord[1]+1}"

class Player:
    def __init__(self, color: Tile, score: int = 0) -> None:
        self.color = color
        self.score = score

class Board:
    def __init__(self, size: int = 8) -> None:
        self.size = size
        self.tiles: list[list[Tile]] = []
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
        self.tiles = [[Tile.NONE] * self.size for _ in range(self.size)]
        h = self.size // 2
        self.tiles[h-1][h-1] = Tile.WHITE
        self.tiles[h][h] = Tile.WHITE
        self.tiles[h-1][h] = Tile.BLACK
        self.tiles[h][h-1] = Tile.BLACK


    def get_bookends(self, coord: tuple[int, int]) -> list[list[tuple[int, int]]]:
        if self.tiles[coord[0]][coord[1]] != Tile.NONE:
            return []

        lines = [[] for _ in range(self.size)]
        finished = [False] * self.size
        t_x, t_y = coord
        tiles = self.tiles
        tile = self.current_turn
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

        for idx in range(1, self.size+1):
            bookend(0, t_x - idx, t_y)
            bookend(1, t_x + idx, t_y)
            bookend(2, t_x, t_y - idx)
            bookend(3, t_x, t_y + idx)
            bookend(4, t_x - idx, t_y - idx)
            bookend(5, t_x - idx, t_y + idx)
            bookend(6, t_x + idx, t_y - idx)
            bookend(7, t_x + idx, t_y + idx)
        return [l for l in lines if l]
                
    def is_move_legal(self, coord: tuple[int, int]) -> bool:
        return not not self.get_bookends(coord)

    def do_move(self, coord: tuple[int, int]):
        lines = self.get_bookends(coord)
        if not lines:
            raise IllegalMoveException(f"Move {coord} illegal for player {self.current_turn.name}.")
        
        for line in lines:
            for tile in line:
                self.tiles[tile[0]][tile[1]] = self.current_turn
        self.tiles[coord[0]][coord[1]] = self.current_turn

        self.current_turn = self.current_turn.invert()

    @property
    def game_over(self) -> bool:
        for i in range(self.size):
            for j in range(self.size):
                if self.is_move_legal((i, j)):
                    return False
        return True

    def print(self):
        print(f" {name_map}")
        for row in range(self.size):
            print(row+1,end='')
            for col in range(self.size):
                y = self.tiles[col][row]
                print("_" if y == Tile.NONE else "O" if y == Tile.WHITE else "X", end="")
            print("\n", end="")

def interface(ai: Tile = Tile.BLACK):
    game = Board(8)
    while not game.game_over:
        game.print()
        legal = False
        while not legal:
            if game.current_turn == ai or True:
                coord = evaluation(StaticBoard.from_data(game.size, game.tiles), game.current_turn)
                move = coord_to_tile_name(coord)
                print(f'AI <{game.current_turn.name}>, making a move: {move}')
            else:
                move = input(f"Player <{game.current_turn.name}>, make a move: ")
                try:
                    coord = tile_name_to_coord(move)
                except ValueError:
                    print(f"{move} is not a valid move.")
                    continue
            try:
                legal = game.is_move_legal(coord)
                if not legal:
                    print(f"{move} is not a legal move.")
            except ValueError as e:
                print(e.args[0])
                continue
        game.do_move(coord)
    print(f"Game over! W:{game.get_player_score(Tile.WHITE)} B:{game.get_player_score(Tile.BLACK)}")

def main():
    interface()

if __name__ == "__main__":
    main()