import pygame
from .config import WINDOW_WIDTH, WINDOW_HEIGHT, BUILDING_TYPES, EXPANSION_COST

class Button:
    def __init__(self, x, y, width, height, text, color):
        self.rect = pygame.Rect(x, y, width, height)
        self.text = text
        self.color = color
        self.hovered = False

    def draw(self, screen):
        # Draw subtle shadow
        shadow_rect = self.rect.copy()
        shadow_rect.x += 3
        shadow_rect.y += 3
        pygame.draw.rect(screen, (0,0,0), shadow_rect, border_radius=8)
        # Use rounded rectangle drawing
        draw_color = (min(self.color[0] + 20, 255),
                      min(self.color[1] + 20, 255),
                      min(self.color[2] + 20, 255)) if self.hovered else self.color
        pygame.draw.rect(screen, draw_color, self.rect, border_radius=8)
        pygame.draw.rect(screen, (0, 0, 0), self.rect, 2, border_radius=8)
        
        font = pygame.font.Font(None, 24)
        text_surface = font.render(self.text, True, (255, 255, 255))
        text_rect = text_surface.get_rect(center=self.rect.center)
        screen.blit(text_surface, text_rect)

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
        
        # Government interface
        button_y = 10
        button_height = 30
        self.buttons = {
            'policies': Button(10, button_y, 100, button_height, 'Policies', (150, 150, 200)),
            'election': Button(120, button_y, 100, button_height, 'Elections', (200, 150, 150)),
            'taxes': Button(230, button_y, 100, button_height, 'Taxes', (150, 200, 150)),
            'laws': Button(340, button_y, 100, button_height, 'Laws', (200, 200, 150)),
            'scenario': Button(450, button_y, 100, button_height, 'Scenario', (200, 200, 200))  # new button
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
        if event.type == pygame.MOUSEBUTTONDOWN:
            mouse_pos = pygame.mouse.get_pos()
            screen_pos = self.screen_to_world(mouse_pos)
            
            # Handle button clicks
            for button_type, button in self.buttons.items():
                if button.rect.collidepoint(mouse_pos):
                    if button_type == 'policies':
                        self.policy_menu_open = not self.policy_menu_open
                        self.law_menu_open = False
                        self.show_election_info = False
                    elif button_type == 'election':
                        self.show_election_info = not self.show_election_info
                        self.policy_menu_open = False
                        self.law_menu_open = False
                    elif button_type == 'taxes':
                        # Toggle tax adjustment interface
                        self.policy_menu_open = True
                        self.law_menu_open = False
                        self.show_election_info = False
                    elif button_type == 'laws':
                        self.law_menu_open = not self.law_menu_open
                        self.policy_menu_open = False
                        self.show_election_info = False
                    elif button_type == 'scenario':
                        # Manually trigger a new scenario if one is not active
                        if not self.world.scenario_manager.active_scenario:
                            self.world.scenario_manager.trigger_scenario()
                        return
                    return
            
            # Handle policy adjustments
            if self.policy_menu_open:
                self.handle_policy_click(mouse_pos)
            elif self.law_menu_open:
                self.handle_law_click(mouse_pos)
            else:
                # Handle colonist selection
                self.show_colonist_info = False
                self.selected_colonist = None
                for colonist in self.world.colonists:
                    dx = colonist.x - screen_pos[0]
                    dy = colonist.y - screen_pos[1]
                    if (dx*dx + dy*dy) < 100:  # Click radius
                        self.selected_colonist = colonist
                        self.show_colonist_info = True
                        break
            
            # Handle building placement
            if event.button == 1:  # Left click
                if self.selected_building_type and self.hovering_grid_pos:
                    # Try to place building
                    x, y = self.world.get_pixel_position(*self.hovering_grid_pos)
                    success, message = self.world.build_structure(self.selected_building_type, x, y)
                    if not success:
                        self.tooltip_text = message
            elif event.button == 3:  # Right click
                self.show_building_menu = not self.show_building_menu
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
            
            # If a scenario is active, allow decisions via number keys
            if self.world.scenario_manager.active_scenario:
                if event.key == pygame.K_1:
                    self.world.scenario_manager.choose_option(0)
                elif event.key == pygame.K_2:
                    self.world.scenario_manager.choose_option(1)
                # Add additional keys if more options are added
        
        elif event.type == pygame.KEYUP:
            if event.key in self.keys_pressed:
                self.keys_pressed[event.key] = False

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

        """Update UI state and suggestions"""
        # Update building zones periodically
        self.update_timer += 1
        if self.update_timer >= self.UPDATE_INTERVAL:
            self.update_timer = 0
            if self.show_building_menu:
                self.world.update_building_zones()
                self.world.update_colony_needs()
                self.tooltip_text = self.generate_building_suggestion()

    def handle_input(self, event):
        if event.type == pygame.MOUSEBUTTONDOWN:
            if event.button == 1:  # Left click
                if self.selected_building_type and self.hovering_grid_pos:
                    # Attempt to place building
                    x, y = self.world.get_pixel_position(*self.hovering_grid_pos)
                    success, message = self.world.build_structure(self.selected_building_type, x, y)
                    if success:
                        # Update suggestions immediately after placement
                        self.world.update_building_zones()
                        self.world.update_colony_needs()
                        self.tooltip_text = self.generate_building_suggestion()
                    else:
                        self.tooltip_text = message
            elif event.button == 3:  # Right click
                self.show_building_menu = not self.show_building_menu
                self.selected_building_type = None
                if self.show_building_menu:
                    self.world.update_building_zones()

        elif event.type == pygame.KEYDOWN:
            if event.key == pygame.K_ESCAPE:
                self.selected_building_type = None
                self.show_building_menu = False
            elif event.key == pygame.K_b:
                self.show_building_menu = not self.show_building_menu
                if self.show_building_menu:
                    self.world.update_building_zones()

    def screen_to_world(self, pos):
        """Convert screen coordinates to world coordinates"""
        return ((pos[0] - self.camera_x) / self.zoom,
                (pos[1] - self.camera_y) / self.zoom)

    def world_to_screen(self, pos):
        """Convert world coordinates to screen coordinates"""
        return (pos[0] * self.zoom + self.camera_x,
                pos[1] * self.zoom + self.camera_y)

    def render(self):
        # Draw buttons
        for button in self.buttons.values():
            button.draw(self.screen)
        
        # Draw stats
        stats_y = 50
        stats = [
            f"Score:",
            f"Population: {len(self.world.colonists)}",
            f"Treasury: ${self.world.treasury:,.2f}",
            f"GDP: ${self.world.gdp:,.2f}",
            f"Average Happiness: {self.get_average_happiness():,.1f}%",
            f"Birth Rate: {self.get_birth_rate():,.1f}/year",
            f"Employment Rate: {self.get_employment_rate():,.1f}%",
            f"Map Size: {self.world.current_size}x{self.world.current_size}"
        ]
        
        for i, stat in enumerate(stats):
            text = self.font.render(stat, True, (255, 255, 255))
            self.screen.blit(text, (10, stats_y + i * 25))
        
        # Draw current leader info if exists
        if self.world.leader and self.world.leader in self.world.colonists:
            leader_y = stats_y + len(stats) * 25 + 20
            leader_stats = [
                "Current Leader:",
                f"Name: Colonist #{self.world.colonists.index(self.world.leader)}",
                f"Age: {int(self.world.leader.age)}",
                f"Approval: {self.get_leader_approval():,.1f}%",
                f"Political Alignment: {self.get_political_description(self.world.leader.political_alignment)}",
                f"Term Remaining: {self.get_term_remaining()} days"
            ]
            
            for i, stat in enumerate(leader_stats):
                text = self.font.render(stat, True, (200, 200, 255))
                self.screen.blit(text, (10, leader_y + i * 25))
        elif self.world.election_timer >= self.world.term_length - 200:
            # Show election status if no leader and election is upcoming
            text = self.font.render("Election in Progress...", True, (255, 200, 200))
            self.screen.blit(text, (10, stats_y + len(stats) * 25 + 20))
        
        # Draw menus
        if self.policy_menu_open:
            self.draw_policy_menu()
        if self.law_menu_open:
            self.draw_law_menu()
        if self.show_election_info:
            self.draw_election_info()
        if self.show_colonist_info and self.selected_colonist:
            self.draw_colonist_info()
        
        # Render scenario overlay if active
        if self.world.scenario_manager.active_scenario:
            self.world.scenario_manager.render(self.screen, self.font)
        
        # Render colony status indicators
        self._render_resource_indicators(self.screen)
        self._render_alerts(self.screen)
        
        # Render building menu if open
        if self.show_building_menu:
            self._render_building_menu(self.screen)
            
        # Render building placement preview
        if self.selected_building_type:
            self._render_building_preview(self.screen)
            
        # Render tooltip
        if self.tooltip_text:
            self._render_tooltip(self.screen)

    def get_average_happiness(self):
        if not self.world.colonists:
            return 0
        return sum(c.happiness for c in self.world.colonists) / len(self.world.colonists)

    def get_birth_rate(self):
        """Calculate births per year based on recent history"""
        if not hasattr(self.world, 'birth_history'):
            return 0
            
        # Calculate births per year based on recent history
        recent_time = 60 * 60  # Last minute in ticks
        current_time = pygame.time.get_ticks()
        recent_births = len([event for event in self.world.birth_history 
                           if current_time - event['time'] < recent_time])
        return recent_births * (365 / 60)  # Extrapolate to yearly rate

    def get_employment_rate(self):
        """Calculate the percentage of working-age colonists who have jobs"""
        working_age_colonists = [c for c in self.world.colonists 
                               if 18 <= c.age <= 65]
        if not working_age_colonists:
            return 0
        employed = len([c for c in working_age_colonists if c.job])
        return (employed / len(working_age_colonists)) * 100

    def get_leader_approval(self):
        """Calculate the percentage of colonists who support the current leader"""
        if not self.world.leader or not self.world.colonists or self.world.leader not in self.world.colonists:
            return 0
        supporters = len([c for c in self.world.colonists 
                         if abs(c.political_alignment - self.world.leader.political_alignment) < 0.3])
        return (supporters / len(self.world.colonists)) * 100

    def get_political_description(self, alignment):
        if alignment < 0.2:
            return "Very Conservative"
        elif alignment < 0.4:
            return "Conservative"
        elif alignment < 0.6:
            return "Moderate"
        elif alignment < 0.8:
            return "Progressive"
        else:
            return "Very Progressive"

    def get_term_remaining(self):
        if not self.world.leader:
            return 0
        term_length = 1000  # ticks
        elapsed = self.world.election_timer
        return (term_length - elapsed) // 60  # Convert to days

    def draw_policy_menu(self):
        """Enhanced policy menu with improved visual feedback"""
        menu_x = self.screen.get_width() - 310
        menu_y = 10
        width = 300
        height = len(self.policies) * 60 + 20  # Adjusted for new spacing
        
        # Draw background panel
        s = pygame.Surface((width, height))
        s.set_alpha(230)  # More opaque
        s.fill((40, 40, 50))  # Slightly blue tint
        self.screen.blit(s, (menu_x, menu_y))
        pygame.draw.rect(self.screen, (100, 100, 150), (menu_x, menu_y, width, height), 1)
        
        # Draw title
        title = self.font.render("Policy Settings", True, (200, 200, 255))
        self.screen.blit(title, (menu_x + 10, menu_y + 10))
        
        y = menu_y + 40
        for policy, value in self.policies.items():
            # Draw policy name
            name = policy.replace('_', ' ').title()
            text = self.font.render(name, True, (255, 255, 255))
            self.screen.blit(text, (menu_x + 10, y))
            
            if isinstance(value, bool):
                # Draw toggle switch
                self.draw_toggle(menu_x + 10, y + 25, value, "")
            else:
                # Draw slider with current value
                range_info = self.policy_ranges.get(policy, {'min': 0, 'max': 100, 'step': 1, 'format': '{:.0f}'})
                self.draw_slider(menu_x + 10, y + 25, 200, 20, value, range_info)
                
                # Draw current value
                value_text = range_info['format'].format(value)
                text = self.font.render(value_text, True, (200, 200, 255))
                self.screen.blit(text, (menu_x + 220, y + 25))
            
            y += 60

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
        menu_x = self.screen.get_width() - 310
        menu_y = 10
        width = 300
        height = 400
        
        # Draw background
        s = pygame.Surface((width, height))
        s.set_alpha(200)
        s.fill((50, 50, 50))
        self.screen.blit(s, (menu_x, menu_y))
        
        # Draw laws with toggles
        y = menu_y + 20
        for law, value in self.laws.items():
            text = f"{law.replace('_', ' ').title()}: {'Enforced' if value else 'Not Enforced'}"
            text_surface = self.font.render(text, True, (255, 255, 255))
            self.screen.blit(text_surface, (menu_x + 10, y))
            y += 30

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
        """Draw detailed information about selected colonist"""
        info_x = self.screen.get_width() - 300
        info_y = 100
        padding = 10
        line_height = 25
        
        # Draw background
        pygame.draw.rect(self.screen, (50, 50, 50, 200),
                        (info_x, info_y, 290, 400))
        
        # Draw colonist information
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
        
        for i, line in enumerate(info_lines):
            text = self.font.render(line, True, (255, 255, 255))
            self.screen.blit(text, (info_x + padding, info_y + padding + i * line_height))

    def _render_resource_indicators(self, screen):
        """Render resource levels and colony statistics"""
        y = 10
        for resource, amount in self.world.colony_inventory.items():
            text = f"{resource.title()}: {amount:.1f}"
            color = (255, 255, 255)
            if amount < 100:  # Low resource warning
                color = (255, 200, 200)
            self.draw_text(screen, text, 10, y, color)
            y += 25
            
        # Render colony stats
        stats = self.world.building_requirements
        if stats:
            self.draw_text(screen, f"Housing needed: {stats['housing']}", 10, y, (255, 255, 255))
            y += 25
            self.draw_text(screen, f"Jobs needed: {stats['jobs']}", 10, y, (255, 255, 255))
            y += 25
            self.draw_text(screen, f"Average happiness: {stats['happiness']:.1f}%", 10, y, (255, 255, 255))

    def _render_building_menu(self, screen):
        """Render the building placement menu"""
        menu_rect = pygame.Rect(screen.get_width() - 200, 0, 200, screen.get_height())
        pygame.draw.rect(screen, (0, 0, 0, 180), menu_rect)
        
        y = 10
        for building_type, data in BUILDING_TYPES.items():
            button_rect = pygame.Rect(menu_rect.x + 10, y, 180, 40)
            color = (100, 100, 200) if building_type == self.selected_building_type else (70, 70, 70)
            pygame.draw.rect(screen, color, button_rect)
            
            # Draw building name and cost
            self.draw_text(screen, building_type.title(), button_rect.x + 5, y + 5, (255, 255, 255))
            cost_text = ", ".join(f"{amount} {res}" for res, amount in data.get('cost', {}).items())
            self.draw_text(screen, cost_text, button_rect.x + 5, y + 22, (200, 200, 200), size=12)
            
            # Handle click
            if button_rect.collidepoint(pygame.mouse.get_pos()):
                self.tooltip_text = data.get('description', '')
                if pygame.mouse.get_pressed()[0]:
                    self.selected_building_type = building_type
            
            y += 50

    def _render_building_preview(self, screen):
        """Render building placement preview"""
        mouse_pos = pygame.mouse.get_pos()
        world_pos = self.screen_to_world(mouse_pos)
        grid_x, grid_y = self.world.get_grid_position(world_pos[0], world_pos[1])
        self.hovering_grid_pos = (grid_x, grid_y)
        
        if 0 <= grid_x < self.world.current_size and 0 <= grid_y < self.world.current_size:
            pixel_x, pixel_y = self.world.get_pixel_position(grid_x, grid_y)
            
            # Check if placement is valid
            can_build, message = self.world.can_build(self.selected_building_type, pixel_x, pixel_y)
            color = (100, 255, 100, 128) if can_build else (255, 100, 100, 128)
            
            # Draw preview rectangle
            preview_rect = pygame.Rect(
                pixel_x - self.camera_x,
                pixel_y - self.camera_y,
                TILE_SIZE,
                TILE_SIZE
            )
            pygame.draw.rect(screen, color, preview_rect)
            
            self.tooltip_text = message

    def _render_alerts(self, screen):
        """Render resource and need alerts"""
        y = screen.get_height() - 100
        for alert in self.world.resource_alerts:
            self.draw_text(screen, alert, 10, y, (255, 100, 100))
            y += 25

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
        """Generate building suggestions based on colony needs"""
        suggestions = []
        stats = self.world.building_requirements
        
        if stats['housing'] > 0:
            suggestions.append(f"Need housing for {stats['housing']} colonists")
        
        if stats['jobs'] > 0:
            suggestions.append(f"Need jobs for {stats['jobs']} colonists")
        
        for resource, data in stats['resources'].items():
            if data['amount'] < 5:  # Low resource threshold
                suggestions.append(f"Low on {resource}. Build more {resource} production.")
        
        if stats['happiness'] < 70:
            suggestions.append("Consider building amenities to increase happiness")
            
        return "\n".join(suggestions) if suggestions else "Colony is doing well!"

    def draw_text(self, screen, text, x, y, color=(255, 255, 255), size=24):
        """Helper method to draw text on screen"""
        font = pygame.font.Font(None, size)
        text_surface = font.render(text, True, color)
        screen.blit(text_surface, (x, y))
