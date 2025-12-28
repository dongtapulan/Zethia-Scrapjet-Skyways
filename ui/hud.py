import pygame
from settings import *

class HUD:
    def __init__(self):
        # 1. Fonts (Ensure these are defined in settings or use default)
        self.main_font = pygame.font.SysFont("Arial", 24, bold=True)
        self.hint_font = pygame.font.SysFont("Arial", 18, italic=True)
        
        # 2. Tutorial/Hint State
        self.hint_text = ""
        self.hint_alpha = 0  # For fading in/out
        self.hint_timer = 0
        
        # 3. Bar Dimensions
        self.bar_w, self.bar_h = 180, 12
        self.margin = 25

    def show_hint(self, text, duration=3.0):
        """Triggers a clean tutorial popup."""
        self.hint_text = text
        self.hint_timer = duration
        self.hint_alpha = 255

    def update(self, dt, player):
        # Logic for fading hints
        if self.hint_timer > 0:
            self.hint_timer -= dt
        else:
            self.hint_alpha = max(0, self.hint_alpha - 200 * dt)

        # Context-aware tutorial hints
        if player.weight > 700 and self.hint_timer <= 0:
            self.show_hint("PLANE TOO HEAVY - PRESS 'F' TO SHOOT SCRAP AMMO!")

    def draw(self, screen, player, score):
        # --- 1. Top Left: Gauges ---
        draw_x, draw_y = self.margin, self.margin
        
        # Heat Bar
        self._draw_bar(screen, draw_x, draw_y, player.heat / HEAT_MAX, 
                       WHITE if player.is_stalled else HEAT_RED, "ENGINE HEAT")
        
        # Weight Bar
        self._draw_bar(screen, draw_x, draw_y + 40, player.weight / player.max_weight, 
                       (50, 150, 255), "CARGO WEIGHT")

        # --- 2. Top Right: Score ---
        score_surface = self.main_font.render(f"SCRAP VALUE: {score}", True, WHITE)
        score_rect = score_surface.get_rect(topright=(WIDTH - self.margin, self.margin))
        screen.blit(score_surface, score_rect)

        # --- 3. Bottom Center: Tutorial Container ---
        if self.hint_alpha > 0:
            self._draw_hint_box(screen)

    def _draw_bar(self, screen, x, y, ratio, color, label):
        # Label text
        lbl = self.hint_font.render(label, True, WHITE)
        screen.blit(lbl, (x, y - 18))
        
        # Background/Border
        pygame.draw.rect(screen, (40, 40, 40), (x, y, self.bar_w, self.bar_h))
        # Fill
        fill_w = int(max(0, min(1.0, ratio)) * self.bar_w)
        if fill_w > 0:
            pygame.draw.rect(screen, color, (x, y, fill_w, self.bar_h))
        # Subtle Border
        pygame.draw.rect(screen, WHITE, (x, y, self.bar_w, self.bar_h), 1)

    def _draw_hint_box(self, screen):
        """Draws the clean container for tutorial text."""
        hint_surf = self.hint_font.render(self.hint_text, True, WHITE)
        hint_surf.set_alpha(self.hint_alpha)
        
        # Container Box
        box_w = hint_surf.get_width() + 40
        box_h = 40
        box_rect = pygame.Rect(0, 0, box_w, box_h)
        box_rect.center = (WIDTH // 2, HEIGHT - 100)
        
        # Semi-transparent background
        bg_surf = pygame.Surface((box_w, box_h), pygame.SRCALPHA)
        pygame.draw.rect(bg_surf, (0, 0, 0, 180), (0, 0, box_w, box_h), border_radius=10)
        bg_surf.set_alpha(self.hint_alpha)
        
        screen.blit(bg_surf, box_rect)
        screen.blit(hint_surf, hint_surf.get_rect(center=box_rect.center))