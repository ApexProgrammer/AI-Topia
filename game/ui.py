import pygame
from .config import WINDOW_WIDTH, WINDOW_HEIGHT, BUILDING_TYPES, EXPANSION_COST

class Button:
    def __init__(self, x, y, width, height, text, color):
        self.rect = pygame.Rect(x, y, width, height)
        self.text = text
        self.color = color
        self.hovered = False

    def draw(self, screen):
        color = (min(self.color[0] + 20, 255),
                min(self.color[1] + 20, 255),
                min(self.color[2] + 20, 255)) if self.hovered else self.color
        pygame.draw.rect(screen, color, self.rect)
        pygame.draw.rect(screen, (0, 0, 0), self.rect, 2)
        
        font = pygame.font.Font(None, 24)
        text_surface = font.render(self.text, True, (0, 0, 0))
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
            'laws': Button(340, button_y, 100, button_height, 'Laws', (200, 200, 150))
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
        
        elif event.type == pygame.KEYUP:
            if event.key in self.keys_pressed:
                self.keys_pressed[event.key] = False

    def handle_policy_click(self, mouse_pos):
        """Handle clicks in the policy menu"""
        menu_x = self.screen.get_width() - 310
        menu_y = 10
        
        # Calculate click positions for policy adjustments
        y = menu_y + 20
        for policy, value in self.policies.items():
            if isinstance(value, bool):
                # Toggle boolean policies
                if menu_x + 10 <= mouse_pos[0] <= menu_x + 290 and y <= mouse_pos[1] <= y + 25:
                    self.policies[policy] = not value
            elif policy == 'tax_rate':
                # Adjust tax rate with +/- buttons
                if menu_x + 200 <= mouse_pos[0] <= menu_x + 220 and y <= mouse_pos[1] <= y + 25:
                    self.policies[policy] = min(0.5, self.policies[policy] + 0.01)
                elif menu_x + 230 <= mouse_pos[0] <= menu_x + 250 and y <= mouse_pos[1] <= y + 25:
                    self.policies[policy] = max(0.05, self.policies[policy] - 0.01)
            elif policy == 'minimum_wage':
                # Adjust minimum wage with +/- buttons
                if menu_x + 200 <= mouse_pos[0] <= menu_x + 220 and y <= mouse_pos[1] <= y + 25:
                    self.policies[policy] = min(20, self.policies[policy] + 0.5)
                elif menu_x + 230 <= mouse_pos[0] <= menu_x + 250 and y <= mouse_pos[1] <= y + 25:
                    self.policies[policy] = max(5, self.policies[policy] - 0.5)
            elif policy == 'birth_incentive':
                # Adjust birth incentive with +/- buttons
                if menu_x + 200 <= mouse_pos[0] <= menu_x + 220 and y <= mouse_pos[1] <= y + 25:
                    self.policies[policy] = min(500, self.policies[policy] + 25)
                elif menu_x + 230 <= mouse_pos[0] <= menu_x + 250 and y <= mouse_pos[1] <= y + 25:
                    self.policies[policy] = max(0, self.policies[policy] - 25)
            y += 30

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
        menu_x = self.screen.get_width() - 310
        menu_y = 10
        width = 300
        height = 400
        
        # Draw background
        s = pygame.Surface((width, height))
        s.set_alpha(200)
        s.fill((50, 50, 50))
        self.screen.blit(s, (menu_x, menu_y))
        
        # Draw policy options with sliders/toggles
        y = menu_y + 20
        for policy, value in self.policies.items():
            if isinstance(value, bool):
                text = f"{policy.replace('_', ' ').title()}: {'On' if value else 'Off'}"
            elif policy == 'tax_rate':
                text = f"Tax Rate: {value*100:.1f}%"
            elif policy == 'minimum_wage':
                text = f"Minimum Wage: ${value:.2f}/hr"
            elif policy == 'birth_incentive':
                text = f"Birth Incentive: ${value}"
            else:
                text = f"{policy.replace('_', ' ').title()}: {value}"
            
            text_surface = self.font.render(text, True, (255, 255, 255))
            self.screen.blit(text_surface, (menu_x + 10, y))
            y += 30

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
