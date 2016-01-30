import unittest

from mock import patch

from games import GameWithOneMove, GameWithTwoMoves, SimpleDiceRollingGame
from mcts import MCTS


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
