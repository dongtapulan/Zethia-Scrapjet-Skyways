import pygame
import random
import math
from settings import WIDTH, HEIGHT, WHITE

class IntroCutscene:
    def __init__(self, screen):
        self.screen = screen
        self.font = pygame.font.SysFont("Georgia", 28, italic=True)
        self.active = True
        
        # New Lore-Heavy Script
        self.script = [
            "The horizon used to be a promise. Now, it's a warning.",
            "The blue is being bled out of the world, replaced by a violet rot.",
            "I can feel the ley lines screaming... the Withering is no longer silent.",
            "I am not the first to fly into this storm, and I pray I am not the last.",
            "A crimson streak in the distance... a flash of indigo lightning...",
            "They are out there, fighting for a world that has forgotten them.",
            "I can't let them face this shadow alone. Not anymore.",
            "My father built these wings for the stars. I'll use them for the survivors.",
            "Ignition. The sky belongs to us."
        ]
        
        self.current_line = 0
        self.displayed_text = ""
        self.char_index = 0
        self.type_speed = 0.05  
        self.type_timer = 0
        
        # Color Transition Logic
        self.color_progress = 0.0
        self.start_color = pygame.Color(135, 206, 235)  # SkyBlue
        self.end_color = pygame.Color(25, 10, 45)       # Deep Blight Purple
        
        # Fade to Black Logic
        self.fade_alpha = 0
        self.is_fading_out = False
        
        # Music Logic
        try:
            pygame.mixer.music.load("assets/sfx/cutscene_theme.mp3")
            pygame.mixer.music.set_volume(0.6)
            pygame.mixer.music.play(-1)
        except:
            print("Cutscene music file not found.")

        # Aesthetics
        self.particles = [{"pos": [random.randint(0, WIDTH), random.randint(0, HEIGHT)], 
                           "vel": [random.uniform(-0.8, 0.8), random.uniform(-0.4, -1.2)],
                           "size": random.randint(1, 3)} for _ in range(60)]
        
        self.black_bar_height = 0
        self.target_bar_height = HEIGHT // 6

    def update(self, dt):
        if not self.active: return

        # 1. Handle Final Fade Out
        if self.is_fading_out:
            self.fade_alpha += 300 * dt
            if self.fade_alpha >= 255:
                self.fade_alpha = 255
                self.active = False
            return

        # 2. Sky Color Transition
        target_progress = self.current_line / (len(self.script) - 1)
        self.color_progress += (target_progress - self.color_progress) * dt * 0.4
        self.current_sky_color = self.start_color.lerp(self.end_color, min(self.color_progress, 1.0))

        # 3. Animate Black Bars
        if self.black_bar_height < self.target_bar_height:
            self.black_bar_height += 100 * dt

        # 4. Typewriter Logic
        if self.current_line < len(self.script):
            self.type_timer += dt
            if self.type_timer >= self.type_speed:
                if self.char_index < len(self.script[self.current_line]):
                    self.displayed_text += self.script[self.current_line][self.char_index]
                    self.char_index += 1
                    self.type_timer = 0
        
        # 5. Particles
        for p in self.particles:
            p["pos"][0] += p["vel"][0]
            p["pos"][1] += p["vel"][1]
            if p["pos"][1] < 0: p["pos"][1] = HEIGHT

    def handle_input(self, event):
        if self.is_fading_out: return

        if event.type == pygame.KEYDOWN or event.type == pygame.MOUSEBUTTONDOWN:
            if self.char_index < len(self.script[self.current_line]):
                self.displayed_text = self.script[self.current_line]
                self.char_index = len(self.script[self.current_line])
            else:
                self.current_line += 1
                if self.current_line >= len(self.script):
                    self.start_exit_sequence()
                else:
                    self.displayed_text = ""
                    self.char_index = 0

    def start_exit_sequence(self):
        self.is_fading_out = True
        pygame.mixer.music.fadeout(1000) # Smooth music exit

    def draw(self):
        # Draw Sky
        self.screen.fill(self.current_sky_color)
        
        # Draw Particles
        for p in self.particles:
            p_surf = pygame.Surface((p["size"]*2, p["size"]*2), pygame.SRCALPHA)
            pygame.draw.circle(p_surf, (255, 255, 255, 120), (p["size"], p["size"]), p["size"])
            self.screen.blit(p_surf, (int(p["pos"][0]), int(p["pos"][1])))

        # Draw Cinematic Bars
        pygame.draw.rect(self.screen, (0, 0, 0), (0, 0, WIDTH, self.black_bar_height))
        pygame.draw.rect(self.screen, (0, 0, 0), (0, HEIGHT - self.black_bar_height, WIDTH, self.black_bar_height))

        # Draw Text
        if self.current_line < len(self.script) and not self.is_fading_out:
            shadow = self.font.render(self.displayed_text, True, (10, 10, 15))
            text_surf = self.font.render(self.displayed_text, True, (245, 245, 245))
            text_rect = text_surf.get_rect(center=(WIDTH // 2, HEIGHT // 2))
            
            self.screen.blit(shadow, (text_rect.x + 2, text_rect.y + 2))
            self.screen.blit(text_surf, text_rect)

        # Draw Fade Overlay
        if self.fade_alpha > 0:
            fade_surf = pygame.Surface((WIDTH, HEIGHT))
            fade_surf.fill((0, 0, 0))
            fade_surf.set_alpha(self.fade_alpha)
            self.screen.blit(fade_surf, (0, 0))