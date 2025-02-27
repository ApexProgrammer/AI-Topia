import unittest
from game.world import World

class TestScoring(unittest.TestCase):
    def setUp(self):
        self.world = World()

    def test_initial_score(self):
        """Test that initial score is calculated correctly"""
        initial_colonists = len(self.world.colonists)
        expected_score = (initial_colonists * 100) + int(self.world.treasury / 100)
        self.assertEqual(self.world.calculate_score(), expected_score)

    def test_score_with_population_change(self):
        """Test score changes with population"""
        initial_score = self.world.calculate_score()
        
        # Add a colonist (this is a simplified test - in reality you'd use proper colonist creation)
        initial_len = len(self.world.colonists)
        self.world.colonists.append(self.world.colonists[0].__class__(0, 0, self.world))
        
        new_score = self.world.calculate_score()
        self.assertEqual(new_score, initial_score + 100)

    def test_score_with_treasury_change(self):
        """Test score changes with treasury"""
        initial_score = self.world.calculate_score()
        
        # Add 1000 to treasury (should add 10 points)
        self.world.treasury += 1000
        new_score = self.world.calculate_score()
        self.assertEqual(new_score, initial_score + 10)

if __name__ == '__main__':
    unittest.main()
