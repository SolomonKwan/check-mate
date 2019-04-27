
"""
A chess simulator. Simulates a chess game between human and/or computer
opponents.

Created November 2018.

@author: S. Kwan

@TODO:
    Add Chess960 option
    Add AI
    Add PGN
    Add GUI
    Fix the unresolved reference error of the pgn.py import
"""

import copy
import random
import sys
from timeit import default_timer as timer

import board
import error
import fen
import pgn


def run_game():
    """
    The main entry point of the program.
    :return: The exit status of the game upon completion.
    """

    moves = []
    # print(ai.minimax(game, 2, True, moves))
    game.display((0, 0), (0, 0))
    while True:

        # Check end of game
        status = game.is_end_of_game(moves)
        if status:
            return status

        # Check and record board positions
        found = False
        for pos, count in moves:
            if pos == game:
                found = True
                new_count = count + 1
                moves[moves.index((pos, count))] = (pos, new_count)
        if not found:
            moves.append((copy.deepcopy(game), 1))

        # Process player turns
        legal_moves = game.get_legal_moves()
        if (game.turn and white == 'c') or (not game.turn and black == 'c'):
            # Computer turn
            random_move = legal_moves[random.randint(0, len(legal_moves) - 1)]
            start, end = random_move
            x1, y1 = start
            x2, y2 = end
        else:
            # Human turn
            x1 = int(input('x start: '))
            y1 = int(input('y start: '))
            x2 = int(input('x end: '))
            y2 = int(input('y end: '))

            while ((x1, y1), (x2, y2)) not in game.get_legal_moves():
                x1 = int(input('x start: '))
                y1 = int(input('y start: '))
                x2 = int(input('x end: '))
                y2 = int(input('y end: '))

        # Check if move is an en passant capture
        if game.en_passant is not None:
            x3, y3 = game.en_passant
            if (game.pos[y1][x1] == 'P' or game.pos[y1][x1] == 'p') and \
                    x2 == x3 and y2 == y3:
                ep = True
            else:
                ep = False
        else:
            ep = False

        pgn.update_pgn(game, (x1, y1), (x2, y2))
        game.make_move((x1, y1), (x2, y2), ep)
        game.display((x1, y1), (x2, y2))


if __name__ == '__main__':
    # Check the command line arguments
    error_code = error.check_args(sys.argv)
    if error_code:
        error.exit_game(error_code)
    white = sys.argv[1]
    black = sys.argv[2]

    # Check the fen string
    error_code = fen.check_fen(board.standard_start, white, black)
    if error_code:
        error.exit_game(error_code)

    # Prep the game
    game = board.Position(board.standard_start, white, black)

    # Play the game
    begin = timer()
    error_code = run_game()
    finish = timer()

    # Print the pgn and time taken to run then exit
    print('\nTime taken: ', finish - begin, '\n\n')
    print(game.pgn)
    error.exit_game(error_code)
