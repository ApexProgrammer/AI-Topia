import pygame
import random
import math
from ..ai.neural_network import ColonistBrain, INPUT_SIZE
from ..config import (COLONIST_SPEED, WORKING_AGE, RETIREMENT_AGE, 
                     REPRODUCTION_AGE_MIN, REPRODUCTION_AGE_MAX, 
                     BUILDING_TYPES, TILE_SIZE, MOVEMENT_SPEED,
                     MARRIAGE_CHANCE, ANIMATION_SPEED, WALK_FRAMES, 
                     RESOURCE_CONSUMPTION_RATE, JOB_SALARIES, MINIMUM_WAGE)
from .building import Building

class Colonist:
    def __init__(self, x, y, world):
        self.x = x
        self.y = y
        self.world = world
        self.brain = ColonistBrain()
        
        # Basic attributes
        self.age = random.randint(18, 50)
        self.gender = random.choice(['M', 'F'])
        self.health = 100
        self.energy = 100
        self.money = 1000
        self.happiness = 100
        
        # Visualization
        self.color = (255, 200, 200) if self.gender == 'F' else (200, 200, 255)
        self.size = 10
        
        # Animation state
        self.animation_frame = 0
        self.direction = 'right'  # right, left, up, down
        self.is_walking = False
        
        # Resources
        self.inventory = {
            'food': 0,
            'goods': 0,
            'money': self.money
        }
        
        # Leadership and skills
        self.leadership = random.randint(0, 100)
        self.construction_skill = random.randint(0, 100)
        self.business_skill = random.randint(0, 100)
        
        # Building projects
        self.current_project = None
        self.project_progress = 0
        
        # Personality traits
        self.traits = {
            'ambition': random.randint(20, 100),
            'sociability': random.randint(20, 100),
            'intelligence': random.randint(20, 100),
            'creativity': random.randint(20, 100),
            'work_ethic': random.randint(20, 100),
            'leadership': random.randint(20, 100)
        }
        
        # Status
        self.job = None
        self.home = None
        self.spouse = None
        self.children = []
        self.role = None  # leader, builder, worker, etc.
        
        # AI state
        self.current_task = None
        self.target_position = None
        self.path = []
        
        # Relationships
        self.relationships = {}
        self.friends = []
        self.enemies = []
        
        # Political views
        self.political_alignment = random.random()  # 0 = conservative, 1 = progressive
        self.voted_for = None

        # Movement and pathfinding attributes
        self.target_position = None
        self.current_grid_x = x // TILE_SIZE
        self.current_grid_y = y // TILE_SIZE
        self.interpolation_progress = 1.0
        self.start_pos = (x, y)
        self.prev_pos = (x, y)
        self.next_pos = (x, y)
        self.animation_timer = 0
        self.direction = 'right'
        self.is_walking = False
        self.movement_cooldown = 0
        self.last_move_time = 0
        self.current_path = []  # Store path to target
        self.path_index = 0     # Current position in path
        self.last_target = None # Remember last valid target

    def update(self, speed_multiplier=1.0):
        # Store previous position for interpolation
        self.prev_pos = (self.x, self.y)
        
        # Update relationships
        self.update_relationships()
        
        # Get AI decision focused on gathering and social needs
        state = self.get_state()
        action = self.brain.decide_action(state)
        
        # Execute action with personality influence
        self.execute_action(action)
        
        # Handle movement
        self.move_towards_target()
        
        # Update animation and basic needs
        if self.is_walking:
            self.animation_frame += ANIMATION_SPEED * speed_multiplier
            if self.animation_frame >= WALK_FRAMES:
                self.animation_frame = 0
        
        # Update animation timer for smoother transitions
        if self.is_walking:
            self.animation_timer += ANIMATION_SPEED * speed_multiplier
            if self.animation_timer >= 1.0:
                self.animation_timer = 0
                self.animation_frame = (self.animation_frame + 1) % WALK_FRAMES
        
        self.update_basic_needs(speed_multiplier)
        self.update_happiness()
        self.age += 0.0005 * speed_multiplier

    def update_basic_needs(self, speed_multiplier=1.0):
        """Update basic needs like energy, health, and resources"""
        # Energy consumption based on work ethic and activity
        base_energy_loss = RESOURCE_CONSUMPTION_RATE * (2 - self.traits['work_ethic']/100) * speed_multiplier
        if self.is_walking:
            base_energy_loss *= 1.5
        self.energy = max(0, min(100, self.energy - base_energy_loss))
        
        # Health regeneration when resting
        if self.energy > 50:
            self.health = min(100, self.health + (0.05 * speed_multiplier))
        elif self.energy < 20:
            self.health = max(0, self.health - (0.02 * speed_multiplier))
        
        # Food consumption and effects
        if self.inventory['food'] > 0:
            food_consumed = RESOURCE_CONSUMPTION_RATE * speed_multiplier
            self.inventory['food'] = max(0, self.inventory['food'] - food_consumed)
            self.health = min(100, self.health + (0.1 * speed_multiplier))
            self.energy = min(100, self.energy + (0.2 * speed_multiplier))
        else:
            self.health = max(0, self.health - (0.05 * speed_multiplier))
            self.energy = max(0, self.energy - (0.1 * speed_multiplier))
        
        # Work and earn money
        if self.job and WORKING_AGE <= self.age <= RETIREMENT_AGE:
            # Calculate work efficiency
            efficiency = (1 + (self.traits['work_ethic'] - 50) / 100) * (self.energy / 100)
            
            # Get base salary for job type
            base_salary = JOB_SALARIES.get(self.job.type, MINIMUM_WAGE)
            
            # Calculate daily earnings with bonuses
            earned = (base_salary / 30) * efficiency  # Daily wage
            if self.traits['intelligence'] > 70:
                earned *= 1.2  # Smart worker bonus
            if self.traits['creativity'] > 70:
                earned *= 1.1  # Creative worker bonus
                
            self.money += earned
            self.inventory['money'] = self.money
            
            # Produce resources if applicable
            if hasattr(self.job, 'produces'):
                production = self.job.production_rate * efficiency
                if self.job.produces in self.inventory:
                    self.inventory[self.job.produces] += production
                else:
                    self.inventory[self.job.produces] = production

    def update_happiness(self):
        """Update happiness based on various factors"""
        # Base happiness changes
        if self.health < 50:
            self.happiness -= 0.2
        elif self.health > 80:
            self.happiness += 0.1
            
        if self.energy < 30:
            self.happiness -= 0.2
        elif self.energy > 70:
            self.happiness += 0.1
            
        # Social factors
        if self.spouse:
            self.happiness += 0.2
        if len(self.children) > 0:
            self.happiness += 0.1 * len(self.children)
        if len(self.friends) > 0:
            self.happiness += 0.05 * len(self.friends)
            
        # Economic factors
        if self.job:
            self.happiness += 0.1
        if self.home:
            self.happiness += 0.2
        if self.money > 1000:
            self.happiness += 0.1
        elif self.money < 100:
            self.happiness -= 0.2
            
        # Cap happiness
        self.happiness = max(0, min(100, self.happiness))

    def seek_job(self):
        """Find and move to an available job with enhanced resource production priority"""
        if not self.job and WORKING_AGE <= self.age <= RETIREMENT_AGE:
            available_jobs = self.world.get_available_jobs()
            if available_jobs:
                # Filter jobs by skills and traits with resource production priority
                suitable_jobs = []
                for job in available_jobs:
                    score = 0
                    # Base score from traits
                    if job.type == 'farmer':
                        score = self.traits['work_ethic'] * 1.2  # Priority for food production
                    elif job.type == 'wood_gatherer':
                        score = (self.traits['work_ethic'] + self.traits['intelligence']) / 2 * 1.1
                    elif job.type == 'stone_gatherer':
                        score = (self.traits['work_ethic'] + self.traits['intelligence']) / 2 * 1.1
                    elif job.type == 'metal_gatherer':
                        score = (self.traits['work_ethic'] + self.traits['intelligence']) / 2 * 1.1
                    elif job.type == 'goods_worker':
                        score = (self.traits['creativity'] + self.traits['intelligence']) / 2 * 1.15
                    elif job.type == 'factory_worker':
                        score = (self.traits['work_ethic'] + self.traits['intelligence']) / 2
                    elif job.type == 'shopkeeper':
                        score = (self.traits['sociability'] + self.traits['creativity']) / 2
                    elif job.type == 'banker':
                        score = self.traits['intelligence']
                    elif job.type == 'government_worker':
                        score = (self.traits['intelligence'] + self.traits['leadership']) / 2
                    
                    # Additional score based on colony needs
                    if hasattr(job.building, 'produces'):
                        resource = job.building.produces
                        if resource in self.world.colony_inventory:
                            current_amount = self.world.colony_inventory[resource]
                            if current_amount < 100:  # Low resource threshold
                                score *= 1.5  # Significant boost for needed resources
                            elif current_amount < 200:  # Medium resource threshold
                                score *= 1.2  # Moderate boost
                    
                    if score > 40:  # Lowered threshold to ensure more job assignments
                        suitable_jobs.append((job, score))
                
                if suitable_jobs:
                    # Choose job weighted by suitability score
                    job, _ = max(suitable_jobs, key=lambda x: x[1])
                    self.move_to_job(job)

    def move_to_job(self, job):
        """Move to and take a job with improved pathfinding"""
        if not job:
            return False
            
        job_grid_x, job_grid_y = self.world.get_grid_position(job.x, job.y)
        
        # Find best adjacent position to job
        best_pos = None
        shortest_path = None
        
        for dx, dy in [(0,1), (1,0), (0,-1), (-1,0)]:
            check_x = job_grid_x + dx
            check_y = job_grid_y + dy
            
            if (0 <= check_x < self.world.current_size and 
                0 <= check_y < self.world.current_size):
                
                # Check if position is walkable
                occupants = self.world.get_grid_occupants(check_x, check_y)
                if not any(isinstance(occupant, Building) for occupant in occupants):
                    test_pos = self.world.get_pixel_position(check_x, check_y)
                    if self.set_target_position(test_pos):
                        path_len = len(self.current_path)
                        if shortest_path is None or path_len < shortest_path:
                            shortest_path = path_len
                            best_pos = test_pos
                            
        if best_pos:
            self.target_position = best_pos
            self.job = job
            job.employee = self
            self.happiness += 10
            return True
            
        return False

    def move_towards_target(self):
        """Move towards target position with improved pathfinding"""
        if not self.target_position:
            if random.random() < 0.005:
                self.random_movement()
            return

        # Handle interpolation between grid positions
        if self.interpolation_progress < 1.0:
            # Simple linear interpolation at constant speed
            self.interpolation_progress = min(1.0, self.interpolation_progress + MOVEMENT_SPEED)
            
            # Update position with linear interpolation
            self.x = self.start_pos[0] + (self.next_pos[0] - self.start_pos[0]) * self.interpolation_progress
            self.y = self.start_pos[1] + (self.next_pos[1] - self.start_pos[1]) * self.interpolation_progress
            
            # Update animation state continuously
            self.is_walking = True
            self.animation_timer = (self.animation_timer + ANIMATION_SPEED) % 1.0
            return

        # Check if we need a new path
        if not self.current_path:
            # Try to set target again or clear it if invalid
            if not self.set_target_position(self.target_position):
                self.target_position = None
                self.is_walking = False
                return

        # Get next path position
        if self.path_index < len(self.current_path):
            next_grid_x, next_grid_y = self.current_path[self.path_index]
            current_grid_x, current_grid_y = self.world.get_grid_position(self.x, self.y)

            # Update direction based on movement
            dx = next_grid_x - current_grid_x
            dy = next_grid_y - current_grid_y
            
            if dx != 0 or dy != 0:
                # Remove from current grid
                self.world.remove_from_grid(self, current_grid_x, current_grid_y)

                # Update direction based on primary movement axis
                if abs(dx) > abs(dy):
                    self.direction = 'right' if dx > 0 else 'left'
                else:
                    self.direction = 'down' if dy > 0 else 'up'

                # Store positions for interpolation
                self.start_pos = (self.x, self.y)
                new_pos = self.world.get_pixel_position(next_grid_x, next_grid_y)
                self.next_pos = new_pos
                self.interpolation_progress = 0.0
                
                # Add to new grid position
                self.world.add_to_grid(self, next_grid_x, next_grid_y)
                self.is_walking = True
                self.path_index += 1
            else:
                # Reached target grid position
                self.path_index += 1
        else:
            # Reached end of path
            self.target_position = None
            self.current_path = []
            self.path_index = 0
            self.is_walking = False

    def random_movement(self):
        """Generate random movement within the grid"""
        if not self.target_position:
            current_grid_x, current_grid_y = self.world.get_grid_position(self.x, self.y)
            
            # Try each direction in random order
            directions = [(0,1), (1,0), (0,-1), (-1,0)]
            random.shuffle(directions)
            
            for dx, dy in directions:
                new_grid_x = current_grid_x + dx
                new_grid_y = current_grid_y + dy
                
                if (0 <= new_grid_x < self.world.current_size and 
                    0 <= new_grid_y < self.world.current_size):
                    
                    # Check if position is walkable
                    occupants = self.world.get_grid_occupants(new_grid_x, new_grid_y)
                    if not any(isinstance(occupant, Building) for occupant in occupants):
                        target_pos = self.world.get_pixel_position(new_grid_x, new_grid_y)
                        if self.set_target_position(target_pos):
                            break

    def seek_home(self):
        """Find and move to an available home with improved pathfinding"""
        available_homes = self.world.get_available_homes()
        if not available_homes:
            return False
            
        # Find closest available home with valid path
        best_home = None
        shortest_path = None
        best_pos = None
        
        for home in available_homes:
            home_grid_x, home_grid_y = self.world.get_grid_position(home.x, home.y)
            
            # Check adjacent positions
            for dx, dy in [(0,1), (1,0), (0,-1), (-1,0)]:
                check_x = home_grid_x + dx
                check_y = home_grid_y + dy
                
                if (0 <= check_x < self.world.current_size and 
                    0 <= check_y < self.world.current_size):
                    
                    # Check if position is walkable
                    occupants = self.world.get_grid_occupants(check_x, check_y)
                    if not any(isinstance(occupant, Building) for occupant in occupants):
                        test_pos = self.world.get_pixel_position(check_x, check_y)
                        if self.set_target_position(test_pos):
                            path_len = len(self.current_path)
                            if shortest_path is None or path_len < shortest_path:
                                shortest_path = path_len
                                best_pos = test_pos
                                best_home = home
                                
        if best_pos and best_home:
            self.target_position = best_pos
            self.home = best_home
            best_home.current_occupants += 1
            return True
            
        return False

    def seek_social_interaction(self):
        """Move towards other colonists with improved pathfinding"""
        current_grid_x, current_grid_y = self.world.get_grid_position(self.x, self.y)
        range_tiles = 5
        
        # Find nearby colonists and sort by distance
        nearby_colonists = []
        for dx in range(-range_tiles, range_tiles + 1):
            for dy in range(-range_tiles, range_tiles + 1):
                check_x = current_grid_x + dx
                check_y = current_grid_y + dy
                if (0 <= check_x < self.world.current_size and 
                    0 <= check_y < self.world.current_size):
                    occupants = self.world.get_grid_occupants(check_x, check_y)
                    colonists = [o for o in occupants 
                               if isinstance(o, Colonist) and o != self]
                    for colonist in colonists:
                        dist = abs(dx) + abs(dy)  # Manhattan distance
                        nearby_colonists.append((dist, colonist))
        
        # Sort by distance and try each colonist until we find a valid path
        if nearby_colonists:
            nearby_colonists.sort(key=lambda x: x[0])
            for _, target in nearby_colonists:
                target_grid_x, target_grid_y = self.world.get_grid_position(target.x, target.y)
                
                # Try positions near target in order of proximity
                for dx, dy in [(0,0), (0,1), (1,0), (0,-1), (-1,0)]:
                    check_x = target_grid_x + dx
                    check_y = target_grid_y + dy
                    if (0 <= check_x < self.world.current_size and 
                        0 <= check_y < self.world.current_size):
                        # Check if position is walkable
                        occupants = self.world.get_grid_occupants(check_x, check_y)
                        if not any(isinstance(occupant, Building) for occupant in occupants):
                            test_pos = self.world.get_pixel_position(check_x, check_y)
                            if self.set_target_position(test_pos):
                                return True
            
        return False

    def seek_partner(self):
        """Find and move towards a potential partner"""
        potential_partners = self.world.get_potential_partners(self)
        if potential_partners:
            target = random.choice(potential_partners)
            target_grid_x, target_grid_y = self.world.get_grid_position(target.x, target.y)
            
            # Find nearby empty tile
            for dx, dy in [(0,0), (0,1), (1,0), (0,-1), (-1,0)]:
                check_x = target_grid_x + dx
                check_y = target_grid_y + dy
                if (0 <= check_x < self.world.current_size and 
                    0 <= check_y < self.world.current_size):
                    occupants = self.world.get_grid_occupants(check_x, check_y)
                    if not any(isinstance(occupant, Building) for occupant in occupants):
                        self.target_position = self.world.get_pixel_position(check_x, check_y)
                        
                        # Attempt to form partnership with increased chance
                        if random.random() < MARRIAGE_CHANCE:
                            self.spouse = target
                            target.spouse = self
                            # Boost happiness for new couple
                            self.happiness += 20
                            target.happiness += 20
                        break

    def render(self, screen, camera_x=0, camera_y=0, zoom=1.0):
        """Render colonist with walking animation"""
        # Calculate screen position
        screen_x = int((self.x + camera_x) * zoom)
        screen_y = int((self.y + camera_y) * zoom)
        size = int(10 * zoom)  # Base size
        
        # Draw body
        color = (255, 200, 200) if self.gender == 'F' else (200, 200, 255)
        pygame.draw.circle(screen, color, (screen_x, screen_y), size)
        
        # Enhanced walking animation with consistent leg length across all directions
        if self.is_walking:
            # Calculate leg movement using sine wave
            leg_phase = self.animation_timer * math.pi * 2
            leg_length = 6 * zoom  # Standard leg length
            step_offset = abs(math.sin(leg_phase)) * 3 * zoom  # Reduced offset for more natural look
            
            # Base positions for legs
            base_left = screen_x - 3 * zoom
            base_right = screen_x + 3 * zoom
            base_y = screen_y + size
            
            # Draw legs based on direction
            if self.direction == 'right':
                # Right movement - legs swing forward/back
                leg_y = base_y + leg_length
                pygame.draw.line(screen, color,
                               (base_left, base_y),
                               (base_left - step_offset, leg_y),
                               max(1, int(2 * zoom)))
                pygame.draw.line(screen, color,
                               (base_right, base_y),
                               (base_right + step_offset, leg_y),
                               max(1, int(2 * zoom)))
            elif self.direction == 'left':
                # Left movement - legs swing forward/back (mirrored)
                leg_y = base_y + leg_length
                pygame.draw.line(screen, color,
                               (base_left, base_y),
                               (base_left + step_offset, leg_y),
                               max(1, int(2 * zoom)))
                pygame.draw.line(screen, color,
                               (base_right, base_y),
                               (base_right - step_offset, leg_y),
                               max(1, int(2 * zoom)))
            elif self.direction == 'up':
                # Up movement - legs move side to side
                pygame.draw.line(screen, color,
                               (base_left - step_offset, base_y),
                               (base_left - step_offset, base_y + leg_length),
                               max(1, int(2 * zoom)))
                pygame.draw.line(screen, color,
                               (base_right + step_offset, base_y),
                               (base_right + step_offset, base_y + leg_length),
                               max(1, int(2 * zoom)))
            else:  # down
                # Down movement - legs move side to side
                pygame.draw.line(screen, color,
                               (base_left + step_offset, base_y),
                               (base_left + step_offset, base_y + leg_length),
                               max(1, int(2 * zoom)))
                pygame.draw.line(screen, color,
                               (base_right - step_offset, base_y),
                               (base_right - step_offset, base_y + leg_length),
                               max(1, int(2 * zoom)))
        
        # Draw current activity indicator
        if self.current_task:
            indicator_color = {
                'working': (255, 255, 0),
                'building': (255, 128, 0),
                'shopping': (0, 255, 255),
                'socializing': (255, 192, 203)
            }.get(self.current_task, (255, 255, 255))
            pygame.draw.circle(screen, indicator_color,
                             (screen_x, screen_y - size - 3 * zoom),
                             max(2, int(3 * zoom)))
        
        # Draw relationship indicators
        if self.spouse:
            # Draw heart for married colonists
            pygame.draw.circle(screen, (255, 0, 0),
                             (screen_x, screen_y - size - 8 * zoom),
                             max(2, int(3 * zoom)))

    def get_state(self):
        """Get current state for AI input"""
        # Total 22 features as per INPUT_SIZE configuration
        basic_state = [
            self.x / self.world.width,  # Normalized position
            self.y / self.world.height,
            self.age / 100,  # Normalized age
            self.health / 100,
            self.energy / 100,
            self.money / 10000,  # Normalized money
            self.happiness / 100,
            1 if self.job else 0,
            1 if self.home else 0,
            1 if self.spouse else 0,
        ]
        
        # Add personality traits
        trait_state = [trait_value / 100 for trait_value in self.traits.values()]
        
        # Add social state
        social_state = [
            len(self.friends) / 10,  # Normalized number of friends
            len(self.enemies) / 10,  # Normalized number of enemies
            sum(self.relationships.values()) / (len(self.relationships) * 100) if self.relationships else 0,  # Average relationship strength
        ]
        
        # Add environmental state
        env_state = [
            len(self.world.get_available_jobs()) / 20,  # Normalized available jobs
            len(self.world.get_available_homes()) / 20,  # Normalized available homes
            self.world.treasury / 100000,  # Normalized treasury
        ]
        
        return basic_state + trait_state + social_state + env_state

    def update_relationships(self):
        """Update relationships with other colonists"""
        for other in self.world.colonists:
            if other != self:
                # Initialize relationship if not exists
                if other not in self.relationships:
                    compatibility = self.calculate_compatibility(other)
                    self.relationships[other] = compatibility
                
                # Update relationship based on proximity and interaction
                if ((self.x - other.x)**2 + (self.y - other.y)**2)**0.5 < 50:  # If colonists are close
                    change = random.randint(-2, 2)
                    self.relationships[other] = max(-100, min(100, self.relationships[other] + change))
                    
                    # Update friends and enemies
                    if self.relationships[other] > 50 and other not in self.friends:
                        self.friends.append(other)
                    elif self.relationships[other] < -50 and other not in self.enemies:
                        self.enemies.append(other)

    def calculate_compatibility(self, other):
        """Calculate initial compatibility with another colonist"""
        trait_diff = sum(abs(self.traits[t] - other.traits[t]) for t in self.traits)
        base_compatibility = 100 - trait_diff/len(self.traits)
        return base_compatibility + random.randint(-20, 20)

    def execute_action(self, action):
        """Execute the action chosen by the AI - removed building decisions"""
        if action == 0:  # Find job/gather resources
            if not self.job and WORKING_AGE <= self.age <= RETIREMENT_AGE:
                self.seek_job()
        elif action == 1:  # Find home
            if not self.home:
                self.seek_home()
        elif action == 2:  # Rest
            if self.home:
                self.target_position = (self.home.x, self.home.y)
                self.energy = min(100, self.energy + 10)
        elif action == 3:  # Work/Gather
            if self.job:
                self.target_position = (self.job.x, self.job.y)
                self.gather_resources()
        elif action == 4:  # Socialize
            self.seek_social_interaction()
        elif action == 5:  # Visit shop
            self.visit_nearest_shop()
        elif action == 6:  # Random movement
            self.random_movement()

    def gather_resources(self):
        """Enhanced resource gathering with efficiency bonuses"""
        if not self.job:
            return
            
        # Calculate base efficiency from traits and energy with improved weights
        efficiency = (
            (self.traits['work_ethic'] / 100) * 0.5 +    # Increased work ethic importance
            (self.energy / 100) * 0.2 +                  # Energy level contribution
            (self.happiness / 100) * 0.2 +               # Happiness bonus
            (self.traits['intelligence'] / 100) * 0.1    # Skill bonus
        )
        
        # Enhanced job-specific trait bonuses
        if hasattr(self.job, 'type'):
            if self.job.type == 'farmer':
                efficiency *= 1.2  # Increased farming efficiency
            elif self.job.type == 'wood_gatherer':
                efficiency *= 1.15
            elif self.job.type == 'stone_gatherer':
                efficiency *= 1.1
            elif self.job.type == 'metal_gatherer':
                efficiency *= 1.1
            elif self.job.type == 'goods_worker':
                efficiency *= 1.15
        
        # Enhanced proximity bonus for resource gathering
        if hasattr(self.job, 'building'):
            distance = ((self.x - self.job.building.x)**2 + 
                       (self.y - self.job.building.y)**2)**0.5
            if distance < 50:  # Close to workplace
                efficiency *= 1.3  # Increased proximity bonus
            elif distance < 100:  # Medium distance
                efficiency *= 1.1
        
        # Produce resources with calculated efficiency
        if hasattr(self.job, 'produces'):
            base_production = self.job.production_rate * efficiency
            # Add experience bonus (0-20% extra)
            if hasattr(self, 'work_experience'):
                experience_bonus = min(0.2, self.work_experience / 500)
                production = base_production * (1 + experience_bonus)
            else:
                production = base_production
                
            # Add to world's shared inventory
            self.world.add_to_colony_inventory(self.job.produces, production)
            
            # Energy cost of gathering - reduced for experienced workers
            energy_cost = 0.1 * (1 - (experience_bonus if hasattr(self, 'work_experience') else 0))
            self.energy = max(0, self.energy - energy_cost)
            
            # Small happiness boost from successful gathering
            if random.random() < 0.15:  # Increased chance for happiness boost
                self.happiness = min(100, self.happiness + 1)
            
            # Earn money for work with efficiency bonus
            base_salary = JOB_SALARIES.get(self.job.type, MINIMUM_WAGE)
            earned = (base_salary / 30) * efficiency * (1 + experience_bonus if hasattr(self, 'work_experience') else 1)
            self.money += earned
            self.inventory['money'] = self.money
            
            # Increment work experience
            if not hasattr(self, 'work_experience'):
                self.work_experience = 0
            self.work_experience += 0.1

    def visit_nearest_shop(self):
        """Find and move to the nearest shop with pathfinding"""
        shops = [b for b in self.world.buildings if b.building_type == 'shop']
        if not shops:
            return False
        
        # Sort shops by distance and try each until we find a valid path
        current_grid_x, current_grid_y = self.world.get_grid_position(self.x, self.y)
        shop_distances = []
        
        for shop in shops:
            shop_grid_x, shop_grid_y = self.world.get_grid_position(shop.x, shop.y)
            dist = abs(shop_grid_x - current_grid_x) + abs(shop_grid_y - current_grid_y)
            shop_distances.append((dist, shop))
        
        shop_distances.sort(key=lambda x: x[0])
        
        for _, shop in shop_distances:
            shop_grid_x, shop_grid_y = self.world.get_grid_position(shop.x, shop.y)
            
            # Try positions adjacent to shop
            for dx, dy in [(0,1), (1,0), (0,-1), (-1,0)]:
                check_x = shop_grid_x + dx
                check_y = shop_grid_y + dy
                if (0 <= check_x < self.world.current_size and 
                    0 <= check_y < self.world.current_size):
                    # Check if position is walkable
                    occupants = self.world.get_grid_occupants(check_x, check_y)
                    if not any(isinstance(occupant, Building) for occupant in occupants):
                        test_pos = self.world.get_pixel_position(check_x, check_y)
                        if self.set_target_position(test_pos):
                            return True
        
        return False

    def set_target_position(self, target_pos):
        """Set a new target position with validation"""
        if not target_pos or not self.world:
            return False
            
        # Convert target to grid coordinates
        target_grid_x, target_grid_y = self.world.get_grid_position(target_pos[0], target_pos[1])
        current_grid_x, current_grid_y = self.world.get_grid_position(self.x, self.y)
        
        # Validate target is within bounds
        if not (0 <= target_grid_x < self.world.current_size and 
                0 <= target_grid_y < self.world.current_size):
            return False
            
        # Check if target is occupied by a building
        occupants = self.world.get_grid_occupants(target_grid_x, target_grid_y)
        if any(isinstance(occupant, Building) for occupant in occupants):
            # Find nearest accessible position
            for dx, dy in [(0,1), (1,0), (0,-1), (-1,0), (1,1), (-1,1), (1,-1), (-1,-1)]:
                check_x = target_grid_x + dx
                check_y = target_grid_y + dy
                if (0 <= check_x < self.world.current_size and 
                    0 <= check_y < self.world.current_size):
                    check_occupants = self.world.get_grid_occupants(check_x, check_y)
                    if not any(isinstance(occupant, Building) for occupant in check_occupants):
                        target_grid_x, target_grid_y = check_x, check_y
                        break
            else:
                return False  # No accessible position found
        
        # Calculate path to target
        self.current_path = self.find_path(current_grid_x, current_grid_y, 
                                         target_grid_x, target_grid_y)
        if not self.current_path:
            return False
            
        self.target_position = target_pos
        self.last_target = target_pos
        self.path_index = 0
        return True

    def find_path(self, start_x, start_y, target_x, target_y):
        """Simple A* pathfinding"""
        if not (0 <= target_x < self.world.current_size and 
               0 <= target_y < self.world.current_size):
            return []
            
        # Manhattan distance heuristic
        def heuristic(x, y):
            return abs(target_x - x) + abs(target_y - y)
        
        # Initialize search with a more robust open set structure
        open_set = {(start_x, start_y)}  # Use set for O(1) operations
        open_set_f = {(start_x, start_y): heuristic(start_x, start_y)}  # Track f scores
        came_from = {}
        g_score = {(start_x, start_y): 0}
        
        while open_set:
            # Find node with minimum f_score
            current = min(open_set, key=lambda pos: open_set_f[pos])
            current_x, current_y = current
            
            if current_x == target_x and current_y == target_y:
                # Reconstruct path
                path = []
                while current in came_from:
                    path.append(current)
                    current = came_from[current]
                path.append((start_x, start_y))
                path.reverse()
                return path
                
            # Remove current from open set
            open_set.remove(current)
            open_set_f.pop(current)
            
            # Check neighbors
            for dx, dy in [(0,1), (1,0), (0,-1), (-1,0)]:
                next_x, next_y = current_x + dx, current_y + dy
                neighbor = (next_x, next_y)
                
                if not (0 <= next_x < self.world.current_size and 
                       0 <= next_y < self.world.current_size):
                    continue
                    
                # Check if neighbor is walkable
                occupants = self.world.get_grid_occupants(next_x, next_y)
                if any(isinstance(occupant, Building) for occupant in occupants):
                    continue
                
                tentative_g = g_score[current] + 1
                
                if neighbor not in g_score or tentative_g < g_score[neighbor]:
                    # Found better path to neighbor
                    came_from[neighbor] = current
                    g_score[neighbor] = tentative_g
                    f_score = tentative_g + heuristic(next_x, next_y)
                    open_set_f[neighbor] = f_score
                    open_set.add(neighbor)
        
        return []  # No path found
