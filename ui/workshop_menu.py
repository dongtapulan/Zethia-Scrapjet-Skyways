import pygame
import random
import math
from settings import *

class DustParticle:
    """Floating dust motes to add ambience to the workshop."""
    def __init__(self):
        self.reset()
        self.x = random.randint(0, WIDTH)
        self.y = random.randint(0, HEIGHT)

    def reset(self):
        self.x = random.randint(0, WIDTH)
        self.y = HEIGHT + 10
        self.vel_y = -random.uniform(10, 30)
        self.vel_x = random.uniform(-10, 10)
        self.alpha = random.randint(50, 150)
        self.size = random.randint(1, 3)

    def update(self, dt):
        self.y += self.vel_y * dt
        self.x += self.vel_x * dt
        if self.y < -10:
            self.reset()

    def draw(self, screen):
        s = pygame.Surface((self.size, self.size))
        s.set_alpha(self.alpha)
        s.fill(WHITE)
        screen.blit(s, (self.x, self.y))

class WorkshopMenu:
    def __init__(self, screen, upgrade_manager):
        self.screen = screen
        self.manager = upgrade_manager
        
        try:
            self.bg = pygame.image.load("assets/backgrounds/workshop.jpeg").convert()
            self.bg = pygame.transform.scale(self.bg, (WIDTH, HEIGHT))
        except:
            self.bg = pygame.Surface((WIDTH, HEIGHT))
            self.bg.fill((20, 15, 10))

        # Modern UI Fonts
        self.font_main = pygame.font.SysFont("Impact", 50)
        self.font_ui = pygame.font.SysFont("Impact", 24)
        self.font_small = pygame.font.SysFont("Arial", 16, bold=True)
        
        self.particles = [DustParticle() for _ in range(40)]
        self.selected_index = 0
        
        # This dynamically pulls the keys from UpgradeManager (missiles, lightning_charges, etc.)
        self.stat_names = list(self.manager.stats.keys())

        self.feedback_msg = ""
        self.feedback_timer = 0
        self.feedback_color = LUMEN_GOLD
        self.glow_anim = 0

    def show_feedback(self, message, color=LUMEN_GOLD):
        self.feedback_msg = message
        self.feedback_timer = 2.0
        self.feedback_color = color

    def handle_input(self, event):
        if event.type == pygame.KEYDOWN:
            if event.key == pygame.K_UP:
                self.selected_index = (self.selected_index - 1) % len(self.stat_names)
            elif event.key == pygame.K_DOWN:
                self.selected_index = (self.selected_index + 1) % len(self.stat_names)
            elif event.key == pygame.K_RETURN:
                stat = self.stat_names[self.selected_index]
                
                # Check for enough bolts before calling manager
                cost = self.manager.get_upgrade_cost(stat)
                
                success = self.manager.attempt_upgrade(stat, None)
                
                if success:
                    # Weapon categories check
                    is_weapon = any(k in stat for k in ["charges", "fuel", "missile", "bomb"])
                    if is_weapon:
                        self.show_feedback(f"STOCK ADDED: {stat.replace('_', ' ').upper()}", (100, 220, 255))
                    else:
                        self.show_feedback(f"SYSTEM UPGRADED: {stat.upper()}", (50, 255, 100))
                else:
                    self.show_feedback("INSUFFICIENT DATA/BOLTS", (255, 80, 80))
                
                return stat 
            elif event.key == pygame.K_ESCAPE:
                return "BACK"
        return None

    def update(self, dt):
        for p in self.particles:
            p.update(dt)
        if self.feedback_timer > 0:
            self.feedback_timer -= dt
        self.glow_anim += 5 * dt

    def draw(self):
        # Draw base background with dark tint
        self.screen.blit(self.bg, (0, 0))
        dark_overlay = pygame.Surface((WIDTH, HEIGHT), pygame.SRCALPHA)
        dark_overlay.fill((0, 0, 0, 160))
        self.screen.blit(dark_overlay, (0, 0))
        
        for p in self.particles:
            p.draw(self.screen)

        # Top Bar
        pygame.draw.rect(self.screen, (20, 20, 25), (0, 0, WIDTH, 100))
        pygame.draw.line(self.screen, LUMEN_GOLD, (0, 100), (WIDTH, 100), 3)
        
        header = self.font_main.render("WEI'S CUSTOMS", True, LUMEN_GOLD)
        self.screen.blit(header, (40, 25))
        
        bolts = self.font_ui.render(f"AVAIL. SCRAP: {self.manager.total_bolts} B", True, WHITE)
        self.screen.blit(bolts, (WIDTH - 300, 35))

        # Feedback Notification
        if self.feedback_timer > 0:
            f_surf = self.font_ui.render(self.feedback_msg, True, self.feedback_color)
            f_rect = f_surf.get_rect(center=(WIDTH//2, 130))
            self.screen.blit(f_surf, f_rect)

        # Drawing Upgrade Cards
        for i, name in enumerate(self.stat_names):
            data = self.manager.stats[name]
            is_sel = i == self.selected_index
            
            # Layout logic: Split into two columns
            col = i // 4 
            row = i % 4
            x = 60 + (col * 480)
            y = 180 + (row * 110)
            
            card_rect = pygame.Rect(x, y, 440, 90)
            
            # Selection Glow
            if is_sel:
                pulse = math.sin(self.glow_anim) * 4
                pygame.draw.rect(self.screen, LUMEN_GOLD, card_rect.inflate(pulse, pulse), 0, 12)
            
            # Card Body
            bg_color = (45, 45, 55) if not is_sel else (70, 65, 50)
            pygame.draw.rect(self.screen, bg_color, card_rect, 0, 10)
            pygame.draw.rect(self.screen, LUMEN_GOLD if is_sel else (100, 100, 110), card_rect, 2, 10)

            # Icon/Type Decorator
            is_weapon = any(k in name for k in ["charges", "fuel", "missile", "bomb"])
            icon_color = (100, 200, 255) if is_weapon else (150, 255, 150)
            pygame.draw.rect(self.screen, icon_color, (x+15, y+15, 10, 60), border_radius=5)

            # Text Rendering
            display_name = name.replace("_", " ").upper()
            label = self.font_ui.render(display_name, True, WHITE)
            self.screen.blit(label, (x + 40, y + 15))
            
            # Cost or Maxed
            current_cost = self.manager.get_upgrade_cost(name)
            if data["level"] < data.get("max", 10):
                cost_color = WHITE if self.manager.total_bolts >= current_cost else (255, 100, 100)
                cost_label = self.font_ui.render(f"{current_cost} B", True, cost_color)
                self.screen.blit(cost_label, (card_rect.right - 90, y + 15))
            else:
                max_label = self.font_ui.render("MAX", True, (100, 255, 100))
                self.screen.blit(max_label, (card_rect.right - 80, y + 15))

            # Progress Bar or Ammo Count (THE FIX IS HERE)
            if not is_weapon:
                bar_bg = pygame.Rect(x + 40, y + 55, 300, 15)
                pygame.draw.rect(self.screen, (20, 20, 25), bar_bg, border_radius=5)
                progress = data["level"] / data["max"]
                pygame.draw.rect(self.screen, (150, 255, 150), (x+40, y+55, 300 * progress, 15), border_radius=5)
            else:
                # Show specific count for weapons using 'level' key
                ammo_text = self.font_small.render(f"STARTING STOCK: {data['level']}", True, (100, 200, 255))
                self.screen.blit(ammo_text, (x + 45, y + 53))

        # Footer
        footer_text = "[UP/DOWN] BROWSE   [ENTER] PURCHASE   [ESC] LAUNCH"
        footer_surf = self.font_small.render(footer_text, True, (150, 150, 150))
        self.screen.blit(footer_surf, (WIDTH // 2 - footer_surf.get_rect().width // 2, HEIGHT - 40))