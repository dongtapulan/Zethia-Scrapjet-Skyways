import pygame
from settings import *

class HUD:
    def __init__(self):
        # 1. Load Custom 8-Bit Font
        try:
            # Using the font path defined in settings
            self.main_font = pygame.font.Font("assets/fonts/8-bitanco.ttf", 24)
            self.hint_font = pygame.font.Font("assets/fonts/8-bitanco.ttf", 16)
            self.dist_font = pygame.font.Font("assets/fonts/8-bitanco.ttf", 20)
        except:
            # Fallback if font file is missing
            self.main_font = pygame.font.SysFont("Arial", 22, bold=True)
            self.hint_font = pygame.font.SysFont("Arial", 16, italic=True)
            self.dist_font = pygame.font.SysFont("Arial", 18, bold=True)
        
        # 2. Tutorial/Hint State
        self.hint_text = ""
        self.hint_alpha = 0 
        self.hint_timer = 0
        
        # 3. Bar Dimensions
        self.bar_w, self.bar_h = 200, 14 
        self.margin = 25

    def show_hint(self, text, duration=3.0):
        self.hint_text = text
        self.hint_timer = duration
        self.hint_alpha = 255

    def update(self, dt, player):
        if self.hint_timer > 0:
            self.hint_timer -= dt
        else:
            self.hint_alpha = max(0, self.hint_alpha - 200 * dt)

        # Logic for weight warning
        if player.weight > (MAX_WEIGHT_CAPACITY * 0.8) and self.hint_timer <= 0:
            self.show_hint("CRITICAL WEIGHT - SHED SCRAP TO GAIN LIFT!")

    def draw(self, screen, player, score):
        # --- 1. Top Left: Gauges Stack ---
        draw_x, draw_y = self.margin, self.margin
        
        # Hull Integrity (Health)
        health_ratio = player.health / PLAYER_HEALTH
        self._draw_bar(screen, draw_x, draw_y, health_ratio, 
                       (255, 50, 50), "HULL INTEGRITY")
        
        # Engine Heat
        heat_ratio = player.heat / HEAT_MAX
        heat_color = WHITE if player.is_stalled else HEAT_RED
        self._draw_bar(screen, draw_x, draw_y + 50, heat_ratio, 
                       heat_color, "ENGINE HEAT")
        
        # Cargo Weight
        weight_ratio = player.weight / player.max_weight
        self._draw_bar(screen, draw_x, draw_y + 100, weight_ratio, 
                       (50, 150, 255), "CARGO WEIGHT")

        # --- 2. Top Right: Score & Distance ---
        # Scrap Value
        score_surface = self.main_font.render(f"SCRAP: {score}", True, LUMEN_GOLD)
        score_rect = score_surface.get_rect(topright=(WIDTH - self.margin, self.margin))
        screen.blit(score_surface, score_rect)
        
        # Distance Meter
        dist_surface = self.dist_font.render(f"DIST: {int(player.distance)}m", True, WHITE)
        dist_rect = dist_surface.get_rect(topright=(WIDTH - self.margin, self.margin + 40))
        screen.blit(dist_surface, dist_rect)

        # --- 3. Bottom Left: Ordinance Inventory (New) ---
        self._draw_weapons(screen, player)

        # --- 4. Bottom Center: Tutorial Container ---
        if self.hint_alpha > 0:
            self._draw_hint_box(screen)

    def _draw_bar(self, screen, x, y, ratio, color, label):
        lbl = self.hint_font.render(label, True, WHITE)
        screen.blit(lbl, (x, y - 20))
        
        pygame.draw.rect(screen, (20, 20, 20), (x, y, self.bar_w, self.bar_h))
        fill_w = int(max(0, min(1.0, ratio)) * self.bar_w)
        if fill_w > 0:
            pygame.draw.rect(screen, color, (x, y, fill_w, self.bar_h))
            pygame.draw.rect(screen, (255, 255, 255, 50), (x, y, fill_w, self.bar_h // 3))
        
        pygame.draw.rect(screen, WHITE, (x, y, self.bar_w, self.bar_h), 2)

    def _draw_weapons(self, screen, player):
        """Draws missile and bomb counts in the bottom left."""
        start_x = self.margin
        start_y = HEIGHT - 80

        # Missile UI
        m_color = WHITE if player.missiles > 0 else (100, 100, 100)
        m_text = self.main_font.render(f"[R] MISSILES: {player.missiles}", True, m_color)
        screen.blit(m_text, (start_x, start_y))

        # Bomb UI
        b_color = (100, 200, 255) if player.bombs > 0 else (100, 100, 100)
        b_text = self.main_font.render(f"[G] G-BOMBS: {player.bombs}", True, b_color)
        screen.blit(b_text, (start_x, start_y + 35))

    def _draw_hint_box(self, screen):
        hint_surf = self.hint_font.render(self.hint_text, True, WHITE)
        hint_surf.set_alpha(self.hint_alpha)
        
        box_w = hint_surf.get_width() + 40
        box_h = 50
        box_rect = pygame.Rect(0, 0, box_w, box_h)
        box_rect.center = (WIDTH // 2, HEIGHT - 120)
        
        bg_surf = pygame.Surface((box_w, box_h), pygame.SRCALPHA)
        pygame.draw.rect(bg_surf, (0, 0, 0, 200), (0, 0, box_w, box_h))
        pygame.draw.rect(bg_surf, WHITE, (0, 0, box_w, box_h), 2)
        bg_surf.set_alpha(self.hint_alpha)
        
        screen.blit(bg_surf, box_rect)
        screen.blit(hint_surf, hint_surf.get_rect(center=box_rect.center))