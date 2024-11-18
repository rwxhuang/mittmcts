from mittmcts import MCTS, flamegraph
from test.games import PhantomTicTacToe


def main():
    result = (MCTS(PhantomTicTacToe)
              .get_simulation_result(20000, get_leaf_nodes=True))
    flamegraph(result)


if __name__ == '__main__':
    main()
