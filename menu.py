import sys, subprocess, pygame
import game.config as config  # Adjust config dynamically

pygame.init()
screen = pygame.display.set_mode((config.WINDOW_WIDTH, config.WINDOW_HEIGHT))
pygame.display.set_caption("Colony Sim - Game Menu")

def run_menu(screen):
    font = pygame.font.Font(None, 36)
    clock = pygame.time.Clock()

    # Define adjustable options
    options = [
        {"name": "INITIAL_COLONISTS", "value": config.INITIAL_COLONISTS, "min": 50, "max": 500, "step": 10},
        {"name": "TILE_SIZE", "value": config.TILE_SIZE, "min": 16, "max": 64, "step": 4}
    ]
    menu_items = [opt["name"] for opt in options] + ["START GAME"]
    selected_index = 0
    running = True

    def render_menu():
        screen.fill((30, 30, 30))
        for i, item in enumerate(menu_items):
            if item == "START GAME":
                text = item
            else:
                opt = next(o for o in options if o["name"] == item)
                text = f"{item}: {opt['value']}"
            color = (255, 255, 0) if i == selected_index else (255, 255, 255)
            rendered = font.render(text, True, color)
            screen.blit(rendered, (100, 100 + i * 50))
        pygame.display.flip()

    while running:
        clock.tick(30)
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False  # Let caller decide how to quit
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_DOWN:
                    selected_index = (selected_index + 1) % len(menu_items)
                elif event.key == pygame.K_UP:
                    selected_index = (selected_index - 1) % len(menu_items)
                elif event.key == pygame.K_LEFT:
                    if menu_items[selected_index] != "START GAME":
                        opt = next(o for o in options if o["name"] == menu_items[selected_index])
                        opt["value"] = max(opt["min"], opt["value"] - opt["step"])
                elif event.key == pygame.K_RIGHT:
                    if menu_items[selected_index] != "START GAME":
                        opt = next(o for o in options if o["name"] == menu_items[selected_index])
                        opt["value"] = min(opt["max"], opt["value"] + opt["step"])
                elif event.key == pygame.K_RETURN:
                    if menu_items[selected_index] == "START GAME":
                        # Update configuration constants dynamically
                        for opt in options:
                            setattr(config, opt["name"], opt["value"])
                        running = False
        render_menu()
