import random
from DSS_adapter import return_best_contract
from Deal import random_deal
from BidBot import BidBot


class GameState:

    players = ['N', 'E', 'S', 'W']

    def __init__(self, genome1, genome2, config):

        # Variables for bot NN
        self.genome1 = genome1
        self.genome2 = genome2
        self.config = config

        # Initialize game state variables
        self.previous_bids = []
        self.bots = []
        self.scores = []


        self.deal = random_deal()

        # pre-solved deal for testing

        # self.deal = {'N': ['7S', '4S', '2S', '9H', '5H', '2H', '5D', '3D', 'KC', 'JC','10C', '9C', '5C'],
        #      'E': ['9S', '5S', '3S', 'AH', 'KH', '8H', '7H', 'JD', '9D', '7D', '2D', '7C', '4C'],
        #      'S': ['KS', 'JS', '10S', 'QH', 'JH', '6H', 'KD', 'QD', '8D', 'AC', 'QC', '8C', '2C'],
        #      'W': ['AS', 'QS', '8S', '6S', '10H', '4H', '3H', 'AD', '10D', '6D', '4D', '6C', '3C']}
        
        self.next_player = random.randint(0, 3)

        self.vulnerable = random.choice(['none', 'N/S', 'E/W', 'BOTH'])


        # N, S bots get Genome1, E, W bots get Genome2
        for Player in self.deal:
            if Player in ['N', 'S']:
                
                genome = self.genome1
            else:
                
                genome = self.genome2

            self.register_bot(BidBot(Player, self.vulnerable, self.deal[Player], genome, self.config))

    
    # 
    def add_bid(self):
        # promt next player for a bid
        player = self.players[self.next_player]
        bid = self.bots[self.next_player].choose_bid()

        # add bid to bids and get new next player
        player_and_bid = [player,bid]
        self.previous_bids.append(player_and_bid)
        # next player is:
        self.next_player = (self.next_player + 1) % 4

        # Update the state in the bots
        for BidBot in self.bots:
            BidBot.update_previous_bids(player_and_bid)
    

    def register_bot(self, BidBot):
        self.bots.append(BidBot)

    # how many PASS bids have occurred
    def pass_count(self):
        bids = self.previous_bids
        if len(bids) > 0:
            count = 0
            index = len(bids) - 1
            while bids[index][1] == 'PASS' and index >= 0:
                index -= 1
                count += 1
            return count
        return 0
    
    # 3 passes in a row ends the game
    def bidding_is_finished(self):
        return len(self.previous_bids) > 3 and self.pass_count() >= 3
    

    # compare each bot to the score associated with ideal play 
    def calculate_scores(self):

        best_team, best_contract , best_score = return_best_contract(self.deal, self.vulnerable)
        # print(f"best: {best_contract} for {best_score}")

        for BidBot in self.bots:
            # get each bots score
            bot_score = BidBot.get_score(self.deal)
            best_score_temp = best_score

            # if the bot is defending, its best possible score is negative
            if BidBot.get_team() != best_team:
                best_score_temp *= -1


            # total difference from best score
            score_diff = -1 * abs(best_score_temp - bot_score)
            
            self.scores.append(score_diff)
            

        return self.scores     

    # finds player and bid from the previous bids
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

    # getters and setters for testing   
    def get_next_player(self):
        return self.players[self.next_player]
    
    def get_vulnerability(self):
        return self.vulnerable
    
    def get_previous_bids(self):
        return self.previous_bids
    
    def set_deal(self, deal):
        self.deal = deal

    def get_deal(self):
        return self.deal
    # ----------------------------------------------

    
    def print_hands(self):
        for Player in self.deal:
            print(f"{Player}: {self.deal[Player]}")


    # for printing final scores in a game
    def print_scores(self):
        best_team, best_contract , best_score = return_best_contract(self.deal, self.vulnerable)
        print(f"best: {best_contract} by {best_team} for {best_score}")

        # print actual last played contract
        player, contract, doubled = self.get_last_bid()

        if doubled == 'N':
            print(f"Contract played: {contract} by {player}")
        else:
            print(f"Contract played: {contract}{doubled} by {player}")

        bot_scores = []
        diff = []
        for BidBot in self.bots:
            # get each bots score
            bot_score = BidBot.get_score(self.deal)
            bot_scores.append(bot_score)
            best_score_temp = best_score
            # if the bot is defending, its best possible score is negative
            if BidBot.get_team() != best_team:
                best_score_temp *= -1


            # total difference from best score
            score_diff = bot_score - best_score_temp
            
            diff.append(score_diff)

        
        print(f"scores: {bot_scores}")
        print(f"diff from ideal: {diff}")




