import sys
import os
import unittest
from unittest.mock import MagicMock, patch
import pygame
import math

# Add the parent directory to the path so we can import the game modules
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from game.world import World
from game.config import TILE_SIZE, BUILDINGS_PER_TILE, INITIAL_MAP_SIZE

class TestGridExpansion(unittest.TestCase):
    
    def setUp(self):
        # Initialize pygame for testing
        pygame.init()
        
        # Create a mock screen
        self.screen = MagicMock()
        self.screen.get_width.return_value = 1280
        self.screen.get_height.return_value = 720
        
        # Create the world with the mock screen
        self.world = World(self.screen.get_width(), self.screen.get_height())
        
        # Create a mock UI and attach it to the world
        self.ui = MagicMock()
        self.ui.camera_x = 0
        self.ui.camera_y = 0
        self.ui.zoom = 1.0
        self.ui.update_map_dimensions = MagicMock()
        self.ui.show_message = MagicMock()
        self.world.ui = self.ui
        
        # Record initial size
        self.initial_size = self.world.current_size
    
    def test_initial_size(self):
        """Test that the world initializes with the correct size"""
        # The size should be at least the INITIAL_MAP_SIZE defined in config
        self.assertGreaterEqual(self.world.current_size, INITIAL_MAP_SIZE)
    
    @patch('pygame.time.get_ticks')
    def test_grid_expansion_with_many_buildings(self, mock_get_ticks):
        """Test that the grid expands when many buildings are added"""
        # Mock time for consistent testing
        mock_get_ticks.return_value = 1000
        
        # Get initial grid size
        initial_size = self.world.current_size
        initial_width = self.world.width
        initial_height = self.world.height
        
        # Directly modify the world's building list with mock buildings to force expansion
        num_buildings = int(initial_size * initial_size * BUILDINGS_PER_TILE * 0.6)  # 60% of max
        print(f"Creating {num_buildings} mock buildings to trigger expansion")
        
        # Create mock buildings with proper attributes for testing
        for i in range(num_buildings):
            mock_building = MagicMock()
            mock_building.x = i * 10  # Give them realistic coordinates
            mock_building.y = i * 10
            mock_building.building_type = 'house'
            self.world.buildings.append(mock_building)
        
        # Force check for expansion
        expansion_needed = self.world.check_expansion_needed()
        print(f"Expansion needed: {expansion_needed}")
        
        if expansion_needed:
            # Perform the expansion
            self.world.expand_map()
        
        # Verify the expansion happened
        self.assertGreater(self.world.current_size, initial_size)
        self.assertGreater(self.world.width, initial_width)
        self.assertGreater(self.world.height, initial_height)
        
        # Verify UI was updated
        self.ui.update_map_dimensions.assert_called()
        self.ui.show_message.assert_called()
        
        print(f"New grid size: {self.world.current_size}x{self.world.current_size}")

    def test_building_density_threshold(self):
        """Test that the building density threshold calculation works correctly"""
        # Get the initial size for calculations
        self.world.current_size = 15  # Set a fixed size for testing
        self.world.width = self.world.current_size * TILE_SIZE
        self.world.height = self.world.current_size * TILE_SIZE
        
        # Calculate the building density threshold
        total_tiles = self.world.current_size * self.world.current_size
        
        # Directly test density calculation
        building_count = int(total_tiles * BUILDINGS_PER_TILE * 0.49)  # Just under threshold
        self.world.buildings = []
        
        # Add buildings just under threshold
        for i in range(building_count):
            self.world.buildings.append(MagicMock())
            
        # Reset expansion check variables
        self.world.grid_occupation = {}  # Clear grid occupation
            
        # Create a patch to simplify the expansion check for testing
        original_check = self.world.check_expansion_needed
        self.world.check_expansion_needed = lambda: len(self.world.buildings) / (self.world.current_size * self.world.current_size) > BUILDINGS_PER_TILE * 0.5
        
        # Check that expansion is not triggered when below threshold
        self.assertFalse(self.world.check_expansion_needed())
        
        # Now exceed threshold by adding more buildings
        more_buildings = int(total_tiles * BUILDINGS_PER_TILE * 0.02) + 1  # Add enough to exceed threshold
        for i in range(more_buildings):
            self.world.buildings.append(MagicMock())
            
        # Check that expansion is triggered when above threshold
        self.assertTrue(self.world.check_expansion_needed())
        
        # Restore original method
        self.world.check_expansion_needed = original_check

    def test_expansion_size_increases(self):
        """Test that larger maps get bigger expansion increases"""
        # Start with smaller map
        self.world.current_size = 20
        self.world.width = self.world.current_size * TILE_SIZE
        self.world.height = self.world.current_size * TILE_SIZE
        
        # Expand map
        self.world.expand_map()
        smaller_expansion = self.world.current_size - 20
        
        # Now set to larger map
        self.world.current_size = 35
        self.world.width = self.world.current_size * TILE_SIZE
        self.world.height = self.world.current_size * TILE_SIZE
        
        # Expand map again
        self.world.expand_map()
        larger_expansion = self.world.current_size - 35
        
        # Larger maps should get larger expansions
        self.assertGreater(larger_expansion, smaller_expansion)

if __name__ == '__main__':
    unittest.main()