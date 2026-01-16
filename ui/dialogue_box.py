import pygame
import random
from settings import *

class DialogueBox:
    def __init__(self):
        # Using a monospaced font or bold Arial for that 'comms' feel
        self.font = pygame.font.SysFont("Arial", 18, bold=True)
        self.active = False
        self.timer = 0
        self.display_text = ""
        self.current_char_index = 0
        self.typewriter_speed = 0.03 
        self.typewriter_timer = 0
        
        # UI Layout Constants
        self.width = 400
        self.height = 90
        self.portrait_size = 64
        self.padding = 15
        
        # Position Logic
        self.target_y = HEIGHT - self.height - 20
        self.hidden_y = HEIGHT + 120
        self.current_y = self.hidden_y
        
        # --- ASTRAL & FRUSTRATION POOLS ---
        
        self.quips_frustration = [
            "This scrap-bucket is shaking apart!",
            "Engine's screaming louder than I am!",
            "Who built this jet? A toddler?!",
            "Too heavy... way too heavy!",
            "Stop stalling on me, you junk heap!"
        ]
        
        self.quips_enemies = [
            "Get out of my sky, you purple creeps!",
            "Eat recycled lead, monster!",
            "I'm gonna turn you into spare parts!",
            "That was a close one... too close!"
        ]

        # The Lore-Heavy Astral Pools
        self.quips_companions = {
            "RED": [ # The only one he clearly sees
                "Red, watch my six! Don't just hover there!",
                "You seeing this, Red? Tell me I'm not crazy.",
                "Glad you're real... I think.",
                "Keep that shield up! I'm taking heat!"
            ],
            "TINE": [ # The Electric Astral Projection
                "Is it just me, or is the air... static-y?",
                "Whoa! That lightning didn't come from the clouds...",
                "My instruments are glitching. Is someone behind me?",
                "I hear a hum in my headset... like a whisper."
            ],
            "CICI": [ # The Oracle/Gold Guardian
                "That gold glow... it feels like a warm memory.",
                "Did my hull just fix itself? That's impossible.",
                "I feel lighter... like someone's lifting the wings.",
                "I can smell ozone and... flowers? In a wasteland?"
            ],
            "SKYFALL": [ # Rare teaser for the sequel!
                "CRITICAL ERROR: Protocol 'Skyfall' detected...",
                "Signal lost... Searching for Guardian Sync...",
                "The sky is falling... but I'm still flying.",
                "Wei... can you hear us? ---[SIGNAL LOST]---"
            ]
        }

        # Load Portrait
        try:
            self.portrait = pygame.image.load("assets/sprites/huey_plane1.png").convert_alpha()
            self.portrait = pygame.transform.scale(self.portrait, (self.portrait_size, self.portrait_size))
        except:
            self.portrait = pygame.Surface((self.portrait_size, self.portrait_size))
            self.portrait.fill((100, 100, 100))

    def trigger_random_quip(self, category="frustration"):
        if not self.active:
            # Chance to trigger a Skyfall teaser instead of a regular quip
            if random.random() < 0.05:
                category = "SKYFALL"

            if category in self.quips_companions:
                pool = self.quips_companions[category]
            elif category == "enemies":
                pool = self.quips_enemies
            else:
                pool = self.quips_frustration
                
            self.display_text = random.choice(pool)
            self.active = True
            self.timer = 5.0
            self.current_char_index = 0
            self.typewriter_timer = 0

    def update(self, dt, player):
        # 1. Random triggers based on context
        if not self.active:
            if random.random() < 0.003: # Check for a quip roughly every few seconds
                # Priority: Companions first if they are "active" in lore/items
                if player.laser_fuel > 10:
                    self.trigger_random_quip("RED")
                elif player.lightning_charges > 0:
                    self.trigger_random_quip("TINE")
                elif player.scrap > 100: # Cici likes high scrap/gold
                    self.trigger_random_quip("CICI")
                elif player.heat > (HEAT_MAX * 0.7) or player.weight > 400:
                    self.trigger_random_quip("frustration")
                else:
                    self.trigger_random_quip("enemies")

        # 2. Typewriter and Sliding logic
        if self.active:
            self.timer -= dt
            if self.current_char_index < len(self.display_text):
                self.typewriter_timer += dt
                if self.typewriter_timer >= self.typewriter_speed:
                    self.current_char_index += 1
                    self.typewriter_timer = 0
            
            # Slide Up
            self.current_y += (self.target_y - self.current_y) * 0.1
            if self.timer <= 0:
                self.active = False
        else:
            # Slide Down
            self.current_y += (self.hidden_y - self.current_y) * 0.1

    def draw(self, screen):
        if self.current_y >= HEIGHT: return

        # Draw main container (Glass UI)
        rect = pygame.Rect(20, self.current_y, self.width, self.height)
        
        # Background: Dark blue tint for 'spectral/tech' feel
        bg_surf = pygame.Surface((self.width, self.height), pygame.SRCALPHA)
        pygame.draw.rect(bg_surf, (10, 20, 40, 240), (0, 0, self.width, self.height), border_radius=15)
        
        # Border: Glows gold if a Skyfall quip, cyan otherwise
        border_color = (255, 215, 0) if "Skyfall" in self.display_text else (0, 200, 255)
        pygame.draw.rect(bg_surf, border_color, (0, 0, self.width, self.height), 2, border_radius=15)
        screen.blit(bg_surf, rect)

        # Draw Portrait
        screen.blit(self.portrait, (rect.x + self.padding, rect.y + (self.height - self.portrait_size)//2))

        # Text Layout
        text_x = rect.x + self.portrait_size + (self.padding * 2)
        visible_text = self.display_text[:self.current_char_index]
        
        words = visible_text.split(' ')
        lines = []
        current_line = ""
        
        for word in words:
            test_line = current_line + word + " "
            if self.font.size(test_line)[0] < (self.width - (self.portrait_size + self.padding * 3)):
                current_line = test_line
            else:
                lines.append(current_line)
                current_line = word + " "
        lines.append(current_line)

        for i, line in enumerate(lines):
            if i > 2: break 
            # Spectral text color for companions
            color = (200, 255, 200) if any(x in self.display_text for x in ["whisper", "ghost", "memory", "Skyfall"]) else WHITE
            txt_surf = self.font.render(line, True, color)
            screen.blit(txt_surf, (text_x, rect.y + self.padding + (i * 22)))