import pygame
import sys
from settings import*
from core.input_handler import InputHandler

class Engine:
    def __init__(self):
        pygame.init()
        self.screen = pygame.display.set_mode((WIDTH, HEIGHT))
        pygame.display.set_caption("Zethia: Scrap-Jet Skyways")
        self.clock = pygame.time.Clock()
        self.running = True
        
        # Core Systems
        self.input_handler = InputHandler()
        
        # The 'Game' instance will be attached here later 
        # to separate engine logic from game content
        self.game_state = None 

    def run(self, game_instance):
        """
        The Master Loop.
        Pass in your Main Game class here.
        """
        self.game_state = game_instance
        
        while self.running:
            # 1. Delta Time (seconds since last frame)
            dt = self.clock.tick(FPS) / 1000.0
            
            # 2. Event Dispatcher
            self.handle_events()
            
            # 3. Update Logic
            if self.game_state:
                # Pass inputs down to the game state
                flight_input = self.input_handler.get_flight_input()
                combat_input = self.input_handler.get_combat_input()
                
                self.game_state.update(dt, flight_input, combat_input)
            
            # 4. Rendering
            self.screen.fill(SKY_BLUE) # Clear screen
            if self.game_state:
                self.game_state.draw(self.screen)
            
            pygame.display.flip()

    def handle_events(self):
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                self.running = False
                pygame.quit()
                sys.exit()
            
            # Handle Menu-specific events or state swaps here
            if self.game_state:
                self.game_state.handle_event(event)