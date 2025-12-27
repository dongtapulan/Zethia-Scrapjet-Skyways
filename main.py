import pygame
import sys
from settings import *
from entities.player import Player
from world.parallax import ParallaxBackground
from entities.scrap import ScrapManager
from ui.menus import MainMenu

class Game:
    def __init__(self):
        pygame.init()
        self.screen = pygame.display.set_mode((WIDTH, HEIGHT))
        pygame.display.set_caption("Zethia: Scrap-Jet Skyways")
        self.clock = pygame.time.Clock()
        self.running = True
        
        # State Machine
        self.state = "MENU"
        self.menu = MainMenu(self.screen)
        
        # Objects
        self.player = None
        self.parallax = None
        self.scrap_manager = None
        self.score = 0

    def reset_game(self):
        """Initializes Arcade Mode."""
        self.player = Player()
        self.parallax = ParallaxBackground()
        self.scrap_manager = ScrapManager()
        self.score = 0
        self.state = "PLAYING"
        # Fade out menu music if you have separate game music
        # pygame.mixer.music.fadeout(1000)

    def run(self):
        while self.running:
            dt = self.clock.tick(FPS) / 1000.0
            
            if self.state == "MENU":
                self.handle_menu_events()
                self.menu.update(dt)
                self.menu.draw()
                pygame.display.flip()
            elif self.state == "PLAYING":
                self.events()
                self.update(dt)
                self.draw()

    def handle_menu_events(self):
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                self.running = False
            
            selection = self.menu.handle_input(event)
            if selection == "Arcade Mode":
                self.reset_game()
            elif selection == "Exit":
                self.running = False

    def events(self):
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                self.running = False
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE:
                    # Return to menu and skip splash
                    self.state = "MENU"
                    self.menu.menu_state = "READY"
                    self.menu.button_alphas = [255] * len(self.menu.options)

    def update(self, dt):
        keys = pygame.key.get_pressed()
        self.parallax.update(0, dt)
        self.scrap_manager.update(dt, self.player.rect.center)
        self.player.handle_input(keys, dt)
        self.player.update(dt)

        # Collision logic
        hits = pygame.sprite.spritecollide(self.player, self.scrap_manager.scrap_group, True)
        for scrap in hits:
            self.score += scrap.value
            self.player.weight += scrap.weight_value
            self.player.weight = min(self.player.weight, self.player.max_weight)

    def draw(self):
        self.screen.fill(SKY_BLUE)
        self.parallax.draw(self.screen)
        self.scrap_manager.draw(self.screen)
        self.player.draw(self.screen)
        # Score Overlay (Optional simple text before HUD)
        pygame.display.flip()

if __name__ == "__main__":
    game = Game()
    game.run()
    pygame.quit()
    sys.exit()