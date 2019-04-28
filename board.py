
import copy
import random
from timeit import default_timer as timer
import error
import fen
import pgn

BLACK = 0
BLACK_PAWN_RANK = 1
BLACK_IN_BETWEEN_RANK = 2
BLACK_TWO_SQUARE_MOVE_RANK = 3
BLACK_EN_PASSANT_RANK = 4
BLACK_KING_SIDE_CASTLE = 2
BLACK_QUEEN_SIDE_CASTLE = 3

WHITE = 1
WHITE_PAWN_RANK = 6
WHITE_IN_BETWEEN_RANK = 5
WHITE_TWO_SQUARE_MOVE_RANK = 4
WHITE_EN_PASSANT_RANK = 3
WHITE_KING_SIDE_CASTLE = 0
WHITE_QUEEN_SIDE_CASTLE = 1

IS_EN_PASSANT = True
NOT_EN_PASSANT = False

# The ranks of the board and their associated index
ranks = {
    '8': 0, '7': 1, '6': 2, '5': 3, '4': 4, '3': 5, '2': 6, '1': 7
}
inv_ranks = {
    0: '8', 1: '7', 2: '6', 3: '5', 4: '4', 5: '3', 6: '2', 7: '1'
}

# The files of the board and their associated index
files = {
    'a': 0, 'b': 1, 'c': 2, 'd': 3, 'e': 4, 'f': 5, 'g': 6, 'h': 7
}
inv_files = {
    0: 'a', 1: 'b', 2: 'c', 3: 'd', 4: 'e', 5: 'f', 6: 'g', 7: 'h'
}

# New standard game position
standard_start = 'rnbqkbnr/pppppppp/8/8/8/8/PPPPPPPP/RNBQKBNR w KQkq - 0 1'

# The characters representing the pieces
pieces = {
    'K': '\u2654', 'Q': '\u2655', 'R': '\u2656', 'B': '\u2657', 'N': '\u2658',
    'P': '\u2659', 'k': '\u265A', 'q': '\u265B', 'r': '\u265C', 'b': '\u265D',
    'n': '\u265E', 'p': '\u265F', ' ': '\u00A0'
}


class Position:
    def __init__(self, position, white, black):
        """
        Initialise the position.
        :param position: The FEN string representing the starting position.
        :param white: A character representing if white is a human or computer.
        :param black: A character representing if black is a human or computer.
        """
        self.piece_count = {
            'K': 0, 'Q': 0, 'R': 0, 'dB': 0, 'lB': 0, 'N': 0, 'P': 0, 'k': 0,
            'q': 0, 'r': 0, 'db': 0, 'lb': 0, 'n': 0, 'p': 0
        }
        self.pos = fen.get_position(position, self.piece_count)
        self.turn = fen.get_turn(position.split(' ')[1])
        self.castling = fen.CASTLING_OPTIONS[position.split(' ')[2]]
        self.en_passant = fen.get_en_passant(position.split(' ')[3])
        self.halfmove = int(position.split(' ')[4])
        self.fullmove = int(position.split(' ')[5])
        self.current_fen = fen.get_fen(self.pos, self.turn, self.castling,
                                       self.en_passant, self.halfmove,
                                       self.fullmove)
        self.white = white
        self.black = black
        self.pgn = pgn.set_up_pgn()

    def __eq__(self, other):
        """
        Check whether two instances of the Position are the same. If they have
        the same current board position, the same player to move, the same
        castling privileges and the same en passant square, they are considered
        the same. Else, they are not the same.
        :param other: The other instance to compare to.
        :return: True if the same, false otherwise.
        """
        if isinstance(other, Position) and other.pos == self.pos and \
            other.turn == self.turn and other.castling == self.castling \
                and other.en_passant == self.en_passant:
            return True
        else:
            return False

    def __ne__(self, other):
        """
        Checks whether two instances of the Position class are different. If
        the instances differ in any combination of current position, the player
        to move, castling privileges or en passant square, they are considered
        different.
        :param other: The other instance to compare to.
        :return: The negation of the return of the __eq__ method.
        """
        return not self.__eq__(other)

    def get_king_coordinates(self):
        """
        Gets the x and y coordinates of the king of the player whose turn it
        is. Assumes that the kings are always present on the board.
        :return: A tuple (x, y) of the king's coordinates.
        """

        # Determine the king character
        if self.turn:
            king = 'K'
        else:
            king = 'k'

        # Find the kings coordinates
        x = -1
        y = -1
        for rank in self.pos:
            if king in rank:
                x = rank.index(king)
                y = self.pos.index(rank)

        return x, y

    def display(self, start, end):
        """
        Displays the information regarding the current board position. This
        consists of the board position, last move, turn, number of legal moves,
        en passant and castling privileges and the current FEN string.
        :return: Nothing.
        """

        print(self.pgn)
        # Print the board position
        print('  0 1 2 3 4 5 6 7')
        i = 0
        for rank in self.pos:
            print(8 - i, end=' ')
            print(*['.' if item == ' ' else item for item in rank], end=' ')
            print(i, end=' ')
            print()
            i += 1
        print('  a b c d e f g h', end='\n')

        # Print the information regarding the current board position
        print('Last move: ', start, end)
        print('Turn: ', self.turn)
        print('Num of legal moves: ', len(self.get_legal_moves()))
        print('En passant: ', self.en_passant)
        print('Castling: ', self.castling)
        print("Halfmove: ", self.halfmove)
        print("Fullmove: ", self.fullmove)
        print(self.current_fen, end='\n\n')

    def kings_apart(self, coordinates):
        """
        Check if the kings are adjacent. Assumes that both kings are present on
        the board.
        :param coordinates: The current coordinate of the king of the player
        whose turn it is.
        :return: True if the kings are apart, false otherwise.
        """
        if self.turn:
            king = 'k'
        else:
            king = 'K'
        x, y = coordinates

        # Check if the kings are adjacent
        for i in [-1, 0, 1]:
            for j in [-1, 0, 1]:
                if (i != 0 or j != 0) and (0 <= x + i <= 7 and
                                           0 <= y + j <= 7) and \
                        (self.pos[y + j][x + i] == king):
                    return False
        return True

    def make_move(self, start, end, en_passant):
        """
        Move the piece at start coordinate to end coordinate. Assumes the move
        is legal. At the end of this method, the check_promotions method is
        always called and the turn is then toggled.
        :param start: The starting location of the piece to move.
        :param end: The end location of the piece to move.
        :param en_passant: A boolean indicating whether the move is en passant
        :return: Nothing.
        """
        x, y = start
        x_new, y_new = end

        # The piece to move and the piece to move to
        piece = self.pos[y][x]
        end_piece = self.pos[y_new][x_new]

        # Actually move the piece and update piece count
        self.pos[y][x] = ' '
        if end_piece != ' ':
            # Capture move
            if end_piece != 'B' and end_piece != 'b':
                self.piece_count[end_piece] -= 1
            elif end_piece == 'B' and ((x_new % 2 == 0 and y_new % 2 == 0) or
                                       (x_new % 2 == 1 and y_new % 2 == 1)):
                self.piece_count['lB'] -= 1
            elif end_piece == 'B' and ((x_new % 2 == 0 and y_new % 2 == 1) or
                                       (x_new % 2 == 1 and y_new % 2 == 0)):
                self.piece_count['dB'] -= 1
            elif end_piece == 'b' and ((x_new % 2 == 0 and y_new % 2 == 0) or
                                       (x_new % 2 == 1 and y_new % 2 == 1)):
                self.piece_count['lb'] -= 1
            else:
                self.piece_count['db'] -= 1
        self.pos[y_new][x_new] = piece

        # Update castling and move rook if castling
        if x == 0 and y == 0:
            self.castling[BLACK_QUEEN_SIDE_CASTLE] = False
        elif x == 7 and y == 0:
            self.castling[BLACK_KING_SIDE_CASTLE] = False
        elif x == 0 and y == 7:
            self.castling[WHITE_QUEEN_SIDE_CASTLE] = False
        elif x == 7 and y == 7:
            self.castling[WHITE_KING_SIDE_CASTLE] = False
        elif x == 4 and y == 0:
            self.castling[BLACK_KING_SIDE_CASTLE] = False
            self.castling[BLACK_QUEEN_SIDE_CASTLE] = False
            if x_new == 6 and y_new == 0 and piece == 'k':
                self.pos[0][7] = ' '
                self.pos[0][5] = 'r'
            elif x_new == 2 and y_new == 0 and piece == 'k':
                self.pos[0][0] = ' '
                self.pos[0][3] = 'r'
        elif x == 4 and y == 7:
            self.castling[WHITE_KING_SIDE_CASTLE] = False
            self.castling[WHITE_QUEEN_SIDE_CASTLE] = False
            if x_new == 6 and y_new == 7 and piece == 'K':
                self.pos[7][7] = ' '
                self.pos[7][5] = 'R'
            elif x_new == 2 and y_new == 7 and piece == 'K':
                self.pos[7][0] = ' '
                self.pos[7][3] = 'R'

        # Remove piece captured en passant
        if en_passant:
            if self.turn:
                self.piece_count['p'] -= 1
                self.pos[y_new + 1][x_new] = ' '
            else:
                self.piece_count['P'] -= 1
                self.pos[y_new - 1][x_new] = ' '

        # En passant update
        self.en_passant = None
        if piece == 'P' and y == WHITE_PAWN_RANK and \
                y_new == WHITE_TWO_SQUARE_MOVE_RANK:
            self.en_passant = (x, WHITE_IN_BETWEEN_RANK)
        elif piece == 'p' and y == BLACK_PAWN_RANK and \
                y_new == BLACK_TWO_SQUARE_MOVE_RANK:
            self.en_passant = (x, BLACK_IN_BETWEEN_RANK)

        # Update halfmove clock
        if piece == 'P' or piece == 'p' or end_piece != ' ':
            self.halfmove = 0
        else:
            self.halfmove += 1

        # Update fullmove clock
        if not self.turn:
            self.fullmove += 1

        # Check promotions
        self.check_promotions()

        # Toggle the turn
        self.turn = 1 - self.turn

        # Update FEN
        self.current_fen = fen.get_fen(self.pos, self.turn, self.castling,
                                       self.en_passant, self.halfmove,
                                       self.fullmove)

    def is_attacked(self, coordinates):
        """
        Checks if the square at the given coordinates is attacked. Makes calls
        to other functions to achieve this.
        :param coordinates: The coordinates of the square to check.
        :return: True if the square is attacked, false otherwise.
        """

        if self.horizontal_or_vertical_attack(coordinates):
            return True

        if self.diagonal_attack(coordinates):
            return True
        if self.knight_attack(coordinates):
            return True

        if self.pawn_attack(coordinates):
            return True

        return False

    def horizontal_or_vertical_attack(self, coordinates):
        """
        Check if the square at the given coordinates is attacked horizontally
        or vertically by an enemy queen or rook.
        :param coordinates: The (x, y) coordinates of the square to check.
        :return: True if the square is attacked, false otherwise.
        """

        x, y = coordinates

        # Determine the queen and rook pieces
        if self.turn:
            queen = 'q'
            rook = 'r'
        else:
            queen = 'Q'
            rook = 'R'

        multipliers = [
            (-1, 1), (-2, 2), (-3, 3), (-4, 4), (-5, 5), (-6, 6), (-7, 7)
        ]

        blocked_hn = False
        blocked_hp = False
        blocked_vn = False
        blocked_vp = False
        for multiplier in multipliers:
            neg_shift, pos_shift = multiplier
            x_new_n = x + neg_shift
            y_new_n = y + neg_shift
            x_new_p = x + pos_shift
            y_new_p = y + pos_shift

            if 0 <= x_new_n <= 7 and not blocked_hn:
                char = self.pos[y][x_new_n]
                if char == rook or char == queen:
                    return True
                elif char != ' ' and char != rook and char != queen:
                    blocked_hn = True

            if 0 <= x_new_p <= 7 and not blocked_hp:
                char = self.pos[y][x_new_p]
                if char == rook or char == queen:
                    return True
                elif char != ' ' and char != rook and char != queen:
                    blocked_hp = True

            if 0 <= y_new_n <= 7 and not blocked_vn:
                char = self.pos[y_new_n][x]
                if char == rook or char == queen:
                    return True
                elif char != ' ' and char != rook and char != queen:
                    blocked_vn = True

            if 0 <= y_new_p <= 7 and not blocked_vp:
                char = self.pos[y_new_p][x]
                if char == rook or char == queen:
                    return True
                elif char != ' ' and char != rook and char != queen:
                    blocked_vp = True
        return False

    def diagonal_attack(self, coordinates):
        """
        Check if the square at the given coordinates is attacked diagonally by
        an enemy queen or bishop.
        :param coordinates: The (x, y) coordinates of the square to check.
        :return: True if the square is attacked, false otherwise.
        """

        x, y = coordinates

        # Determine the queen and bishop pieces
        if self.turn:
            queen = 'q'
            bishop = 'b'
        else:
            queen = 'Q'
            bishop = 'B'

        # Search for a diagonal attack
        for i in [-1, 1]:
            for j in [-1, 1]:
                for k in list(range(1, 8)):
                    x_new = x + i * k
                    y_new = y + j * k

                    if 0 <= x_new <= 7 and 0 <= y_new <= 7:
                        char = self.pos[y_new][x_new]
                        if char != ' ' and char != queen and char != bishop:
                            break
                        elif char == queen or char == bishop:
                            return True
                    else:
                        continue

        return False

    def knight_attack(self, coordinates):
        """
        Check if the square at the given coordinates is attacked an enemy
        knight.
        :param coordinates: The (x, y) coordinates of the square to check.
        :return: True if the square is attacked, false otherwise.
        """

        x, y = coordinates

        # Determine the knight piece
        if self.turn:
            knight = 'n'
        else:
            knight = 'N'

        # Search for a knight attack
        for i in [-1, 1, -2, 2]:
            for j in [-1, 1, -2, 2]:
                if abs(i) != abs(j):
                    x_new = x + i
                    y_new = y + j
                    if 0 <= x_new <= 7 and 0 <= y_new <= 7:
                        char = self.pos[y_new][x_new]
                        if char == knight:
                            return True

        return False

    def pawn_attack(self, coordinates):
        """
        Check if the square at the given coordinates is attacked by an enemy
        pawn.
        :param coordinates: The (x, y) coordinates of the square to check.
        :return: True if the square is attacked, false otherwise.
        """

        x, y = coordinates

        # Determine the pawn piece
        if self.turn:
            pawn = 'p'
            i = -1
        else:
            pawn = 'P'
            i = 1

        # Search for an attack from an enemy pawn
        if 0 <= y + i <= 7 and 0 <= x - 1 <= 7:
            if self.pos[y + i][x - 1] == pawn:
                return True
        if 0 <= y + i <= 7 and 0 <= x + 1 <= 7:
            if self.pos[y + i][x + 1] == pawn:
                return True

        return False

    def get_legal_moves(self):
        """
        Get all the legal moves from a given position.
        :return: A list of tuples of two tuples consisting of the start and end
        coordinates. Entries of the form ((start_x, start_y), (end_x, end_y)).
        """

        # The legal moves from a position. Entries are of the form
        # ((start_x, start_y), (end_x, end_y))
        legal_moves = []

        # Find and add the legal moves
        self.get_king_moves(legal_moves)
        self.get_queen_bishop_rook_moves(legal_moves)
        self.get_knight_moves(legal_moves)
        self.get_pawn_moves(legal_moves)

        return legal_moves

    def get_king_moves(self, moves):
        """
        Gets the legal moves by the king from a given position.
        :param moves: The list to add the legal moves.
        :return: Nothing.
        """
        x, y = self.get_king_coordinates()

        # Get the adjacent squares of the king
        for i in [-1, 0, 1]:
            for j in [-1, 0, 1]:
                if i != 0 or j != 0:
                    x_new = x + i
                    y_new = y + j

                    # Find the legal moves and add them
                    if 0 <= x_new <= 7 and 0 <= y_new <= 7:
                        char = self.pos[y_new][x_new]
                        if self.turn:
                            if (char.islower() or char == ' ') and char != 'k':
                                self.make_check_and_add_move((x, y),
                                                             (x_new, y_new),
                                                             NOT_EN_PASSANT,
                                                             moves)
                        else:
                            if (char.isupper() or char == ' ') and char != 'K':
                                self.make_check_and_add_move((x, y),
                                                             (x_new, y_new),
                                                             NOT_EN_PASSANT,
                                                             moves)

        # Check for castling moves
        if self.turn and x == 4 and y == 7:
            # King side castle
            if self.castling[WHITE_KING_SIDE_CASTLE] and \
                    self.pos[7][5] == ' ' and \
                    self.pos[7][6] == ' ' and not self.is_attacked((5, 7)) \
                    and not self.is_attacked((6, 7)) and not \
                    self.is_attacked(self.get_king_coordinates()):
                moves.append(((4, 7), (6, 7)))

            # Queen side castle
            if self.castling[WHITE_QUEEN_SIDE_CASTLE] and \
                    self.pos[7][1] == ' ' and self.pos[7][2] == ' ' and \
                    self.pos[7][3] == ' ' and not self.is_attacked((2, 7)) \
                    and not self.is_attacked((3, 7)) and not \
                    self.is_attacked(self.get_king_coordinates()):
                moves.append(((4, 7), (2, 7)))

        elif not self.turn and x == 4 and y == 0:
            # King side castle
            if self.castling[BLACK_KING_SIDE_CASTLE] and \
                    self.pos[0][5] == ' ' and self.pos[0][6] == ' ' and \
                    not self.is_attacked((5, 0)) and not \
                    self.is_attacked((6, 0)) and not \
                    self.is_attacked(self.get_king_coordinates()):
                moves.append(((4, 0), (6, 0)))

            # Queen side castle
            if self.castling[BLACK_QUEEN_SIDE_CASTLE] and \
                    self.pos[0][1] == ' ' and self.pos[0][2] == ' ' and \
                    self.pos[0][3] == ' ' and not self.is_attacked((2, 0)) \
                    and not self.is_attacked((3, 0)) and not \
                    self.is_attacked(self.get_king_coordinates()):
                moves.append(((4, 0), (2, 0)))

    def get_queen_bishop_rook_moves(self, moves):
        """
        Retrieves the moves that a queen, bishop and rook can make and adds
        them to the moves list. Assumes that the enemy king is not in check.
        :param moves: The list of valid moves in the current position.
        :return: Nothing.
        """
        # Determine the queen, bishop and rook characters
        if self.turn:
            queen = 'Q'
            bishop = 'B'
            rook = 'R'
        else:
            queen = 'q'
            bishop = 'b'
            rook = 'r'

        # Find the queens
        queens = []
        bishops = []
        rooks = []
        y = 0
        for rank in self.pos:
            x = 0
            for item in rank:
                if item == queen:
                    queens.append((x, y))
                if item == bishop:
                    bishops.append((x, y))
                if item == rook:
                    rooks.append((x, y))
                x += 1
            y += 1

        # Find the range of the queens and add
        for start in queens:
            self.get_vertical_range(start, moves)
            self.get_horizontal_range(start, moves)
            self.get_diagonal_range(start, moves)

        # Find the range of the bishops and add
        for start in bishops:
            self.get_diagonal_range(start, moves)

        # Find the range of the rooks and add
        for start in rooks:
            self.get_vertical_range(start, moves)
            self.get_horizontal_range(start, moves)

    def get_knight_moves(self, moves):
        """
        Retrieves and stores the knight moves to the moves list. Assumes that
        the enemy king is not in check.
        :param moves: The list of legal moves in the current position.
        :return: Nothing.
        """
        # Determine the knight characters
        if self.turn:
            knight = 'N'
        else:
            knight = 'n'

        # Find the knights
        knights = []
        y = 0
        for rank in self.pos:
            x = 0
            for item in rank:
                if item == knight:
                    knights.append((x, y))
                x += 1
            y += 1

        # Determine the knights range
        for knight in knights:
            x, y = knight

            for i in [-2, -1, 1, 2]:
                for j in [-2, -1, 1, 2]:
                    x_new = x + i
                    y_new = y + j
                    if abs(i) != abs(j) and 0 <= x_new <= 7 and 0 <= y_new \
                            <= 7:
                        char = self.pos[y_new][x_new]
                        if self.turn and char.islower() or char == ' ':
                            self.make_check_and_add_move(knight, (x_new,
                                                                  y_new),
                                                         NOT_EN_PASSANT, moves)

                        elif not self.turn and char.isupper() or char == ' ':
                            self.make_check_and_add_move(knight, (x_new,
                                                                  y_new),
                                                         NOT_EN_PASSANT, moves)

    def get_pawn_moves(self, moves):
        """
        Gets the moves that the pawns can make and stores them in the moves
        list. Assumes that no pawns are in their promotion rank. Assumes that
        enemy king is not in check
        :param moves: The list of legal moves in the current position.
        :return: Nothing.
        """
        # Determine pawn characters
        if self.turn:
            pawn = 'P'
        else:
            pawn = 'p'

        # Find the pawn positions
        pawns = []
        y = 0
        for rank in self.pos:
            x = 0
            for item in rank:
                if item == pawn:
                    pawns.append((x, y))
                x += 1
            y += 1

        # Find the pawn movements
        for item in pawns:
            x, y = item

            if self.turn:
                y_new = y - 1
                y1 = WHITE_PAWN_RANK
                y2 = WHITE_IN_BETWEEN_RANK
                y3 = WHITE_TWO_SQUARE_MOVE_RANK
                y4 = WHITE_EN_PASSANT_RANK
                self.check_pawn_moves(moves, (x, y), y_new, y1, y2, y3, y4)
            else:
                y_new = y + 1
                y1 = BLACK_PAWN_RANK
                y2 = BLACK_IN_BETWEEN_RANK
                y3 = BLACK_TWO_SQUARE_MOVE_RANK
                y4 = BLACK_EN_PASSANT_RANK
                self.check_pawn_moves(moves, (x, y), y_new, y1, y2, y3, y4)

    def get_vertical_range(self, start, moves):
        """
        Determines the vertical range of the queen and rook and stores it in
        the moves list. Assumes enemy king is not in check.
        :param start: The starting coordinates of the piece.
        :param moves: The list of legal moves in the current position.
        :return: Nothing.
        """

        x, y = start

        # Get the piece moves from inside outwards
        for i in [-1, 1]:
            for j in list(range(1, 8)):
                y_new = y + i * j

                if 0 <= y_new <= 7:
                    char = self.pos[y_new][x]

                    if self.get_moves(char, start, x, y_new, moves):
                        break

    def get_horizontal_range(self, start, moves):
        """
        Determines the horizontal range of the piece and stores in in the moves
        list. Assumes enemy king is not in check
        :param start: The start coordinates of the piece to find the range of.
        :param moves: The list of legal moves in the current position.
        :return: Nothing.
        """

        x, y = start

        # Get the piece moves from inside outwards
        for i in [-1, 1]:
            for j in list(range(1, 8)):
                x_new = x + i * j

                if 0 <= x_new <= 7:
                    char = self.pos[y][x_new]

                    if self.get_moves(char, start, x_new, y, moves):
                        break

    def get_diagonal_range(self, start, moves):
        """
        Determines the diagonal range of the piece and stores it in the moves
        list. Assumes the enemy king is not in check.
        :param start: The starting coordinates of the piece.
        :param moves: The list of legal moves in the current position.
        :return: Nothing.
        """
        x, y = start

        # Determine the diagonal range from inside outwards
        for i in [-1, 1]:
            for j in [-1, 1]:
                for k in list(range(1, 8)):
                    x_new = x + i * k
                    y_new = y + j * k

                    if 0 <= x_new <= 7 and 0 <= y_new <= 7:
                        char = self.pos[y_new][x_new]

                        if self.get_moves(char, start, x_new, y_new, moves):
                            break

    def get_moves(self, char, start, x, y, moves):
        """
        Determines the type of piece move. i.e. a move to an empty space, a
        move next to a friendly piece or a capture. Assumes the enemy king is
        not in check. Returns a boolean value to indicate whether checking
        further beyond the current position is unnecessary.
        :param char: The character at the prospective square.
        :param start: The start coordinate of the piece to get the moves of.
        :param x: The x coordinate of the prospective square.
        :param y: The y coordinate of the prospective square.
        :param moves: The list of legal moves in the current position.
        :return: True if further searching beyond the prospective square is not
        needed, false otherwise.
        """
        # White's turn
        if self.turn:
            if char == ' ':
                self.make_check_and_add_move(start, (x, y), NOT_EN_PASSANT,
                                             moves)
            elif char.islower():
                self.make_check_and_add_move(start, (x, y), NOT_EN_PASSANT,
                                             moves)
                return True
            elif char.isupper():
                return True

        # Black's turn
        else:
            if char == ' ':
                self.make_check_and_add_move(start, (x, y), NOT_EN_PASSANT,
                                             moves)
            elif char.isupper():
                self.make_check_and_add_move(start, (x, y), NOT_EN_PASSANT,
                                             moves)
                return True
            elif char.islower():
                return True

        return False

    def check_promotions(self):
        """
        Checks if a pawn has reached the other end for a promotion. If one has,
        then the user is prompted for a promotion option. The chosen option is
        then processed and the board is updated.
        :return: Nothing.
        """
        # Determine pawn character
        if self.turn:
            pawn = 'P'
            rank = self.pos[0]
            choices = ['Q', 'N', 'R', 'B']
            y = 0
        else:
            pawn = 'p'
            rank = self.pos[7]
            choices = ['q', 'n', 'r', 'b']
            y = 7

        # Check for a pawn promotion
        if pawn in rank:
            x = rank.index(pawn)

            # Choose a promotion
            if (self.turn and self.white == 'c') or (not self.turn and
                                                     self.black == 'c'):
                choice = choices[random.randint(0, 3)]
            elif self.turn and self.white == 'h':
                print('Choose one of: Q, N, R, B')
                choice = input('Enter here: ')
                while choice not in choices:
                    choice = input('Invalid choice. Choose again: ')
            else:
                print('Choose one of: q, n, r, b')
                choice = input('Enter here: ')
                while choice not in choices:
                    choice = input('Invalid choice. Choose again: ')

            # Make the pawn promotion
            self.piece_count[pawn] -= 1
            self.pos[y][x] = choice
            if choice != 'B' and choice != 'b':
                self.piece_count[choice] += 1
            elif choice == 'B' and ((x % 2 == 0 and y % 2 == 0) or
                                    (x % 2 == 1 and y % 2 == 1)):
                self.piece_count['lB'] += 1
            elif choice == 'B' and ((x % 2 == 0 and y % 2 == 1) or
                                    (x % 2 == 1 and y % 2 == 0)):
                self.piece_count['dB'] += 1
            elif choice == 'b' and ((x % 2 == 0 and y % 2 == 0) or
                                    (x % 2 == 1 and y % 2 == 1)):
                self.piece_count['lb'] += 1
            elif choice == 'b' and ((x % 2 == 0 and y % 2 == 1) or
                                    (x % 2 == 1 and y % 2 == 0)):
                self.piece_count['db'] += 1

            self.pgn = ''.join((self.pgn, '=', choice.upper()))

    def check_pawn_moves(self, moves, start, y_new, y1, y2, y3, y4):
        """
        Determines the moves that the pawns can make and adds them to the moves
        list. Assumes the enemy king is not in check.
        :param moves: The list of legal moves in the current position.
        :param start: The start coordinates of the pawn.
        :param y_new: The rank number in front of the pawn.
        :param y1: The starting pawn rank number.
        :param y2: The rank number in from of the starting pawn rank.
        :param y3: The rank number of the two square pawn move.
        :param y4: The rank the pawn must be on to capture en passant
        :return: Nothing.
        """
        # One square advance
        x, y = start
        if self.pos[y_new][x] == ' ':
            self.make_check_and_add_move(start, (x, y_new), NOT_EN_PASSANT,
                                         moves)

        # Two square initial move
        if y == y1 and self.pos[y2][x] == ' ' and self.pos[y3][x] == ' ':
            self.make_check_and_add_move(start, (x, y3), NOT_EN_PASSANT, moves)

        # Capture moves
        if self.turn:
            if 0 <= x - 1 <= 7 and self.pos[y_new][x - 1].islower():
                self.make_check_and_add_move(start, (x - 1, y_new),
                                             NOT_EN_PASSANT, moves)
            if 0 <= x + 1 <= 7 and self.pos[y_new][x + 1].islower():
                self.make_check_and_add_move(start, (x + 1, y_new),
                                             NOT_EN_PASSANT, moves)
        else:
            if 0 <= x - 1 <= 7 and self.pos[y_new][x - 1].isupper():
                self.make_check_and_add_move(start, (x - 1, y_new),
                                             NOT_EN_PASSANT, moves)
            if 0 <= x + 1 <= 7 and self.pos[y_new][x + 1].isupper():
                self.make_check_and_add_move(start, (x + 1, y_new),
                                             NOT_EN_PASSANT, moves)

        # En passant moves
        if self.en_passant is not None:
            x1, y1 = self.en_passant
            if 0 <= x - 1 <= 7 and x - 1 == x1 and y_new == y1 and y == y4:
                self.make_check_and_add_move(start, (x1, y1), IS_EN_PASSANT,
                                             moves)
            elif 0 <= x + 1 <= 7 and x + 1 == x1 and y_new == y1 and y == y4:
                self.make_check_and_add_move(start, (x1, y1), IS_EN_PASSANT,
                                             moves)

    def is_end_of_game(self, moves):
        """
        Check if it is the end of game. If it is a draw, print the draw message
        and reason why. If it is a stalemate, print the stalemate message. If
        it is checkmate, print the checkmate message.
        :return: The appropriate exit status.
        """

        status = 0

        # Three fold repetition
        for key, value in moves:
            if value >= 3:
                status = error.THREEFOLD_REPETITION

        # 50 move rule
        if self.halfmove >= 100:
            status = error.FIFTY_MOVE_RULE

        # Insufficient material
        if self.insufficient_material():
            status = error.INSUFFICIENT_MATERIAL

        # Check for stalemate
        if not self.is_attacked(self.get_king_coordinates()) and \
                len(self.get_legal_moves()) == 0:
            status = error.STALEMATE

        # Check for checkmate
        if self.is_attacked(self.get_king_coordinates()) and \
                len(self.get_legal_moves()) == 0:
            if self.turn:
                status = error.BLACK_WINS
            else:
                status = error.WHITE_WINS

        return status

    def make_check_and_add_move(self, start, end, en_passant, moves):
        """
        Makes a move and checks whether it is a legal move. If the move is
        legal, it is added to the moves list. Assumes that the enemy king is
        not in check.
        :param start: The start coordinates of the piece to move.
        :param end: The end coordinates of the piece to move.
        :param en_passant: A boolean indicating if the move is en passant.
        :param moves: The list of legal moves in the current position.
        :return: Nothing.
        """
        x, y = start
        x_new, y_new = end

        # Copy the current position
        last_pos = copy.deepcopy(self.pos)

        # The piece to move
        piece = self.pos[y][x]

        # Actually move the piece
        self.pos[y][x] = ' '
        self.pos[y_new][x_new] = piece

        # Remove piece captured if en passant
        if en_passant:
            if self.turn:
                self.pos[y_new + 1][x_new] = ' '
            else:
                self.pos[y_new - 1][x_new] = ' '

        # Check if king is put in check
        if not self.is_attacked(self.get_king_coordinates()) and \
                self.kings_apart(self.get_king_coordinates()):
            moves.append((start, end))

        # Undo the move
        self.pos = copy.deepcopy(last_pos)

    def insufficient_material(self):
        """
        Check for a draw by insufficient material.
        :return: True if a draw, false otherwise.
        """
        pieces_sum = sum(self.piece_count.values())

        # King vs King
        if self.piece_count['K'] == 1 and self.piece_count['k'] == 1 and \
                pieces_sum == 2:
            return True

        # King and bishop(s) vs king (same colour bishop(s))
        if self.piece_count['K'] == 1 and self.piece_count['lB'] and \
                self.piece_count['k'] == 1 and (pieces_sum -
                                                self.piece_count['lB']) == 2:
            return True
        if self.piece_count['K'] == 1 and self.piece_count['dB'] and \
                self.piece_count['k'] == 1 and (pieces_sum -
                                                self.piece_count['dB']) == 2:
            return True
        if self.piece_count['K'] == 1 and self.piece_count['k'] == 1 and \
                self.piece_count['lb'] and (pieces_sum -
                                            self.piece_count['lb'] == 2):
            return True
        if self.piece_count['K'] == 1 and self.piece_count['k'] == 1 and \
                self.piece_count['db'] and (pieces_sum -
                                            self.piece_count['db'] == 2):
            return True

        # King and knight vs King
        if self.piece_count['K'] == 1 and self.piece_count['N'] == 1 and \
                self.piece_count['k'] == 1 and (pieces_sum -
                                                self.piece_count['N'] == 2):
            return True
        if self.piece_count['K'] == 1 and self.piece_count['k'] == 1 and \
                self.piece_count['n'] == 1 and (pieces_sum -
                                                self.piece_count['n'] == 2):
            return True

        # King and bishop(s) vs king and bishop(s) (same colour bishops)
        if self.piece_count['K'] == 1 and self.piece_count['lB'] and \
                self.piece_count['dB'] == 0 and self.piece_count['k'] == 1 \
                and self.piece_count['lb'] and self.piece_count['db'] == 0 \
                and (pieces_sum - self.piece_count['lB'] -
                     self.piece_count['lb']) == 2:
            return True
        if self.piece_count['K'] == 1 and self.piece_count['lB'] == 0 and \
                self.piece_count['dB'] and self.piece_count['k'] == 1 and \
                self.piece_count['lb'] == 0 and self.piece_count['db'] and \
                (pieces_sum - self.piece_count['dB'] -
                 self.piece_count['db']) == 2:
            return True

        return False
