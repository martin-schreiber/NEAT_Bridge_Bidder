import ctypes
from ctypes import c_int, c_uint, POINTER
from Scoring import get_score_from_result
import os
"""This is a set of helper functions to calculate the best possible contract from any given deal
It uses the Double Dummy Solver (DDS) algorithm, defined and implemented by Bo Haglund / Soren Hein 2014-2018.
https://github.com/dds-bridge/dds/blob/develop/README.md

The DDS is implemented in C++ and provides an interface to the functions in libdds.so
"""

# 

# IMPORTANT: This is set up to run on a linux system, this section should change to run on any other system
# Define the path to the shared library
lib_path = os.path.abspath('./dds/src/libdds.so')
# Load the shared library
libdds = ctypes.CDLL(lib_path)

# Constants
DDS_HANDS = 4
DDS_SUITS = 4
DDS_STRAINS = 5

# Define the ddTableDeal struct
class ddTableDeal(ctypes.Structure):
    _fields_ = [("cards", c_uint * DDS_SUITS * DDS_HANDS)]

tableDeal = ddTableDeal()

# Define the ddTableResults struct
class ddTableResults(ctypes.Structure):
    _fields_ = [("resTable", c_int * DDS_HANDS * DDS_STRAINS)]

tableResults = ddTableResults()

# Define the CalcDDtable function prototype
libdds.CalcDDtable.argtypes = (ddTableDeal, POINTER(ddTableResults))
libdds.CalcDDtable.restype = c_int


# Constants for the card ranks
card_ranks = {
    '2': 0x0004, '3': 0x0008, '4': 0x0010, '5': 0x0020,
    '6': 0x0040, '7': 0x0080, '8': 0x0100, '9': 0x0200,
    'T': 0x0400, 'J': 0x0800, 'Q': 0x1000, 'K': 0x2000, 'A': 0x4000
}

# Constants for the suits
suits = {'S': 0, 'H': 1, 'D': 2, 'C': 3, 'NT': 4}

# Constants for hands
hands = {'N': 0, 'E': 1, 'S': 2, 'W': 3}


# ------------------------------------------------------------------



# Function to convert initial deal format to CalcDDtable.cpp format
def convert_initial_to_DDS_format(initial):
    # Initialize a 2D list for deal with zeros
    deal = [[0 for _ in range(4)] for _ in range(4)]
    
    # Iterate over each hand and its cards in the initial dictionary
    for hand, cards in initial.items():
        # Iterate over each card in the hand
        for card in cards:
            # Ensure '10' is represented as 'T'
            rank_char = 'T' if card.startswith('10') else card[0]
            
            # Ensure we have a valid rank character
            if rank_char not in card_ranks:
                raise ValueError(f"Invalid card rank: {rank_char}")
            
            rank = card_ranks[rank_char]  # Get the bit value for the card rank
            suit = suits[card[-1]]        # Get the suit index (0 for 'S', 1 for 'H', etc.)
            hand_idx = hands[hand]        # Get the hand index (0 for 'N', 1 for 'E', etc.)
            deal[suit][hand_idx] |= rank  # Set the corresponding bit in the deal structure
    
    return deal


def getExpectedTricks(initial, dealer, contract):
    return getFullResults(initial).resTable[suits[contract]][hands[dealer]]




def getFullResults(initial):

    # Get DDS format
    deal = convert_initial_to_DDS_format(initial)

    # add values to appropriate struct
    for h in range(DDS_HANDS):
        for s in range(DDS_SUITS):
            tableDeal.cards[h][s] = deal[s][h]



    # Call the function from the libdds.so library
    result = libdds.CalcDDtable(tableDeal, ctypes.byref(tableResults))

    
    

    return tableResults

def return_best_contract(deal, vuln):
    full_results = getFullResults(deal)

    player, contract , score = find_max(full_results,vuln)

    # print(f"highest ideal bid: {contract} by {player} for a score of: {score}")

    if player in ['N','S']:
        team = ['N','S']
    else: 
        team = ['E', 'W']
    return team, contract , score


# find the best possible score for each contract
def find_max(table, vuln):
    best_value = -float('inf')
    best_player = None
    best_contract = None

    suits = ['S','H','D','C','NT']
    players = ['N','E','S','W']




    for strain in range(DDS_STRAINS):
        for hand in range(DDS_HANDS):

            entry = table.resTable[strain][hand]
            if entry > 6:
                
                contract = str(entry-6) + suits[strain]
                doubled = 'N'
                declarer = players[hand]

                if vuln == 'BOTH':
                    vulnerable = True
                else: 
                    vulnerable = declarer in vuln

                making = entry
                
                value = get_score_from_result(contract, doubled, declarer, vulnerable, making)
                

                if value > best_value:
                    best_value = value
                    best_player = declarer
                    best_contract = contract

    return best_player, best_contract, best_value      

    

   
# Function to print the table results
def printTable(table):

    # Define the dcardSuit array for printing suits
    dcardSuit = ['S', 'H', 'D', 'C']

    print(f"{'':>5} {'North':>5} {'South':>5} {'East':>5} {'West':>5}")

    print(f"{'NT':>5} {table.resTable[4][0]:>5} {table.resTable[4][2]:>5} {table.resTable[4][1]:>5} {table.resTable[4][3]:>5}")

    for suit in range(DDS_SUITS):
        print(f"{dcardSuit[suit]:>5} {table.resTable[suit][0]:>5} {table.resTable[suit][2]:>5} {table.resTable[suit][1]:>5} {table.resTable[suit][3]:>5}")
    print()



