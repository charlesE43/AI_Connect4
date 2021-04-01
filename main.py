import numpy as np
import math
import pygame
import sys
import random

ROW_COUNT = 6
COL_COUNT = 7
EVEN = 0
ODD = 1
WINDOW_LENGTH = 4
EMPTY = 0

BLUE = (0,0,255)
BLACK = (0,0,0)
RED = (255,0,0)
YELLOW = (255,255,0)

gameOver = False

player = 0
cpu = 1

p_piece = 1
c_piece = 2

pygame.init()

SQUARESIZE = 100
width = COL_COUNT * SQUARESIZE
height = (ROW_COUNT+1) * SQUARESIZE

size = (width, height)

RADIUS = int(SQUARESIZE/2 - 5)


def createBoard():
    board = np.zeros((ROW_COUNT,COL_COUNT))
    return board

#Drops piece
def putPiece(board, row, col, piece):
    board[row][col] = piece

#Checks if piece can go into this position
def is_valid(board, col):
    return board[ROW_COUNT-1][col] == 0

#returns the next open spot
def get_next_open_spot(board, col):
    for r in range(ROW_COUNT):
        if board[r][col] == 0:
            return r


def print_board(board):
    print(np.flip(board, 0))


def winning_move(board, piece):
    #check horizontals
    for c in range(COL_COUNT-3):
        for r in range(ROW_COUNT):
            if board[r][c] == piece and board[r][c+1] == piece and board[r][c+2] == piece and board[r][c+3] == piece:
                return True

    #check horizontals
    for c in range(COL_COUNT):
        for r in range(ROW_COUNT-3):
            if board[r][c] == piece and board[r+1][c] == piece and board[r+2][c] == piece and board[r+3][c] == piece:
                return True

    #check pos diagnols
    for c in range(COL_COUNT-3):
        for r in range(ROW_COUNT-3):
            if board[r][c] == piece and board[r+1][c+1] == piece and board[r+2][c+2] == piece and board[r+3][c+3] == piece:
                return True

    #check neg diagnols
    for c in range(COL_COUNT-3):
        for r in range(3, ROW_COUNT):
            if board[r][c] == piece and board[r-1][c+1] == piece and board[r-2][c+2] == piece and board[r-3][c+3] == piece:
                return True


def drawBoard(board):
    for c in range(COL_COUNT):
        for r in range(ROW_COUNT):
            if board[r][c] == 0:
                pygame.draw.rect(screen, BLUE, (c * SQUARESIZE, r * SQUARESIZE + SQUARESIZE, SQUARESIZE, SQUARESIZE))
                pygame.draw.circle(screen, BLACK, (
                int(c * SQUARESIZE + SQUARESIZE / 2), int(r * SQUARESIZE + SQUARESIZE + SQUARESIZE / 2)), RADIUS)

    for c in range(COL_COUNT):
        for r in range(ROW_COUNT):
            if board[r][c] == 1:
                pygame.draw.circle(screen, RED, (
                    int(c * SQUARESIZE + SQUARESIZE / 2), height - int(r * SQUARESIZE + SQUARESIZE / 2)), RADIUS)
            elif board[r][c] == 2:
                pygame.draw.circle(screen, YELLOW, (
                    int(c * SQUARESIZE + SQUARESIZE / 2), height - int(r * SQUARESIZE + SQUARESIZE / 2)), RADIUS)
    pygame.display.update()


def eval_window(window, piece):
    score = 0
    opp_piece = p_piece
    if piece == p_piece:
        opp_piece = c_piece


    if window.count(piece) == 4:
        score+=100
    elif window.count(piece) == 3 and window.count(EMPTY) == 1:
        score +=5
    elif window.count(piece) == 2 and window.count(EMPTY) == 2:
        score+=2

    if window.count(opp_piece) == 3 and window.count(EMPTY) == 1:
        score-=4

    return score


def score_pos(board, piece):
    score = 0

    #Center Score
    center_array = [int(i) for i in list(board[:, COL_COUNT//2])]
    ctr_count = center_array.count(piece)
    score +=ctr_count*3

    # Check Horizontals
    for r in range(ROW_COUNT):
        r_array = [int (i) for i in list(board[r, :])]
        for c in range(COL_COUNT-3):
            window = r_array[c:c+WINDOW_LENGTH]
            score+= eval_window(window, piece)

    # Check Verticals
    for c in range(COL_COUNT):
        c_array = [int(i) for i in list(board[:, c])]
        for r in range(ROW_COUNT - 3):
            window = c_array[r:r + WINDOW_LENGTH]
            score += eval_window(window, piece)

    #Positive Diagnols
    for r in range(ROW_COUNT-3):
        for c in range(COL_COUNT-3):
            window = [board[r+i][c+i] for i in range(WINDOW_LENGTH)]
            score += eval_window(window, piece)

    #Negative Diagnols
    for r in range(ROW_COUNT-3):
        for c in range(COL_COUNT-3):
            window = [board[r+3-i][c+i] for i in range(WINDOW_LENGTH)]
            score += eval_window(window, piece)

    return score


def isTermNode(board):
    return winning_move(board, p_piece) or winning_move(board, c_piece) or len(get_valid_locations(board)) == 0

#Minimax alogrithm implemented
def minimax(board, depth, alpha, beta, maxPlayer):
    v_location = get_valid_locations(board)
    is_term = isTermNode(board )
    if depth == 0 or is_term:
        if is_term:
            if winning_move(board, c_piece):
                return (None, 10000000)
            elif winning_move(board, p_piece):
                return (None, -10000000)
            else: #Game over
                return (None, 0)
        else:
            return (None, score_pos(board, c_piece))

    if maxPlayer:
        val = -math.inf
        column = random.choice(v_location)
        for col in v_location:
            row = get_next_open_spot(board, col)
            board_copy = board.copy()
            putPiece(board_copy, row, col, c_piece)
            new_score = minimax(board_copy, depth-1, alpha, beta, False)[1]
            if new_score > val:
                val = new_score
                column = col
            alpha = max(alpha, val)
            if alpha >= beta:
                break
        return column, val
    else: #Minimize
        column = random.choice(v_location)
        val = math.inf
        for col in v_location:
            row = get_next_open_spot(board, col)
            board_copy = board.copy()
            putPiece(board_copy, row, col, p_piece)
            new_score = minimax(board_copy, depth-1, alpha, beta, True)[1]
            if new_score < val:
                val = new_score
                column = col
            beta = min(alpha, val)
            if alpha >= beta:
                break
        return column, val



def get_valid_locations(board):
    valid_locations = []
    for c in range(COL_COUNT):
        if is_valid(board, c):
            valid_locations.append(c)

    return valid_locations


def pick_best_move(board, piece):
    best_score = 0
    valid_locations = get_valid_locations(board)
    best_col = random.choice(valid_locations)
    for c in valid_locations:
        row = get_next_open_spot(board,c)
        tmp_board = board.copy()
        putPiece(tmp_board, row, c, piece)
        score = score_pos(tmp_board, piece)

        if score > best_score:
            best_score = score
            best_col = c

    return best_col


board = createBoard()
screen = pygame.display.set_mode(size)
drawBoard(board)
pygame.display.update()

myFont = pygame.font.SysFont("monospace", 75)

turn = random.randint(player,cpu)


#Game Loop
while not gameOver:

    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            sys.exit()

        if event.type == pygame.MOUSEMOTION:
            pygame.draw.rect(screen, BLACK, (0,0, width, SQUARESIZE))
            xpos = event.pos[0]
            if turn == player:
                pygame.draw.circle(screen, RED, (xpos, int(SQUARESIZE/2)), RADIUS)

        pygame.display.update()

        if event.type == pygame.MOUSEBUTTONDOWN:
            pygame.draw.rect(screen, BLACK, (0, 0, width, SQUARESIZE))
            # Get P1 input
            if turn == player:
                xpos = event.pos[0]
                col = int(math.floor(xpos/SQUARESIZE))

                if is_valid(board, col):
                    row = get_next_open_spot(board, col)
                    putPiece(board, row, col, p_piece)

                    if winning_move(board, p_piece):
                        label = myFont.render("Player 1 wins!!", 1, RED)
                        screen.blit(label, (40,10))
                        gameOver = True

                turn =1
                print_board(board)
                drawBoard(board)


    # Get cpu choice
    if turn == cpu and not gameOver:

        col, minimax_score = minimax(board, 3, -math.inf, math.inf, True)

        if is_valid(board, col):
            row = get_next_open_spot(board, col)
            putPiece(board, row, col, c_piece)

            if winning_move(board, c_piece):
                label = myFont.render("CPU wins!!", 1, YELLOW)
                screen.blit(label, (40, 10))
                gameOver = True

            drawBoard(board)
            turn = 0

            if gameOver:
                pygame.time.wait(3000)
