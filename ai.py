
import copy


def search(game):
    moves = game.get_legal_moves()
    depth = 3

    move_num = 1
    for move in moves:
        start, end = move
        x1, y1 = start
        x2, y2 = end

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

        game_copy = copy.deepcopy(game)
        game_copy.make_move(start, end, ep)
        print('move: ', move_num)
        game_copy.display(start, end)


def minimax(node, depth, maximizingPlayer, moves):
    if depth == 0 or node.is_end_of_game(moves):
        return raw_material(node.pos)
    if maximizingPlayer:
        value = -500
        for move in node.get_legal_moves():
            start, end = move
            x1, y1 = start
            x2, y2 = end
            # Check if move is an en passant capture
            if node.en_passant is not None:
                x3, y3 = node.en_passant
                if (node.pos[y1][x1] == 'P' or node.pos[y1][x1] == 'p') and \
                        x2 == x3 and y2 == y3:
                    ep = True
                else:
                    ep = False
            else:
                ep = False
            child_node = copy.deepcopy(node)
            child_node.make_move(start, end, ep)
            value = max(value, minimax(child_node, depth - 1, False, moves))
            return value
    else:
        value = 500
        for move in node.get_legal_moves():
            start, end = move
            x1, y1 = start
            x2, y2 = end
            # Check if move is an en passant capture
            if node.en_passant is not None:
                x3, y3 = node.en_passant
                if (node.pos[y1][x1] == 'P' or node.pos[y1][x1] == 'p') and \
                        x2 == x3 and y2 == y3:
                    ep = True
                else:
                    ep = False
            else:
                ep = False

            value = max(value, minimax(copy.deepcopy(node).make_move(start, end, ep),
                                       depth - 1, True, moves))
            return value


def raw_material(pos):
    """
    Calculates a value of the board based on raw material.
    :param pos: List of lists of the pieces on the board.
    :return: A numerical value.
    """
    # Calculate material value of the pieces
    material_value = 0
    for rank in pos:
        for item in rank:
            if item == 'Q':
                material_value += 9
            elif item == 'q':
                material_value -= 9
            elif item == 'R':
                material_value += 5
            elif item == 'r':
                material_value -= 5
            elif item == 'N':
                material_value += 3
            elif item == 'n':
                material_value -= 3
            elif item == 'B':
                material_value += 3.15
            elif item == 'b':
                material_value -= 3.15
            elif item == 'P':
                material_value += 1
            elif item == 'p':
                material_value -= 1

    return material_value


def evaluate_pos(pos):
    """
    Gives a rough estimate of the value of the board position. Has human
    knowledge input.
    :param pos: The list of the lists of the pieces of board.
    :return: A value between -1 and 1 that determines the value of the position.
    -1 is a certain win for black and 1 is a certain win for white.
    """
    evaluation = 0
    evaluation += raw_material(pos)

    return evaluation



