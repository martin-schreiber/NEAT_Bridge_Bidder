import unittest
from Scoring import get_score_from_result

class TestBridgeScoring(unittest.TestCase):

    # def get_score_from_result(contract, doubled, declarer, vulnerable, making):

    def test_partscore(self):
        # Testing partscore. 1NT making 9, not vuln, not doubled. 
        self.assertEqual(get_score_from_result('1NT', 'N', 'N', False, 9), 150)
        

    def test_game(self):
        # Testing getting game, doubled into game, and XX into game
        self.assertEqual(get_score_from_result('3NT', 'N', 'N', False, 9), 400)
        self.assertEqual(get_score_from_result('1C', 'N', 'N', False, 13), 190) #test part score even though points are >100
        self.assertEqual(get_score_from_result('2H', 'X', 'N', False, 8), 470)
        self.assertEqual(get_score_from_result('2H', 'X', 'N', False, 8), 470)
        self.assertEqual(get_score_from_result('2C', 'XX', 'N', True, 8), 760)

    def test_slam(self):
        # testing slams
        self.assertEqual(get_score_from_result('6NT', 'N', 'N', False, 12), 990)
        self.assertEqual(get_score_from_result('7D', 'XX', 'N', True, 13), 2660)

    def test_defeated(self):
        self.assertEqual(get_score_from_result('3NT', 'N', 'N', False, 8), -50)
        self.assertEqual(get_score_from_result('3NT', 'X', 'N', False, 0), -2300)
        self.assertEqual(get_score_from_result('3NT', 'XX', 'N', True, 2), -4000)

    def test_declarer(self):
        self.assertEqual(get_score_from_result('2C', 'XX', 'E', True, 8), 760)
        self.assertEqual(get_score_from_result('3NT', 'N', 'W', False, 8), -50)

        


if __name__ == '__main__':
    unittest.main(verbosity=3)
