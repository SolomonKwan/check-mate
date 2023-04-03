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
    Check if faster to pass class to function or attributes individually
"""

import copy
import random
import sys
import argparse
from timeit import default_timer as timer

import board
import error
import fen
import pgn


def run_game(game, black, white):
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
            pgn.add_results(game, status)
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
        if (game.turn and white == "c") or (not game.turn and black == "c"):
            # Computer turn
            random_move = legal_moves[random.randint(0, len(legal_moves) - 1)]
            start, end = random_move
            x1, y1 = start
            x2, y2 = end
        else:
            # Human turn
            x1 = int(input("x start: "))
            y1 = int(input("y start: "))
            x2 = int(input("x end: "))
            y2 = int(input("y end: "))

            while ((x1, y1), (x2, y2)) not in game.get_legal_moves():
                x1 = int(input("x start: "))
                y1 = int(input("y start: "))
                x2 = int(input("x end: "))
                y2 = int(input("y end: "))

        # Check if move is an en passant capture
        if game.en_passant is not None:
            x3, y3 = game.en_passant
            if (
                (game.pos[y1][x1] == "P" or game.pos[y1][x1] == "p")
                and x2 == x3
                and y2 == y3
            ):
                ep = True
            else:
                ep = False
        else:
            ep = False

        pgn.update_pgn(game, (x1, y1), (x2, y2))
        game.make_move((x1, y1), (x2, y2), ep)
        pgn.add_check(game)
        game.display((x1, y1), (x2, y2))


def main():
    parser = argparse.ArgumentParser(description="A chess platform written in python")

    parser.add_argument(
        "white",
        type=error.player_type,
        default="c",
        help="A character used to determine if a human or computer player"
        " should be used for the white piece. Use 'c' for the white piece "
        "to play as a computer and any other character for the white piece to "
        "be a human player.",
    )

    parser.add_argument(
        "black",
        type=error.player_type,
        default="c",
        help="A character used to determine if a human or computer player"
        " should be used for the white piece. Use 'c' for the white piece "
        "to play as a computer and any other character for the white piece to "
        "be a human player.",
    )

    args = parser.parse_args()

    white = args.white
    black = args.black

    # Check the fen string
    error_code = fen.check_fen(board.standard_start, white, black)
    if error_code:
        error.exit_game(error_code)

    # Prep the game
    game = board.Position(board.standard_start, white, black)

    # Play the game
    begin = timer()
    error_code = run_game(game, black, white)
    finish = timer()

    # Print the pgn and time taken to run then exit
    print("\nTime taken: ", finish - begin, "\n\n")
    print(game.pgn)
    error.exit_game(error_code)


if __name__ == "__main__":
    main()
