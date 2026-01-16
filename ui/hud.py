import pygame
import math
from settings import *

class HUD:
    def __init__(self):
        # 1. Load Custom Fonts
        try:
            self.main_font = pygame.font.Font("assets/fonts/8-bitanco.ttf", 24)
            self.hint_font = pygame.font.Font("assets/fonts/8-bitanco.ttf", 16)
            self.dist_font = pygame.font.Font("assets/fonts/8-bitanco.ttf", 20)
        except:
            self.main_font = pygame.font.SysFont("Arial", 22, bold=True)
            self.hint_font = pygame.font.SysFont("Arial", 16, italic=True)
            self.dist_font = pygame.font.SysFont("Arial", 18, bold=True)
        
        # 2. SFX
        try:
            self.sfx_warning = pygame.mixer.Sound("assets/sfx/low_health_beep.mp3")
            self.sfx_warning.set_volume(0.2)
        except:
            self.sfx_warning = None
            
        # 3. State & Animation
        self.hint_text = ""
        self.hint_alpha = 0 
        self.hint_timer = 0
        self.pulse_time = 0 
        
        # 4. Dimensions
        self.bar_w, self.bar_h = 220, 16 
        self.margin = 30

    def show_hint(self, text, duration=3.0):
        self.hint_text = text
        self.hint_timer = duration
        self.hint_alpha = 255

    def update(self, dt, player):
        self.pulse_time += dt * 5
        
        # Hint fading
        if self.hint_timer > 0:
            self.hint_timer -= dt
        else:
            self.hint_alpha = max(0, self.hint_alpha - 200 * dt)

        # Smart Warnings
        if player.is_alive:
            if player.weight > (MAX_WEIGHT_CAPACITY * 0.85) and self.hint_timer <= 0:
                self.show_hint("WARNING: MAXIMUM CARGO WEIGHT REACHED", 2.0)
            elif player.health < (PLAYER_HEALTH * 0.25) and self.hint_timer <= 0:
                self.show_hint("CRITICAL HULL DAMAGE", 1.0)
            # CHANGE: Added Low Fuel warning for Laser
            elif player.laser_fuel > 0 and player.laser_fuel < 50 and self.hint_timer <= 0:
                self.show_hint("LASER CORE LOW", 0.5)

    def draw(self, screen, player, score):
        # --- 1. Top Left: Cockpit Gauges ---
        self._draw_status_panel(screen, player)
        
        # --- 2. Top Right: Expedition Data ---
        self._draw_score_panel(screen, score, player.distance)

        # --- 3. Bottom Left: Ordinance System ---
        self._draw_weapons_hud(screen, player)

        # --- 4. Center: Warnings/Tutorials ---
        if self.hint_alpha > 0:
            self._draw_hint_box(screen)

    def _draw_status_panel(self, screen, player):
        x, y = self.margin, self.margin
        panel_rect = pygame.Rect(x - 10, y - 10, self.bar_w + 20, 160)
        self._draw_glass_rect(screen, panel_rect)

        # Hull Integrity
        h_ratio = player.health / player.max_health # Updated to use dynamic max_health
        h_color = (255, 50, 50)
        if h_ratio < 0.3:
            pulse = (math.sin(self.pulse_time * 2) + 1) / 2
            h_color = (255, 50 + (200 * pulse), 50 + (200 * pulse))
        self._draw_bar(screen, x, y + 20, h_ratio, h_color, "HULL STABILITY")

        # Engine Heat
        heat_ratio = player.heat / player.heat_system.max_heat # Updated for dynamic heat
        heat_color = HEAT_RED
        if player.is_stalled:
            heat_color = WHITE if (int(self.pulse_time * 2) % 2 == 0) else (255, 255, 100)
        self._draw_bar(screen, x, y + 70, heat_ratio, heat_color, "THERMAL LOAD")

        # Cargo Weight
        w_ratio = player.weight / player.max_weight
        w_color = (0, 200, 255) if w_ratio < 0.8 else (255, 165, 0)
        self._draw_bar(screen, x, y + 120, w_ratio, w_color, "CARGO MASS")

    def _draw_score_panel(self, screen, score, distance):
        x = WIDTH - self.margin
        y = self.margin
        score_txt = self.main_font.render(f"{score:06}", True, LUMEN_GOLD)
        score_rect = score_txt.get_rect(topright=(x, y))
        lbl = self.hint_font.render("SCRAP CREDITS", True, (150, 150, 150))
        screen.blit(lbl, (x - lbl.get_width(), y - 15))
        screen.blit(score_txt, score_rect)
        dist_txt = self.dist_font.render(f"{int(distance)}m", True, WHITE)
        screen.blit(dist_txt, (x - dist_txt.get_width(), y + 35))

    def _draw_weapons_hud(self, screen, player):
        """Ordinance Display including Specials."""
        x, y = self.margin, HEIGHT - 180 # Moved up to fit new rows
        
        # 1. Missile (R)
        self._draw_weapon_icon(screen, x, y, "R", f"MISSILE x{player.missiles}", WHITE, player.missiles > 0)
        
        # 2. G-Bomb (G)
        self._draw_weapon_icon(screen, x, y + 40, "G", f"G-BOMB x{player.bombs}", (100, 200, 255), player.bombs > 0)

        # 3. Tine's Lightning (Q) - CHANGE: Added Lightning
        l_color = (150, 230, 255)
        self._draw_weapon_icon(screen, x, y + 80, "Q", f"LIGHTNING x{player.lightning_charges}", l_color, player.lightning_charges > 0)

        # 4. Red's Laser (E) - CHANGE: Added Laser Fuel Bar
        laser_color = (255, 50, 50)
        self._draw_weapon_icon(screen, x, y + 120, "E", "RED LASER", laser_color, player.laser_fuel > 0)
        # Laser Fuel mini-bar
        fuel_ratio = player.laser_fuel / 300 # Assuming 300 is max fuel capacity
        self._draw_mini_bar(screen, x + 180, y + 132, fuel_ratio, laser_color)

    def _draw_weapon_icon(self, screen, x, y, key, label, color, active):
        """Helper to draw weapon slots consistently."""
        alpha = 255 if active else 80
        # Key Box
        pygame.draw.rect(screen, (30, 30, 30), (x, y, 30, 30))
        pygame.draw.rect(screen, color if active else (100, 100, 100), (x, y, 30, 30), 1)
        k_text = self.hint_font.render(key, True, color if active else (100, 100, 100))
        screen.blit(k_text, k_text.get_rect(center=(x+15, y+15)))
        
        # Text Label
        txt = self.main_font.render(f"  {label}", True, color if active else (100, 100, 100))
        txt.set_alpha(alpha)
        screen.blit(txt, (x + 35, y + 2))

    def _draw_mini_bar(self, screen, x, y, ratio, color):
        """Small bar for secondary fuels."""
        w, h = 80, 8
        pygame.draw.rect(screen, (20, 20, 20), (x, y, w, h))
        pygame.draw.rect(screen, color, (x, y, int(w * ratio), h))
        pygame.draw.rect(screen, (100, 100, 100), (x, y, w, h), 1)

    def _draw_bar(self, screen, x, y, ratio, color, label):
        lbl = self.hint_font.render(label, True, (200, 200, 200))
        screen.blit(lbl, (x, y - 18))
        bg_rect = pygame.Rect(x, y, self.bar_w, self.bar_h)
        pygame.draw.rect(screen, (30, 30, 35), bg_rect)
        fill_w = int(max(0, min(1.0, ratio)) * self.bar_w)
        if fill_w > 0:
            fill_rect = pygame.Rect(x, y, fill_w, self.bar_h)
            pygame.draw.rect(screen, color, fill_rect)
        pygame.draw.rect(screen, (150, 150, 150), bg_rect, 1)

    def _draw_glass_rect(self, screen, rect):
        glass = pygame.Surface((rect.width, rect.height), pygame.SRCALPHA)
        pygame.draw.rect(glass, (0, 0, 0, 140), (0, 0, rect.width, rect.height))
        length = 10
        pygame.draw.line(glass, (0, 200, 255), (0,0), (length, 0), 2)
        pygame.draw.line(glass, (0, 200, 255), (0,0), (0, length), 2)
        screen.blit(glass, rect)

    def _draw_hint_box(self, screen):
        hint_surf = self.hint_font.render(self.hint_text, True, WHITE)
        hint_surf.set_alpha(self.hint_alpha)
        border_color = WHITE
        if any(word in self.hint_text for word in ["WARNING", "CRITICAL", "LOW"]):
            s = (math.sin(self.pulse_time * 2) + 1) / 2
            border_color = (255, 50 + (100 * s), 50 + (100 * s))
        box_w = hint_surf.get_width() + 60
        box_h = 44
        box_rect = pygame.Rect(0, 0, box_w, box_h)
        box_rect.center = (WIDTH // 2, HEIGHT - 250)
        bg_surf = pygame.Surface((box_w, box_h), pygame.SRCALPHA)
        pygame.draw.rect(bg_surf, (20, 0, 0, 180), (0, 0, box_w, box_h))
        pygame.draw.rect(bg_surf, border_color, (0, 0, box_w, box_h), 2)
        bg_surf.set_alpha(self.hint_alpha)
        screen.blit(bg_surf, box_rect)
        screen.blit(hint_surf, hint_surf.get_rect(center=box_rect.center))