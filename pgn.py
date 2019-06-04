
import board
import error

NO_AMBIGUITY = 0
USE_FILE = 1
USE_RANK = 2
USE_FILE_AND_RANK = 3


def set_up_pgn():
    return "[Event \"The Rapture\"]\n" \
           "[Site \"Brisbane, QLD AUS\"]\n" \
           "[Date \"??\"]\n" \
           "[Round \"\"]\n" \
           "[White \"\"]\n" \
           "[Black \"\"]\n" \
           "[Result \"*\"]\n\n"


def update_pgn(game, start, end):
    """
    Updates the pgn.
    :param game: The Position instance representing the game.
    :param start: The starting square of the move just made.
    :param end: The end square of the move just made.
    :return: Nothing.
    """

    x, y = start
    x_new, y_new = end

    # Add move count
    if game.turn:
        game.pgn = ''.join((game.pgn, str(game.fullmove), '. '))

    # The piece to move and the piece to move to
    piece = game.pos[y][x]
    end_piece = game.pos[y_new][x_new]

    # Add castling
    castling = False
    if (piece == 'k' and start == (4, 0) and end == (6, 0)) or \
            (piece == 'K' and start == (4, 7) and end == (6, 7)):
        game.pgn = ''.join((game.pgn, 'O-O'))
        castling = True
    elif (piece == 'k' and start == (4, 0) and end == (2, 0)) or \
            (piece == 'K' and start == (4, 7) and end == (2, 7)):
        game.pgn = ''.join((game.pgn, 'O-O-O'))
        castling = True

    # Add king moves and captures
    if (piece == 'K' or piece == 'k') and not castling:
        if end_piece == ' ':
            game.pgn = ''.join((game.pgn, 'K', board.inv_files[x_new],
                                board.inv_ranks[y_new]))
        else:
            game.pgn = ''.join((game.pgn, 'Kx', board.inv_files[x_new],
                                board.inv_ranks[y_new]))

    # Add pawn advances
    if (piece == 'P' or piece == 'p') and x == x_new:
        game.pgn = ''.join((game.pgn, board.inv_files[x],
                            board.inv_ranks[y_new]))
    elif piece == 'P' or piece == 'p':
        game.pgn = ''.join((game.pgn, board.inv_files[x], 'x',
                            board.inv_files[x_new], board.inv_ranks[y_new]))

    # Add moves of other pieces and other pawn moves
    if piece != 'K' and piece != 'k' and piece != 'P' and piece != 'p':
        add_move(game, piece, end_piece, start, end)


def add_move(game, piece, end_piece, start, end):
    """
    Adds the move made by a piece other than a king or pawn to the pgn.
    :param game: The position instance representing the game.
    :param piece: The piece that is being moved.
    :param end_piece: The piece that is in the end square.
    :param start: The starting square of the move.
    :param end: The ending square of the move.
    :return: Nothing.
    """
    x, y = start
    x_new, y_new = end

    if end_piece == ' ':
        char = ''
    else:
        char = 'x'

    # More than one of this piece and moving to empty square
    ambiguity = check_for_ambiguity(game, piece, start, end)
    if ambiguity == NO_AMBIGUITY:
        game.pgn = ''.join((game.pgn, piece.upper(), char,
                            board.inv_files[x_new], board.inv_ranks[y_new]))
    elif ambiguity == USE_FILE:
        game.pgn = ''.join((game.pgn, piece.upper(), board.inv_files[x], char,
                            board.inv_files[x_new], board.inv_ranks[y_new]))
    elif ambiguity == USE_RANK:
        game.pgn = ''.join((game.pgn, piece.upper(), board.inv_ranks[y], char,
                            board.inv_files[x_new], board.inv_ranks[y_new]))
    else:
        game.pgn = ''.join((game.pgn, piece.upper(), board.inv_files[x], char,
                            board.inv_ranks[y], board.inv_files[x_new],
                            board.inv_ranks[y_new]))


def check_for_ambiguity(game, piece, start, end):
    """
    Checks if there is ambiguity as to which piece is moving.
    :param game: The Position instance of the game.
    :param piece: The piece that is being moved.
    :param start: The start square of the move.
    :param end: The end square of the move.
    :return: The ambiguity type.
    """
    x_old, y_old = start
    x_new, y_new = end

    # Queen
    if piece == 'Q' or piece == 'q':
        # Find the queens
        queens = []
        get_vertical_attacks(queens, end, piece, game)
        get_horizontal_attacks(queens, end, piece, game)
        get_diagonal_attacks(queens, end, piece, game)

        return find_sol_type(queens, x_old, y_old)

    # Bishop
    if piece == 'B' or piece == 'b':
        # Find the bishops
        bishops = []
        get_diagonal_attacks(bishops, end, piece, game)

        return find_sol_type(bishops, x_old, y_old)

    # Knight
    if piece == 'N' or piece == 'n':
        # Find the knights
        knights = []
        for i in [-2, -1, 1, 2]:
            for j in [-2, -1, 1, 2]:
                if 0 <= y_new + j <= 7 and 0 <= x_new + i <= 7:
                    if game.pos[y_new + j][x_new + i] == piece:
                        knights.append((x_new + i, y_new + j))
        return find_sol_type(knights, x_old, y_old)

    # Rook
    if piece == 'R' or piece == 'r':
        # Find the rooks
        rooks = []
        get_vertical_attacks(rooks, end, piece, game)
        get_horizontal_attacks(rooks, end, piece, game)
        return find_sol_type(rooks, x_old, y_old)


def find_sol_type(pieces, x_old, y_old):
    """
    Determines the type of ambiguity.
    :param pieces: The pieces of a certain type and colour on the board that
    can reach the same square.
    :param x_old: The old x coordinates.
    :param y_old: The old y coordinates.
    :return: The ambiguity type.
    """
    # Check for possible ambiguity. If none, return.
    if len(pieces) == 1:
        return NO_AMBIGUITY
    pieces.remove((x_old, y_old))

    # Check ambiguity solution type
    files = [x for x, y in pieces]
    ranks = [y for x, y in pieces]
    if x_old not in files:
        return USE_FILE
    elif y_old not in ranks:
        return USE_RANK
    else:
        return USE_FILE_AND_RANK


def get_vertical_attacks(pieces, end, piece, game):
    """
    Gets the pieces of the same type that attack the end square vertically.
    :param pieces: The pieces that can reach the end square.
    :param end: The end square coordinates.
    :param piece: The piece to find.
    :param game: The Position instance of the game.
    :return: Nothing.
    """
    x, y = end
    for i in [-1, 1]:
        for j in range(1, 8):
            y_new = y + i * j

            if 0 <= y_new <= 7:
                char = game.pos[y_new][x]
                if char == piece:
                    pieces.append((x, y_new))
                    break
                elif char == ' ':
                    continue
                elif char != piece and char != ' ':
                    break


def get_horizontal_attacks(pieces, end, piece, game):
    """
    Gets the pieces of the same type that attack the end square horizontally.
    :param pieces: The pieces that can attack the end square horizontally.
    :param end: The end square coordinates.
    :param piece: The piece to find.
    :param game: The Position instance of the game.
    :return: Nothing.
    """
    x, y = end
    for i in [-1, 1]:
        for j in range(1, 8):
            x_new = x + i * j

            if 0 <= x_new <= 7:
                char = game.pos[y][x_new]
                if char == piece:
                    pieces.append((x_new, y))
                    break
                elif char == ' ':
                    continue
                elif char != piece and char != ' ':
                    break


def get_diagonal_attacks(pieces, end, piece, game):
    """
    Gets the pieces that can attack the end square diagonally.
    :param pieces: The list of pieces that can attack the end square
    diagonally.
    :param end: The end square coordinates.
    :param piece: The piece to search for.
    :param game: The Position instance of the game.
    :return: Nothing.
    """
    x, y = end
    for i in [-1, 1]:
        for j in [-1, 1]:
            for k in range(1, 8):
                x_new = x + i * k
                y_new = y + j * k

                if 0 <= x_new <= 7 and 0 <= y_new <= 7:
                    char = game.pos[y_new][x_new]
                    if char == piece:
                        pieces.append((x_new, y_new))
                        break
                    elif char == ' ':
                        continue
                    elif char != piece and char != ' ':
                        break


def add_check(game):
    """
    Adds to check symbol if a king is in check.
    :param game: The Position instance of the game.
    :return: Nothing.
    """
    if game.is_attacked(game.get_king_coordinates()):
        game.pgn = ''.join((game.pgn, '+'))
    game.pgn += ' '


def add_results(game, status):
    """
    Adds the result of the game.
    :param game: The Position instance of the game.
    :param status: The end of game status.
    :return:
    """
    if status == error.WHITE_WINS:
        game.pgn = game.pgn[:-2]
        game.pgn = ''.join((game.pgn, '# 1-0'))
    elif status == error.BLACK_WINS:
        game.pgn = game.pgn[:-2]
        game.pgn = ''.join((game.pgn, '# 0-1'))
    else:
        game.pgn = game.pgn[:-1]
        game.pgn = ''.join((game.pgn, ' 1/2-1/2'))
