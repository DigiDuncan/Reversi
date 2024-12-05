from random import choices, choice, random

from board import Board, Tile, IllegalMoveException

type WeightTable = tuple[tuple[float, ...], ...]

class OrthelloAI:

    def __init__(self, pickyness: float, chaos: float, depth: int, weights: WeightTable):
        self.pickyness: float = pickyness
        self.chaos: float = chaos
        self.depth: int = depth
        self.weights: WeightTable = weights

    def pick_move(self, board: Board, turn: Tile) -> tuple[tuple[int, int], list[list[tuple[int, int]]]]:
        moves = board.get_available_moves(turn)
        # We assume that the interface will call a game before we get to pick a move

        # Evaluate every possible move
        evaluations = {}
        for coord, move in moves.items():
            evaluations[coord] = self.search(board.update(turn, coord, move), turn.invert, -100000, 100000)

        ranked = sorted(moves.keys(), key=lambda c: evaluations[c], reverse=True)
        if self.chaos < random():
            # The AI has locked in
            coord = ranked[0]
            return ranked, moves[ranked]
    
        cap = max(1, int((1.0 - self.pickyness) * len(ranked)))
        picks = ranked[:cap]
        weights = [evaluations[tile] for tile in picks]
        if not sum(weights):
            pick = choice(picks)
        else:
            offset = min(weights)
            pick = choices(picks, [weight - offset + 1 for weight in weights])[0]
        return pick, moves[pick]

    def search(self, board: Board, turn: Tile, alpha: float, beta: float, depth: int = 0) -> float:
        if depth == self.depth:
            return self.evaluate(board, turn)
        
        moves = board.get_available_moves(turn)
        if not moves:
            a, b = board.get_counts
            if turn == Tile.BLACK:
                a, b = b, a
            if a < b:
                return -20000 # loses
            elif b < a:
                return 20000 # Wins
            else: 
                 return 0
        
        for coord, move in moves.items():
            new = board.update(turn, coord, move)
            result = -self.search(new, turn.invert(), -beta, -alpha, depth+1)
            if result >= beta:
                # The move is too good so let's prune it
                return beta
            alpha = max(result, alpha)

        return alpha

    def evaluate(self, board: Board, turn: Tile) -> float:
        tiles = board.tiles
        weights = self.weights

        white_score = 0
        black_score = 0

        for col in range(board.size):
            for row in range(board.size):
                t = tiles[col][row]
                if t == Tile.WHITE:
                    white_score += weights[col][row]
                elif t == Tile.BLACK:
                    black_score += weights[col][row]

        perspective = 1 if turn == Tile.WHITE else -1
        return (white_score - black_score) * perspective
    

peak_weights = (
    (10000, -3000, 1000, 800, 800, 1000, -3000, 10000),
    (-3000, -5000, -450, -500, -500, -450, -5000, -3000),
    (1000, -450, 30, 10, 10, 30, -450, 1000),
    (800, -500, 10, 50, 50, 10, -500, 800),
    (800, -500, 10, 50, 50, 10, -500, 800),
    (1000, -450, 30, 10, 10, 30, -450, 1000),
    (-3000, -5000, -450, -500, -500, -450, -5000, -3000),
    (10000, -3000, 1000, 800, 800, 1000, -3000, 10000)
)

radial_weights = (
    (10, 5, 5, 5, 5, 5, 5, 10),
    (5,  3, 3, 3, 3, 3, 3, 5),
    (5,  3, 1, 1, 1, 1, 3, 5),
    (5,  3, 1, 0, 0, 1, 3, 5),
    (5,  3, 1, 0, 0, 1, 3, 5),
    (5,  3, 1, 1, 1, 1, 3, 5),
    (5,  3, 3, 3, 3, 3, 3, 5),
    (10, 5, 5, 5, 5, 5, 5, 10)
)

plain_weights = (
    (1, 1, 1, 1, 1, 1, 1, 1),
    (1, 1, 1, 1, 1, 1, 1, 1),
    (1, 1, 1, 1, 1, 1, 1, 1),
    (1, 1, 1, 1, 1, 1, 1, 1),
    (1, 1, 1, 1, 1, 1, 1, 1),
    (1, 1, 1, 1, 1, 1, 1, 1),
    (1, 1, 1, 1, 1, 1, 1, 1),
    (1, 1, 1, 1, 1, 1, 1, 1)
)

random_weights = (
    (0, 0, 0, 0, 0, 0, 0, 0),
    (0, 0, 0, 0, 0, 0, 0, 0),
    (0, 0, 0, 0, 0, 0, 0, 0),
    (0, 0, 0, 0, 0, 0, 0, 0),
    (0, 0, 0, 0, 0, 0, 0, 0),
    (0, 0, 0, 0, 0, 0, 0, 0),
    (0, 0, 0, 0, 0, 0, 0, 0),
    (0, 0, 0, 0, 0, 0, 0, 0)
)

# --- AI ----
GOBLIN = OrthelloAI(0.0, 1.0, 0, random_weights)