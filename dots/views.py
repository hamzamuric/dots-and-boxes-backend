from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
import json


# TODO: ako preko trenutnog poteza moze da se dodje do necega dobrog, ne znaci da je jednako dobar kao drugi koji dolazi do iste stvari odma
#  zbog ovoga igra dobro na dubinu 1


@csrf_exempt
def index(request):
    data = request.body
    data = json.loads(data)
    difficulty = data['difficultity']
    try:
        move = minimax((data['horizontalLines'], data['verticalLines']), 1, 1, None, None, None)
        print(move)
        return JsonResponse({'error': False, 'side': move[1], 'i': move[2], 'j': move[3]})
    except Exception as e:
        print("ERROR: ", e)
        return JsonResponse({'error': True})


def copy_state(state):
    horizontal_lines = [x for x in [y for y in state[0]]]
    vertical_lines = [x for x in [y for y in state[1]]]
    # horizontal_lines = [elements[:] for elements in state[0]]
    # vertical_lines = [elements[:] for elements in state[1]]
    return horizontal_lines, vertical_lines


def moves(state):
    # mozda bude brze ako ne generisem prvo sve horizontalne pa sve vertikalne
    for i, lines in enumerate(state[0]):
        for j, move in enumerate(lines):
            if move == 0:
                yield 0, i, j
    for i, lines in enumerate(state[1]):
        for j, move in enumerate(lines):
            if move == 0:
                yield 1, i, j


def closes_box(state, side, i, j):
    horizontal_lines_count = len(state[0])
    vertical_lines_count = len(state[1])

    if side == 0:
        if i > 0:
            if state[0][i - 1][j] != 0 and state[1][j][i - 1] != 0 and state[1][j + 1][i - 1] != 0:
                return True
        if i < horizontal_lines_count - 1:
            if state[0][i + 1][j] != 0 and state[1][j][i] != 0 and state[1][j + 1][i] != 0:
                return True
    elif side == 1:
        if i > 0:
            if state[1][i - 1][j] != 0 and state[0][j][i - 1] != 0 and state[0][j + 1][i - 1] != 0:
                return True
        if i < vertical_lines_count - 1:
            if state[1][i + 1][j] != 0 and state[0][j][i] != 0 and state[0][j + 1][i] != 0:
                return True

    return False


def good_for_opponent(state, side, i, j):
    return False
    horizontal_lines_count = len(state[0])
    vertical_lines_count = len(state[1])

    if side == 0:
        if i > 0:
            count = 0
            if state[0][i - 1][j] != 0:
                count += 1
            if state[1][j][i - 1] != 0:
                count += 1
            if state[1][j + 1][i - 1] != 0:
                count += 1
            if count == 2:
                return True
        if i < horizontal_lines_count - 1:
            count = 0
            if state[0][i + 1][j] != 0:
                count += 1
            if state[1][j][i] != 0:
                count += 1
            if state[1][j + 1][i] != 0:
                count += 1
            if count == 2:
                return True

    elif side == 1:
        if i > 0:
            count = 0
            if state[1][i - 1][j] != 0:
                count += 1
            if state[0][j][i - 1] != 0:
                count += 1
            if state[0][j + 1][i - 1] != 0:
                count += 1
            if count == 2:
                return True
        if i < vertical_lines_count - 1:
            count = 0
            if state[1][i + 1][j] != 0:
                count += 1
            if state[0][j][i] != 0:
                count += 1
            if state[0][j + 1][i] != 0:
                count += 1
            if count == 2:
                return True

    return False


def evaluate(state, maximizing, side, i, j):
    if is_end(state):
        return 300 * maximizing, side, i, j

    if closes_box(state, side, i, j):
        return 50 * maximizing, side, i, j

    if good_for_opponent(state, side, i, j):
        return -100 * maximizing, side, i, j

    return 10 * maximizing, side, i, j


def is_end(state):
    for lines in state[0]:
        for line in lines:
            if line == 0:
                return False
    for lines in state[1]:
        for line in lines:
            if line == 0:
                return False
    return True


def max_move(move1, move2):
    return move1 if move1[0] >= move2[0] else move2


def min_move(move1, move2):
    return move1 if move1[0] < move2[0] else move2


def minimax(state, maximizing, depth, side, i, j):
    if depth == 0 or is_end(state):
        return evaluate(state, maximizing, side, i, j)
    if maximizing == 1:
        #            (value, side, i,    j,    move)
        max_player = (-1000, None, None, None, None)
        for side, i, j in moves(copy_state(state)):

            is_maximizing = maximizing
            if not closes_box(state, side, i, j):
                is_maximizing = -is_maximizing

            old_state = state[side][i][j]
            state[side][i][j] = maximizing
            player = minimax(copy_state(state), is_maximizing, depth - 1, side, i, j)
            state[side][i][j] = old_state
            max_player = max_move(max_player, player)

        return max_player
    else:
        #            (value, side, i,    j,    move)
        min_player = (+1000, None, None, None, None)
        for side, i, j in moves(copy_state(state)):

            is_maximizing = maximizing
            if not closes_box(state, side, i, j):
                is_maximizing = -is_maximizing

            old_state = state[side][i][j]
            state[side][i][j] = maximizing
            player = minimax(copy_state(state), is_maximizing, depth - 1, side, i, j)
            state[side][i][j] = old_state
            min_player = min_move(min_player, player)

        return min_player
