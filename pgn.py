
import board


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
        game.pgn += 'O-O '
        castling = True
    elif (piece == 'k' and start == (4, 0) and end == (2, 0)) or \
            (piece == 'K' and start == (4, 7) and end == (2, 7)):
        game.pgn += 'O-O-O '
        castling = True

    # Add king moves and captures
    if piece == 'K' or piece == 'k' and not castling:
        if end_piece == ' ':
            game.pgn += 'K' + board.inv_files[x_new] + \
                        board.inv_ranks[y_new] + ' '
        else:
            game.pgn += 'Kx' + board.inv_files[x_new] + \
                        board.inv_ranks[y_new] + ' '


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


def add_results(pgn):
    pass
