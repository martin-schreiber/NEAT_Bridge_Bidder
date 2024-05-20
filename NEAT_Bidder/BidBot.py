import random
import neat
from DSS_adapter import getExpectedTricks
from Scoring import get_score_from_result
from Deal import bid_options as master_options

class BidBot:

    # variables for encoding input layer
    all_bids = ['PASS', 'X', 'XX', '1C', '1D', '1H', '1S', '1NT', '2C', '2D', '2H', '2S', '2NT', '3C', '3D', '3H', '3S', '3NT', '4C', '4D', '4H', '4S', '4NT', '5C', '5D', '5H', '5S', '5NT', '6C', '6D', '6H', '6S', '6NT', '7C', '7D', '7H', '7S', '7NT']
    ranks = ['2', '3', '4', '5', '6', '7', '8', '9', '10', 'J', 'Q', 'K', 'A']
    suits = ['C', 'D', 'H', 'S']
    players = ['N', 'E', 'S', 'W']
    rank_to_int = {rank: i for i, rank in enumerate(ranks)}
    suit_to_int = {suit: i for i, suit in enumerate(suits)}
    bid_to_int = {bid: i for i, bid in enumerate(all_bids)}
    player_to_int = {player: i for i, player in enumerate(players)}
    # -------------------------------------------------------------

    def __init__(self, name, game_vulnerability, hand, genome, config):

        # Bot details
        self.name = name
        self.game_vulnerability = game_vulnerability

        if game_vulnerability == 'BOTH':
            self.vulnerability = True
        else: 
            self.vulnerability = name in game_vulnerability
        if self.name in ['N','S']:
            self.my_team = ['N','S']
        else:
            self.my_team = ['E','W']
        self.hand = hand

        # game state
        self.previous_bids = []

        # bid has form {bid: {valid: , priority:}}
        self.possible_bids  = {bid: {'valid': True, 'priority': 1} for bid in self.all_bids}

        # Bidding NN 
        self.genome = genome
        self.net = neat.nn.FeedForwardNetwork.create(self.genome, config)
        genome.fitness = 0.0
        
    # returns my score based on the final contract 
    def get_score(self, deal):

        # find the played contract
        declarer, contract , doubled = self.get_last_bid()

        # determine vulnerability of contract holder
        if declarer in self.my_team:
            vuln = self.vulnerability 
        else:
            if self.game_vulnerability == 'BOTH':
                vuln = True
            else: 
                vuln = declarer in self.game_vulnerability
        
        # calculate expected score of played contract

        if contract == 'PASS':
            score = 0
        else:
            suit = contract[1:]
            # get expected result of contract
            expected = getExpectedTricks(deal, declarer, suit)
            
            # get score from expected result
            declarer_score = get_score_from_result(contract,doubled,declarer,vuln,expected)
            
            # determine if score is a penalty or not
            if declarer in self.my_team:
                score = declarer_score
                
            else:
                score = -1*declarer_score

        return score
    


    
    # adds a bid from another bot
    def update_previous_bids(self, bid):
        self.previous_bids.append(bid)
    
    
        
    # get only the currently valid bids
    def get_valid_bids(self):
        valid_bids = {bid: valid for bid, valid in self.possible_bids.items() if valid['valid']}
        return valid_bids
    
    # choose a bid from the list of valid bids
    def choose_bid(self):

        # work out which are valid
        self.set_valid_bids()   
        self.assign_priorities()
        bids = self.get_valid_bids()
        
        # select bid with highest priority
        highest_priority_bid = max(bids, key=lambda bid: bids[bid]['priority'])

        return highest_priority_bid
    

    def encode_card(self,card):
        suit = card[-1]
        rank = card[:-1]
        return [self.rank_to_int[rank], self.suit_to_int[suit]]
    
    def encode_bid(self, bid):
        player = self.player_to_int[bid[0]]
        bid_int = self.bid_to_int[bid[1]]
        return [player, bid_int]

    # encode vulnerability, hand details and previous bids for the input to the net
    def encode_input(self):
        encoded = [int(self.vulnerability)]
        
        for card in self.hand:
            encoded.extend(self.encode_card(card))

        for bid in self.previous_bids:
            encoded.extend(self.encode_bid(bid))

        while len(encoded) < 200:
            encoded.extend([-1])

        return encoded

    # run game details through net and assign priorities to possible bids based on output
    def assign_priorities(self):
        NNinput = self.encode_input()
        NNoutput = self.net.activate(NNinput)
        # print(f"bot: {self.name} with output: {NNoutput}")

        for i, bid in enumerate(self.possible_bids):
            self.possible_bids[bid]['priority'] = NNoutput[i]

        
            


    # find contract and player of last bid
    def get_last_bid(self):
        
        # Move down the list of bids until a bid that isnt PASS, X or XX
        index = len(self.previous_bids) - 1
        while self.previous_bids[index][1] in ['PASS','X','XX'] and index >= 0:
            index -= 1

        last_player = self.previous_bids[index][0]
        last_contract = self.previous_bids[index][1]

        # Move down the list to find the last actual bid
        index = len(self.previous_bids) - 1
        while self.previous_bids[index][1] == 'PASS' and index >= 0:
            index -= 1

        last_bid = self.previous_bids[index][1]
        if last_bid in ['X','XX']:
            doubled = last_bid
        else:
            doubled = 'N'

        return last_player, last_contract, doubled
    

    def set_valid_bids(self):

        bids = ['PASS']
        bid_options = master_options.copy()
        
        # remove the options until you reach the current last bid
        if len(self.previous_bids) > 0:
            last_player, last_bid , doubled = self.get_last_bid()
        
        
            if last_bid != 'PASS':
                while bid_options[0] != last_bid:
                    bid_options.pop(0)
                bid_options.pop(0) # remove current bid

                if self.name in ['N', 'S']:
                    opponents = ['E', 'W']
                else: 
                    opponents = ['N', 'S']

                # determine if doubling is possible
                if last_player in opponents and doubled not in ['X','XX']:
                
                    bids.append('X')

                if last_player not in opponents and doubled == 'X':
                
                    bids.append('XX')
        

        bids.append(bid_options)
        valid_bids =  self.flatten(bids)

        # change valid flag on possible bids
        for bid in self.possible_bids:
            if bid in valid_bids:
                self.possible_bids[bid]['valid'] = True
            else:
                self.possible_bids[bid]['valid'] = False
        
    
    def flatten(self, lst):
        flat_list = []
        for item in lst:
            if isinstance(item, list):
                flat_list.extend(self.flatten(item))
            else:
                flat_list.append(item)
        return flat_list
    
    def get_team(self):
        return self.my_team