#!/usr/local/bin/python3
# /usr/bin/python3
# Set the path to your python3 above

from platform import win32_ver
from gtp_connection import GtpConnection
from board_util import GoBoardUtil
from board import GoBoard
from math import log, sqrt
import sys
import random


class Go0:
    def __init__(self):
        """
        NoGo player that selects moves randomly from the set of legal moves.

        Parameters
        ----------
        name : str
            name of the player (used by the GTP interface).
        version : float
            version number (used by the GTP interface).
        """
        self.name = "Go0"
        self.version = 1.0
        self.selection = 'rr'
        self.policy = 'random'
        self.simulations = 10
        self.weights = self.open_file('weights')
    
    def open_file(self, file_name):
        weights = dict()
        f = open(file_name, 'r')
        for line in f:
            data = line.split(' ')
            weights[int(data[0])] = float(data[1])
        f.close()

        return weights
    
    def simulate(self, board, move, toplay):
        board_copy = board.copy()
        board_copy.play_move(move, toplay)
        return self.play_game(board_copy)

    def simulate_move(self, board, move, toplay):
        win = 0
        for i in range(self.simulations):
            result = self.simulate(board, move, toplay)
            if result == toplay:
                win += 1
        return win
    
    def play_game(self, board):
        if self.policy == 'random':
            while 1:
                player = board.current_player
                move = GoBoardUtil.generate_random_move(board, player)
                if not move:
                    return GoBoardUtil.opponent(player)
                board.play_move(move, player)

        elif self.policy == 'pattern':
            while 1:
                player = board.current_player
                moves = GoBoardUtil.generate_legal_moves(board, player)
                if len(moves) == 0:
                    return GoBoardUtil.opponent(player)
                
                move_weights = dict()
                weight_sum = 0
                for move in moves:
                    grid = [move+board.NS-1, move+board.NS, move+board.NS+1, move-1, move+1, move-board.NS-1, move-board.NS, move-board.NS+1]
                    weight = 0
                    for i in range(len(grid)):
                        value = board.board[grid[i]]
                        weight += value * (4 ** i)
                    move_weight = self.weights.get(weight)
                    move_weights[move] = move_weight
                    weight_sum += move_weight
                
                for key in move_weights.keys():
                    move_weights[key] = move_weights[key]/weight_sum
                
                prob = random.uniform(0,1)
                for move in move_weights.keys():
                    if prob <= move_weights[move]:
                        board.play_move(move, player)
                        break


    def get_move(self, board, color):
        legal_moves = GoBoardUtil.generate_legal_moves(board, color)
        sims = len(legal_moves) * 10
        probablity = {}
        best = -1
        best_move = None

        if self.selection == 'rr':
            for move in legal_moves:
                wins = self.simulate_move(board, move, color)
                probablity[move] = wins/sims
            for move in probablity.keys():
                if probablity[move] > best:
                    best = probablity[move]
                    best_move = move
            return best_move
        
        elif self.selection == 'ucb':
            C = 0.4
            stats = []
            for i in range(len(legal_moves)):
                stats.append([0,0])
            for n in len(sims):
                max = -1
                max_score = -float("inf")
                for j in range(len(stats)):
                    if stats[j][1] == 0:
                        score = float("inf")
                    else:
                        score = (stats[j][0] / stats[j][1]) + C * sqrt(log(n) / stats[j][1])
                    if score > max_score:
                        max_score = score
                        max = j
                
                result = self.simulate(board, max, color)
                if result == color:
                    stats[max][0] += 1
                stats[max][1] += 1

                max_arm = -1
                max_arm_count = -float("inf")
                for i in range(len(stats)):
                    if stats[i][1] > max_arm_count:
                        max_arm = i
                        max_arm_count = stats[i][1]
                return max_arm

def run():
    """
    start the gtp connection and wait for commands.
    """
    board = GoBoard(7)
    con = GtpConnection(Go0(), board)
    con.start_connection()


if __name__ == "__main__":
    run()
