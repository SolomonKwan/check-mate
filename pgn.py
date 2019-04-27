
import board

NO_AMBIGUITY = 0
USE_FILE = 1
USE_RANK = 2
USE_FILE_AND_RANK = 3


def set_up_pgn():
    pgn = "[Event \"The Rapture\"]\n" \
          "[Site \"Brisbane, QLD AUS\"]\n" \
          "[Date \"??\"]\n" \
          "[Round \"\"]\n" \
          "[White \"\"]\n" \
          "[Black \"\"]\n" \
          "[Result \"*\"]\n" \
          "\n"

    return pgn


def update_pgn(game, start, end):

    x, y = start
    x_new, y_new = end

    # Add move count
    if game.turn:
        game.pgn += str(game.fullmove) + '. '

    # The piece to move and the piece to move to
    piece = game.pos[y][x]
    end_piece = game.pos[y_new][x_new]

    # Add castling
    castling = False
    if (piece == 'k' and start == (4, 0) and end == (6, 0)) or \
            (piece == 'K' and start == (4, 7) and end == (6, 7)):
        game.pgn += 'O-O'
        castling = True
    elif (piece == 'k' and start == (4, 0) and end == (2, 0)) or \
            (piece == 'K' and start == (4, 7) and end == (2, 7)):
        game.pgn += 'O-O-O'
        castling = True

    # Add moves and captures
    if (piece == 'K' or piece == 'k') and not castling:
        if end_piece == ' ':
            game.pgn += 'K' + board.inv_files[x_new] + \
                        board.inv_ranks[y_new]
        else:
            game.pgn += 'Kx' + board.inv_files[x_new] + \
                        board.inv_ranks[y_new]

    # Add moves of other pieces
    if piece != 'K' and piece != 'k':
        add_move(game, piece, end_piece, start, end)

    # Add promotion moves

    # if piece == 'k' and not (x == 4 and y == 0) and \
    #         (not (x_new == 6 and y_new == 0) or
    #          not (x_new == 2 and y_new == 0)):
    #     if end_piece == ' ':
    #         self.pgn += 'K' + inv_files[x_new] + inv_ranks[y_new] + ' '
    #     else:
    #         self.pgn += 'Kx' + inv_files[x_new] + inv_ranks[y_new] + ' '
    # elif piece == 'K' and not (x == 4 and y == 7) and \
    #         (not (x_new == 6 and y_new == 7) or
    #          not (x_new == 2 and y_new == 7)):
    #     if end_piece == ' ':
    #         self.pgn += 'K' + inv_files[x_new] + inv_ranks[y_new] + ' '
    #     else:
    #         self.pgn += 'Kx' + inv_files[x_new] + inv_ranks[y_new] + ' '
    # elif piece == 'P' or piece == 'p':
    #     if en_passant:
    #         self.pgn += inv_files[x_new] + 'x' + inv_ranks[y_new] + ' '
    #     elif end_piece == ' ':
    #         self.pgn += inv_files[x_new] + str(8 - y_new) + ' '
    #     else:
    #         pass


def add_move(game, piece, end_piece, start, end):
    x, y = start
    x_new, y_new = end

    if piece != 'B' and piece != 'b' and piece != 'P' and piece != 'p':
        if game.piece_count[piece] == 1 and end_piece == ' ':
            # Only one of this piece and moving to empty square
            game.pgn += piece.upper() + board.inv_files[x_new] + \
                        board.inv_ranks[y_new]
        elif game.piece_count[piece] == 1:
            # Only one of this piece and capturing
            game.pgn += piece.upper() + 'x' + board.inv_files[x_new] + \
                        board.inv_ranks[y_new]
        elif end_piece == ' ':
            # More than one of this piece and moving to empty square
            ambiguity = check_for_ambiguity(game, piece, start, end)
            if ambiguity == NO_AMBIGUITY:
                game.pgn += piece.upper() + board.inv_files[x_new] + \
                            board.inv_ranks[y_new]
            elif ambiguity == USE_FILE:
                game.pgn += piece.upper() + board.inv_files[x] + \
                            board.inv_files[x_new] + board.inv_ranks[y_new]
            elif ambiguity == USE_RANK:
                game.pgn += piece.upper() + board.inv_ranks[y] + \
                            board.inv_files[x_new] + board.inv_ranks[y_new]
            else:
                game.pgn += piece.upper() + board.inv_files[x] + \
                            board.inv_ranks[y] + board.inv_files[x_new] + \
                            board.inv_ranks[y_new]
        else:
            # More than one of this piece and capturing
            ambiguity = check_for_ambiguity(game, piece, start, end)
            if NO_AMBIGUITY:
                game.pgn += piece.upper() + 'x' + board.inv_files[x_new] + \
                            board.inv_ranks[y_new]
            elif ambiguity == USE_FILE:
                game.pgn += piece.upper() + board.inv_files[x] + 'x' + \
                            board.inv_files[x_new] + board.inv_ranks[y_new]
            elif ambiguity == USE_RANK:
                game.pgn += piece.upper() + board.inv_ranks[y] + 'x' + \
                            board.inv_files[x_new] + board.inv_ranks[y_new]
            else:
                game.pgn += piece.upper() + board.inv_files[x] + \
                            board.inv_ranks[y] + 'x' + \
                            board.inv_files[x_new] + board.inv_ranks[y_new]
    else:
        pass


def check_for_ambiguity(game, piece, start, end):
    x_old, y_old = start
    x_new, y_new = end
    # Queen
    if piece == 'Q' or piece == 'q':
        # Find the queens
        queens = []
        get_vertical_attacks(queens, end, piece, game)
        get_horizontal_attacks(queens, end, piece, game)
        get_diagonal_attacks(queens, end, piece, game)

        # Check for possible ambiguity. If none, return.
        if len(queens) == 1:
            return NO_AMBIGUITY
        queens.remove((x_old, y_old))

        # Check ambiguity solution type
        files = [x for x, y in queens]
        ranks = [y for x, y in queens]
        if x_old not in files:
            return USE_FILE
        elif y_old not in ranks:
            return USE_RANK
        else:
            return USE_FILE_AND_RANK

    # Bishop

    # Knight
    if piece == 'N' or piece == 'n':
        # Find the knights
        knights = []
        for i in [-2, -1, 1, 2]:
            for j in [-2, -1, 1, 2]:
                if 0 <= y_new + j <= 7 and 0 <= x_new + i <= 7:
                    if game.pos[y_new + j][x_new + i] == piece:
                        knights.append((x_new + i, y_new + j))

        # Check for possible ambiguity. If none, return.
        if len(knights) == 1:
            return NO_AMBIGUITY
        knights.remove((x_old, y_old))

        # Check ambiguity solution type
        files = [x for x, y in knights]
        ranks = [y for x, y in knights]
        if x_old not in files:
            return USE_FILE
        elif y_old not in ranks:
            return USE_RANK
        else:
            return USE_FILE_AND_RANK


    # Rook
    if piece == 'R':
        pass
    elif piece == 'r':
        pass

    # Pawn
    if piece == 'P':
        pass
    elif piece == 'p':
        pass


def get_vertical_attacks(pieces, end, piece, game):
    x, y = end
    for i in [-1, 1]:
        for j in list(range(1, 8)):
            y_new = y + i * j

            if 0 <= y_new <= 7:
                char = game.pos[y_new][x]
                if char == piece:
                    pieces.append((x, y_new))
                elif char == ' ':
                    continue
                elif char != piece and char != ' ':
                    break


def get_horizontal_attacks(pieces, end, piece, game):
    x, y = end
    for i in [-1, 1]:
        for j in list(range(1, 8)):
            x_new = x + i * j

            if 0 <= x_new <= 7:
                char = game.pos[y][x_new]
                if char == piece:
                    pieces.append((x_new, y))
                elif char == ' ':
                    continue
                elif char != piece and char != ' ':
                    break


def get_diagonal_attacks(pieces, end, piece, game):
    x, y = end
    for i in [-1, 1]:
        for j in [-1, 1]:
            for k in list(range(1, 8)):
                x_new = x + i * k
                y_new = y + j * k

                if 0 <= x_new <= 7 and 0 <= y_new <= 7:
                    char = game.pos[y_new][x_new]
                    if char == piece:
                        pieces.append((x_new, y_new))
                    elif char == ' ':
                        continue
                    elif char != piece and char != ' ':
                        break


def add_check(game):
    if game.is_attacked(game.get_king_coordinates()):
        game.pgn += '+'
    game.pgn += ' '


def add_results(pgn):
    pass
