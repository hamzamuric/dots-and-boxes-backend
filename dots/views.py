from django.http import JsonResponse, FileResponse
from django.views.decorators.csrf import csrf_exempt
import json
from random import shuffle


@csrf_exempt
def index(request):
    data = request.body
    data = json.loads(data)
    difficulty = data['difficulty']
    depth = data['depth']
    h_lines = data['horizontalLines']
    v_lines = data['verticalLines']
    state = (h_lines, v_lines)
    try:
        if difficulty == 0:
            print("Playing easy")
            move = minimax(state, 1, depth, None, None, None)
        elif difficulty == 1:
            print("Playing medium")
            move = alphabeta_medium(state, 1, depth, None, None, None, -1000, 1000)
        else:
            print("Playing hard")
            move = alphabeta(state, 1, depth, None, None, None, 0, -1000, 1000)

        print(f"Depth: {depth}")
        print(move)
        return JsonResponse({'error': False, 'side': move[1], 'i': move[2], 'j': move[3]})
    except Exception as e:
        print("ERROR: ", e)
        return JsonResponse({'error': True})


def moves(state, is_easy=False):
    result = []
    for i, lines in enumerate(state[0]):
        for j, move in enumerate(lines):
            if move == 0:
                result.append((0, i, j))
    for i, lines in enumerate(state[1]):
        for j, move in enumerate(lines):
            if move == 0:
                result.append((1, i, j))

    if not is_easy:
        shuffle(result)
    return result


def closes_box(state, side, i, j):
    horizontal_lines_count = len(state[0])
    vertical_lines_count = len(state[1])

    if side == 0:
        if i > 0 and state[0][i - 1][j] != 0 and state[1][j][i - 1] != 0 and state[1][j + 1][i - 1] != 0:
            return True
        if i < horizontal_lines_count - 1 and state[0][i + 1][j] != 0 and state[1][j][i] != 0 and state[1][j + 1][i] != 0:
            return True
    elif side == 1:
        if i > 0 and state[1][i - 1][j] != 0 and state[0][j][i - 1] != 0 and state[0][j + 1][i - 1] != 0:
            return True
        if i < vertical_lines_count - 1 and state[1][i + 1][j] != 0 and state[0][j][i] != 0 and state[0][j + 1][i] != 0:
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


def evaluate(state, maximizing, side, i, j, current, is_easy=False):
    if closes_box(state, side, i, j):
        return current + 1 * maximizing, side, i, j

    if not is_easy and good_for_opponent(state, side, i, j):
        return current - 1 * maximizing, side, i, j

    return current, side, i, j


def alphabeta_medium(state, maximizing, depth, side, i, j, alpha, beta):
    if depth == 0 or is_end(state):
        return evaluate(state, maximizing, side, i, j, 0)

    if maximizing == 1:
        #            (value, side, i,    j)
        max_player = (-1000, None, None, None)
        for side, i, j in moves(state):

            is_maximizing = maximizing
            if not closes_box(state, side, i, j):
                is_maximizing = -is_maximizing

            state[side][i][j] = maximizing
            player = alphabeta_medium(state, is_maximizing, depth - 1, side, i, j, alpha, beta)
            state[side][i][j] = 0
            if player[0] > max_player[0]:
                max_player = (player[0], side, i, j)
            alpha = max(alpha, max_player[0])
            if beta <= alpha:
                break

        return max_player
    else:
        #            (value, side, i,    j)
        min_player = (1000, None, None, None)
        for side, i, j in moves(state):

            is_maximizing = maximizing
            if not closes_box(state, side, i, j):
                is_maximizing = -is_maximizing

            state[side][i][j] = maximizing
            player = alphabeta_medium(state, is_maximizing, depth - 1, side, i, j, alpha, beta)
            state[side][i][j] = 0
            if player[0] < min_player[0]:
                min_player = (player[0], side, i, j)
            beta = min(beta, min_player[0])
            if beta <= alpha:
                break

        return min_player


def alphabeta(state, maximizing, depth, side, i, j, current, alpha, beta):
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
            player = alphabeta(state, is_maximizing, depth - 1, side, i, j, value[0] + current, alpha, beta)
            state[side][i][j] = 0
            if player[0] > max_player[0]:
                max_player = (player[0], side, i, j)
            alpha = max(alpha, max_player[0])
            if beta <= alpha:
                break

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
            player = alphabeta(state, is_maximizing, depth - 1, side, i, j, value[0] + current, alpha, beta)
            state[side][i][j] = 0
            if player[0] < min_player[0]:
                min_player = (player[0], side, i, j)
            beta = min(beta, min_player[0])
            if beta <= alpha:
                break

        return min_player


def minimax(state, maximizing, depth, side, i, j):
    if depth == 0 or is_end(state):
        return evaluate(state, maximizing, side, i, j, 0, is_easy=True)

    if maximizing == 1:
        #            (value, side, i,    j)
        max_player = (-1000, None, None, None)
        for side, i, j in moves(state, is_easy=True):

            is_maximizing = maximizing
            if not closes_box(state, side, i, j):
                is_maximizing = -is_maximizing

            state[side][i][j] = maximizing
            player = minimax(state, is_maximizing, depth - 1, side, i, j)
            state[side][i][j] = 0
            if player[0] > max_player[0]:
                max_player = (player[0], side, i, j)

        return max_player
    else:
        #            (value, side, i,    j)
        min_player = (1000, None, None, None)
        for side, i, j in moves(state, is_easy=True):

            is_maximizing = maximizing
            if not closes_box(state, side, i, j):
                is_maximizing = -is_maximizing

            state[side][i][j] = maximizing
            player = minimax(state, is_maximizing, depth - 1, side, i, j)
            state[side][i][j] = 0
            if player[0] < min_player[0]:
                min_player = (player[0], side, i, j)

        return min_player
