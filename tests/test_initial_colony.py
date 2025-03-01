import unittest
from game.world import World
from game.config import BUILDING_TYPES, COLONISTS_PER_TILE, BUILDINGS_PER_TILE
from game.entities.colonist import Colonist
from game.entities.building import Building

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

    def test_reproduction_system(self):
        """Test the reproduction system and population growth"""
        initial_population = len(self.world.colonists)
        self.world.handle_reproduction()
        new_population = len(self.world.colonists)
        self.assertGreaterEqual(new_population, initial_population, "Population should increase or stay the same")

    def test_map_expansion(self):
        """Test the map expansion logic"""
        initial_size = self.world.current_size
        self.world.expand_map()
        new_size = self.world.current_size
        self.assertGreater(new_size, initial_size, "Map size should increase after expansion")

    def test_family_housing(self):
        """Test the addition of family housing type"""
        self.assertIn('family_house', BUILDING_TYPES, "Family housing type should be in building types")
        family_house = BUILDING_TYPES['family_house']
        self.assertEqual(family_house['max_occupants'], 6, "Family house should have a max occupancy of 6")

    def test_grid_expansion(self):
        """Test that the grid expands when population and building thresholds are met"""
        # Add colonists to meet the population threshold
        initial_size = self.world.current_size
        for _ in range(int(COLONISTS_PER_TILE * initial_size * initial_size) + 1):
            colonist = Colonist(0, 0, self.world)
            self.world.colonists.append(colonist)
        
        # Add buildings to meet the building threshold
        for _ in range(int(BUILDINGS_PER_TILE * initial_size * initial_size) + 1):
            building = Building(building_type='house', x=0, y=0, world=self.world)
            self.world.buildings.append(building)
        
        # Check if expansion is needed
        self.assertTrue(self.world.check_expansion_needed(), "Grid should expand when population and building thresholds are met")
        
        # Perform expansion
        self.world.expand_map()
        new_size = self.world.current_size
        self.assertGreater(new_size, initial_size, "Grid size should increase after expansion")

if __name__ == '__main__':
    unittest.main()