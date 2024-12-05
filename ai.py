from random import choices, random

from board import StaticBoard, Tile, IllegalMoveException

type WeightTable = tuple[tuple[float, ...], ...]

class PlayerAI:

    def __init__(self, pickyness: float, chaos: float, depth: int, weights: WeightTable):
        self.pickyness: float = pickyness
        self.chaos: float = chaos
        self.depth: int = depth
        self.weights: WeightTable = weights

    def search(self, board: StaticBoard, tile: Tile, depth: int = 0):
        if depth == self.depth:
            return self.evaulate()

        

    def evaluate(self, board: StaticBoard, tile: Tile, depth: int = 0) -> tuple[tuple[int, int], float]:
        def score_bookend(coord, bookend):
            score = self.weights[coord[0]][coord[1]]
            for line in bookend:
                for spot in line:
                    score += self.weights[spot[0]][spot[1]]
            return score
    
        moves = board.get_available_moves(tile)    
        evaluations = ((coord, score_bookend(coord, move)) for coord, move in moves.items())
        ranked = sorted(evaluations, key=lambda e: e[1], reverse=True)
        if self.chaos < random():
            return ranked[0][0] 

        allowed = max(1, int(len(ranked) * self.pickyness))
        coords, weights = zip(*ranked[:allowed])
        choice = choices(coords, weights)[0]
        return choice

def evaluation(board: StaticBoard, tile: Tile):
    moves = board.get_available_moves(tile)
    if not moves:
        raise IllegalMoveException(f'{tile.name} cannot make a move')
    evaluations = ((coord, sum(len(bookend) for bookend in move)) for coord, move in moves.items())
    coords, weights = zip(*evaluations)
    best = choices(tuple(coords), weights=tuple(weights))[0]
    return best

peak = (
    (10000, -3000, 1000, 800, 800, 1000, -3000, 10000),
    (-3000, -5000, -450, -500, -500, -450, -5000, -3000),
    (1000, -450, 30, 10, 10, 30, -450, 1000),
    (800, -500, 10, 50, 50, 10, -500, 800),
    (800, -500, 10, 50, 50, 10, -500, 800),
    (1000, -450, 30, 10, 10, 30, -450, 1000),
    (-3000, -5000, -450, -500, -500, -450, -5000, -3000),
    (10000, -3000, 1000, 800, 800, 1000, -3000, 10000)
)