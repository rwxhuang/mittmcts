# from six.moves import input

from mittmcts import MCTS, Draw
from test.games import PhantomTicTacToe


def main():
    state = PhantomTicTacToe.initial_state()
    while True:
        if state.winner:
            PhantomTicTacToe.print_board(state)
            if state.winner is Draw:
                print('Draw!')
            elif state.winner:
                print(state.winner + ' wins')
            break
        if state.current_player == 'X':
            while True:
                PhantomTicTacToe.print_board(state)
                try:
                    move = int(input('Move:'))
                    state = PhantomTicTacToe.apply_move(state, move)
                    break
                except ValueError:
                    print('That is not a legal move')
        else:
            result = (MCTS(PhantomTicTacToe, state)
                      .get_simulation_result(10000))
            state = PhantomTicTacToe.apply_move(state, result.move)


if __name__ == '__main__':
    main()
