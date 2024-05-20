from Deal import print_deal
import neat
import numpy as np
import pickle
import os
from GameState import GameState


# Use the genome to bid
def eval_genomes(genomes, config):
    
    for (genome_id1, genome1), (genome_id2, genome2) in zip(genomes[0::2], genomes[1::2]):
        
        trials = 20
        sums = [0,0,0,0]

        for _ in range(trials):
            # start a game with 2 genome 

            game = GameState(genome1, genome2, config)

            # play the game
            while game.bidding_is_finished() == False:
                game.add_bid()

            score = game.calculate_scores()
            for i in range(4):
                sums[i] += score[i]
        
        # compute average difference from perfect play
        averages = [s / trials for s in sums]
        print(f"average difference from best score: {averages[0]}")

        # feedback the fitness to the genome
        genome1.fitness = averages[0]
        genome2.fitness = averages[1]

        



# Load the configuration file
config_path = "config-feedforward"
config = neat.config.Config(neat.DefaultGenome, neat.DefaultReproduction,
                            neat.DefaultSpeciesSet, neat.DefaultStagnation,
                            config_path)

def run_neat():
    # Create the population
    population = neat.Population(config)

    # Add a reporter 
    population.add_reporter(neat.StdOutReporter(True))
    stats = neat.StatisticsReporter()
    population.add_reporter(stats)

    # Run the NEAT algorithm
    winner = population.run(eval_genomes, 100)

    # Save the winning genome
    with open('best_genome.pkl', 'wb') as f:
        pickle.dump(winner, f)

    return winner

def load_winner():
    with open('best_genome.pkl', 'rb') as f:
        winner = pickle.load(f)
    return winner

def play_game_with_winner(winner, config):

    game_state = GameState(winner,winner, config)
    
    # print game details and show cards
    print(f"\nVulnerability: {game_state.get_vulnerability()}")
    deal = game_state.get_deal()
    print_deal(deal)

    # play game
    while game_state.bidding_is_finished() == False:
        game_state.add_bid()

    # print bidding sequence
    print(f"\nBidding went: {game_state.get_previous_bids()}")

    # print scores for reference 
    game_state.calculate_scores()
    game_state.print_scores()


# Check if a saved genome exists
if os.path.exists('best_genome.pkl'):
    print("Loading saved genome...")
    winner = load_winner()
else:
    print("Training new genome...")
    winner = run_neat()

# Create the neural network from the winning genome
print("Playing game with winning genome...")

play_game_with_winner(winner, config)

