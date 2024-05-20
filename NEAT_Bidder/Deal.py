import random


# THESE ARE ALL HELPER FUNCTIONS TO DEAL AND DISPLAY CARDS

# Define a deck of cards
suits = ['S','H','D','C']
values = ['A', 'K', 'Q', 'J', '10', '9', '8', '7', '6', '5', '4', '3', '2']
players = ['N','E','S','W']

bid_options = [level + suit for level in ['1','2','3','4','5','6','7'] for suit in ['C','D','H','S','NT']]

# return a random deal, to 4 players N, E, S W
def random_deal():
    deck = [f"{value}{suit}" for suit in suits for value in values]
    # Shuffle the deck
    random.shuffle(deck)
    # Deal the cards to 4 players
    players_cards = {f"{players[i]}": deck[i*13:(i+1)*13] for i in range(4)}
    # sort each player's hand
    sorted_players_hands = {player: sort_player_hand(cards) for player, cards in players_cards.items()}

    return sorted_players_hands

def sort_player_hand( hand):
        # Define sorting helpers
        suit_priority = {'S':0,'H':1,'D':2,'C':3}
        value_priority = {value: i for i, value in enumerate(values)}

        # Sort function for cards
        def card_sort_key(card):
            # print(card)
            value, suit = card[:-1] , card[-1]
            return (suit_priority[suit], value_priority[value])

        # Sort and return the hand
        return sorted(hand, key=card_sort_key)


# print deal in good format to read
def print_deal(deal):
    # Define the constants
    HANDS = ['N', 'E', 'S', 'W']
    SUITS = ['S', 'H', 'D', 'C']
    RANKS = ['A', 'K', 'Q', 'J', '10', '9', '8', '7', '6', '5', '4', '3', '2']
    HAND_LINES = 13
    FULL_LINE = 80

    # Create the text representation for each line
    text = [[' ' for _ in range(FULL_LINE)] for _ in range(HAND_LINES)]

    for h, hand in enumerate(HANDS):
        if h == 0:
            offset, line = FULL_LINE // 4 - 1, 0  # Reduced offset for N
        elif h == 1:
            offset, line = FULL_LINE // 2, 4
        elif h == 2:
            offset, line = FULL_LINE // 4 - 1, 8  # Reduced offset for S
        else:
            offset, line = 0, 4

        for s, suit in enumerate(SUITS):
            c = offset
            for rank in RANKS:
                
                card = rank + suit
                if card in deal[hand]:
                    if rank == '10':
                        text[line + s][c] = '1'
                        text[line + s][c + 1] = '0'
                        c += 2
                    else:
                        text[line + s][c] = card[0]
                        c += 1

            if c == offset:
                text[line + s][c] = '-'
            
            if h != 3:
                text[line + s] = text[line + s][:c]

    # Print the title and dashes
    print('-' * 80)

    # Print the hand text
    for i in range(HAND_LINES):
        print(''.join(text[i]).rstrip())

    print('-' * 80)
    print("\n")