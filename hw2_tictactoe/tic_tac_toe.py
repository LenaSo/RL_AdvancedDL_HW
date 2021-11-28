import copy
import numpy as np

def board_empty_spaces(board):
    res = np.where(board == 0)
    #return np.array([ (i, j) for i, j in zip(res[0], res[1]) ])
    return np.column_stack((res[0], res[1]))

def get_actions(state):
    board, cur_turn = state
    actions = board_empty_spaces(board)
    return actions

def board_get_hash(board):
    n_cols, n_rows = board.shape
    #hash = ''.join(['%s' % (x+1) for x in board.reshape(n_rows * n_cols)])
    hash = (3**np.arange(n_cols * n_rows) * (1 + board.reshape(n_rows * n_cols))).sum()
    return hash


def board_print(board):
    n_cols, n_rows = board.shape
    print('╭', ('───┬' * n_cols)[:-1], '╮', sep='')
    for i in range(0, n_rows):
        if i != 0:
            print('├', ('───┼' * n_cols)[:-1], '┤', sep='')
        out = '│ '
        for j in range(0, n_cols):
            if board[i, j] == 1:
                token = 'x'
            if board[i, j] == -1:
                token = 'o'
            if board[i, j] == 0:
                token = ' '
            out += token + ' │ '
        print(out, sep='')
    print('╰', ('───┴' * n_cols)[:-1], '╯', sep='')

    
def check_n_win(board, cur_p, n_win):
    # проверим выигрыш
    n_cols, n_rows = board.shape
    cur_marks = np.where(board == cur_p)
    win = False
    for i,j in np.column_stack((cur_marks[0], cur_marks[1])): 
    #for i,j in zip(cur_marks[0], cur_marks[1]):
        if i <= n_rows - n_win:
            if np.all(board[i : i + n_win, j] == cur_p):
                win = True
        if not win:
            if j <= n_cols - n_win:
                if np.all(board[i, j : j + n_win] == cur_p):
                    win = True
        if not win:
            if i <= n_rows - n_win and j <= n_cols - n_win:
                if np.all(np.array([ board[i + k, j + k] == cur_p 
                                    for k in range(n_win) ])):
                    win = True
        if not win:
            if i <= n_rows - n_win and j >= n_win - 1:
                if np.all(np.array([ board[i + k, j - k] == cur_p 
                                    for k in range(n_win) ])):
                    win = True
        if win:
            break
    return win
       
    
class TicTacToe:
    def __init__(self, n_rows=3, n_cols=3, n_win=3):
        self.n_rows = n_rows
        self.n_cols = n_cols
        self.n_win = n_win

        self.reset()
        
    def reset(self):
        self.board = np.zeros((self.n_rows, self.n_cols), dtype=np.int32)
        self.cur_turn = 1
        return self.get_state()
    
    def get_state(self):
        return self.board.copy(), self.cur_turn 

    def step(self, action):
        if self.board[action[0], action[1]] != 0:
            print('!!!!!Unavaliable action', action, self.board)
            return self.get_state(), -10, True
        
        self.board[action[0], action[1]] = self.cur_turn
        
        reward = 0
        done = False
        if check_n_win(self.board, self.cur_turn, self.n_win):
            reward = self.cur_turn
            done = True
        elif len(board_empty_spaces(self.board)) == 0:
            done = True

        self.cur_turn = -self.cur_turn
        
        return self.get_state(), reward, done
