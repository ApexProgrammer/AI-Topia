import sys
import os
import unittest
from unittest.mock import MagicMock, patch
import pygame
import math

# Add the parent directory to the path so we can import the game modules
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from game.world import World
from game.config import (TILE_SIZE, BUILDINGS_PER_TILE, INITIAL_MAP_SIZE, 
                        EXPANSION_BUFFER)

class TestGridRendering(unittest.TestCase):
    
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
        
        # Record initial size and offset
        self.initial_size = self.world.current_size
        self.initial_offset_x = self.world.offset_x
        self.initial_offset_y = self.world.offset_y
    
    def test_grid_render_all_lines(self):
        """Test that all grid lines are rendered"""
        # For testing the grid lines, we'll use a different approach
        # since pygame's surface is hard to mock correctly
        
        # Store the original pygame.draw.line function
        original_draw_line = pygame.draw.line
        
        # Keep track of how many times draw.line is called
        line_count = 0
        
        # Create a replacement function that counts calls
        def count_line_calls(*args, **kwargs):
            nonlocal line_count
            line_count += 1
            # Don't actually draw anything during the test
            pass
        
        # Replace pygame's draw.line with our counting function
        pygame.draw.line = count_line_calls
        
        try:
            # Create a real surface for the test
            test_surface = pygame.Surface((800, 600))
            
            # Call the render method
            self.world.render(test_surface)
            
            # Calculate expected line count (vertical + horizontal grid lines)
            expected_line_calls = (self.world.current_size + 1) * 2  # Horizontal + Vertical lines
            
            # Check that we have at least the minimum number of expected grid lines
            # In the real implementation, there might be additional decorative lines
            self.assertGreaterEqual(line_count, expected_line_calls, 
                         f"Expected at least {expected_line_calls} grid lines, but only {line_count} were drawn")
        finally:
            # Restore the original function
            pygame.draw.line = original_draw_line
    
    def test_building_placement_after_expansion(self):
        """Test that building placement works correctly after grid expansion"""
        # Get initial position before expansion
        initial_grid_x, initial_grid_y = 5, 5
        initial_pixel_x, initial_pixel_y = self.world.get_pixel_position(initial_grid_x, initial_grid_y)
        
        # Record the initial offset values
        initial_offset_x = self.world.offset_x
        initial_offset_y = self.world.offset_y
        
        # Record grid position
        pre_grid_pos = (initial_grid_x, initial_grid_y)
        
        # Expand the map
        self.world.expand_map()
        
        # After expansion, we need to get the same grid position
        post_expansion_pixel_x, post_expansion_pixel_y = self.world.get_pixel_position(initial_grid_x, initial_grid_y)
        
        # Calculate how much the offset changed
        offset_change_x = self.world.offset_x - initial_offset_x
        offset_change_y = self.world.offset_y - initial_offset_y
        
        # The exact pixel positions will change after expansion, 
        # but pixel positions should be consistent with the offset change
        expected_x = initial_pixel_x + offset_change_x
        expected_y = initial_pixel_y + offset_change_y
        
        # Round to integers for comparison to avoid floating point issues
        self.assertAlmostEqual(post_expansion_pixel_x, expected_x, delta=1,
                             msg="Pixel X position should account for offset change")
        self.assertAlmostEqual(post_expansion_pixel_y, expected_y, delta=1,
                             msg="Pixel Y position should account for offset change")
        
        # A building placed at the same grid coordinates should maintain its grid position
        # after expansion, even though the absolute pixel coordinates might change
        post_grid_x, post_grid_y = self.world.get_grid_position(post_expansion_pixel_x, post_expansion_pixel_y)
        self.assertEqual((post_grid_x, post_grid_y), pre_grid_pos,
                        "Grid positions should remain consistent after expansion")
    
    def test_grid_expansion_adds_outer_layer(self):
        """Test that grid expansion adds a new outer layer to the grid"""
        # Get initial size and center
        initial_size = self.world.current_size
        initial_center_x = initial_size // 2
        initial_center_y = initial_size // 2
        
        # Get center pixel position before expansion
        center_pixel_x, center_pixel_y = self.world.get_pixel_position(initial_center_x, initial_center_y)
        
        # Expand the map
        self.world.expand_map()
        
        # Get new size
        new_size = self.world.current_size
        
        # Calculate expected new center
        # The center should still be at the same pixel position
        new_center_grid_x, new_center_grid_y = self.world.get_grid_position(center_pixel_x, center_pixel_y)
        
        # Assert that the grid expanded in all directions evenly around the center
        expansion_amount = (new_size - initial_size) / 2
        self.assertAlmostEqual(new_center_grid_x, initial_center_x + expansion_amount, delta=1,
                              msg="Grid should expand evenly in X direction")
        self.assertAlmostEqual(new_center_grid_y, initial_center_y + expansion_amount, delta=1,
                              msg="Grid should expand evenly in Y direction")

if __name__ == '__main__':
    unittest.main()