#!/usr/bin/env python3
import argparse
import atexit
import time

from agents.AlphaBetaPlayer import AlphaBetaAreaPlayer, AlphaBetaPlayer
from agents.MCTSPlayer import MCTS, MCTSPlayer, MCTSTrainer
from isolation import Agent, logger
from run_match_sync import play_sync
from sample_players import GreedyPlayer, MinimaxPlayer, RandomPlayer



def run_backpropagation(args):
    if args.get('save', 1):
        atexit.register(MCTS.save)  # Autosave on Ctrl-C

    agent1 = TEST_AGENTS.get(args['agent'].upper(),    Agent(MCTSTrainer, "MCTSTrainer"))
    agent2 = TEST_AGENTS.get(args['opponent'].upper(), Agent(MCTSTrainer, "MCTSTrainer"))
    if agent1.name == agent2.name:
        agent1 = Agent(agent1.agent_class, agent1.name+'1')
        agent2 = Agent(agent2.agent_class, agent2.name+'2')
    agents = (agent1, agent2)

    scores = {
        agent: []
        for agent in agents
        }
    start_time = time.perf_counter()
    match_id = 0
    while True:
        if args.get('rounds',  0) and args['rounds']  <= match_id:                         break
        if args.get('timeout', 0) and args['timeout'] <= time.perf_counter() - start_time: break

        match_id += 1
        agent_order = ( agents[(match_id)%2], agents[(match_id+1)%2] )  # reverse player order between matches
        winner, game_history, match_id = play_sync(agent_order, match_id=match_id)

        winner_idx = agent_order.index(winner)
        loser      = agent_order[int(not winner_idx)]
        scores[winner] += [ 1 ]
        scores[loser]  += [ 0 ]

        for agent_idx, agent in enumerate(agent_order):
            if callable(getattr(agent.agent_class, 'backpropagate', None)):
                agent.agent_class.backpropagate(agent_idx, winner_idx, game_history)

        if args.get('progress'):
            print('+' if winner == agents[0] else '-', end='', flush=True)

        frequency = args.get('frequency', 100)
        if (  frequency != 0 and match_id % frequency == 0
            or match_id != 0 and match_id == args.get('rounds')
        ):
            message = " match_id: {:4d} | last {} = {:3.0f}% | all = {:3.0f}% | {} vs {}" .format(
                match_id, frequency,
                100 * sum(scores[agents[0]][-frequency:]) / frequency,
                100 * sum(scores[agents[0]]) / len(scores[agents[0]]),
                agents[0].name,
                agents[1].name,
                )
            print(message); logger.info(message)

    if args.get('save', 1):
        MCTS.save()
        atexit.unregister(MCTS.save)


TEST_AGENTS = {
    "RANDOM":    Agent(RandomPlayer,        "Random Agent"),
    "GREEDY":    Agent(GreedyPlayer,        "Greedy Agent"),
    "MINIMAX":   Agent(MinimaxPlayer,       "Minimax Agent"),
    "ALPHABETA": Agent(AlphaBetaPlayer,     "AlphaBeta Agent"),
    "AREA":      Agent(AlphaBetaAreaPlayer, "AlphaBeta Area Agent"),
    "MCA":       Agent(MCTSPlayer,          "MCTS Agent"),
    "MCT":       Agent(MCTSTrainer,         "MCTS Trainer"),
    }
def argparser():
    parser = argparse.ArgumentParser()
    parser.add_argument('-r', '--rounds',     type=int, default=0)
    parser.add_argument(      '--timeout',    type=int, default=0)    # train_mcts() timeout global for
    parser.add_argument('-t', '--time_limit', type=int, default=150)  # play_sync()  timeout per round
    parser.add_argument('-a', '--agent',      type=str, default='MCT')
    parser.add_argument('-o', '--opponent',   type=str, default='MCA')
    parser.add_argument('-f', '--frequency',  type=int, default=100)
    parser.add_argument(      '--progress',   action='store_true')    # show progress bat
    parser.add_argument('-s', '--save',       type=int, default=1)
    return vars(parser.parse_args())

if __name__ == '__main__':
    args = argparser()
    run_backpropagation(args)
