from __future__ import annotations

from board import Board, Tile
from ai import OrthelloAI, MASTER

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

def play(white_ai: OrthelloAI = None, black_ai: OrthelloAI = None, size: int = 8):
    board = Board(size)
    turn = Tile.WHITE
    while not board.is_game_over(turn):
        board.print()
        if turn == Tile.WHITE and white_ai is not None:
            coord, bookends = white_ai.pick_move(board, turn)
            move = coord_to_tile_name(coord)
            print(f'White Ai picks {move}')
        elif turn == Tile.BLACK and black_ai is not None:
            coord, bookends = black_ai.pick_move(board, turn)
            move = coord_to_tile_name(coord)
            print(f'Black Ai picks {move}')
        else:
            move = input(f"{turn.name} Player, pick a move: ")
            try:
                coord = tile_name_to_coord(move)
            except ValueError:
                print(f"{move} is not a valid move.")
                continue
            bookends = board.get_bookends(coord, turn)
        
        if not bookends:
            print(f'{move} is not a valid move.')
            continue
        
        board = board.update(turn, coord, bookends)
        turn = turn.invert()
    board.print()
    w, b = board.get_counts()
    print(f"Game over! W:{w} B:{b}")


def main():
    play(None, MASTER)

if __name__ == "__main__":
    main()