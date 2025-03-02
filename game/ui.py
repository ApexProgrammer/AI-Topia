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
        
        # Draw hover effect with reduced intensity
        if self.hovered:
            s = pygame.Surface((self.rect.width, self.rect.height))
            s.set_alpha(15)  # Reduced from  to 15 for more subtle effect
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
            'build': Button(10, button_y, button_width, 30, 'Build', COLORS['button'])
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
        
        # Job Directives
        self.job_directives = {
            'agriculture': 0.5,
            'manufacturing': 0.5,
            'education': 0.5,
            'healthcare': 0.5,
            'commerce': 0.5,
            'research': 0.5
        }
        
        # Resource Priorities
        self.resource_priorities = {
            'food': 'normal',
            'wood': 'normal',
            'stone': 'normal',
            'metal': 'normal',
            'tools': 'normal',
            'medicine': 'normal'
        }
        
        # Labor Policies
        self.labor_policies = {
            'working_hours': 8,  # hours per day
            'safety_standards': 0.5,  # 0-1 scale
            'training_investment': 0.3,  # 0-1 scale
            'specialization': 0.5,  # 0-1 balance between specialist and generalist
            'child_education': True,
            'retirement_age': 65
        }
        
        # Job Override System
        self.critical_positions = set()  # Set of (x,y) tuples for critical position overrides
        self.manual_assignments = {}  # Dict of colonist: (x,y) assignments
        
        # UI states
        self.policy_menu_open = False
        self.law_menu_open = False
        self.show_colonist_info = False
        self.show_election_info = False
        self.directive_menu_open = False
        self.show_job_fair = False
        self.job_fair_candidates = []
        self.selected_priority_resource = None
        
        # Key state tracking
        self.keys_pressed = {
            pygame.K_LEFT: False,
            pygame.K_RIGHT: False,
            pygame.K_UP: False,
            pygame.K_DOWN: False,
            pygame.K_a: False,  # Added A
            pygame.K_d: False,  # Added D
            pygame.K_w: False,  # Added W
            pygame.K_s: False   # Added S
        }
        
        # Building menu and placement
        self.selected_building_type = None
        self.show_building_menu = False
        self.hovering_grid_pos = None
        self.tooltip_text = None

        self.update_timer = 0
        self.UPDATE_INTERVAL = 30  # Update suggestions every 30 frames

        self.selected_building = None
        self.show_building_info = False
        self.show_setup_instructions = True
        
        # Message display state
        self.message = None
        self.message_timer = 0
        self.MESSAGE_DURATION = 120  # Show messages for 2 seconds (60 fps * 2)

        # Visual Feedback
        self.show_efficiency_overlay = False
        self.show_satisfaction_overlay = False
        self.labor_alerts = []

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
            
            # Handle button clicks first
            if self.handle_button_clicks(mouse_pos):
                return

            # Handle building placement with left click only
            if self.show_building_menu and event.button == 1:  # Left click
                if self.selected_building_type and self.hovering_grid_pos:
                    x, y = self.world.get_pixel_position(*self.hovering_grid_pos)
                    success, message = self.world.build_structure(self.selected_building_type, x, y)
                    if success:
                        self.world.update_building_zones()
                        self.world.update_colony_needs()
                        self.tooltip_text = self.generate_building_suggestion()
                    else:
                        self.tooltip_text = message
            
            # Handle building info on right click only
            elif event.button == 3:  # Right click
                self.handle_building_click(mouse_pos, right_click=True)

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

            # Toggle overlays with hotkeys
            if event.key == pygame.K_e:  # 'E' for efficiency
                self.show_efficiency_overlay = not self.show_efficiency_overlay
            elif event.key == pygame.K_s:  # 'S' for satisfaction
                self.show_satisfaction_overlay = not self.show_satisfaction_overlay

        if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:  # Left click
            # Show setup instructions until initial buildings are complete
            if not self.world.initial_setup_complete:
                if not self.show_building_menu:
                    self.show_message("Open the Build menu to place required buildings")
                    self.show_setup_instructions = True

    def handle_button_clicks(self, mouse_pos):
        """Handle UI button clicks and return True if a button was clicked"""
        for button_type, button in self.buttons.items():
            if button.rect.collidepoint(mouse_pos):
                if button_type == 'build':
                    self.show_building_menu = not self.show_building_menu
                    if not self.show_building_menu:
                        self.selected_building_type = None
                        self.tooltip_text = None
                    else:
                        self.world.update_building_zones()
                return True
        return False

    def handle_building_click(self, mouse_pos, right_click=False):
        """Handle building selection and interaction"""
        # Convert screen coordinates to world coordinates
        world_pos = self.screen_to_world(mouse_pos)
        clicked_building = None
        
        # Check for building clicks
        for building in self.world.buildings:
            building_rect = pygame.Rect(
                (building.x + self.camera_x) * self.zoom,
                (building.y + self.camera_y) * self.zoom,
                building.base_size * self.zoom,
                building.base_size * self.zoom
            )
            if building_rect.collidepoint(mouse_pos):
                clicked_building = building
                break
                
        if clicked_building:
            if right_click:
                # Toggle critical position flag
                if (clicked_building.x, clicked_building.y) in self.critical_positions:
                    self.critical_positions.remove((clicked_building.x, clicked_building.y))
                    self.show_message(f"Removed critical position flag from {clicked_building.building_type}")
                else:
                    self.critical_positions.add((clicked_building.x, clicked_building.y))
                    self.show_message(f"Marked {clicked_building.building_type} as critical position")
            else:
                # Select building and show info
                self.selected_building = clicked_building
                self.show_building_info = True

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
        # Update camera position based on both WASD and arrow keys
        if self.keys_pressed[pygame.K_LEFT] or self.keys_pressed[pygame.K_a]:
            self.camera_velocity_x += self.camera_acceleration
        if self.keys_pressed[pygame.K_RIGHT] or self.keys_pressed[pygame.K_d]:
            self.camera_velocity_x -= self.camera_acceleration
        if self.keys_pressed[pygame.K_UP] or self.keys_pressed[pygame.K_w]:
            self.camera_velocity_y += self.camera_acceleration
        if self.keys_pressed[pygame.K_DOWN] or self.keys_pressed[pygame.K_s]:
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
        self.buttons['build'].active = self.show_building_menu

        # Update message timer
        if self.message and self.message_timer > 0:
            self.message_timer -= 1
            if self.message_timer <= 0:
                self.message = None

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
        stats_panel_y = self.buttons['build'].rect.bottom + 20
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

        # Draw score in top right corner
        score_text = f"Score: {self.world.score:,}"
        score_surface = self.font.render(score_text, True, COLORS['text_header'])
        score_x = self.screen.get_width() - score_surface.get_width() - 20
        score_y = 20
        
        # Draw background for score
        padding = 10
        score_bg = pygame.Rect(
            score_x - padding,
            score_y - padding,
            score_surface.get_width() + padding * 2,
            score_surface.get_height() + padding * 2
        )
        pygame.draw.rect(self.screen, COLORS['panel'], score_bg)
        pygame.draw.rect(self.screen, COLORS['border'], score_bg, 1)
        self.screen.blit(score_surface, (score_x, score_y))

        # Draw building info if selected
        if self.show_building_info and self.selected_building:
            self._render_building_info(self.screen)

        # Show initial setup instructions and preview
        if not self.world.initial_setup_complete and self.show_setup_instructions:
            self._render_setup_instructions()

        # Draw message if active
        if self.message and self.message_timer > 0:
            self._render_message()

        # Add directives menu rendering
        if self.directive_menu_open:
            self.draw_directives_menu(self.screen.get_width() - 360, 50)

        # Add job fair and critical position rendering
        if self.show_job_fair:
            self.draw_job_fair(self.screen.get_width() - 420, 50)
            
        # Draw critical position overlays
        self.draw_critical_positions(self.screen)

        # Draw efficiency overlay if enabled
        if self.show_efficiency_overlay:
            self.draw_efficiency_overlay(self.screen)
            
        # Draw satisfaction overlay if enabled
        if self.show_satisfaction_overlay:
            self.draw_satisfaction_overlay(self.screen)

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
        resources = [(resource, amount) for resource, amount in self.world.colony_inventory.items() if resource is not None]
        panel_height = (len(resources) + 4) * resource_spacing + padding * 2  # Extra space for needs
        panel_width = 280
        
        # Draw panel background
        self._draw_panel(x, y, panel_width, panel_height, "Resources & Needs")
        
        current_y = y + padding + 25  # Account for title
        
        # Draw resources
        for resource, amount in resources:
            # Ensure resource is not None before calling title()
            resource_name = resource if resource is None else resource.title()
            text = f"{resource_name}: {amount:.1f}"
            color = COLORS['text'] if amount >= 100 else COLORS['error']  # Fix color logic
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
                color = COLORS[status]
                self.draw_text(screen, text, x + padding, current_y, color)
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
            if resource is not None:  # Check for None resources
                resource_name = resource.title()
                text = f"{resource_name}: {amount:.1f}"
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
                if pygame.mouse.get_pressed()[0] and can_afford:
                    self.selected_building_type = building_type
                    self.world.update_building_zones()
                # Add subtle hover effect
                s = pygame.Surface((button_rect.width, button_rect.height))
                s.set_alpha(15)  # Subtle hover effect
                s.fill((255, 255, 255))
                screen.blit(s, button_rect, special_flags=pygame.BLEND_ADD)
            
            y += button_height + 5

    def _render_building_preview(self, screen):
        """Render building placement preview with improved accuracy during/after expansion"""
        if not self.selected_building_type:
            return
            
        mouse_pos = pygame.mouse.get_pos()
        world_pos = self.screen_to_world(mouse_pos)
        
        # Convert to grid position with proper offsets applied
        grid_x = int((world_pos[0] - self.world.offset_x) / TILE_SIZE)
        grid_y = int((world_pos[1] - self.world.offset_y) / TILE_SIZE)
        self.hovering_grid_pos = (grid_x, grid_y)
        
        # Only show preview for valid grid positions
        if 0 <= grid_x < self.world.current_size and 0 <= grid_y < self.world.current_size:
            # Get exact grid-aligned position with proper offset
            pixel_x = grid_x * TILE_SIZE + self.world.offset_x
            pixel_y = grid_y * TILE_SIZE + self.world.offset_y
            
            # Convert world coordinates to screen coordinates with zoom
            screen_x = int((pixel_x + self.camera_x) * self.zoom)
            screen_y = int((pixel_y + self.camera_y) * self.zoom)
            
            # Get building size and scale with zoom
            building_size = BUILDING_TYPES[self.selected_building_type]['size']
            total_size = int(building_size * TILE_SIZE * self.zoom)
            
            # Check if placement is valid
            can_build, message = self.world.can_build(self.selected_building_type, pixel_x, pixel_y)
            
            # Create preview surface with proper size
            highlight_surface = pygame.Surface((total_size, total_size))
            highlight_surface.set_alpha(160)  # Slightly more opaque for better visibility
            
            # Set color based on validity
            if can_build:
                color = (100, 255, 100)  # Green for valid
                self.tooltip_text = f"Click to build {self.selected_building_type}"
            else:
                color = (255, 100, 100)  # Red for invalid
                self.tooltip_text = message
                
            highlight_surface.fill(color)
            screen.blit(highlight_surface, (screen_x, screen_y))
            
            # Draw grid lines to show tiles more clearly
            line_color = (255, 255, 255)
            line_thickness = max(1, int(self.zoom))
            
            # Draw all vertical grid lines within the building footprint
            for i in range(building_size + 1):
                line_x = screen_x + i * int(TILE_SIZE * self.zoom)
                pygame.draw.line(screen, line_color,
                               (line_x, screen_y),
                               (line_x, screen_y + total_size), line_thickness)
                
            # Draw all horizontal grid lines within the building footprint
            for i in range(building_size + 1):
                line_y = screen_y + i * int(TILE_SIZE * self.zoom)
                pygame.draw.line(screen, line_color,
                               (screen_x, line_y),
                               (screen_x + total_size, line_y), line_thickness)
                
            # Draw building type label if zoomed in enough
            if self.zoom >= 0.8:
                label = self.font.render(self.selected_building_type.title(), True, (255, 255, 255))
                label_bg = pygame.Surface((label.get_width() + 4, label.get_height() + 4))
                label_bg.set_alpha(200)
                label_bg.fill((0, 0, 0))
                screen.blit(label_bg, (screen_x + total_size//2 - label.get_width()//2 - 2, 
                                     screen_y + total_size//2 - label.get_height()//2 - 2))
                screen.blit(label, (screen_x + total_size//2 - label.get_width()//2, 
                                  screen_y + total_size//2 - label.get_height()//2))

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

    def _render_building_info(self, screen):
        """Render detailed building information panel"""
        building = self.selected_building
        info_width = 300
        padding = 10
        line_height = 25
        
        # Prepare info lines
        info_lines = [
            f"Type: {building.building_type.title()}",
            f"Status: {'Complete' if building.is_complete else f'Building ({int(building.construction_progress/building.build_time*100)}%)'}",
        ]
        
        # Add specialized info based on building type
        if building.building_type == 'house':
            info_lines.extend([
                f"Occupants: {building.current_occupants}/{building.capacity}",
                f"Happiness Bonus: +{building.happiness_bonus}"
            ])
        elif hasattr(building, 'jobs'):
            filled_jobs = len([j for j in building.jobs if j.employee])
            info_lines.extend([
                f"Workers: {filled_jobs}/{building.max_jobs}",
                f"Efficiency: {int(filled_jobs/building.max_jobs*100 if building.max_jobs else 0)}%"
            ])
        
        if building.produces:
            info_lines.extend([
                f"Produces: {building.produces.title()}",
                f"Production Rate: {building.production_rate:.1f}/day"
            ])
        
        # Calculate panel dimensions
        panel_height = len(info_lines) * line_height + padding * 2
        
        # Position panel near mouse but ensure it stays on screen
        mouse_pos = pygame.mouse.get_pos()
        panel_x = min(screen.get_width() - info_width - padding, mouse_pos[0])
        panel_y = min(screen.get_height() - panel_height - padding, mouse_pos[1])
        
        # Draw panel background
        self._draw_panel(panel_x, panel_y, info_width, panel_height, f"{building.building_type.title()} Info")
        
        # Draw info lines
        for i, line in enumerate(info_lines):
            self.draw_text(screen, line, panel_x + padding, panel_y + padding + i * line_height, COLORS['text'])

    def _render_setup_instructions(self):
        """Render setup instructions panel"""
        setup_panel_width = 300
        setup_panel_x = self.screen.get_width() - setup_panel_width - (270 if self.show_building_menu else 10)
        setup_panel_y = 100  # Position below score display
        
        setup_status = self.world.get_initial_setup_status()
        
        # Create instruction list
        instructions = [
            "Initial Colony Setup",
            "---------------",
            "Click Build Menu and place:",
            "- Farm (Food production)",
            "- Woodcutter (Wood production) ✓",
            "- Quarry (Stone production) ✓",
            "- Mine (Metal production) ✓",
            "",
        ]
        
        # Wrap status text
        status_lines = []
        words = setup_status.split()
        current_line = "Status: "
        for word in words:
            test_line = current_line + word + " "
            if self.font.size(test_line)[0] < setup_panel_width - 40:
                current_line = test_line
            else:
                status_lines.append(current_line)
                current_line = "        " + word + " "
        status_lines.append(current_line)
        
        instructions.extend(status_lines)
        
        # Calculate panel dimensions
        line_height = 25
        panel_height = (len(instructions) + 1) * line_height + 20
        
        # Draw panel
        s = pygame.Surface((setup_panel_width, panel_height))
        s.set_alpha(180)
        s.fill(COLORS['panel'])
        self.screen.blit(s, (setup_panel_x, setup_panel_y))
        pygame.draw.rect(self.screen, COLORS['border'], (setup_panel_x, setup_panel_y, setup_panel_width, panel_height), 1)
        
        # Draw content
        title = self.font.render("Colony Setup", True, COLORS['text_header'])
        self.screen.blit(title, (setup_panel_x + 10, setup_panel_y + 5))
        
        y = setup_panel_y + 30
        for line in instructions:
            color = COLORS['warning'] if "Don't focus only on" in line else \
                    COLORS['accent'] if "All resources" in line else \
                    COLORS['text_header'] if line.startswith("Status:") else \
                    COLORS['text']
            self.draw_text(self.screen, line, setup_panel_x + 10, y, color)
            y += line_height

    def _render_message(self):
        """Render message overlay"""
        padding = 10
        message_surface = self.font.render(self.message, True, COLORS['text'])
        bg_rect = pygame.Rect(
            (self.screen.get_width() - message_surface.get_width()) // 2 - padding,
            100 - padding,
            message_surface.get_width() + padding * 2,
            message_surface.get_height() + padding * 2
        )
        
        s = pygame.Surface((bg_rect.width, bg_rect.height))
        s.set_alpha(230)
        s.fill(COLORS['panel'])
        self.screen.blit(s, bg_rect)
        pygame.draw.rect(self.screen, COLORS['border'], bg_rect, 1)
        
        self.screen.blit(message_surface, (
            (self.screen.get_width() - message_surface.get_width()) // 2,
            100
        ))

    def show_message(self, msg):
        """Display a message to the user"""
        self.message = msg
        self.message_timer = self.MESSAGE_DURATION

    def draw_directives_menu(self, x, y):
        """Draw the directives menu with industry focus and resource priority settings"""
        menu_width = 350
        padding = 15
        item_height = 60
        
        # Calculate total height needed
        total_items = len(self.job_directives) + len(self.resource_priorities) + 2  # +2 for section headers
        height = total_items * item_height + padding * 2
        
        # Draw background
        self._draw_panel(x, y, menu_width, height, "Colony Directives")
        
        current_y = y + padding + 30
        
        # Draw industry focus section
        self.draw_text(self.screen, "Industry Focus", x + padding, current_y, COLORS['text_header'])
        current_y += 30
        
        for industry, value in self.job_directives.items():
            name = industry.replace('_', ' ').title()
            self.draw_text(self.screen, name, x + padding, current_y, COLORS['text'])
            self.draw_slider(x + padding, current_y + 25, menu_width - padding * 3, 20, value, 
                           {'min': 0, 'max': 1, 'step': 0.1, 'format': '{:.0%}'})
            current_y += item_height
        
        # Draw resource priority section
        current_y += 20
        self.draw_text(self.screen, "Resource Priorities", x + padding, current_y, COLORS['text_header'])
        current_y += 30
        
        for resource, priority in self.resource_priorities.items():
            name = resource.replace('_', ' ').title()
            self.draw_text(self.screen, name, x + padding, current_y, COLORS['text'])
            
            # Draw priority buttons
            button_width = 80
            button_spacing = 10
            priority_options = ['low', 'normal', 'critical']
            
            for i, option in enumerate(priority_options):
                button_x = x + padding + i * (button_width + button_spacing)
                button_rect = pygame.Rect(button_x, current_y + 25, button_width, 25)
                
                # Determine button color based on selection
                if priority == option:
                    color = COLORS['accent']
                else:
                    color = COLORS['button']
                
                pygame.draw.rect(self.screen, color, button_rect, border_radius=4)
                pygame.draw.rect(self.screen, COLORS['border'], button_rect, 1, border_radius=4)
                
                # Draw button text
                text = self.font.render(option.title(), True, COLORS['text'])
                text_rect = text.get_rect(center=button_rect.center)
                self.screen.blit(text, text_rect)
                
                # Handle click
                if button_rect.collidepoint(pygame.mouse.get_pos()) and pygame.mouse.get_pressed()[0]:
                    self.resource_priorities[resource] = option
            
            current_y += item_height

    def handle_directives_click(self, mouse_pos):
        """Handle clicks in the directives menu"""
        if self.directive_menu_open:
            menu_x = self.screen.get_width() - 360
            menu_y = 50
            
            # Check for slider interactions
            y = menu_y + 75  # Start after title and first section header
            
            # Handle industry focus sliders
            for industry in self.job_directives:
                slider_rect = pygame.Rect(menu_x + 15, y + 25, 290, 20)
                if slider_rect.collidepoint(mouse_pos):
                    ratio = (mouse_pos[0] - (menu_x + 15)) / 290
                    self.job_directives[industry] = max(0.0, min(1.0, ratio))
                y += 60
            
            # Skip to resource priority section
            y += 50
            
            # Handle resource priority buttons
            for resource in self.resource_priorities:
                for i, priority in enumerate(['low', 'normal', 'critical']):
                    button_rect = pygame.Rect(menu_x + 15 + i * 90, y + 25, 80, 25)
                    if button_rect.collidepoint(mouse_pos):
                        self.resource_priorities[resource] = priority
                y += 60

    def draw_job_fair(self, x, y):
        """Draw the job fair interface for new colonist career guidance"""
        if not self.show_job_fair or not self.job_fair_candidates:
            return
            
        menu_width = 400
        padding = 15
        item_height = 120
        
        # Calculate height based on candidates
        height = (len(self.job_fair_candidates) * item_height) + padding * 3 + 40  # Extra for header
        
        # Draw background
        self._draw_panel(x, y, menu_width, height, "Colony Job Fair")
        
        current_y = y + padding + 30
        
        for colonist in self.job_fair_candidates:
            # Draw colonist info box
            box_rect = pygame.Rect(x + padding, current_y, menu_width - padding * 2, item_height - 10)
            pygame.draw.rect(self.screen, COLORS['panel_highlight'], box_rect, border_radius=4)
            pygame.draw.rect(self.screen, COLORS['border'], box_rect, 1, border_radius=4)
            
            # Draw colonist details
            name_y = current_y + 10
            self.draw_text(self.screen, f"Colonist {colonist.id}", x + padding * 2, name_y, COLORS['text_header'])
            
            # Draw traits that influence job suitability
            traits_y = name_y + 25
            traits = [
                f"Work Ethic: {colonist.traits['work_ethic']}%",
                f"Intelligence: {colonist.traits['intelligence']}%",
                f"Creativity: {colonist.traits['creativity']}%"
            ]
            for i, trait in enumerate(traits):
                self.draw_text(self.screen, trait, x + padding * 2, traits_y + i * 20, COLORS['text_secondary'])
            
            # Draw job recommendation buttons
            button_y = traits_y + 25
            recommended_jobs = self.get_recommended_jobs(colonist)
            button_width = 100
            for i, (job, score) in enumerate(recommended_jobs):
                button_rect = pygame.Rect(
                    x + padding * 2 + i * (button_width + 10),
                    button_y,
                    button_width,
                    25
                )
                
                # Color based on recommendation strength
                color = COLORS['success'] if score > 0.7 else COLORS['warning'] if score > 0.4 else COLORS['button']
                
                pygame.draw.rect(self.screen, color, button_rect, border_radius=4)
                pygame.draw.rect(self.screen, COLORS['border'], button_rect, 1, border_radius=4)
                
                # Draw job name
                text = self.font.render(job.title(), True, COLORS['text'])
                text_rect = text.get_rect(center=button_rect.center)
                self.screen.blit(text, text_rect)
                
                if button_rect.collidepoint(pygame.mouse.get_pos()):
                    self.tooltip_text = f"Match Score: {score:.0%}"
                    if pygame.mouse.get_pressed()[0]:
                        self.assign_job_preference(colonist, job)
            
            current_y += item_height

    def draw_critical_positions(self, screen):
        """Draw overlay for buildings with critical position flags"""
        for position in self.critical_positions:
            # Find building at this position
            building = next((b for b in self.world.buildings if (b.x, b.y) == position), None)
            if building:
                # Convert building position to screen coordinates
                screen_x = int((building.x + self.camera_x) * self.zoom)
                screen_y = int((building.y + self.camera_y) * self.zoom)
                
                # Draw highlight
                size = int(building.base_size * self.zoom)
                s = pygame.Surface((size, size))
                s.set_alpha(128)
                s.fill((255, 100, 100))  # Red highlight for critical positions
                screen.blit(s, (screen_x, screen_y))
                
                # Draw icon
                icon_size = min(24, size // 2)
                pygame.draw.polygon(screen, COLORS['error'],
                    [
                        (screen_x + size//2, screen_y + icon_size//2),
                        (screen_x + size//2 - icon_size//2, screen_y + icon_size),
                        (screen_x + size//2 + icon_size//2, screen_y + icon_size)
                    ]
                )

    def get_recommended_jobs(self, colonist):
        """Calculate job recommendations based on colonist traits and colony needs"""
        recommendations = []
        
        # Define job requirements and weights
        job_profiles = {
            'farmer': {
                'work_ethic': 0.6,
                'intelligence': 0.2,
                'creativity': 0.2
            },
            'miner': {
                'work_ethic': 0.7,
                'intelligence': 0.2,
                'creativity': 0.1
            },
            'teacher': {
                'intelligence': 0.6,
                'creativity': 0.3,
                'work_ethic': 0.1
            },
            'researcher': {
                'intelligence': 0.7,
                'creativity': 0.2,
                'work_ethic': 0.1
            },
            'merchant': {
                'creativity': 0.5,
                'intelligence': 0.3,
                'work_ethic': 0.2
            }
        }
        
        # Calculate match scores
        for job, requirements in job_profiles.items():
            score = 0
            for trait, weight in requirements.items():
                trait_value = colonist.traits.get(trait, 0) / 100  # Convert to 0-1 scale
                score += trait_value * weight
                
            # Adjust score based on colony needs
            if self.job_directives.get(job, 0) > 0.7:  # High priority industry
                score *= 1.2
            elif self.job_directives.get(job, 0) < 0.3:  # Low priority industry
                score *= 0.8
                
            recommendations.append((job, score))
        
        # Sort by score and return top 3
        recommendations.sort(key=lambda x: x[1], reverse=True)
        return recommendations[:3]

    def assign_job_preference(self, colonist, job_type):
        """Set a colonist's job preference and update the UI"""
        colonist.job_preference = job_type
        self.job_fair_candidates.remove(colonist)
        
        # Check for critical positions that match the job type
        for building in self.world.buildings:
            if ((building.x, building.y) in self.critical_positions and 
                building.building_type == job_type and
                building.is_complete):
                # Find an empty job slot
                for job in building.jobs:
                    if not job.employee:
                        job.employee = colonist
                        colonist.job = job
                        self.manual_assignments[colonist.id] = (building.x, building.y)
                        self.show_message(f"Assigned to critical {job_type} position")
                        return
        
        self.show_message(f"Set job preference: {job_type.title()}")
        
        # If no more candidates, close the job fair
        if not self.job_fair_candidates:
            self.show_job_fair = False

    def draw_efficiency_overlay(self, screen):
        """Draw building efficiency overlay with visual indicators"""
        for building in self.world.buildings:
            if not hasattr(building, 'jobs'):
                continue
                
            # Calculate efficiency
            filled_jobs = len([j for j in building.jobs if j.employee])
            efficiency = filled_jobs / building.max_jobs if building.max_jobs else 0
            
            # Convert building position to screen coordinates
            screen_x = int((building.x + self.camera_x) * self.zoom)
            screen_y = int((building.y + self.camera_y) * self.zoom)
            size = int(building.base_size * self.zoom)
            
            # Create efficiency indicator
            s = pygame.Surface((size, size))
            s.set_alpha(160)
            
            # Color based on efficiency
            if efficiency >= 0.8:
                color = (100, 255, 100)  # Green for high efficiency
            elif efficiency >= 0.5:
                color = (255, 255, 100)  # Yellow for medium efficiency
            else:
                color = (255, 100, 100)  # Red for low efficiency
                
            s.fill(color)
            screen.blit(s, (screen_x, screen_y))
            
            # Draw efficiency percentage
            text = self.font.render(f"{int(efficiency * 100)}%", True, (0, 0, 0))
            text_rect = text.get_rect(center=(screen_x + size//2, screen_y + size//2))
            screen.blit(text, text_rect)

    def draw_satisfaction_overlay(self, screen):
        """Draw worker satisfaction overlay"""
        for building in self.world.buildings:
            if not hasattr(building, 'jobs'):
                continue
                
            # Calculate average satisfaction
            workers = [j.employee for j in building.jobs if j.employee]
            if not workers:
                continue
                
            avg_satisfaction = sum(w.job_satisfaction for w in workers) / len(workers)
            
            # Convert building position to screen coordinates
            screen_x = int((building.x + self.camera_x) * self.zoom)
            screen_y = int((building.y + self.camera_y) * self.zoom)
            size = int(building.base_size * self.zoom)
            
            # Create satisfaction indicator
            s = pygame.Surface((size, 5))  # Thin bar at top of building
            s.set_alpha(200)
            
            # Color based on satisfaction
            if avg_satisfaction >= 0.8:
                color = (100, 255, 100)
            elif avg_satisfaction >= 0.5:
                color = (255, 255, 100)
            else:
                color = (255, 100, 100)
                
            s.fill(color)
            screen.blit(s, (screen_x, screen_y))
            
            # Draw small icon if satisfaction is critically low
            if avg_satisfaction < 0.3:
                icon_size = min(16, size // 3)
                pygame.draw.polygon(screen, COLORS['error'],
                    [
                        (screen_x + size - icon_size, screen_y),
                        (screen_x + size, screen_y),
                        (screen_x + size, screen_y + icon_size)
                    ]
                )

    def update_map_dimensions(self, width, height):
        """Update camera and UI elements when the map size changes"""
        # Update camera bounds based on new map size
        self.world_width = width
        self.world_height = height
        
        # Adjust camera position to ensure the expanded map is visible
        # Center camera on the existing content rather than on the edges
        center_x = width / 2
        center_y = height / 2
        
        # Show a message about the map expansion
        self.show_message(f"Map expanded to {width // TILE_SIZE}x{height // TILE_SIZE} tiles")
        
        # Recalculate building zones with the new dimensions
        if hasattr(self.world, 'update_building_zones'):
            self.world.update_building_zones()
