#!/usr/local/bin/python3
# /usr/bin/python3
# Set the path to your python3 above

from platform import win32_ver
from gtp_connection import GtpConnection
from board_util import GoBoardUtil
from board import GoBoard


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
        self.weights = None
    
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
                move = GoBoardUtil.generate_random_move(board, board.current_player)
                if not move:
                    return GoBoardUtil.opponent(board.current_player)
                board.play_move(move, board.current_player)

        elif self.policy == 'pattern':
            pass

    def get_move(self, board, color):
        legal_moves = GoBoardUtil.generate_legal_moves(board, color)
        probablity = {}

        if self.selection == 'rr':
            for move in legal_moves:
                self.simulate_move(board, move, color)
        
        elif self.selection == 'ucb':
            pass


def run():
    """
    start the gtp connection and wait for commands.
    """
    board = GoBoard(7)
    con = GtpConnection(Go0(), board)
    con.start_connection()


if __name__ == "__main__":
    run()
