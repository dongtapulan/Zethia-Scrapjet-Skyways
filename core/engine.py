import pygame
import sys
from settings import *
from core.input_handler import InputHandler

class Engine:
    def __init__(self):
        # --- FIX: AUDIO LATENCY & QUALITY ---
        # 44100Hz frequency, 16-bit signed sound, 2 channels (stereo), 512 buffer size
        # A smaller buffer (512 or 256) removes the delay in sound effects
        pygame.mixer.pre_init(44100, -16, 2, 512) 
        
        pygame.init()
        
        # Ensure we have enough mixing channels for machine gun + explosions + music
        pygame.mixer.set_num_channels(32)
        
        self.screen = pygame.display.set_mode((WIDTH, HEIGHT))
        pygame.display.set_caption("Zethia: Scrap-Jet Skyways")
        self.clock = pygame.time.Clock()
        self.running = True
        
        # Core Systems
        self.input_handler = InputHandler()
        
        self.game_state = None 

    def run(self, game_instance):
        self.game_state = game_instance
        
        while self.running:
            # 1. Delta Time (seconds since last frame)
            dt = self.clock.tick(FPS) / 1000.0
            
            # 2. Event Dispatcher
            self.handle_events()
            
            # 3. Update Logic
            if self.game_state:
                flight_input = self.input_handler.get_flight_input()
                combat_input = self.input_handler.get_combat_input()
                self.game_state.update(dt, flight_input, combat_input)
            
            # 4. Rendering
            self.screen.fill(SKY_BLUE) 
            if self.game_state:
                self.game_state.draw(self.screen)
            
            pygame.display.flip()

    def handle_events(self):
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                self.running = False
                pygame.quit()
                sys.exit()
            
            if self.game_state:
                self.game_state.handle_event(event)