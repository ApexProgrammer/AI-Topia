import pygame
import random
import textwrap  # new import

class Scenario:
    def __init__(self, prompt, options, id=None):
        # options: list of tuples: (option_text, outcome_effect)
        # outcome_effect: dict with keys e.g. "score", "treasury", "next", "message", etc.
        self.prompt = prompt
        self.options = options
        self.id = id

class ScenarioManager:
    def __init__(self, world):
        self.world = world
        self.active_scenario = None
        self.timer = 0
        self.trigger_interval = 5000  # ticks interval to trigger a scenario
        self.last_message = ""  # new: store last outcome message
        self.outcome_timer = 0             # new: timer for showing outcome
        self.outcome_duration = 100        # new: duration to display outcome
        # Define a pool of scenarios with multiple outcomes and branching
        self.scenario_pool = {
            "ethics_1": Scenario(
                prompt="Allocate funds: Welfare (ethical) vs. Industry (growth)?",
                options=[
                    ("Welfare", {"score": 50, "treasury": -200, "next": "ethics_2", "message": "People are grateful for the support."}),
                    ("Industry", {"score": 20, "treasury": 100, "message": "Industry booms, but social unrest simmers."})
                ],
                id="ethics_1"
            ),
            "ethics_2": Scenario(
                prompt="Following generous funding of welfare, should you invest in education or infrastructure?",
                options=[
                    ("Education", {"score": 40, "treasury": -150, "message": "The population becomes better skilled."}),
                    ("Infrastructure", {"score": 30, "treasury": -100, "message": "Roads and bridges improve colony mobility."})
                ],
                id="ethics_2"
            ),
            "emergency": Scenario(
                prompt="A sudden disaster strikes! Choose to allocate funds for emergency relief or to rebuild critical infrastructure.",
                options=[
                    ("Emergency Relief", {"score": 30, "treasury": -250, "message": "Lives are saved but finances are tight."}),
                    ("Rebuild", {"score": 20, "treasury": -150, "next": "rebuild_followup", "message": "Buildings are restored with a promise of future safety."})
                ],
                id="emergency"
            ),
            "rebuild_followup": Scenario(
                prompt="The rebuilt infrastructure attracts new industries. How should you balance the influx of businesses?",
                options=[
                    ("Tight Regulations", {"score": 35, "treasury": -50, "message": "Businesses follow fair practices."}),
                    ("Laissez-Faire", {"score": 25, "treasury": 100, "message": "The free market thrives, but risks inequality."})
                ],
                id="rebuild_followup"
            ),
            # New scenarios
            "research_investment": Scenario(
                prompt="Innovations surge! Invest in Research or expand Infrastructure?",
                options=[
                    ("Research", {"score": 40, "treasury": -200, "message": "Innovations boost productivity."}),
                    ("Infrastructure", {"score": 20, "treasury": -100, "message": "Improved infrastructure aids commerce."})
                ],
                id="research_investment"
            ),
            "environmental_crisis": Scenario(
                prompt="An environmental crisis emerges. Prioritize Rescue Services or Preventative Measures?",
                options=[
                    ("Rescue Services", {"score": 30, "treasury": -250, "message": "Critical lives are saved at high cost."}),
                    ("Preventative Measures", {"score": 25, "treasury": -150, "message": "Future crises are mitigated."})
                ],
                id="environmental_crisis"
            )
        }

    def update(self):
        self.timer += 1
        # Decrement outcome timer if active and clear outcome when expired
        if self.outcome_timer > 0:
            self.outcome_timer -= 1
            if self.outcome_timer == 0:
                self.last_message = ""
        if not self.active_scenario and self.timer > self.trigger_interval:
            self.trigger_scenario()
            self.timer = 0

    def trigger_scenario(self):
        # Choose a random scenario from the pool
        self.active_scenario = random.choice(list(self.scenario_pool.values()))
        self.last_message = ""  # reset last message on new scenario

    def choose_option(self, index):
        if self.active_scenario and 0 <= index < len(self.active_scenario.options):
            _, outcome = self.active_scenario.options[index]
            # Apply outcome effects
            self.world.score += outcome.get("score", 0)
            self.world.treasury += outcome.get("treasury", 0)
            self.last_message = outcome.get("message", "")  # new: store outcome message
            self.outcome_timer = self.outcome_duration  # new: set timer to display outcome
            # Optionally, output outcome message (could be handled in UI/console)
            # Branch to a follow-up scenario if provided and exists in the pool
            next_id = outcome.get("next")
            if next_id and next_id in self.scenario_pool:
                self.active_scenario = self.scenario_pool[next_id]
            else:
                self.active_scenario = None

    def render(self, screen, font):
        if self.active_scenario or self.last_message:
            # Increase overlay height to display outcome feedback
            overlay = pygame.Surface((400, 250))
            overlay.set_alpha(220)
            overlay.fill((30, 30, 30))
            screen_rect = screen.get_rect()
            overlay_rect = overlay.get_rect(center=screen_rect.center)
            screen.blit(overlay, overlay_rect.topleft)
            
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
                for idx, option in enumerate(self.active_scenario.options):
                    option_line = f"{idx+1}: {option[0]}"
                    option_text = font.render(option_line, True, (200, 200, 200))
                    screen.blit(option_text, (overlay_rect.x + 10, y_offset))
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
