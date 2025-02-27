import sys, pygame
import game.config as config

pygame.init()
screen = pygame.display.set_mode((config.WINDOW_WIDTH, config.WINDOW_HEIGHT))
pygame.display.set_caption("AI-Topia - Game Menu")

# Use the same modern UI color scheme from ui.py
COLORS = {
    'background': (18, 18, 24),
    'panel': (30, 30, 40),
    'accent': (86, 155, 255),
    'accent_hover': (120, 180, 255),
    'text': (255, 255, 255),
    'text_secondary': (180, 180, 200),
    'text_header': (200, 200, 255),
    'button': (60, 60, 80),
    'button_hover': (80, 80, 100),
    'border': (100, 100, 150)
}

def run_menu(screen):
    # Use default pygame font
    font = pygame.font.Font(None, 36)
    title_font = pygame.font.Font(None, 72)
    subtitle_font = pygame.font.Font(None, 32)
    clock = pygame.time.Clock()

    running = True
    button_hovered = False

    # Calculate button dimensions and position
    button_width = 300
    button_height = 60
    button_x = config.WINDOW_WIDTH // 2 - button_width // 2
    button_y = config.WINDOW_HEIGHT // 2
    start_button = pygame.Rect(button_x, button_y, button_width, button_height)

    def render_menu():
        # Draw modern background
        screen.fill(COLORS['background'])

        # Draw title with modern styling
        title_text = title_font.render("AI-Topia", True, COLORS['text_header'])
        subtitle_text = subtitle_font.render("Help your AI civilization survive!", True, COLORS['text_secondary'])
        title_rect = title_text.get_rect(center=(config.WINDOW_WIDTH // 2, config.WINDOW_HEIGHT // 3))
        subtitle_rect = subtitle_text.get_rect(center=(config.WINDOW_WIDTH // 2, config.WINDOW_HEIGHT // 3 + 60))
        screen.blit(title_text, title_rect)
        screen.blit(subtitle_text, subtitle_rect)

        # Draw start button with modern styling
        button_color = COLORS['button_hover'] if button_hovered else COLORS['button']
        pygame.draw.rect(screen, button_color, start_button, border_radius=4)
        pygame.draw.rect(screen, COLORS['border'], start_button, 1, border_radius=4)
        
        # Draw button text
        start_text = font.render("START GAME", True, COLORS['text'])
        text_rect = start_text.get_rect(center=start_button.center)
        screen.blit(start_text, text_rect)

        # Draw hover effect with reduced intensity
        if button_hovered:
            s = pygame.Surface((start_button.width, start_button.height))
            s.set_alpha(15)  # Reduced from 30 to 15 for more subtle effect
            s.fill((255, 255, 255))
            screen.blit(s, start_button, special_flags=pygame.BLEND_ADD)

        pygame.display.flip()

    while running:
        clock.tick(30)
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
            elif event.type == pygame.MOUSEBUTTONDOWN:
                if event.button == 1 and start_button.collidepoint(event.pos):
                    running = False
            elif event.type == pygame.KEYDOWN:
                if event.key == pygame.K_RETURN:
                    running = False
        
        # Update button hover state
        mouse_pos = pygame.mouse.get_pos()
        button_hovered = start_button.collidepoint(mouse_pos)
        
        render_menu()
