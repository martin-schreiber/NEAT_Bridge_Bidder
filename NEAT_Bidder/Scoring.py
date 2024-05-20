def get_score_from_result(contract, doubled, declarer, vulnerable, making):
    """
    Calculate the final score for a contract

    Args:
        contract (str): The contract (e.g., '4H', '6NT'). 
        doubled (str): Indicates if the contract was doubled ('X'), redoubled ('XX'), or not doubled ('N').
        declarer (int): The positions of the declarer ('N', 'E', 'S', 'W').
        vulnerable (bool): Indicates whether the declarer's side is vulnerable.
        making (int): The number of tricks made by the declarer's side.

    Returns:
        int: The score for the contract.
    """
    
    # extract suit and tricks needed from contract
    bid = int(contract[0])
    tricks_needed = bid + 6
    suit = contract[1:]
    
    if making >= tricks_needed: # contract made

        trick_score = get_trick_score(suit, tricks_needed, making, doubled, vulnerable)
        insult_score = get_insult(doubled)
        game_bonus = get_game_bonus(vulnerable, doubled, bid, suit)
        slam_bonus = get_slam_bonus(bid, vulnerable)
        
        part_bonus = get_part_bonus(game_bonus, slam_bonus)
    
        final_score = trick_score + insult_score + game_bonus + slam_bonus + part_bonus
    
    else: #taken down

        final_score =  get_undertrick_points(tricks_needed, making, doubled, vulnerable)

    
    return final_score


def get_undertrick_points(tricks_needed, making, doubled, vulnerable):
    """
    Calculate penalty for failing to make the contract. Dont have to hardcode the
    doubled penalties, but CBF. 

    Args:
        tricks_needed (int): The number of tricks needed to make the contract.
        making (int): The number of tricks made.
        doubled (str): Indicates if the contract was doubled ('X'), redoubled ('XX'), or not doubled ('N').
        vulnerable (bool): Indicates whether the declarer's side is vulnerable.

    Returns:
        int: The penalty points for not making the contract.
    """
    # hardcoded penaties
    doubled_penalty = {'X': {False:[100,300,500,800,1100,1400,1700,2000,2300,2600,2900,3200,3500], 
                            True:[200,500,800,1100,1400,1700,2000,2300,2600,2900,3200,3500,3800]},
                        'XX':{False:[200,600,1000,1600,2200,2800,3400,4000,4600,5200,5800,6400,7000],
                            True:[400,1000,1600,2200,2800,3400,4000,4600,5200,5800,6400,7000,7600]}}
    
    if doubled != 'N':
        return -1 * doubled_penalty[doubled][vulnerable][tricks_needed-making-1]
    
    else: 
        #50 or 100 per trick down
        return -1 * (tricks_needed - making ) * (50 + 50*(vulnerable==True))
        

def get_insult(doubled):
    """
    Calculate insult bonus for a doubled or redoubled contract.

    Args:
        doubled (str): Indicates if the contract was doubled ('X'), redoubled ('XX'), or not doubled ('N').

    Returns:
        int: The insult bonus points.
    """

    insult_points = {'N': 0, 'X': 50, 'XX': 100}

    return insult_points[doubled]

def get_trick_numbers(doubled, tricks_needed, made):
    """
    Calculate the number of tricks and overtricks. Overtricks only count in doubled contracts

    Args:
        doubled (str): Indicates if the contract was doubled ('X'), redoubled ('XX'), or not doubled ('N').
        tricks_needed (int): The number of tricks needed to make the contract.
        made (int): The number of tricks made.

    Returns:
        tuple: A tuple containing the number of tricks and overtricks.
    """

    if doubled != 'N':
        overtricks = made - tricks_needed
        return tricks_needed, overtricks

    else:
        return made, 0
    

def get_trick_score(suit, tricks_needed, made, doubled, vulnerable):
    """
    Calculate the score for tricks made in a contract. Each suit has an associated score, 
    which is taken as is, x2 or x4 depending on the double. 

    In vulnerable contracts, overtricks count for extra.

    Args:
        suit (str): The suit of the contract ('C', 'D', 'H', 'S', 'NT').
        tricks_needed (int): The number of tricks needed to make the contract.
        made (int): The number of tricks made.
        doubled (str): Indicates if the contract was doubled ('X'), redoubled ('XX'), or not doubled ('N').
        vulnerable (bool): Indicates whether the declarer's side is vulnerable.

    Returns:
        int: The score for the tricks made.
    """
    overtrick_points = [50,100]
    doubled_mult = {'N': 1, 'X': 2, 'XX': 4}
    trick_score = {'C': 20, 'D': 20, 'H': 30, 'S': 30, 'NT': 30}

    # count score for each trick won over 6 tricks. 
    tricks, overtricks = get_trick_numbers(doubled, tricks_needed, made)
    score = trick_score[suit]*(tricks-6)*doubled_mult[doubled] + overtricks*overtrick_points[vulnerable == True]*doubled_mult[doubled]

    # In NT contracts, the first trick counts for 40, and then subsequent tricks at 30.
    if suit == 'NT':
        score += 10*doubled_mult[doubled]

    return score


def get_game_bonus(vulnerable, doubled, bid, suit):
    """
    Calculate the game bonus based on the contract outcome.
    If the contract (after doubling) has trick points worth 100 or more, 
    the contract is eligible for a game bonus. Bonus level depends on vulnerability.

    Args:
        trick_score (int): The score for the tricks made by the declarer's side.
        vulnerable (bool): Indicates whether the declarer's side is vulnerable.
        doubled (str): Indicates if the contract was doubled ('N' for not doubled, 'X' for doubled, 'XX' for redoubled).
        bid (int): The level of the bid made by the declarer.
        suit (str): The suit of the contract ('C', 'D', 'H', 'S', 'NT').

    Returns:
        int: The game bonus points awarded 
    """

    game_bonus = [300, 500]
    doubled_mult = {'N': 1, 'X': 2, 'XX': 4}
    trick_score = {'C': 20, 'D': 20, 'H': 30, 'S': 30, 'NT': 30}

    bid_score = bid * trick_score[suit] * doubled_mult[doubled]
    if suit == 'NT':
        bid_score += 10 * doubled_mult[doubled]

    if bid_score >= 100:
        return game_bonus[vulnerable == True]

    return 0 



def get_slam_bonus( bid, vulnerable):
    """
    Calculate the slam bonus if the contract bid is a small slam or a grand slam.
    Bonus depends on vulnerability. 
    Doesnt affect game bonus score, but small-slam and grand-slam are exclusive. 

    Args:
        bid (int): The level of the bid made by the declarer.
        vulnerable (bool): Indicates whether the declarer's side is vulnerable.

    Returns:
        int: The slam bonus points awarded for making a small slam or a grand slam.
    """
    slam = [500, 750]
    grandslam = [1000,1500]
    
    needed = bid + 6
    
    if needed == 12: # small slam
        return slam[vulnerable == True]
    elif needed == 13: # grand slam
        return grandslam[vulnerable == True]
    else: 
        return 0
    
def get_part_bonus(game_bonus, slam_bonus):
    """
    You get a part score bonus if you make a contract, but its not a game or slam contract
    
    Args:
        game_bonus (int): The game bonus points awarded for the contract, if any.
        slam_bonus (int): The slam bonus points awarded for the contract, if any.

    Returns:
        int: Returns 50 points as a part score bonus if neither a game nor slam bonus has been awarded; otherwise, returns 0 points.
    """
    if game_bonus == slam_bonus == 0:
        return 50
    else:
        return 0

