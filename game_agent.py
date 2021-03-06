"""This file contains all the classes you must complete for this project.

You can use the test cases in agent_test.py to help during development, and
augment the test suite with your own test cases to further test your code.

You must test your agent's strength against a set of agents with known
relative strength using tournament.py and include the results in your report.
"""
import math

class Timeout(Exception):
    """Subclass base exception for code clarity."""
    pass


def custom_score(game, player):
    """Calculate the heuristic value of a game state from the point of view
    of the given player.

    Note: this function should be called from within a Player instance as
    `self.score()` -- you should not need to call this function directly.

    Parameters
    ----------
    game : `isolation.Board`
        An instance of `isolation.Board` encoding the current state of the
        game (e.g., player locations and blocked cells).

    player : object
        A player instance in the current game (i.e., an object corresponding to
        one of the player objects `game.__player_1__` or `game.__player_2__`.)

    Returns
    -------
    float
        The heuristic value of the current game state to the specified player.
    """

    if game.is_loser(player):
        return float("-inf")

    if game.is_winner(player):
        return float("inf")

    return diff_distance_from_mid(game, player)

def within_radius(game, player):
    # The Heuristic function will be (own_moves - opp_moves) * how close to middle
    # This is because since there are no wraparounds at the edge of the board, it
    # is generally better to seek squares in the middle of the board

    # find middle of board
    mid_row = game.width//2
    mid_col = game.height//2

    # distance of present point to middle of square
    player_row, player_col = game.get_player_location(player)

    level = max( abs(mid_row-player_row), abs(mid_col-player_col) )

    own_moves = len(game.get_legal_moves(player))
    opp_moves = len(game.get_legal_moves(game.get_opponent(player)))

    if level > 0:
        # max_side = max(game.width, game.height) // 2
        return float(own_moves - opp_moves) + float(1/level)
    else:
        return float(own_moves - opp_moves)


def own_distance_from_mid(game, player):
    # The Heuristic function will be (own_moves - opp_moves) + 1/distance_from_midpoint_of_player
    # This is because since there are no wraparounds at the edge of the board, it
    # is generally better to seek squares in the middle of the board

    # find middle of board
    mid_row = game.width//2
    mid_col = game.height//2

    # distance of present point to middle of square
    own_row, own_col = game.get_player_location(player)

    row_diff = math.pow(own_row - mid_row, 2)
    col_diff = math.pow(own_col - mid_col, 2)

    own_moves = len(game.get_legal_moves(player))
    opp_moves = len(game.get_legal_moves(game.get_opponent(player)))

    if row_diff+col_diff > 0:
        return float(own_moves - opp_moves) + float( 1/math.sqrt(row_diff + col_diff) ) # The greater the distance from mid the smaller the weight
    else:
        return float(own_moves - opp_moves)


def diff_distance_from_mid(game, player):
    # The Heuristic function will be
    # (own_moves - opp_moves) + 1/distance_from_midpoint_of_player - 1/distance_from_midpoint_of_opponent
    # This is because since there are no wraparounds at the edge of the board, it is generally better to seek squares
    # in the middle of the board if you are the player, and to force the opponent to the edge.

    # find middle of board
    mid_row = game.width//2
    mid_col = game.height//2

    # distance of present point to middle of square
    own_row, own_col = game.get_player_location(player)
    own_row_diff = math.pow(own_row - mid_row, 2)
    own_col_diff = math.pow(own_col - mid_col, 2)

    opp_row, opp_col = game.get_player_location(game.get_opponent(player))
    opp_row_diff = math.pow(opp_row - mid_row, 2)
    opp_col_diff = math.pow(opp_col - mid_col, 2)

    own_moves = len(game.get_legal_moves(player))
    opp_moves = len(game.get_legal_moves(game.get_opponent(player)))

    # weight = 0
    # if (own_row_diff+own_col_diff) > 0:
    #     weight += float( 1/math.sqrt(own_row_diff + own_col_diff) ) # The greater the distance from mid of player the smaller the weight
    # if (opp_row_diff+opp_col_diff) > 0:
    #     weight -= float( 1/math.sqrt(opp_row_diff + opp_col_diff) ) # The greater the distance from mid of opponent the larger the weight

    # The greater the distance from mid of player the smaller the weight
    # The greater the distance from mid of opponent the larger the weight
    weight = math.sqrt(opp_row_diff + opp_col_diff) - math.sqrt(own_row_diff + own_col_diff)

    return float(own_moves - opp_moves) + weight


class CustomPlayer:
    """Game-playing agent that chooses a move using your evaluation function
    and a depth-limited minimax algorithm with alpha-beta pruning. You must
    finish and test this player to make sure it properly uses minimax and
    alpha-beta to return a good move before the search time limit expires.

    Parameters
    ----------
    search_depth : int (optional)
        A strictly positive integer (i.e., 1, 2, 3,...) for the number of
        layers in the game tree to explore for fixed-depth search. (i.e., a
        depth of one (1) would only explore the immediate sucessors of the
        current state.)

    score_fn : callable (optional)
        A function to use for heuristic evaluation of game states.

    iterative : boolean (optional)
        Flag indicating whether to perform fixed-depth search (False) or
        iterative deepening search (True).

    method : {'minimax', 'alphabeta'} (optional)
        The name of the search method to use in get_move().

    timeout : float (optional)
        Time remaining (in milliseconds) when search is aborted. Should be a
        positive value large enough to allow the function to return before the
        timer expires.
    """

    def __init__(self, search_depth=3, score_fn=custom_score,
                 iterative=True, method='minimax', timeout=10.):
        self.search_depth = search_depth
        self.iterative = iterative
        self.score = score_fn
        self.method = method
        self.time_left = None
        self.TIMER_THRESHOLD = timeout

    def get_move(self, game, legal_moves, time_left):
        """Search for the best move from the available legal moves and return a
        result before the time limit expires.

        This function must perform iterative deepening if self.iterative=True,
        and it must use the search method (minimax or alphabeta) corresponding
        to the self.method value.

        **********************************************************************
        NOTE: If time_left < 0 when this function returns, the agent will
              forfeit the game due to timeout. You must return _before_ the
              timer reaches 0.
        **********************************************************************

        Parameters
        ----------
        game : `isolation.Board`
            An instance of `isolation.Board` encoding the current state of the
            game (e.g., player locations and blocked cells).

        legal_moves : list<(int, int)>
            A list containing legal moves. Moves are encoded as tuples of pairs
            of ints defining the next (row, col) for the agent to occupy.

        time_left : callable
            A function that returns the number of milliseconds left in the
            current turn. Returning with any less than 0 ms remaining forfeits
            the game.

        Returns
        -------
        (int, int)
            Board coordinates corresponding to a legal move; may return
            (-1, -1) if there are no available legal moves.
        """

        self.time_left = time_left

        # Perform any required initializations, including selecting an initial
        # move from the game board (i.e., an opening book), or returning
        # immediately if there are no legal moves

        # If no legal moves then return immediately
        if not legal_moves:
            return (-1, -1)

        # In case we run out of time we always have a move handy
        move = legal_moves[0]
        score = self.score(game, self)


        try:
            # The search method call (alpha beta or minimax) should happen in
            # here in order to avoid timeout. The try/except block will
            # automatically catch the exception raised by the search method
            # when the timer gets close to expiring
            if self.iterative:
                depth_counter = 1
                while True:
                    if self.method == 'minimax':
                        score, move = self.minimax(game, depth_counter, True)
                    elif self.method == 'alphabeta':
                        score, move = self.alphabeta(game, depth_counter, float("-inf"), float("inf"), True)
                    depth_counter += 1
            else:
                if self.method == 'minimax':
                    score, move = self.minimax(game, self.search_depth, True)
                elif self.method == 'alphabeta':
                    score, move = self.alphabeta(game, self.search_depth, float("-inf"), float("inf"), True)

        except Timeout:
            # Handle any actions required at timeout, if necessary
            return move

        # Return the best move from the last completed search iteration
        return move

    def minimax(self, game, depth, maximizing_player=True):
        """Implement the minimax search algorithm as described in the lectures.

        Parameters
        ----------
        game : isolation.Board
            An instance of the Isolation game `Board` class representing the
            current game state

        depth : int
            Depth is an integer representing the maximum number of plies to
            search in the game tree before aborting

        maximizing_player : bool
            Flag indicating whether the current search depth corresponds to a
            maximizing layer (True) or a minimizing layer (False)

        Returns
        -------
        float
            The score for the current search branch

        tuple(int, int)
            The best move for the current branch; (-1, -1) for no legal moves

        Notes
        -----
            (1) You MUST use the `self.score()` method for board evaluation
                to pass the project unit tests; you cannot call any other
                evaluation function directly.
        """
        if self.time_left() < self.TIMER_THRESHOLD:
            raise Timeout()

        legal_moves = game.get_legal_moves()

        if ( depth < 1 ) or ( len(legal_moves) == 0 ):
            last_move = game.get_player_location(self)
            last_score = self.score(game, self)
            return last_score, last_move

        elif maximizing_player:
            max_move = legal_moves[0]
            max_score = float("-inf")
            for move in legal_moves:
                new_game = game.forecast_move(move)
                new_score, new_move = self.minimax(new_game, depth-1, False)
                if new_score > max_score:
                    max_score = new_score
                    max_move = move
            return max_score, max_move

        else:
            min_move = legal_moves[0]
            min_score = float("inf")
            for move in legal_moves:
                new_game = game.forecast_move(move)
                new_score, new_move = self.minimax(new_game, depth-1, True)
                if new_score < min_score:
                    min_score = new_score
                    min_move = move
            return min_score, min_move

    def alphabeta(self, game, depth, alpha=float("-inf"), beta=float("inf"), maximizing_player=True):
        """Implement minimax search with alpha-beta pruning as described in the
        lectures.

        Parameters
        ----------
        game : isolation.Board
            An instance of the Isolation game `Board` class representing the
            current game state

        depth : int
            Depth is an integer representing the maximum number of plies to
            search in the game tree before aborting

        alpha : float
            Alpha limits the lower bound of search on minimizing layers

        beta : float
            Beta limits the upper bound of search on maximizing layers

        maximizing_player : bool
            Flag indicating whether the current search depth corresponds to a
            maximizing layer (True) or a minimizing layer (False)

        Returns
        -------
        float
            The score for the current search branch

        tuple(int, int)
            The best move for the current branch; (-1, -1) for no legal moves

        Notes
        -----
            (1) You MUST use the `self.score()` method for board evaluation
                to pass the project unit tests; you cannot call any other
                evaluation function directly.
        """
        if self.time_left() < self.TIMER_THRESHOLD:
            raise Timeout()

        legal_moves = game.get_legal_moves()

        if ( depth < 1 ) or ( len(legal_moves) == 0 ):
            final_row, final_col = game.get_player_location(self)
            final_score = self.score(game, self)
            return final_score, (final_row, final_col)

        elif maximizing_player:
            max_move = legal_moves[0]
            max_score = float("-inf")
            for move in legal_moves:
                new_game = game.forecast_move(move)
                new_score, new_move = self.alphabeta(new_game, depth-1, alpha, beta, False)
                if new_score > max_score:
                    max_score = new_score
                    max_move = move
                alpha = max(alpha, max_score)
                if beta <= alpha:
                    break
            return max_score, max_move

        else:
            min_move = legal_moves[0]
            min_score = float("inf")
            for move in legal_moves:
                new_game = game.forecast_move(move)
                new_score, new_move = self.alphabeta(new_game, depth-1, alpha, beta, True)
                if new_score < min_score:
                    min_score = new_score
                    min_move = move
                beta = min(beta, min_score)
                if beta <= alpha:
                    break
            return min_score, min_move
