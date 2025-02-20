import sys, subprocess, pygame
import game.config as config  # Adjust config dynamically

pygame.init()
screen = pygame.display.set_mode((config.WINDOW_WIDTH, config.WINDOW_HEIGHT))
pygame.display.set_caption("AI-Topia - Game Menu")

def run_menu(screen):
    # Use default pygame font instead of custom font
    font = pygame.font.Font(None, 36)
    title_font = pygame.font.Font(None, 72)
    subtitle_font = pygame.font.Font(None, 32)
    clock = pygame.time.Clock()

    # Reorder menu items to put START GAME first
    options = [
        {"name": "INITIAL COLONISTS", "value": config.INITIAL_COLONISTS, "min": 50, "max": 500, "step": 10},
        {"name": "TILE SIZE", "value": config.TILE_SIZE, "min": 16, "max": 64, "step": 4}
    ]
    menu_items = ["START GAME"] + [opt["name"] for opt in options]
    selected_index = 0
    running = True

    def handle_mouse_click(pos):
        for i, item in enumerate(menu_items):
            y_position = 180 + i * 70
            text = item if item == "START GAME" else f"{item}: {next(o for o in options if o['name'] == item)['value']}"
            
            # Calculate button dimensions
            rendered = font.render(text, True, (255, 255, 255))
            text_width = rendered.get_width()
            button_width = max(300, text_width + 40)
            button_height = 50
            button_x = config.WINDOW_WIDTH // 2 - button_width // 2
            button_rect = pygame.Rect(button_x, y_position - 10, button_width, button_height)
            
            if button_rect.collidepoint(pos):
                return i
        return None

    def render_menu():
        # Clean black background
        screen.fill((0, 0, 0))

        # Draw title with white text
        title_text = title_font.render("AI-Topia", True, (255, 255, 255))
        subtitle_text = subtitle_font.render("Help your AI civilization survive!", True, (200, 200, 200))
        title_rect = title_text.get_rect(center=(config.WINDOW_WIDTH // 2, 60))
        subtitle_rect = subtitle_text.get_rect(center=(config.WINDOW_WIDTH // 2, 120))
        screen.blit(title_text, title_rect)
        screen.blit(subtitle_text, subtitle_rect)

        # Draw menu items with button backgrounds
        for i, item in enumerate(menu_items):
            y_position = 180 + i * 70  # Increased spacing between items
            
            # Get text content first to determine button width
            if item == "START GAME":
                text = item
            else:
                opt = next(o for o in options if o["name"] == item)
                text = f"{item}: {opt['value']}"
            
            # Calculate required button width based on text
            rendered = font.render(text, True, (255, 255, 255))
            text_width = rendered.get_width()
            button_width = max(300, text_width + 40)  # Minimum 300px or text width + padding
            button_height = 50
            
            # Center button
            button_x = config.WINDOW_WIDTH // 2 - button_width // 2
            button_rect = pygame.Rect(button_x, y_position - 10, button_width, button_height)
            
            # Draw button - simplified styling
            if i == selected_index:
                # Selected button is filled white with black text
                pygame.draw.rect(screen, (255, 255, 255), button_rect)
                color = (0, 0, 0)
            else:
                # Unselected button is just white outline
                pygame.draw.rect(screen, (0, 0, 0), button_rect)
                pygame.draw.rect(screen, (255, 255, 255), button_rect, 2)
                color = (255, 255, 255)
            
            # Draw text centered in button
            rendered = font.render(text, True, color)
            text_rect = rendered.get_rect(center=button_rect.center)
            screen.blit(rendered, text_rect)

        pygame.display.flip()

    while running:
        clock.tick(30)
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False  # Let caller decide how to quit
            elif event.type == pygame.MOUSEBUTTONDOWN:
                if event.button == 1:  # Left click
                    clicked_index = handle_mouse_click(event.pos)
                    if clicked_index is not None:
                        selected_index = clicked_index
                        if menu_items[selected_index] == "START GAME":
                            # Update configuration constants dynamically
                            for opt in options:
                                setattr(config, opt["name"], opt["value"])
                            running = False
            elif event.type == pygame.KEYDOWN:
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

        # Handle mouse hover for visual feedback
        mouse_pos = pygame.mouse.get_pos()
        hover_index = handle_mouse_click(mouse_pos)
        if hover_index is not None and hover_index != selected_index:
            selected_index = hover_index

        render_menu()
