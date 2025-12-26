import pygame
import sys
from settings import *
from entities.player import Player
from world.parallax import ParallaxBackground  # NEW: Import the background class

class Game:
    def __init__(self):
        pygame.init()
        self.screen = pygame.display.set_mode((WIDTH, HEIGHT))
        pygame.display.set_caption("Zethia: Scrap-Jet Skyways")
        self.clock = pygame.time.Clock()
        self.running = True

        # Game Objects
        self.player = Player()
        self.parallax = ParallaxBackground()  # NEW: Initialize the background
        
        # We'll use PLAYER_SPEED from settings for the scroll speed
        self.scroll_speed = 200 

    def run(self):
        while self.running:
            dt = self.clock.tick(FPS) / 1000.0
            self.events()
            self.update(dt)
            self.draw()

    def events(self):
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                self.running = False
            
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE:
                    self.running = False

    def update(self, dt):
        keys = pygame.key.get_pressed()
        
        # 1. Update Background Scrolling
        self.parallax.update(0, dt) # NEW

        # 2. Update Player
        self.player.handle_input(keys, dt)
        self.player.update(dt)

    def draw(self):
        # 1. Fill base Sky color (Layer 0)
        self.screen.fill(SKY_BLUE)

        # 2. Draw Parallax Layers (Clouds, Trees, Ground)
        self.parallax.draw(self.screen) # NEW

        # 3. Draw the player on top of the world
        self.screen.blit(self.player.image, self.player.rect)
        
        # 4. Draw HUD elements
        self.player.draw_hud_elements(self.screen)

        pygame.display.flip()

if __name__ == "__main__":
    game = Game()
    game.run()
    pygame.quit()
    sys.exit()