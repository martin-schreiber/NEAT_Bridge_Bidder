# NEAT Bridge Bidder

This project implements an AI for bidding in the game of bridge using the NEAT (NeuroEvolution of Augmenting Topologies) algorithm.

Games of bridge are managed by the observer class GameState, and players are 4 bots in teams of 2. 
Each team uses a different algorithm to bid against each other. 

Best play is evaluated using the Double Dummy Solver (DDS) algorithm, defined and implemented by Bo Haglund / Soren Hein 2014-2018. https://github.com/dds-bridge/dds/blob/develop/README.md

This is provided as a set of functions written in C++, and is used via an adapter for a linux system.


## Files

- `BidBot.py`: Contains the `BidBot` class for bidding
- `config-feedforward`: Configuration file for the NEAT algorithm.
- `Deal.py`: Helper functions to deal and display cards
- `dds`: Directory containing the double dummy solver (DDS) by Bo Haglund / Soren Hein 2014-2018.
- `DSS_adapter.py`: Adapter to interface with the DDS.
- `GameState.py`: Observer to manage state of the bridge game.
- `NEAT_bidder.py`: Main script for training and running the NEAT-based bidder.
- `Scoring.py`: Contains functions for scoring bridge hands.
- `test_scoring.py`: Unit tests for the scoring functions.

## Usage

IMPORTANT: 
Before the bidding AI can be trained, the C++ library to provide the helper functions must be compiled. 
Instructions can be found in dds/README.md

The library should be compiled using the Makefile: dds/src/Makefiles/Makefile_linux_shared

************************************


Bidding AI can be trained by running: 

	python3 NEAT_bidder.py


If there is an existing genome, the game will start, set 4 bots against each other and display the results. 

If there is no genome present, then the NEAT algorithm will run


