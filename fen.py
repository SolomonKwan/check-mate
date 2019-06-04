
import board
import error

SPACE_SPLIT_NUM = 6
SLASH_SPLIT_NUM = 8

CASTLING_OPTIONS = {
    'KQkq': [True, True, True, True], 'KQk': [True, True, True, False],
    'KQq': [True, True, False, True], 'Kkq': [True, False, True, True],
    'Qkq': [False, True, True, True], 'Kk': [True, False, True, False],
    'Kq': [True, False, False, True], 'Qk': [False, True, True, False],
    'Qq': [False, True, False, True], 'KQ': [True, True, False, False],
    'kq': [False, False, True, True], 'K': [True, False, False, False],
    'k': [False, False, True, False], 'Q': [False, True, False, False],
    'q': [False, False, False, True], '-': [False, False, False, False]
}


def check_fen(line, white, black):
    """
    Checks the format of the FEN string.
    :param line: The FEN string representing a board position
    :param white: Character representing a human or computer
    :param black: Character representing a human or computer
    :return: The appropriate error code as outlined in error.py
    """

    # Check for correct number of [space] separated substrings
    space_split = line.split(' ')
    if len(space_split) != SPACE_SPLIT_NUM:
        return error.INVALID_FEN

    # Check for correct number of / separated substrings
    slash_split = space_split[0].split('/')
    if len(slash_split) != SLASH_SPLIT_NUM:
        return error.INVALID_FEN

    # Check that pawns do not appear on own home rank or on enemy home rank
    if 'P' in slash_split[0] or 'p' in slash_split[0] or 'P' in \
            slash_split[7] or 'p' in slash_split[7]:
        return True

    # Check each rank and make sure each king appears once
    kings = [0, 0]
    for rank in slash_split:
        error_code = check_rank(rank, kings)
        if error_code:
            return error_code
    if kings[0] != 1 or kings[1] != 1:
        return error.INVALID_FEN

    # Check the turn
    if space_split[1] != 'w' and space_split[1] != 'b':
        return error.INVALID_FEN

    # Check king placements
    error_code = check_kings(slash_split)
    if error_code:
        return error_code

    # Check castling rights
    error_code = check_castling(slash_split, space_split[2])
    if error_code:
        return error_code

    # Check En passant
    error_code = check_en_passant(slash_split, space_split[3])
    if error_code:
        return error_code

    # Check halfmoves and fullmoves
    error_code = check_moves(space_split[4], space_split[5])
    if error_code:
        return error_code

    # Check that player turns and check are consistent
    game = board.Position(line, white, black)
    game.turn = 1 - game.turn
    if game.is_attacked(game.get_king_coordinates()):
        return error.INVALID_FEN

    return error.NORMAL


def check_rank(rank, kings):
    """
    Check that the string representing the rank is formatted correctly and is
    consistent (i.e. represents 8 items and has valid chars).
    :param rank: The string representing the rank.
    :param kings: A list of size two where the first element is the number of
    white kings and the second element is the number of black kings.
    :return: The appropriate error code if an error occurred, 0 otherwise.
    """
    # Check for consecutive digits
    i = 0
    while i < len(rank):
        if rank[i].isdigit() and i != len(rank) - 1 and rank[i + 1].isdigit():
            return error.INVALID_FEN
        i += 1

    # Check for invalid chars and count the kings
    for item in rank:
        if item not in board.pieces and not item.isdigit():
            return error.INVALID_FEN
        elif item == 'K':
            kings[0] += 1
        elif item == 'k':
            kings[1] += 1

    # Check that correct num of items appear
    item_count = 0
    for item in rank:
        if not item.isdigit():
            item_count += 1
        else:
            item_count += int(item)
    if item_count != 8:
        return error.INVALID_FEN

    return error.NORMAL


def check_kings(board_lines):
    """
    Check that the kings are not next to each other as represented in the FEN
    string. Assumes that the correct number of kings appears on the board.
    :param board_lines: A list of the strings representing the ranks of the
    board.
    :return: The appropriate error code if an error occurs, 0 otherwise.
    """

    white_king = (None, None)
    black_king = (None, None)

    # Find the coordinates of the kings
    for rank in board_lines:
        if 'K' in rank:
            x = rank.index('K')
            y = board_lines.index(rank)
            white_king = (x, y)
        if 'k' in rank:
            x = rank.index('k')
            y = board_lines.index(rank)
            black_king = (x, y)

    x1, y1 = white_king
    x2, y2 = black_king

    # Check if the kings are next to each other
    if abs(x1 - x2) <= 1 and abs(y1 - y2) <= 1:
        return error.INVALID_FEN

    return error.NORMAL


def check_en_passant(board_lines, en_passant):
    """
    Checks that the en passant part of the string is formatted correctly and
    that a pawn is giving the en passant.
    :param board_lines: List of strings of the ranks of the board.
    :param en_passant: The en passant part of the string
    :return: The appropriate error code if an error occurs, 0 otherwise.
    """
    if en_passant != '-':
        # Check en passant length is two
        if len(en_passant) != 2:
            return error.INVALID_FEN

        # Check that the files and ranks are valid
        if en_passant[0] not in board.files or (en_passant[1] != '6' and
                                                en_passant[1] != '3'):
            return error.INVALID_FEN

        # Check that a pawn is giving the en passant
        x = board.files[en_passant[0]]
        if en_passant[1] == '3':
            rank = board_lines[4]
            pawn_piece = 'P'
        else:
            rank = board_lines[3]
            pawn_piece = 'p'

        item_count = 0
        for item in rank:
            if item.isdigit():
                item_count += int(item)
            else:
                item_count += 1
            if item_count == x + 1 and item != pawn_piece:
                return error.INVALID_FEN
            elif item_count >= x + 1:
                break

        # Passed the file without a pawn, i.e. incorrect
        if item_count != x + 1:
            return error.INVALID_FEN

    return error.NORMAL


def check_castling(board_lines, castling):
    """
    Checks that the castling part of the FEN string is correctly formatted and
    that the board position allows for the indicated castling(s). Does not take
    into account whether the king and/or rook(s) have previously moved.
    :param board_lines: The list of strings representing each rank.
    :param castling: The castling string
    :return: Appropriate error code if an error occurs, 0 otherwise
    """
    # Check that the castling option is a valid string
    if castling not in CASTLING_OPTIONS:
        return error.INVALID_FEN

    # Find x coordinates of the kings
    count1, count2 = 0, 0
    for item in board_lines[7]:
        if item == 'K':
            break
        if item.isdigit():
            count1 += int(item)
        else:
            count1 += 1
    for item in board_lines[0]:
        if item == 'k':
            break
        if item.isdigit():
            count2 += int(item)
        else:
            count2 += 1

    i = 0
    while i < len(castling):
        if castling[i] == 'K':
            if count1 != 4 or board_lines[7][-1] != 'R':
                return error.INVALID_FEN
        elif castling[i] == 'Q':
            if count1 != 4 or board_lines[7][0] != 'R':
                return error.INVALID_FEN
        elif castling[i] == 'k':
            if count2 != 4 or board_lines[0][-1] != 'r':
                return error.INVALID_FEN
        elif castling[i] == 'q':
            if count2 != 4 or board_lines[0][0] != 'r':
                return error.INVALID_FEN
        i += 1

    return error.NORMAL


def check_moves(halfmoves, fullmoves):
    """
    Check that the halfmoves and full moves are valid.
    :param halfmoves: The halfmoves value.
    :param fullmoves: The fullmoves value.
    :return: The appropriate error code if invalid.
    """
    # Check for an integer
    try:
        int(halfmoves)
        int(fullmoves)
    except ValueError:
        return error.INVALID_FEN

    # Check for correct integer range
    if int(halfmoves) < 0:
        return error.INVALID_FEN
    if int(fullmoves) <= 0:
        return error.INVALID_FEN

    return error.NORMAL


def get_position(fen_string, piece_count):
    """
    Constructs a board position from FEN. Assumes that the FEN is valid. Also
    counts the number of each pieces, distinguishing light/dark square bishops.
    :param fen_string: The FEN string.
    :param piece_count: A dictionary containing counts of all pieces.
    :return: A list of lists representing the board position and a dictionary of
    the number of each piece on the board.
    """
    position = fen_string.split(' ')[0].split('/')
    pos = []

    y = 0
    for item in position:
        x = 0
        rank = []
        for item2 in item:
            if not item2.isdigit():
                rank.append(item2)
                if item2 != 'B' and item2 != 'b':
                    piece_count[item2] += 1
                elif item2 == 'B' and ((x % 2 == 0 and y % 2 == 0) or
                                       (x % 2 == 1 and y % 2 == 1)):
                    piece_count['lB'] += 1
                elif item2 == 'B' and ((x % 2 == 0 and y % 2 == 1) or
                                       (x % 2 == 1 and y % 2 == 0)):
                    piece_count['dB'] += 1
                elif item2 == 'b' and ((x % 2 == 0 and y % 2 == 0) or
                                       (x % 2 == 1 and y % 2 == 1)):
                    piece_count['lb'] += 1
                elif item2 == 'b' and ((x % 2 == 0 and y % 2 == 1) or
                                       (x % 2 == 1 and y % 2 == 0)):
                    piece_count['db'] += 1
                x += 1
            else:
                rank.extend([' '] * int(item2))
                x += int(item2)
        pos.append(rank)
        y += 1
    return pos


def get_turn(char):
    """
    Determines the boolean value representing player turn. Assumes that the
    char is valid (i.e. one of 'w' or 'b').
    :param char: The char representing the player whose turn it is.
    :return: The player turn boolean.
    """
    if char == 'w':
        return board.WHITE
    else:
        return board.BLACK


def get_en_passant(string):
    """
    Determines the coordinates of the en passant square. Assumes that the
    string is in the correct format.
    :param string: The en passant string.
    :return: A tuple representing the x and y coordinates of the square.
    """
    if string != '-':
        x = board.files[string[0]]
        y = board.ranks[string[1]]
    else:
        return None

    return x, y


def get_fen(pos, turn, castling, en_passant, halfmove, fullmove):
    """
    Get the FEN of the current board position. Assumes that the board is in a
    valid state and that the board and other given parameters are consistent.
    :param pos: The list of lists representing the board state.
    :param turn: The player whose turn it is.
    :param castling: The castling privileges.
    :param en_passant: The en passant square.
    :param halfmove: The number of halfmoves.
    :param fullmove: The number of fullmoves.
    :return: The FEN string.
    """
    fen = ''

    # Construct the board part of the fen
    i = 0
    for rank in pos:
        space_count = 0
        for item in rank:
            if item != ' ':
                if space_count != 0:
                    fen = ''.join((fen, str(space_count)))
                    space_count = 0
                fen = ''.join((fen, item))
            else:
                space_count += 1
        i += 1
        if space_count != 0:
            fen = ''.join((fen, str(space_count)))
        if i != 8:
            fen = ''.join((fen, '/'))
    fen = ''.join((fen, ' '))

    # Add whose turn
    if turn:
        fen = ''.join((fen, 'w'))
    else:
        fen = ''.join((fen, 'b'))
    fen = ''.join((fen, ' '))

    # Add the castling
    i = 0
    for value in castling:
        if i == 0 and value:
            fen = ''.join((fen, 'K'))
        if i == 1 and value:
            fen = ''.join((fen, 'Q'))
        if i == 2 and value:
            fen = ''.join((fen, 'k'))
        if i == 3 and value:
            fen = ''.join((fen, 'q'))
        i += 1
    count = 0
    for item in castling:
        if not item:
            count += 1
    if count == 4:
        fen = ''.join((fen, '-'))
    fen = ''.join((fen, ' '))

    # Add en passant square
    if en_passant is not None:
        x, y = en_passant
        for key, value in board.files.items():
            if value == x:
                fen = ''.join((fen, key))
        for key, value in board.ranks.items():
            if value == y:
                fen = ''.join((fen, key))
    else:
        fen = ''.join((fen, '-'))
    fen = ''.join((fen, ' '))

    # Half and full moves
    fen = ''.join((fen, str(halfmove)))
    fen = ''.join((fen, ' '))
    fen = ''.join((fen, str(fullmove)))

    return fen
