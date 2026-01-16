import pygame
import random
import math
from settings import WIDTH, HEIGHT, WHITE

class IntroCutscene:
    def __init__(self, screen):
        self.screen = screen
        self.font = pygame.font.SysFont("Georgia", 26, italic=True)
        self.active = True
        
        # Revised Lore: Focusing on Huey's loneliness and the mystery of the companions
        self.script = [
            "The world is quiet now. Just the hum of the engine and the rot in the air.",
            "I’ve spent my life feeling like a ghost... left behind long before the sky turned purple.",
            "They say the Withering took everything, but I never had much to lose.",
            "We survive by not asking questions. We just fly.",
            "But lately, the scrap is... different. It hums with a warmth I don't recognize.",
            "A spark of Indigo that feels too enthusiastic for a dying world...", # Tine hint
            "A Golden glow that feels like a kind hand resting on my shoulder.", # Cici hint
            "Am I finally not flying alone? Or am I just losing my mind to the rot?",
            "The Life Tree is screaming. The corruption must be purged.",
            "Maybe these projections are the keys to the Zethia we once knew.",
            "Ignition. For the Tree. For the friends I haven't met yet.",
            "--- PROJECT SKYFALL: SYNCING SOUL-CORE ---" 
        ]
        
        self.current_line = 0
        self.displayed_text = ""
        self.char_index = 0
        self.type_speed = 0.06  
        self.type_timer = 0
        
        # Visual State
        self.color_progress = 0.0
        self.start_color = pygame.Color(40, 40, 60)   # Somber, lonely grey
        self.end_color = pygame.Color(20, 0, 40)      # Deep "Withering" purple
        
        self.fade_alpha = 0
        self.is_fading_out = False
        
        # Astral/Lore effects
        self.glitch_timer = 0
        self.is_glitching = False
        self.indigo_flash = 0 
        self.gold_glow = 0    

        try:
            pygame.mixer.music.load("assets/sfx/cutscene_theme.mp3")
            pygame.mixer.music.set_volume(0.5)
            pygame.mixer.music.play(-1)
        except:
            pass

        self.particles = [{"pos": [random.randint(0, WIDTH), random.randint(0, HEIGHT)], 
                           "vel": [random.uniform(-0.5, 0.5), random.uniform(-0.2, -0.8)],
                           "size": random.randint(1, 2)} for _ in range(50)]
        
        self.black_bar_height = 0
        self.target_bar_height = HEIGHT // 5

    def update(self, dt):
        if not self.active: return

        if self.is_fading_out:
            self.fade_alpha += 250 * dt
            if self.fade_alpha >= 255:
                self.active = False
            return

        # Background color transition
        target_progress = self.current_line / (len(self.script) - 1)
        self.color_progress += (target_progress - self.color_progress) * dt * 0.3
        self.current_sky_color = self.start_color.lerp(self.end_color, min(self.color_progress, 1.0))

        # Trigger flashes based on text content
        if "Indigo" in self.displayed_text: self.indigo_flash = 120
        if "Golden" in self.displayed_text: self.gold_glow = 80
        
        # Decay flashes
        if self.indigo_flash > 0: self.indigo_flash -= 150 * dt
        if self.gold_glow > 0: self.gold_glow -= 100 * dt

        if self.black_bar_height < self.target_bar_height:
            self.black_bar_height += 80 * dt

        # Typewriter Logic
        if self.current_line < len(self.script):
            self.type_timer += dt
            if self.type_timer >= self.type_speed:
                if self.char_index < len(self.script[self.current_line]):
                    self.displayed_text += self.script[self.current_line][self.char_index]
                    self.char_index += 1
                    self.type_timer = 0

        # Sequel Teaser Glitch
        if "SKYFALL" in self.displayed_text:
            self.glitch_timer += dt
            if self.glitch_timer > 0.08:
                self.is_glitching = not self.is_glitching
                self.glitch_timer = 0

        for p in self.particles:
            p["pos"][1] += p["vel"][1]
            if p["pos"][1] < 0: p["pos"][1] = HEIGHT

    def handle_input(self, event):
        if self.is_fading_out: return
        
        # Restricting skip to SPACE and RETURN (Enter)
        if event.type == pygame.KEYDOWN:
            if event.key in [pygame.K_SPACE, pygame.K_RETURN]:
                if self.char_index < len(self.script[self.current_line]):
                    # Finish typing the current line
                    self.displayed_text = self.script[self.current_line]
                    self.char_index = len(self.script[self.current_line])
                else:
                    # Move to next line
                    self.current_line += 1
                    if self.current_line >= len(self.script):
                        self.start_exit_sequence()
                    else:
                        self.displayed_text = ""
                        self.char_index = 0

    def start_exit_sequence(self):
        self.is_fading_out = True
        pygame.mixer.music.fadeout(2000)

    def draw(self):
        self.screen.fill(self.current_sky_color)
        
        # Draw Lore Flashes
        if self.indigo_flash > 0:
            s = pygame.Surface((WIDTH, HEIGHT))
            s.fill((100, 0, 255))
            s.set_alpha(int(self.indigo_flash))
            self.screen.blit(s, (0,0))
        if self.gold_glow > 0:
            s = pygame.Surface((WIDTH, HEIGHT))
            s.fill((255, 200, 0))
            s.set_alpha(int(self.gold_glow))
            self.screen.blit(s, (0,0))

        for p in self.particles:
            pygame.draw.circle(self.screen, (200, 200, 255, 100), (int(p["pos"][0]), int(p["pos"][1])), p["size"])

        # Cinema Bars
        pygame.draw.rect(self.screen, (0, 0, 0), (0, 0, WIDTH, int(self.black_bar_height)))
        pygame.draw.rect(self.screen, (0, 0, 0), (0, HEIGHT - int(self.black_bar_height), WIDTH, int(self.black_bar_height)))

        # Text Rendering
        if self.current_line < len(self.script) and not self.is_fading_out:
            text_color = (0, 255, 240) if self.is_glitching else (235, 235, 245)
            offset = random.randint(-2, 2) if self.is_glitching else 0
            
            text_surf = self.font.render(self.displayed_text, True, text_color)
            text_rect = text_surf.get_rect(center=(WIDTH // 2 + offset, HEIGHT // 2))
            
            # Shadow
            shadow = self.font.render(self.displayed_text, True, (15, 15, 25))
            self.screen.blit(shadow, (text_rect.x + 2, text_rect.y + 2))
            self.screen.blit(text_surf, text_rect)

        # Fade to Black
        if self.fade_alpha > 0:
            fade_surf = pygame.Surface((WIDTH, HEIGHT))
            fade_surf.fill((0, 0, 0))
            fade_surf.set_alpha(int(self.fade_alpha))
            self.screen.blit(fade_surf, (0, 0))