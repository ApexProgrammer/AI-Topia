import pygame
import sys
from game.world import World
from game.ui import UI
from game.config import FPS, TITLE

import menu  # use the refactored menu

class Game:
    def __init__(self):
        pygame.init()
        
        # Get the screen info
        screen_info = pygame.display.Info()
        self.width = screen_info.current_w
        self.height = screen_info.current_h
        
        # Create a maximized window
        self.screen = pygame.display.set_mode((self.width, self.height), pygame.NOFRAME)
        pygame.display.set_caption(TITLE)
        self.clock = pygame.time.Clock()
        
        # Initialize world and UI with proper references
        self.world = World(screen_width=self.width, screen_height=self.height)
        self.ui = UI(self.screen, self.world)
        self.world.set_ui(self.ui)
        
        self.running = True

    def handle_events(self):
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                self.running = False
            elif event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE:
                    self.running = False
            self.ui.handle_event(event)
            self.world.handle_event(event)

    def update(self):
        self.world.update()
        self.ui.update()

    def render(self):
        self.screen.fill((0, 0, 0))  # Clear screen
        self.world.render(self.screen)
        self.ui.render()
        pygame.display.flip()

    def run(self):
        # Transition from menu to game in the same pygame instance
        menu.run_menu(self.screen)
        
        while self.running:
            self.handle_events()
            self.update()
            self.render()
            self.clock.tick(FPS)

        pygame.quit()
        sys.exit()

if __name__ == "__main__":
    game = Game()
    game.run()
