from collections import namedtuple
from copy import copy
import unittest

from mock import patch

from mcts import MCTS


class GameWithOneMove(object):
    State = namedtuple('GameWithOneMoveState',
                       'winner, current_player')

    @classmethod
    def initial_state(cls):
        return cls.State(winner=None, current_player=1)

    @classmethod
    def get_moves(cls, state):
        if state.winner:
            return (False, [])
        else:
            return (False, ['win'])

    @classmethod
    def apply_move(cls, state, move):
        if move != 'win':
            raise ValueError('Invalid move')
        new_state = state._replace(winner=state.current_player)
        return new_state

    @classmethod
    def get_winner(cls, state):
        return state.winner

    @classmethod
    def current_player(cls, state):
        return state.current_player


class GameWithTwoMoves(object):
    State = namedtuple('GameWithOneMoveState',
                       'board, winner, current_player')

    @classmethod
    def initial_state(cls):
        return cls.State(board=[0, 0], winner=None, current_player=1)

    @classmethod
    def get_moves(cls, state):
        return (False, [position for position, player in enumerate(state.board)
                        if player == 0])

    @classmethod
    def apply_move(cls, state, move):
        if state.board[move] != 0:
            raise ValueError('Invalid move')
        new_board = copy(state.board)
        new_board[move] = state.current_player
        new_state = state._replace(current_player=state.current_player + 1,
                                   board=new_board)
        if move == 1:
            new_state = new_state._replace(winner=state.current_player)
        return new_state

    @classmethod
    def get_winner(cls, state):
        return state.winner

    @classmethod
    def current_player(cls, state):
        return state.current_player


class SimpleDiceRollingGame(object):
    State = namedtuple('SimpleDiceRollingGameState',
                       'score, winner, round, dice_to_roll')
    die_roll_outcome = range(1, 7)

    @classmethod
    def initial_state(cls):
        return cls.State(score=0,
                         winner=None,
                         dice_to_roll=0,
                         round=0)

    @classmethod
    def get_moves(cls, state):
        if state.round == 2:
            return (False, [])

        if state.round == 0:
            return (False, [0, 1, 2])

        elif state.dice_to_roll == 0:
            return (True, [0])
        elif state.dice_to_roll == 1:
            return (True, cls.die_roll_outcome)
        elif state.dice_to_roll == 2:
            return (True, [x + y
                           for x in cls.die_roll_outcome
                           for y in cls.die_roll_outcome])

    @classmethod
    def apply_move(cls, state, move):
        new_state = state
        if state.round == 0:
            new_state = new_state._replace(dice_to_roll=move)

        if state.round == 1:
            new_state = new_state._replace(score=state.score + move)
            if new_state.score > 5:
                new_state = new_state._replace(winner=1)
            else:
                new_state = new_state._replace(winner=2)

        new_state = new_state._replace(round=state.round + 1)
        return new_state

    @classmethod
    def get_winner(cls, state):
        return state.winner

    @classmethod
    def current_player(cls, state):
        return 1


class TestMCTS(unittest.TestCase):
    def test_game_with_one_move(self):
        move, root = MCTS(GameWithOneMove).get_move_and_root(100)
        self.assertEqual(move, 'win')
        self.assertEqual(root.children[0].wins_by_player[1], 100)

    def test_game_with_two_possible_moves(self):
        move, root = MCTS(GameWithTwoMoves).get_move_and_root(100)
        self.assertEqual(root.children[0].move, 0)
        self.assertEqual(root.children[0].wins_by_player[1], 0)
        self.assertIsNone(root.children[0].winner)
        self.assertEqual(root.children[0].children[0].winner, 2)
        self.assertEqual(root.children[0].children[0].wins_by_player,
                         {2: root.children[0].children[0].visits})
        self.assertEqual(root.children[1].move, 1)
        self.assertEqual(root.children[1].winner, 1)
        self.assertEqual(root.children[1].wins_by_player,
                         {1: root.children[1].visits})
        self.assertEqual(move, 1)

    def test_random_moves_selected_randomly(self):
        with patch('mcts.choice') as mock_choice:
            # always choose the first item in random choices
            # (lowest die rolls in our silly game)
            mock_choice.side_effect = lambda items: items[0]
            move, root = MCTS(SimpleDiceRollingGame).get_move_and_root(100)
            # because the player chooes to roll no dice it always loses
            self.assertEqual(root.children[0].wins_by_player[1], 0)
            self.assertEqual(root.children[1].wins_by_player[1], 0)
            self.assertEqual(root.children[2].wins_by_player[1], 0)
            self.assertEqual(root.wins_by_player[1], 0)

        with patch('mcts.choice') as mock_choice:
            mock_choice.side_effect = lambda items: items[-1]
            move, root = MCTS(SimpleDiceRollingGame).get_move_and_root(100)
            # 100 simulations should be enough time for UCB1 to converge on
            # the always winning choice given our loaded dice
            self.assertEqual(move, 2)
            # because the player chooses the highest die roll the player wins
            # every time it rolls two dice
            self.assertEqual(root.children[2].wins_by_player[1],
                             root.children[2].visits)
