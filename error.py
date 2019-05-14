
import sys

NORMAL = 0
WHITE_WINS = 1
BLACK_WINS = 2
STALEMATE = 3
INSUFFICIENT_MATERIAL = 4
FIFTY_MOVE_RULE = 5
THREEFOLD_REPETITION = 6
INVALID_FEN = 7
INCORRECT_ARGS = 8

ARGUMENT_LEN = 3


def check_args(argv):
    """
    Check the command line arguments.
    :param argv: The command line arguments.
    :return: The appropriate exit code if an error occurs, else NORMAL.
    """
    if len(argv) != ARGUMENT_LEN:
        return INCORRECT_ARGS

    valid_players = ['h', 'c']
    if argv[1] not in valid_players or argv[2] not in valid_players:
        return INCORRECT_ARGS

    return NORMAL


def game_over(status):
    """
    Prints the end of game message according to the result. Does not exit the
    program.
    :param status: The end of game status.
    :return: status.
    """
    if status == NORMAL:
        print('Normal finish')
    elif status == WHITE_WINS:
        print('Checkmate, white wins')
    elif status == BLACK_WINS:
        print('Checkmate, black wins')
    elif status == STALEMATE:
        print('Draw by stalemate')
    elif status == INSUFFICIENT_MATERIAL:
        print('Draw by insufficient material')
    elif status == FIFTY_MOVE_RULE:
        print('Draw by 50-move rule')
    elif status == THREEFOLD_REPETITION:
        print('Draw by threefold repetition')
    elif status == INVALID_FEN:
        print('Error: Invalid FEN string', file=sys.stderr)
    elif status == INCORRECT_ARGS:
        print('Usage: Chess1.0.1 whitePlayer blackPlayer', file=sys.stderr)

    return status


def exit_game(error_code):
    """
    Prints the end of game message and exits the game.
    :param error_code: The exit code.
    :return: Nothing
    """
    game_over(error_code)
    exit(error_code)
