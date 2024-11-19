from mittmcts import MCTS, flamegraph
from test.games import PhantomTicTacToe

import numpy as np
import pickle


def main():
    visited_nodes, result = (MCTS(PhantomTicTacToe)
              .get_simulation_result(50000, get_leaf_nodes=True))
    flamegraph(result)
    p0_infosets_to_counts = {}
    p1_infosets_to_counts = {}

    p0_infosets_to_probs = {}
    p1_infosets_to_probs = {}
    print(len(visited_nodes))
    for node in visited_nodes:
        # Get the infoset from the node's moves.
        moves = node.moves

        visits = {move:child_node.visits for move, child_node in node.get_children().items()}

        # Player 0
        if len(moves) % 2 == 0:
            infoset_p0 = '|'
            p0_moves = set()
            for i in range(len(moves)):
                if i % 2 == 0:
                    infoset_p0 = infoset_p0 + moves[i] + ('*' if moves[i] not in p0_moves else '.')
                p0_moves.add(moves[i])
            if infoset_p0 not in p0_infosets_to_counts or not p0_infosets_to_counts[infoset_p0]:
                p0_infosets_to_counts[infoset_p0] = visits
            else:
                try:
                    p0_infosets_to_counts[infoset_p0] = {ix: p0_infosets_to_counts[infoset_p0][ix] + visits[ix] for ix in visits}
                except:
                    print(p0_infosets_to_counts[infoset_p0], visits, "error occured", infoset_p0, 'p0')
        # Player 1
        else:
            infoset_p1 = '|'
            p1_moves = set()
            for i in range(len(moves)):
                if i % 2 == 1:
                    infoset_p1 = infoset_p1 + moves[i] + ('*' if moves[i] not in p1_moves else '.')
                p1_moves.add(moves[i])
            if infoset_p1 not in p1_infosets_to_counts or not p1_infosets_to_counts[infoset_p1]:
                p1_infosets_to_counts[infoset_p1] = visits
            else:
                try:
                    p1_infosets_to_counts[infoset_p1] = {ix: p1_infosets_to_counts[infoset_p1][ix] + visits[ix] for ix in visits}
                except:
                    print(p1_infosets_to_counts[infoset_p1], visits, "error occured", infoset_p1, 'p1')
    for infoset, counts in p0_infosets_to_counts.items():
        total_counts = sum(counts.values())
        prob_dist = np.zeros(9)
        for idx, count in counts.items():
            prob_dist[idx] = count / total_counts
        p0_infosets_to_probs[infoset] = prob_dist
    
    for infoset, counts in p1_infosets_to_counts.items():
        total_counts = sum(counts.values())
        prob_dist = np.zeros(9)
        for idx, count in counts.items():
            prob_dist[idx] = count / total_counts
        p1_infosets_to_probs[infoset] = prob_dist

    with open('data/infoset_prob_dists.pkl', 'wb') as file:
        pickle.dump({'p0': p0_infosets_to_probs, 'p1': p1_infosets_to_probs}, file)
        


if __name__ == '__main__':
    main()
