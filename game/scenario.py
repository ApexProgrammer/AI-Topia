import pygame
import random
import textwrap  # new import

class Scenario:
    def __init__(self, prompt, options, id=None, difficulty=1):
        # options: list of tuples: (option_text, outcome_effect)
        # outcome_effect: dict with keys e.g. "score", "treasury", "next", "message", etc.
        self.prompt = prompt
        self.options = options
        self.id = id
        self.difficulty = difficulty  # 1-5 scale of difficulty/complexity

class ScenarioManager:
    def __init__(self, world):
        self.world = world
        self.active_scenario = None
        self.timer = 0
        self.trigger_interval = 5000  # ticks interval to trigger a scenario
        self.last_message = ""  # new: store last outcome message
        self.outcome_timer = 0             # new: timer for showing outcome
        self.outcome_duration = 100        # new: duration to display outcome
        self.scenario_history = []         # Track which scenarios have been shown
        self.current_difficulty = 1        # Start with basic scenarios
        
        # Define a pool of scenarios with multiple outcomes and branching
        # Basic (Level 1) Scenarios
        self.basic_scenarios = {
            "ethics_1": Scenario(
                prompt="Allocate funds: Welfare (ethical) vs. Industry (growth)?",
                options=[
                    ("Welfare", {"score": 50, "treasury": -200, "next": "ethics_2", "message": "People are grateful for the support."}),
                    ("Industry", {"score": 20, "treasury": 100, "message": "Industry booms, but social unrest simmers."})
                ],
                id="ethics_1",
                difficulty=1
            ),
            "ethics_2": Scenario(
                prompt="Following generous funding of welfare, should you invest in education or infrastructure?",
                options=[
                    ("Education", {"score": 40, "treasury": -150, "message": "The population becomes better skilled."}),
                    ("Infrastructure", {"score": 30, "treasury": -100, "message": "Roads and bridges improve colony mobility."})
                ],
                id="ethics_2",
                difficulty=1
            ),
            "emergency": Scenario(
                prompt="A sudden disaster strikes! Choose to allocate funds for emergency relief or to rebuild critical infrastructure.",
                options=[
                    ("Emergency Relief", {"score": 30, "treasury": -250, "message": "Lives are saved but finances are tight."}),
                    ("Rebuild", {"score": 20, "treasury": -150, "next": "rebuild_followup", "message": "Buildings are restored with a promise of future safety."})
                ],
                id="emergency",
                difficulty=1
            )
        }
        
        # Intermediate (Level 2-3) Scenarios
        self.intermediate_scenarios = {
            "rebuild_followup": Scenario(
                prompt="The rebuilt infrastructure attracts new industries. How should you balance the influx of businesses?",
                options=[
                    ("Tight Regulations", {"score": 35, "treasury": -50, "message": "Businesses follow fair practices."}),
                    ("Laissez-Faire", {"score": 25, "treasury": 100, "message": "The free market thrives, but risks inequality."})
                ],
                id="rebuild_followup",
                difficulty=2
            ),
            "research_investment": Scenario(
                prompt="Innovations surge! Invest in Research or expand Infrastructure?",
                options=[
                    ("Research", {"score": 40, "treasury": -200, "message": "Innovations boost productivity."}),
                    ("Infrastructure", {"score": 20, "treasury": -100, "message": "Improved infrastructure aids commerce."})
                ],
                id="research_investment",
                difficulty=2
            ),
            "environmental_crisis": Scenario(
                prompt="An environmental crisis emerges. Prioritize Rescue Services or Preventative Measures?",
                options=[
                    ("Rescue Services", {"score": 30, "treasury": -250, "message": "Critical lives are saved at high cost."}),
                    ("Preventative Measures", {"score": 25, "treasury": -150, "message": "Future crises are mitigated."})
                ],
                id="environmental_crisis",
                difficulty=2
            ),
            "resource_shortage": Scenario(
                prompt="A key resource is running low. Implement rationing or seek costly alternative sources?",
                options=[
                    ("Rationing", {"score": 15, "resources": {"food": -50}, "happiness": -10, 
                                 "message": "Rationing creates fairness but lowers morale."}),
                    ("Alternative Sources", {"score": 10, "treasury": -300, 
                                          "message": "Colony finances strain but supplies are maintained."})
                ],
                id="resource_shortage",
                difficulty=3
            ),
            "immigration_policy": Scenario(
                prompt="Refugees are seeking asylum in your colony. What is your immigration policy?",
                options=[
                    ("Open Borders", {"score": 35, "population_increase": 10, "treasury": -200, 
                                    "message": "New arrivals bring skills but strain resources initially."}),
                    ("Selective Immigration", {"score": 25, "population_increase": 5, "treasury": -50, 
                                           "message": "Only skilled workers are accepted, limiting cultural diversity."}),
                    ("Closed Borders", {"score": 5, "message": "The colony remains isolated, maintaining stability but missing opportunities."})
                ],
                id="immigration_policy",
                difficulty=3
            )
        }
        
        # Advanced (Level 4-5) Scenarios - more complex ethical dilemmas
        self.advanced_scenarios = {
            "ethical_crisis": Scenario(
                prompt="A critical position worker is making demands for special treatment threatening to leave. " +
                      "This could severely impact production. How do you respond?",
                options=[
                    ("Meet Demands", {"score": 10, "treasury": -500, "happiness": 5, 
                                    "message": "Production continues but other workers feel inequality."}),
                    ("Negotiate Compromise", {"score": 25, "treasury": -250, 
                                           "message": "A fair balance is struck, though not ideal for either side."}),
                    ("Refuse Demands", {"score": 5, "critical_worker_loss": True, "happiness": -10, 
                                      "message": "The worker leaves, disrupting operations but maintaining equity."})
                ],
                id="ethical_crisis",
                difficulty=4
            ),
            "education_reform": Scenario(
                prompt="Your education system needs reform. Focus on technical skills, liberal arts, or mandatory education with limited freedoms?",
                options=[
                    ("Technical Education", {"score": 20, "skill_bonus": {"mining": 0.5, "farming": 0.5, "crafting": 0.5}, 
                                         "message": "Production efficiency increases, but creative thinking stagnates."}),
                    ("Liberal Arts", {"score": 30, "skill_bonus": {"leadership": 0.5, "education": 0.5}, 
                                    "message": "Innovation flourishes but immediate production needs struggle."}),
                    ("Mandatory Curriculum", {"score": 15, "education_level": 1, "happiness": -5, 
                                           "message": "All citizens become educated, but at the cost of personal freedom."})
                ],
                id="education_reform",
                difficulty=4
            ),
            "healthcare_crisis": Scenario(
                prompt="A serious illness is spreading. Limited medical supplies mean tough choices: Who receives treatment first?",
                options=[
                    ("Treat Critical Workers", {"score": 5, "happiness": -20, 
                                             "message": "Production continues but the moral cost is high."}),
                    ("Treat Most Vulnerable", {"score": 35, "treasury": -400, "worker_productivity": -0.2, 
                                            "message": "Humanitarian actions boost morale but reduce productivity temporarily."}),
                    ("Equal Distribution", {"score": 20, "treasury": -300, "happiness": -5, 
                                         "message": "Fair approach leaves everyone partially helped but no one fully treated."})
                ],
                id="healthcare_crisis",
                difficulty=5
            ),
            "colony_expansion_dilemma": Scenario(
                prompt="Expanding the colony would displace native wildlife. Technological solutions exist but are expensive. How do you proceed?",
                options=[
                    ("Protect Environment", {"score": 40, "treasury": -600, "expansion_delay": 100, 
                                          "message": "The ecosystem is preserved at significant financial cost."}),
                    ("Balanced Approach", {"score": 25, "treasury": -300, "expansion_delay": 50, 
                                        "message": "Some wildlife is protected while development continues carefully."}),
                    ("Prioritize Growth", {"score": 5, "expansion_bonus": 2, "environmental_damage": True, 
                                        "message": "Rapid expansion is achieved, with unknown long-term consequences."})
                ],
                id="colony_expansion_dilemma",
                difficulty=5
            )
        }
        
        # Combine all scenarios into the main pool
        self.scenario_pool = {
            **self.basic_scenarios,
            **self.intermediate_scenarios,
            **self.advanced_scenarios
        }

    def update(self):
        self.timer += 1
        
        # Update difficulty based on colony growth
        self.update_difficulty()
        
        # Decrement outcome timer if active and clear outcome when expired
        if self.outcome_timer > 0:
            self.outcome_timer -= 1
            if self.outcome_timer == 0:
                self.last_message = ""
                
        if not self.active_scenario and self.timer > self.trigger_interval:
            self.trigger_scenario()
            self.timer = 0

    def update_difficulty(self):
        """Update scenario difficulty based on colony size and development"""
        # Get colony metrics for difficulty scaling
        population = len(self.world.colonists)
        building_count = len(self.world.buildings)
        total_resources = sum(self.world.colony_inventory.values())
        
        # Scale difficulty based on colony growth
        if population >= 100 or building_count >= 30 or total_resources >= 5000:
            # Large colony - all difficulty levels
            self.current_difficulty = 5
        elif population >= 50 or building_count >= 20 or total_resources >= 3000:
            # Medium-large colony - up to difficulty 4
            self.current_difficulty = 4
        elif population >= 30 or building_count >= 15 or total_resources >= 2000:
            # Medium colony - up to difficulty 3
            self.current_difficulty = 3
        elif population >= 15 or building_count >= 10 or total_resources >= 1000:
            # Small-medium colony - up to difficulty 2
            self.current_difficulty = 2
        else:
            # Small colony - basic scenarios only
            self.current_difficulty = 1
            
        # Adjust trigger interval based on colony size - larger colonies get scenarios more frequently
        base_interval = 5000
        population_factor = max(0.5, min(1.0, 20 / max(1, population)))
        self.trigger_interval = int(base_interval * population_factor)

    def trigger_scenario(self):
        """Choose a scenario based on current colony difficulty level"""
        # Filter scenarios by appropriate difficulty
        eligible_scenarios = [s for s in self.scenario_pool.values() 
                            if s.difficulty <= self.current_difficulty]
        
        # Remove recently shown scenarios to avoid repetition
        if self.scenario_history:
            recent_ids = [s.id for s in self.scenario_history[-3:]]
            eligible_scenarios = [s for s in eligible_scenarios if s.id not in recent_ids]
        
        # If no eligible scenarios, reset history and try again
        if not eligible_scenarios:
            self.scenario_history = []
            eligible_scenarios = [s for s in self.scenario_pool.values() 
                                if s.difficulty <= self.current_difficulty]
        
        # Weight scenarios so harder ones appear less frequently
        weighted_scenarios = []
        for scenario in eligible_scenarios:
            # Higher difficulty = fewer entries in the weighted list
            weight = max(1, 6 - scenario.difficulty)
            weighted_scenarios.extend([scenario] * weight)
        
        # Choose a random scenario from weighted pool
        self.active_scenario = random.choice(weighted_scenarios)
        self.scenario_history.append(self.active_scenario)
        self.last_message = ""  # reset last message on new scenario

    def choose_option(self, index):
        if self.active_scenario and 0 <= index < len(self.active_scenario.options):
            option, outcome = self.active_scenario.options[index]
            # Apply outcome effects
            self.world.score += outcome.get("score", 0)
            self.world.treasury += outcome.get("treasury", 0)
            
            # Apply resource effects if specified
            if "resources" in outcome:
                for resource, amount in outcome["resources"].items():
                    if resource in self.world.colony_inventory:
                        self.world.colony_inventory[resource] = max(0, self.world.colony_inventory[resource] + amount)
            
            # Apply happiness effects if specified
            if "happiness" in outcome:
                for colonist in self.world.colonists:
                    colonist.happiness = max(0, min(100, colonist.happiness + outcome["happiness"]))
            
            # Handle critical worker loss if specified
            if outcome.get("critical_worker_loss", False):
                self.handle_critical_worker_loss()
                
            # Apply skill bonuses if specified
            if "skill_bonus" in outcome:
                self.apply_skill_bonuses(outcome["skill_bonus"])
                
            # Apply education level boost if specified
            if "education_level" in outcome:
                self.improve_education(outcome["education_level"])
                
            # Apply worker productivity change if specified
            if "worker_productivity" in outcome:
                self.adjust_worker_productivity(outcome["worker_productivity"])
                
            # Handle population increase
            if "population_increase" in outcome:
                self.increase_population(outcome["population_increase"])
            
            self.last_message = outcome.get("message", "")  # store outcome message
            self.outcome_timer = self.outcome_duration  # set timer to display outcome
            
            # Branch to a follow-up scenario if provided and exists in the pool
            next_id = outcome.get("next")
            if next_id and next_id in self.scenario_pool:
                self.active_scenario = self.scenario_pool[next_id]
            else:
                self.active_scenario = None

    def handle_critical_worker_loss(self):
        """Handle the loss of a critical position worker"""
        # Find workers in critical positions
        critical_workers = [c for c in self.world.colonists 
                         if hasattr(c, 'is_critical_position') and c.is_critical_position]
        
        if critical_workers:
            # Remove one worker from their job
            worker = random.choice(critical_workers)
            worker.is_critical_position = False
            if worker.job:
                worker.job.employee = None
                worker.job = None
                worker.happiness -= 20  # Unhappy about losing job
                
            # Log the event
            if hasattr(self.world, 'debug_log'):
                self.world.debug_log("A critical position worker has left their job!")

    def apply_skill_bonuses(self, skill_bonuses):
        """Apply skill bonuses to all colonists"""
        for colonist in self.world.colonists:
            for skill, bonus in skill_bonuses.items():
                if hasattr(colonist, 'skills') and skill in colonist.skills:
                    colonist.skills[skill] = min(100, colonist.skills[skill] + bonus)

    def improve_education(self, level_increase):
        """Improve education level of colonists"""
        for colonist in self.world.colonists:
            if hasattr(colonist, 'education_level'):
                colonist.education_level = min(5, colonist.education_level + level_increase)

    def adjust_worker_productivity(self, modifier):
        """Apply temporary productivity modifier to workers"""
        for building in self.world.buildings:
            if hasattr(building, 'efficiency'):
                building.efficiency = max(0.1, building.efficiency + modifier)

    def increase_population(self, count):
        """Add new colonists to the colony"""
        for _ in range(count):
            # Find a valid position for the new colonist
            x, y = self.find_valid_position()
            if x is not None and y is not None:
                new_colonist = self.world.add_colonist(x, y)
                if new_colonist and hasattr(self.world, 'debug_log'):
                    self.world.debug_log(f"New colonist joined from scenario!")

    def find_valid_position(self):
        """Find a valid position for a new colonist"""
        # Try to place near existing buildings for realism
        if self.world.buildings:
            building = random.choice(self.world.buildings)
            grid_x, grid_y = self.world.get_grid_position(building.x, building.y)
            
            # Try positions around the building
            for dx, dy in [(1, 0), (0, 1), (-1, 0), (0, -1), (1, 1), (-1, 1), (1, -1), (-1, -1)]:
                check_x = grid_x + dx
                check_y = grid_y + dy
                
                if (0 <= check_x < self.world.current_size and 
                    0 <= check_y < self.world.current_size):
                    occupants = self.world.get_grid_occupants(check_x, check_y)
                    if not occupants:  # Empty space
                        return self.world.get_pixel_position(check_x, check_y)
        
        # Fallback: try random positions
        for _ in range(10):  # Try up to 10 times
            grid_x = random.randint(0, self.world.current_size - 1)
            grid_y = random.randint(0, self.world.current_size - 1)
            occupants = self.world.get_grid_occupants(grid_x, grid_y)
            if not occupants:
                return self.world.get_pixel_position(grid_x, grid_y)
                
        return None, None  # Couldn't find valid position

    def render(self, screen, font):
        if self.active_scenario or self.last_message:
            # Increase overlay height to display outcome feedback
            overlay = pygame.Surface((400, 250))
            overlay.set_alpha(220)
            overlay.fill((30, 30, 30))
            screen_rect = screen.get_rect()
            overlay_rect = overlay.get_rect(center=screen_rect.center)
            screen.blit(overlay, overlay_rect.topleft)
            
            # Display difficulty level for active scenario
            if self.active_scenario:
                difficulty_text = f"Difficulty: {self.active_scenario.difficulty}/5"
                diff_surface = font.render(difficulty_text, True, (200, 200, 100))
                screen.blit(diff_surface, (overlay_rect.right - 100, overlay_rect.top + 10))
            
            # Wrap prompt text and outcome message so it fits
            max_width = 380  # overlay width minus padding
            prompt_lines = textwrap.wrap(self.active_scenario.prompt if self.active_scenario else "", width=40)
            y_offset = overlay_rect.y + 20
            for line in prompt_lines:
                prompt_text = font.render(line, True, (255, 255, 255))
                screen.blit(prompt_text, (overlay_rect.x + 10, y_offset))
                y_offset += 25

            # Display options if a scenario is active
            if self.active_scenario:
                y_offset += 10
                for idx, option_tuple in enumerate(self.active_scenario.options):
                    option_text = option_tuple[0]  # Extract just the option text
                    option_line = f"{idx+1}: {option_text}"
                    option_surface = font.render(option_line, True, (200, 200, 200))
                    screen.blit(option_surface, (overlay_rect.x + 10, y_offset))
                    y_offset += 25

            # Display last outcome message if available
            if self.last_message:
                y_offset += 10
                outcome_header = font.render("Outcome:", True, (255, 215, 0))
                screen.blit(outcome_header, (overlay_rect.x + 10, y_offset))
                y_offset += 25
                outcome_lines = textwrap.wrap(self.last_message, width=40)
                for line in outcome_lines:
                    outcome_text = font.render(line, True, (255, 255, 255))
                    screen.blit(outcome_text, (overlay_rect.x + 10, y_offset))
                    y_offset += 25
