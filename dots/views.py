from django.http import JsonResponse, FileResponse
from django.views.decorators.csrf import csrf_exempt
import json
from random import shuffle


@csrf_exempt
def index(request):
    data = request.body
    data = json.loads(data)
    difficulty = data['difficulty']
    try:
        move = minimax((data['horizontalLines'], data['verticalLines']), 1, 4, None, None, None, 0)
        print(move)
        return JsonResponse({'error': False, 'side': move[1], 'i': move[2], 'j': move[3]})
    except Exception as e:
        print("ERROR: ", e)
        return JsonResponse({'error': True})


def moves(state):
    result = []
    for i, lines in enumerate(state[0]):
        for j, move in enumerate(lines):
            if move == 0:
                result.append((0, i, j))
    for i, lines in enumerate(state[1]):
        for j, move in enumerate(lines):
            if move == 0:
                result.append((1, i, j))

    shuffle(result)
    return result


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
    horizontal_lines_count = len(state[0])
    vertical_lines_count = len(state[1])

    if state[side][i][j] != 0:
        return False

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


def evaluate(state, maximizing, side, i, j, current):
    if closes_box(state, side, i, j):
        return current + 20 * maximizing, side, i, j

    if good_for_opponent(state, side, i, j):
        return current - 20 * maximizing, side, i, j

    return current, side, i, j


def minimax(state, maximizing, depth, side, i, j, current):
    if depth == 0 or is_end(state):
        return evaluate(state, maximizing, side, i, j, current)

    if maximizing == 1:
        #            (value, side, i,    j)
        max_player = (-1000, None, None, None)
        for side, i, j in moves(state):

            is_maximizing = maximizing
            if not closes_box(state, side, i, j):
                is_maximizing = -is_maximizing

            value = evaluate(state, maximizing, side, i, j, 0)

            state[side][i][j] = maximizing
            player = minimax(state, is_maximizing, depth - 1, side, i, j, value[0] + current)
            state[side][i][j] = 0
            if player[0] > max_player[0]:
                max_player = (player[0], side, i, j)

        return max_player
    else:
        #            (value, side, i,    j)
        min_player = (1000, None, None, None)
        for side, i, j in moves(state):

            is_maximizing = maximizing
            if not closes_box(state, side, i, j):
                is_maximizing = -is_maximizing

            value = evaluate(state, maximizing, side, i, j, 0)

            state[side][i][j] = maximizing
            player = minimax(state, is_maximizing, depth - 1, side, i, j, value[0] + current)
            state[side][i][j] = 0
            if player[0] < min_player[0]:
                min_player = (player[0], side, i, j)

        return min_player
