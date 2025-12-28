import pygame
import random
from settings import *

class DialogueBox:
    def __init__(self):
        self.font = pygame.font.SysFont("Arial", 18, bold=True)
        self.active = False
        self.timer = 0
        self.display_text = ""
        
        # UI Layout Constants
        self.width = 350
        self.height = 80
        self.portrait_size = 64
        self.padding = 15
        
        # Position: Slide in from bottom-left
        self.target_y = HEIGHT - self.height - 20
        self.hidden_y = HEIGHT + 100
        self.current_y = self.hidden_y
        
        # Personality: Huey's Dialogue Pools
        self.quips_frustration = [
            "This scrap-bucket is shaking apart!",
            "Engine's screaming louder than I am!",
            "Who built this jet? A toddler?!",
            "Too heavy... way too heavy!",
            "Stop stalling on me, you junk heap!"
        ]
        self.quips_enemies = [
            "Where do these purple creeps come from?",
            "Get out of my sky!",
            "Eat recycled lead, monster!",
            "That was a close one... too close!",
            "I'm gonna turn you into spare parts!"
        ]

        # Load Portrait (Reuse Huey's open-eye frame)
        try:
            self.portrait = pygame.image.load("assets/sprites/huey_plane1.png").convert_alpha()
            self.portrait = pygame.transform.scale(self.portrait, (self.portrait_size, self.portrait_size))
        except:
            self.portrait = pygame.Surface((self.portrait_size, self.portrait_size))
            self.portrait.fill((100, 100, 100))

    def trigger_random_quip(self, category="frustration"):
        """Call this to make Huey speak."""
        if not self.active:
            pool = self.quips_frustration if category == "frustration" else self.quips_enemies
            self.display_text = random.choice(pool)
            self.active = True
            self.timer = 4.0  # Dialogue lasts 4 seconds

    def update(self, dt, player):
        # 1. Randomly trigger dialogues if nothing is active
        if not self.active:
            # Very small chance per frame to speak
            if random.random() < 0.002: 
                cat = "frustration" if player.heat > (HEAT_MAX * 0.7) or player.weight > 500 else "enemies"
                self.trigger_random_quip(cat)

        # 2. Handle Timers and Sliding Animation
        if self.active:
            self.timer -= dt
            # Slide Up
            self.current_y += (self.target_y - self.current_y) * 0.1
            if self.timer <= 0:
                self.active = False
        else:
            # Slide Down
            self.current_y += (self.hidden_y - self.current_y) * 0.1

    def draw(self, screen):
        if self.current_y >= HEIGHT: return

        # Draw main container (Semi-transparent dark glass)
        rect = pygame.Rect(20, self.current_y, self.width, self.height)
        
        # Background
        bg_surf = pygame.Surface((self.width, self.height), pygame.SRCALPHA)
        pygame.draw.rect(bg_surf, (20, 20, 20, 220), (0, 0, self.width, self.height), border_radius=12)
        pygame.draw.rect(bg_surf, WHITE, (0, 0, self.width, self.height), 2, border_radius=12)
        screen.blit(bg_surf, rect)

        # Draw Portrait
        screen.blit(self.portrait, (rect.x + self.padding, rect.y + (self.height - self.portrait_size)//2))

        # Draw Text (Wrapped roughly)
        text_x = rect.x + self.portrait_size + (self.padding * 2)
        words = self.display_text.split(' ')
        lines = []
        while words:
            line = ''
            while words and self.font.size(line + words[0])[0] < self.width - text_x - 10:
                line += words.pop(0) + ' '
            lines.append(line)

        for i, line in enumerate(lines):
            txt_surf = self.font.render(line, True, WHITE)
            screen.blit(txt_surf, (text_x, rect.y + self.padding + (i * 22)))