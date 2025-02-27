import unittest
from game.world import World

class TestInitialColony(unittest.TestCase):
    def setUp(self):
        self.world = World()

    def test_initial_colony_setup(self):
        """Test that colony starts with correct initial setup"""
        # Test initial colonist count
        self.assertEqual(len(self.world.colonists), 10, "Colony should start with exactly 10 colonists")

        # Test initial buildings
        government_buildings = [b for b in self.world.buildings if b.building_type == 'government']
        self.assertEqual(len(government_buildings), 1, "Should have exactly 1 government building")
        
        # Verify government building is in center
        gov_building = government_buildings[0]
        center_x = self.world.current_size // 2
        center_y = self.world.current_size // 2
        gov_grid_x, gov_grid_y = self.world.get_grid_position(gov_building.x, gov_building.y)
        self.assertEqual((gov_grid_x, gov_grid_y), (center_x, center_y), "Government building should be in center")

        # Test that only allowed initial buildings exist
        allowed_buildings = {'government', 'farm', 'quarry', 'woodcutter'}
        building_types = {b.building_type for b in self.world.buildings}
        self.assertTrue(building_types.issubset(allowed_buildings), 
                       "Only government, farm, quarry, and woodcutter should exist initially")

if __name__ == '__main__':
    unittest.main()