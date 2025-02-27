import pygame
from .config import WINDOW_WIDTH, WINDOW_HEIGHT, BUILDING_TYPES, EXPANSION_COST, TILE_SIZE

# Modern UI color scheme
COLORS = {
    'background': (18, 18, 24),
    'panel': (30, 30, 40),
    'panel_highlight': (40, 40, 55),
    'accent': (86, 155, 255),
    'accent_hover': (120, 180, 255),
    'text': (255, 255, 255),
    'text_secondary': (180, 180, 200),
    'text_header': (200, 200, 255),
    'success': (100, 200, 100),
    'warning': (255, 180, 100),
    'error': (255, 100, 100),
    'button': (60, 60, 80),
    'button_hover': (80, 80, 100),
    'border': (100, 100, 150)
}

class Button:
    def __init__(self, x, y, width, height, text, color):
        self.rect = pygame.Rect(x, y, width, height)
        self.text = text
        self.base_color = color
        self.color = color
        self.hovered = False
        self.active = False
        self.font = pygame.font.Font(None, 24)

    def draw(self, screen):
        # Determine button color based on state
        if self.active:
            color = COLORS['accent']
        elif self.hovered:
            color = COLORS['button_hover']
        else:
            color = COLORS['button']
        
        # Draw button background with rounded corners
        pygame.draw.rect(screen, color, self.rect, border_radius=4)
        pygame.draw.rect(screen, COLORS['border'], self.rect, 1, border_radius=4)
        
        # Draw text centered
        text_surface = self.font.render(self.text, True, COLORS['text'])
        text_rect = text_surface.get_rect(center=self.rect.center)
        screen.blit(text_surface, text_rect)
        
        # Draw hover effect
        if self.hovered:
            s = pygame.Surface((self.rect.width, self.rect.height))
            s.set_alpha(30)
            s.fill((255, 255, 255))
            screen.blit(s, self.rect, special_flags=pygame.BLEND_ADD)

class UI:
    def __init__(self, screen, world):
        self.screen = screen
        self.world = world
        self.font = pygame.font.Font(None, 24)
        self.selected_colonist = None
        
        # Camera controls
        self.camera_x = 0
        self.camera_y = 0
        self.target_camera_x = 0
        self.target_camera_y = 0
        self.camera_speed = 0.1
        self.zoom = 1.0
        self.target_zoom = 1.0
        self.zoom_speed = 0.1
        self.camera_velocity_x = 0
        self.camera_velocity_y = 0
        self.camera_acceleration = 2.0
        self.camera_friction = 0.9
        self.camera_max_speed = 20.0
        
        # Reorganize button layout with better spacing
        button_width = 100
        button_spacing = 15
        button_y = 10
        self.buttons = {
            'policies': Button(10, button_y, button_width, 30, 'Policies', COLORS['button']),
            'election': Button(10 + (button_width + button_spacing), button_y, button_width, 30, 'Elections', COLORS['button']),
            'taxes': Button(10 + 2 * (button_width + button_spacing), button_y, button_width, 30, 'Taxes', COLORS['button']),
            'laws': Button(10 + 3 * (button_width + button_spacing), button_y, button_width, 30, 'Laws', COLORS['button']),
            'scenario': Button(10 + 4 * (button_width + button_spacing), button_y, button_width, 30, 'Scenario', COLORS['button']),
            'build': Button(10 + 5 * (button_width + button_spacing), button_y, button_width, 30, 'Build', COLORS['button'])
        }
        
        # Policy and law settings
        self.policies = {
            'tax_rate': 0.15,
            'minimum_wage': 10,
            'immigration': True,
            'education': True,
            'healthcare': True,
            'welfare': True,
            'birth_incentive': 100  # Money given for each new child
        }
        
        # Enhanced policy ranges with step sizes and display formats
        self.policy_ranges = {
            'tax_rate': {'min': 0.05, 'max': 0.5, 'step': 0.01, 'format': '{:.0%}'},
            'minimum_wage': {'min': 5, 'max': 20, 'step': 0.5, 'format': '${:.2f}/hr'},
            'birth_incentive': {'min': 0, 'max': 500, 'step': 25, 'format': '${:.0f}'},
            'retirement_age': {'min': 55, 'max': 75, 'step': 1, 'format': '{:.0f} years'}
        }
        
        # Add visual feedback state for active controls
        self.active_slider = None
        self.slider_drag = False
        self.hover_item = None
        
        self.laws = {
            'mandatory_education': True,
            'universal_healthcare': True,
            'minimum_wage_law': True,
            'child_labor': False,
            'retirement_age': 65
        }
        
        # UI states
        self.policy_menu_open = False
        self.law_menu_open = False
        self.show_colonist_info = False
        self.show_election_info = False
        
        # Key state tracking
        self.keys_pressed = {
            pygame.K_LEFT: False,
            pygame.K_RIGHT: False,
            pygame.K_UP: False,
            pygame.K_DOWN: False
        }
        
        # Building menu and placement
        self.selected_building_type = None
        self.show_building_menu = False
        self.hovering_grid_pos = None
        self.tooltip_text = None

        self.update_timer = 0
        self.UPDATE_INTERVAL = 30  # Update suggestions every 30 frames

    def handle_event(self, event):
        """Main event handler for all UI interactions"""
        if event.type == pygame.KEYDOWN:
            if event.key in self.keys_pressed:
                self.keys_pressed[event.key] = True
                
        elif event.type == pygame.KEYUP:
            if event.key in self.keys_pressed:  # Add key release handling
                self.keys_pressed[event.key] = False

        elif event.type == pygame.MOUSEBUTTONDOWN:
            mouse_pos = pygame.mouse.get_pos()
            
            # Handle button clicks
            for button_type, button in self.buttons.items():
                if button.rect.collidepoint(mouse_pos):
                    if button_type == 'policies':
                        self.policy_menu_open = not self.policy_menu_open
                        self.law_menu_open = False
                        self.show_election_info = False
                        self.show_building_menu = False
                    elif button_type == 'election':
                        self.show_election_info = not self.show_election_info
                        self.policy_menu_open = False
                        self.law_menu_open = False
                        self.show_building_menu = False
                    elif button_type == 'taxes':
                        self.policy_menu_open = True
                        self.law_menu_open = False
                        self.show_election_info = False
                        self.show_building_menu = False
                    elif button_type == 'laws':
                        self.law_menu_open = not self.law_menu_open
                        self.policy_menu_open = False
                        self.show_election_info = False
                        self.show_building_menu = False
                    elif button_type == 'scenario':
                        if not self.world.scenario_manager.active_scenario:
                            self.world.scenario_manager.trigger_scenario()
                    elif button_type == 'build':
                        self.show_building_menu = not self.show_building_menu
                        if not self.show_building_menu:
                            self.selected_building_type = None
                            self.tooltip_text = None
                        else:
                            self.world.update_building_zones()
                            self.selected_building_type = None
                    return

            # Handle policy menu clicks
            if self.policy_menu_open:
                self.handle_policy_click(mouse_pos)
            
            # Handle law menu clicks
            elif self.law_menu_open:
                self.handle_law_click(mouse_pos)
            
            # Handle building placement
            elif self.show_building_menu:
                if event.button == 1:  # Left click
                    if self.selected_building_type and self.hovering_grid_pos:
                        x, y = self.world.get_pixel_position(*self.hovering_grid_pos)
                        success, message = self.world.build_structure(self.selected_building_type, x, y)
                        if success:
                            self.world.update_building_zones()
                            self.world.update_colony_needs()
                            self.tooltip_text = self.generate_building_suggestion()
                        else:
                            self.tooltip_text = message
                elif event.button == 3:  # Right click
                    self.selected_building_type = None

        elif event.type == pygame.MOUSEMOTION:
            # Update button hover states
            mouse_pos = pygame.mouse.get_pos()
            for button in self.buttons.values():
                button.hovered = button.rect.collidepoint(mouse_pos)
        
        elif event.type == pygame.KEYDOWN:
            if event.key in self.keys_pressed:
                self.keys_pressed[event.key] = True
            
            # Handle zoom
            if event.key == pygame.K_PLUS or event.key == pygame.K_EQUALS:
                self.target_zoom = min(2.0, self.zoom + 0.2)
            elif event.key == pygame.K_MINUS:
                self.target_zoom = max(0.5, self.zoom - 0.2)
            elif event.key == pygame.K_ESCAPE:
                # Close all menus
                self.show_building_menu = False
                self.policy_menu_open = False
                self.law_menu_open = False
                self.show_election_info = False
                self.selected_building_type = None
                self.tooltip_text = None

    def handle_policy_click(self, mouse_pos):
        """Enhanced policy interaction handling"""
        menu_x = self.screen.get_width() - 310
        menu_y = 10
        y = menu_y + 20
        
        for policy, value in self.policies.items():
            if isinstance(value, bool):
                # Handle toggle clicks
                toggle_rect = pygame.Rect(menu_x + 10, y, 250, 20)
                if toggle_rect.collidepoint(mouse_pos):
                    self.policies[policy] = not value
            
            elif policy in self.policy_ranges:
                # Handle slider interaction
                slider_rect = pygame.Rect(menu_x + 10, y + 25, 200, 20)
                if slider_rect.collidepoint(mouse_pos):
                    range_info = self.policy_ranges[policy]
                    # Calculate value from click position
                    ratio = (mouse_pos[0] - (menu_x + 10)) / 200
                    new_value = range_info['min'] + (range_info['max'] - range_info['min']) * ratio
                    # Round to nearest step
                    steps = round((new_value - range_info['min']) / range_info['step'])
                    new_value = range_info['min'] + steps * range_info['step']
                    # Clamp value
                    new_value = max(range_info['min'], min(range_info['max'], new_value))
                    self.policies[policy] = new_value
                    self.active_slider = (menu_x + 10, y + 25)
                    self.slider_drag = True
            
            y += 60  # Increased spacing for improved layout

    def handle_law_click(self, mouse_pos):
        """Handle clicks in the law menu"""
        menu_x = self.screen.get_width() - 310
        menu_y = 10
        
        # Calculate click positions for law toggles
        y = menu_y + 20
        for law in self.laws:
            if menu_x + 10 <= mouse_pos[0] <= menu_x + 290 and y <= mouse_pos[1] <= y + 25:
                self.laws[law] = not self.laws[law]
            y += 30

    def update(self):
        # Update camera position based on key states
        if self.keys_pressed[pygame.K_LEFT]:
            self.camera_velocity_x += self.camera_acceleration
        if self.keys_pressed[pygame.K_RIGHT]:
            self.camera_velocity_x -= self.camera_acceleration
        if self.keys_pressed[pygame.K_UP]:
            self.camera_velocity_y += self.camera_acceleration
        if self.keys_pressed[pygame.K_DOWN]:
            self.camera_velocity_y -= self.camera_acceleration
        
        # Apply friction
        self.camera_velocity_x *= self.camera_friction
        self.camera_velocity_y *= self.camera_friction
        
        # Clamp velocity
        speed = (self.camera_velocity_x**2 + self.camera_velocity_y**2)**0.5
        if speed > self.camera_max_speed:
            scale = self.camera_max_speed / speed
            self.camera_velocity_x *= scale
            self.camera_velocity_y *= scale
        
        # Update camera position
        self.camera_x += self.camera_velocity_x
        self.camera_y += self.camera_velocity_y
        
        # Smooth zoom interpolation
        if abs(self.zoom - self.target_zoom) > 0.01:
            self.zoom += (self.target_zoom - self.zoom) * self.zoom_speed

        # Update UI state
        if self.show_building_menu:
            self.update_timer += 1
            if self.update_timer >= self.UPDATE_INTERVAL:
                self.update_timer = 0
                self.world.update_building_zones()
                if not self.selected_building_type:
                    self.tooltip_text = self.generate_building_suggestion()
        
        # Update button states
        self.buttons['policies'].active = self.policy_menu_open
        self.buttons['election'].active = self.show_election_info
        self.buttons['laws'].active = self.law_menu_open
        self.buttons['build'].active = self.show_building_menu

    def screen_to_world(self, pos):
        """Convert screen coordinates to world coordinates"""
        return ((pos[0] - self.camera_x) / self.zoom,
                (pos[1] - self.camera_y) / self.zoom)

    def world_to_screen(self, pos):
        """Convert world coordinates to screen coordinates"""
        return (pos[0] * self.zoom + self.camera_x,
                pos[1] * self.zoom + self.camera_y)

    def render(self):
        """Main render function with improved layout and modern styling"""
        # Draw buttons in top-left corner
        for button in self.buttons.values():
            button.draw(self.screen)

        # Stats panel
        stats_panel_x = 10
        stats_panel_y = self.buttons['policies'].rect.bottom + 20
        stats_panel_width = 280
        stats_spacing = 25

        # Stats content
        stats = [
            f"Population: {len(self.world.colonists)}",
            f"Treasury: ${self.world.treasury:,.2f}",
            f"GDP: ${self.world.gdp:,.2f}",
            f"Average Happiness: {self.get_average_happiness():,.1f}%"
        ]
        
        # Calculate panel heights
        stats_panel_height = len(stats) * stats_spacing + 20
        
        # Draw stats panel background
        self._draw_panel(stats_panel_x, stats_panel_y, stats_panel_width, stats_panel_height, "Colony Statistics")
        
        # Draw stats
        for i, stat in enumerate(stats):
            self.draw_text(self.screen, stat, stats_panel_x + 10, stats_panel_y + 30 + i * stats_spacing, COLORS['text'])

        # Resource panel below stats
        resource_panel_y = stats_panel_y + stats_panel_height + 10
        self._render_resource_indicators(self.screen, stats_panel_x, resource_panel_y)

        # Organize other UI elements
        if self.policy_menu_open:
            self.draw_policy_menu(self.screen.get_width() - 320, 50)
        elif self.law_menu_open:
            self.draw_law_menu(self.screen.get_width() - 320, 50)
        elif self.show_election_info:
            self.draw_election_info(self.screen.get_width() - 320, 50)

        # Position colonist info on the left side below resources
        if self.show_colonist_info and self.selected_colonist:
            colonist_panel_y = resource_panel_y + 200  # Adjusted based on resource panel height
            self.draw_colonist_info(10, colonist_panel_y)

        # Building menu and preview
        if self.show_building_menu:
            self._render_building_menu(self.screen)
            # Always render preview if we have a selected building type
            if self.selected_building_type:
                self._render_building_preview(self.screen)

        # Alerts at bottom-left
        self._render_alerts(self.screen)

        # Tooltips
        if self.tooltip_text:
            self._render_tooltip(self.screen)

    def _draw_panel(self, x, y, width, height, title=None):
        """Draw a modern styled panel with optional title"""
        # Panel background
        s = pygame.Surface((width, height))
        s.set_alpha(230)
        s.fill(COLORS['panel'])
        self.screen.blit(s, (x, y))
        
        # Panel border
        pygame.draw.rect(self.screen, COLORS['border'], (x, y, width, height), 1)
        
        # Title if provided
        if title:
            self.draw_text(self.screen, title, x + 10, y + 5, COLORS['text_header'])

    def _render_resource_indicators(self, screen, x, y):
        """Render resource levels in a modern panel"""
        resource_spacing = 25
        padding = 10
        
        # Calculate panel dimensions
        resources = list(self.world.colony_inventory.items())
        panel_height = (len(resources) + 4) * resource_spacing + padding * 2  # Extra space for needs
        panel_width = 280
        
        # Draw panel background
        self._draw_panel(x, y, panel_width, panel_height, "Resources & Needs")
        
        current_y = y + padding + 25  # Account for title
        
        # Draw resources
        for resource, amount in resources:
            text = f"{resource.title()}: {amount:.1f}"
            color = COLORS['error'] if amount < 100 else COLORS['text']
            self.draw_text(screen, text, x + padding, current_y, color)
            current_y += resource_spacing

        # Draw needs section
        current_y += resource_spacing/2  # Add some spacing between sections
        stats = self.world.building_requirements
        if stats:
            needs_text = [
                (f"Housing needed: {stats['housing']}", 'warning' if stats['housing'] > 0 else 'success'),
                (f"Jobs needed: {stats['jobs']}", 'warning' if stats['jobs'] > 0 else 'success'),
                (f"Average happiness: {stats['happiness']:.1f}%", 
                 'success' if stats['happiness'] >= 70 else 'warning')
            ]
            for text, status in needs_text:
                self.draw_text(screen, text, x + padding, current_y, COLORS[status])
                current_y += resource_spacing

    def draw_colonist_info(self, x, y):
        """Draw colonist info panel on the left side"""
        info_width = 280
        padding = 10
        line_height = 25
        
        colonist = self.selected_colonist
        info_lines = [
            f"Age: {int(colonist.age)}",
            f"Health: {int(colonist.health)}%",
            f"Energy: {int(colonist.energy)}%",
            f"Happiness: {int(colonist.happiness)}%",
            f"Money: ${colonist.money:,.2f}",
            "",
            "Stats:",
            f"Ambition: {colonist.traits['ambition']}%",
            f"Sociability: {colonist.traits['sociability']}%",
            f"Work Ethic: {colonist.traits['work_ethic']}%"
        ]
        
        panel_height = len(info_lines) * line_height + padding * 2
        
        # Draw panel background
        s = pygame.Surface((info_width, panel_height))
        s.set_alpha(230)
        s.fill((30, 30, 40))
        self.screen.blit(s, (x, y))
        pygame.draw.rect(self.screen, (100, 100, 150), (x, y, info_width, panel_height), 1)
        
        # Draw information
        for i, line in enumerate(info_lines):
            color = (200, 200, 255) if line.endswith(':') else (255, 255, 255)
            self.draw_text(self.screen, line, x + padding, y + padding + i * line_height, color)

    def draw_policy_menu(self, x, y):
        """Draw policy menu with improved layout"""
        menu_width = 300
        padding = 15
        item_height = 60
        
        height = len(self.policies) * item_height + padding * 2
        
        # Draw background
        s = pygame.Surface((menu_width, height))
        s.set_alpha(230)
        s.fill((30, 30, 40))
        self.screen.blit(s, (x, y))
        pygame.draw.rect(self.screen, (100, 100, 150), (x, y, menu_width, height), 1)
        
        current_y = y + padding
        for policy, value in self.policies.items():
            name = policy.replace('_', ' ').title()
            self.draw_text(self.screen, name, x + padding, current_y, (255, 255, 255))
            
            if isinstance(value, bool):
                self.draw_toggle(x + padding, current_y + 25, value, "")
            else:
                range_info = self.policy_ranges.get(policy, {'min': 0, 'max': 100, 'step': 1, 'format': '{:.0f}'})
                self.draw_slider(x + padding, current_y + 25, menu_width - padding * 3, 20, value, range_info)
            
            current_y += item_height

    def draw_slider(self, x, y, width, height, value, range_info):
        """Draw an improved slider with better visual feedback"""
        # Draw track
        track_rect = pygame.Rect(x, y + height//2 - 2, width, 4)
        pygame.draw.rect(self.screen, (100, 100, 100), track_rect)
        pygame.draw.rect(self.screen, (150, 150, 150), track_rect, 1)
        
        # Calculate knob position
        value_ratio = (value - range_info['min']) / (range_info['max'] - range_info['min'])
        knob_x = x + (width * value_ratio)
        knob_pos = (int(knob_x), y + height//2)
        
        # Draw filled portion
        filled_rect = pygame.Rect(x, y + height//2 - 2, knob_x - x, 4)
        pygame.draw.rect(self.screen, (100, 150, 255), filled_rect)
        
        # Draw knob with hover/active state
        knob_color = (200, 200, 255) if self.active_slider == (x,y) else (150, 150, 255)
        pygame.draw.circle(self.screen, knob_color, knob_pos, 8)
        pygame.draw.circle(self.screen, (255, 255, 255), knob_pos, 8, 1)
        
        return knob_pos, 8  # Return knob position and radius for hit testing

    def draw_toggle(self, x, y, value, text):
        """Draw a toggle switch for boolean settings"""
        width = 40
        height = 20
        toggle_rect = pygame.Rect(x, y, width, height)
        
        # Draw track
        pygame.draw.rect(self.screen, (50,50,50), toggle_rect, border_radius=height//2)
        pygame.draw.rect(self.screen, (100,100,100), toggle_rect, 1, border_radius=height//2)
        
        # Draw knob
        knob_pos = x + width - 15 if value else x + 5
        pygame.draw.circle(self.screen, (150,150,255) if value else (100,100,100), (knob_pos, y + height//2), height//2 - 2)
        
        # Draw label
        label = self.font.render(f"{text}: {'On' if value else 'Off'}", True, (255,255,255))
        self.screen.blit(label, (x + width + 10, y + 2))
        
        return pygame.Rect(x, y, width + 10 + label.get_width(), height)

    def draw_law_menu(self):
        """Draw law menu with improved layout and visibility"""
        menu_width = 300
        menu_x = self.screen.get_width() - menu_width - 10
        menu_y = 10
        padding = 15
        item_height = 40
        
        # Calculate total height
        height = len(self.laws) * item_height + padding * 3
        
        # Draw background
        s = pygame.Surface((menu_width, height))
        s.set_alpha(230)
        s.fill((30, 30, 40))
        self.screen.blit(s, (menu_x, menu_y))
        pygame.draw.rect(self.screen, (100, 100, 150), (menu_x, menu_y, menu_width, height), 1)
        
        # Draw title
        title = self.font.render("Laws", True, (200, 200, 255))
        self.screen.blit(title, (menu_x + padding, menu_y + padding))
        
        y = menu_y + padding * 2 + title.get_height()
        for law, value in self.laws.items():
            # Draw toggle switch
            self.draw_toggle(menu_x + padding, y, value, law.replace('_', ' ').title())
            y += item_height

    def draw_election_info(self):
        if not self.world.election_candidates:
            return
            
        menu_x = self.screen.get_width() - 310
        menu_y = 10
        width = 300
        height = 400
        
        # Draw background
        s = pygame.Surface((width, height))
        s.set_alpha(200)
        s.fill((50, 50, 50))
        self.screen.blit(s, (menu_x, menu_y))
        
        # Draw candidate information
        y = menu_y + 20
        title = self.font.render("Election Candidates:", True, (255, 255, 255))
        self.screen.blit(title, (menu_x + 10, y))
        y += 30
        
        for candidate in self.world.election_candidates:
            info = [
                f"Candidate #{self.world.colonists.index(candidate)}",
                f"Age: {int(candidate.age)}",
                f"Leadership: {candidate.leadership}",
                f"Political: {self.get_political_description(candidate.political_alignment)}",
                f"Support: {self.get_candidate_support(candidate):,.1f}%",
                ""
            ]
            
            for line in info:
                text = self.font.render(line, True, (255, 255, 255))
                self.screen.blit(text, (menu_x + 20, y))
                y += 25

    def get_candidate_support(self, candidate):
        if not self.world.colonists:
            return 0
        supporters = len([c for c in self.world.colonists 
                         if abs(c.political_alignment - candidate.political_alignment) < 0.3])
        return (supporters / len(self.world.colonists)) * 100

    def draw_colonist_info(self):
        """Draw colonist info panel in the right-middle area"""
        info_width = 280
        info_x = self.screen.get_width() - info_width - 10  # Account for padding
        info_y = 100
        padding = 10
        line_height = 25
        
        colonist = self.selected_colonist
        info_lines = [
            f"Age: {int(colonist.age)}",
            f"Gender: {colonist.gender}",
            f"Health: {int(colonist.health)}%",
            f"Energy: {int(colonist.energy)}%",
            f"Money: ${colonist.money:,.2f}",
            f"Happiness: {int(colonist.happiness)}%",
            "",
            "Personality Traits:",
            f"Ambition: {colonist.traits['ambition']}%",
            f"Sociability: {colonist.traits['sociability']}%",
            f"Intelligence: {colonist.traits['intelligence']}%",
            f"Creativity: {colonist.traits['creativity']}%",
            f"Work Ethic: {colonist.traits['work_ethic']}%",
            "",
            f"Friends: {len(colonist.friends)}",
            f"Job: {'Yes' if colonist.job else 'No'}",
            f"Home: {'Yes' if colonist.home else 'No'}",
            f"Spouse: {'Yes' if colonist.spouse else 'No'}",
            f"Children: {len(colonist.children)}"
        ]
        
        # Calculate panel height based on content
        panel_height = len(info_lines) * line_height + padding * 2
        
        # Draw background with improved visibility
        s = pygame.Surface((info_width, panel_height))
        s.set_alpha(230)
        s.fill((30, 30, 40))
        self.screen.blit(s, (info_x, info_y))
        pygame.draw.rect(self.screen, (100, 100, 150), (info_x, info_y, info_width, panel_height), 1)
        
        # Draw information
        for i, line in enumerate(info_lines):
            color = (200, 200, 255) if line.endswith(':') else (255, 255, 255)  # Highlight headers
            self.draw_text(self.screen, line, info_x + padding, info_y + padding + i * line_height, color)

    def _render_building_menu(self, screen):
        """Render building menu with improved resource information"""
        menu_width = 250
        menu_rect = pygame.Rect(screen.get_width() - menu_width, 0, menu_width, screen.get_height())
        
        # Semi-transparent background
        s = pygame.Surface((menu_width, screen.get_height()))
        s.set_alpha(200)
        s.fill((20, 20, 30))
        screen.blit(s, menu_rect)
        
        # Draw title
        title = self.font.render("Buildings", True, (200, 200, 255))
        screen.blit(title, (menu_rect.x + 10, 10))
        
        # Draw resource status bar at top
        resource_y = 40
        for resource, amount in self.world.colony_inventory.items():
            text = f"{resource.title()}: {amount:.1f}"
            color = (255, 100, 100) if amount < 100 else (255, 255, 255)
            self.draw_text(screen, text, menu_rect.x + 10, resource_y, color, size=20)
            resource_y += 20
        
        # Draw building options
        y = resource_y + 20
        for building_type, data in BUILDING_TYPES.items():
            button_height = 80
            button_rect = pygame.Rect(menu_rect.x + 10, y, menu_width - 20, button_height)
            
            # Check if can afford
            can_afford = True
            for resource, amount in data.get('cost', {}).items():
                if self.world.colony_inventory.get(resource, 0) < amount:
                    can_afford = False
                    break
            
            # Background color based on selection and affordability
            if building_type == self.selected_building_type:
                color = (100, 100, 200)
            else:
                color = (60, 60, 80) if can_afford else (60, 30, 30)
            
            pygame.draw.rect(screen, color, button_rect)
            pygame.draw.rect(screen, (100, 100, 150), button_rect, 1)
            
            # Building name
            self.draw_text(screen, building_type.title(), button_rect.x + 5, y + 5, (255, 255, 255), size=20)
            
            # Production info
            if 'produces' in data:
                prod_text = f"Produces: {data['produces']}"
                self.draw_text(screen, prod_text, button_rect.x + 5, y + 25, (200, 255, 200), size=16)
            
            # Cost info
            cost_text = "Cost: " + ", ".join(f"{amount} {res}" for res, amount in data.get('cost', {}).items())
            self.draw_text(screen, cost_text, button_rect.x + 5, y + 45, (200, 200, 200), size=16)
            
            # Jobs info
            if 'max_jobs' in data:
                jobs_text = f"Jobs: {data['max_jobs']}"
                self.draw_text(screen, jobs_text, button_rect.x + 5, y + 65, (200, 200, 255), size=16)
            
            # Handle click event
            if button_rect.collidepoint(pygame.mouse.get_pos()):
                self.tooltip_text = data.get('description', '')
                if pygame.mouse.get_pressed()[0] and can_afford:  # Only allow selection if can afford
                    self.selected_building_type = building_type
                    # Force immediate update of zones
                    self.world.update_building_zones()
            
            y += button_height + 5

    def _render_building_preview(self, screen):
        """Render building placement preview"""
        if not self.selected_building_type:
            return
            
        mouse_pos = pygame.mouse.get_pos()
        world_pos = self.screen_to_world(mouse_pos)
        grid_x, grid_y = self.world.get_grid_position(world_pos[0], world_pos[1])
        self.hovering_grid_pos = (grid_x, grid_y)
        
        if 0 <= grid_x < self.world.current_size and 0 <= grid_y < self.world.current_size:
            # Get exact grid-aligned position
            pixel_x, pixel_y = self.world.get_pixel_position(grid_x, grid_y)
            
            # Convert world coordinates to screen coordinates
            screen_x = (pixel_x + self.camera_x) * self.zoom
            screen_y = (pixel_y + self.camera_y) * self.zoom
            
            # Get building size and scale with zoom
            building_size = BUILDING_TYPES[self.selected_building_type]['size'] 
            total_size = building_size * TILE_SIZE * self.zoom
            
            # Check if placement is valid
            can_build, message = self.world.can_build(self.selected_building_type, pixel_x, pixel_y)
            
            # Create preview surface with proper size
            highlight_surface = pygame.Surface((total_size, total_size))
            highlight_surface.set_alpha(128)
            
            # Set color based on validity
            if can_build:
                color = (100, 255, 100)  # Green for valid
                self.tooltip_text = f"Click to build {self.selected_building_type}"
            else:
                color = (255, 100, 100)  # Red for invalid
                self.tooltip_text = message
                
            highlight_surface.fill(color)
            screen.blit(highlight_surface, (screen_x, screen_y))
            
            # Draw grid lines
            for i in range(building_size + 1):
                # Vertical lines
                line_x = screen_x + i * TILE_SIZE * self.zoom
                pygame.draw.line(screen, (255, 255, 255),
                               (line_x, screen_y),
                               (line_x, screen_y + total_size))
                # Horizontal lines
                line_y = screen_y + i * TILE_SIZE * self.zoom
                pygame.draw.line(screen, (255, 255, 255),
                               (screen_x, line_y),
                               (screen_x + total_size, line_y))

    def _render_alerts(self, screen):
        """Render alerts in bottom-left corner with improved visibility and spacing"""
        alert_spacing = 30
        alert_padding = 20
        alert_y = screen.get_height() - (len(self.world.resource_alerts) * alert_spacing + alert_padding)
        
        for alert in self.world.resource_alerts:
            # Create a semi-transparent background for better readability
            text_surface = self.font.render(alert, True, (255, 100, 100))
            background = pygame.Surface((text_surface.get_width() + 20, 24))
            background.set_alpha(128)
            background.fill((0, 0, 0))
            screen.blit(background, (10, alert_y - 2))
            self.draw_text(screen, alert, 20, alert_y, (255, 100, 100))
            alert_y += alert_spacing

    def _render_tooltip(self, screen):
        """Render tooltip with building suggestions"""
        if not self.tooltip_text:
            return
            
        mouse_pos = pygame.mouse.get_pos()
        padding = 5
        
        # Split tooltip into lines
        lines = self.tooltip_text.split('\n')
        line_surfaces = []
        max_width = 0
        total_height = 0
        
        for line in lines:
            text_surface = self.font.render(line, True, (255, 255, 255))
            line_surfaces.append(text_surface)
            max_width = max(max_width, text_surface.get_width())
            total_height += text_surface.get_height()
            
        # Create tooltip background
        tooltip_rect = pygame.Rect(
            mouse_pos[0] + 20,
            mouse_pos[1] - total_height - 10,
            max_width + padding * 2,
            total_height + padding * 2
        )
        
        # Keep tooltip on screen
        if tooltip_rect.right > screen.get_width():
            tooltip_rect.right = mouse_pos[0] - 20
        if tooltip_rect.top < 0:
            tooltip_rect.top = mouse_pos[1] + 20
            
        # Draw background
        s = pygame.Surface((tooltip_rect.width, tooltip_rect.height))
        s.set_alpha(230)
        s.fill((40, 40, 40))
        screen.blit(s, tooltip_rect)
        pygame.draw.rect(screen, (100, 100, 100), tooltip_rect, 1)
        
        # Draw text
        y = tooltip_rect.top + padding
        for surface in line_surfaces:
            screen.blit(surface, (tooltip_rect.left + padding, y))
            y += surface.get_height()

    def generate_building_suggestion(self):
        """Generate building suggestions based on colony needs and zone scores"""
        suggestions = []
        stats = self.world.building_requirements
        
        # Get the highest scoring zones for each building type
        best_zones = {}
        for scores in self.world.building_zones.values():
            for building_type, score in scores.items():
                if score > best_zones.get(building_type, 0):
                    best_zones[building_type] = score
        
        # Add critical needs first
        if stats.get('housing', 0) > 0:
            house_score = best_zones.get('house', 0)
            if house_score > 70:
                suggestions.append(f"Good housing location available! Need housing for {stats['housing']} colonists")
            else:
                suggestions.append(f"Need housing for {stats['housing']} colonists")
        
        if stats.get('jobs', 0) > 0:
            job_buildings = [b for b, s in best_zones.items() if s > 70 and b in ['farm', 'workshop', 'market']]
            if job_buildings:
                suggestions.append(f"Good location for {job_buildings[0]}! Need jobs for {stats['jobs']} colonists")
            else:
                suggestions.append(f"Need jobs for {stats['jobs']} colonists")
        
        # Add resource suggestions
        for resource, data in stats.get('resources', {}).items():
            if data.get('amount', 100) < 20:  # Low resource threshold
                if resource in best_zones and best_zones[resource] > 60:
                    suggestions.append(f"Good location available for {resource} production!")
        
        return "\n".join(suggestions) if suggestions else "Colony is stable. Build where you like!"

    def draw_text(self, screen, text, x, y, color=None, size=24):
        """Enhanced text drawing with modern styling"""
        if color is None:
            color = COLORS['text']
        font = pygame.font.Font(None, size)
        text_surface = font.render(text, True, color)
        screen.blit(text_surface, (x, y))

    def get_average_happiness(self):
        """Calculate the average happiness of all colonists"""
        if not self.world.colonists:
            return 0.0
        total_happiness = sum(colonist.happiness for colonist in self.world.colonists)
        return total_happiness / len(self.world.colonists)
