import pygame
import random
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
            self.bg.fill((30, 20, 20))

        self.font_main = pygame.font.SysFont("Impact", 42)
        self.font_ui = pygame.font.SysFont("Impact", 28)
        self.font_small = pygame.font.SysFont("Arial", 18)
        
        self.particles = [DustParticle() for _ in range(40)]
        self.selected_index = 0
        self.stat_names = list(self.manager.stats.keys())

        # --- FEEDBACK SYSTEM ---
        self.feedback_msg = ""
        self.feedback_timer = 0
        self.feedback_color = LUMEN_GOLD

    def show_feedback(self, message, color=LUMEN_GOLD):
        self.feedback_msg = message
        self.feedback_timer = 1.5  # Show for 1.5 seconds
        self.feedback_color = color

    def handle_input(self, event):
        if event.type == pygame.KEYDOWN:
            if event.key == pygame.K_UP:
                self.selected_index = (self.selected_index - 1) % len(self.stat_names)
            elif event.key == pygame.K_DOWN:
                self.selected_index = (self.selected_index + 1) % len(self.stat_names)
            elif event.key == pygame.K_RETURN:
                stat = self.stat_names[self.selected_index]
                # Check if purchase is successful
                success = self.manager.attempt_upgrade(stat, None)
                
                if success:
                    self.show_feedback(f"UPGRADED: {stat}!", (50, 255, 50))
                else:
                    # Check why it failed for better feedback
                    curr_level = self.manager.stats[stat]["level"]
                    max_level = self.manager.stats[stat]["max"]
                    if curr_level >= max_level:
                        self.show_feedback("MAX LEVEL REACHED", (200, 50, 50))
                    else:
                        self.show_feedback("NOT ENOUGH BOLTS", (200, 50, 50))
                
                return stat 
            elif event.key == pygame.K_ESCAPE:
                return "BACK"
        return None

    def update(self, dt):
        for p in self.particles:
            p.update(dt)
        
        # Update Feedback Timer
        if self.feedback_timer > 0:
            self.feedback_timer -= dt

    def draw(self):
        self.screen.blit(self.bg, (0, 0))
        
        for p in self.particles:
            p.draw(self.screen)

        # Header
        header_text = self.font_main.render("SCRAP WORKSHOP", True, LUMEN_GOLD)
        self.screen.blit(header_text, (50, 40))
        
        bolt_text = self.font_ui.render(f"BOLTS: {self.manager.total_bolts}", True, WHITE)
        self.screen.blit(bolt_text, (WIDTH - 250, 45))

        # --- DRAW FEEDBACK MESSAGE ---
        if self.feedback_timer > 0:
            # Subtle fade out based on timer
            alpha = min(255, int(self.feedback_timer * 255))
            f_text = self.font_ui.render(self.feedback_msg, True, self.feedback_color)
            f_text.set_alpha(alpha)
            # Position it right under the bolt count
            self.screen.blit(f_text, (WIDTH - 250, 85))

        # Upgrade Containers
        start_y = 150
        for i, name in enumerate(self.stat_names):
            stat_data = self.manager.stats[name]
            cost = self.manager.get_upgrade_cost(name)
            is_selected = i == self.selected_index
            
            box_rect = pygame.Rect(50, start_y + (i * 90), 500, 80)
            
            bg_color = (60, 60, 70, 200) if not is_selected else (100, 80, 40, 230)
            border_color = LUMEN_GOLD if is_selected else (100, 100, 100)
            
            pygame.draw.rect(self.screen, (20, 20, 20), (box_rect.x+4, box_rect.y+4, box_rect.width, box_rect.height), border_radius=10)
            pygame.draw.rect(self.screen, bg_color, box_rect, border_radius=10)
            pygame.draw.rect(self.screen, border_color, box_rect, 3, border_radius=10)

            name_label = self.font_ui.render(name, True, WHITE)
            self.screen.blit(name_label, (box_rect.x + 20, box_rect.y + 15))
            
            for level_dot in range(stat_data["max"]):
                dot_color = LUMEN_GOLD if level_dot < stat_data["level"] else (50, 50, 50)
                pygame.draw.circle(self.screen, dot_color, (box_rect.x + 25 + (level_dot * 25), box_rect.y + 55), 6)

            if stat_data["level"] < stat_data["max"]:
                can_afford = self.manager.total_bolts >= cost
                cost_text = self.font_ui.render(f"{cost} B", True, LUMEN_GOLD if can_afford else (200, 50, 50))
                self.screen.blit(cost_text, (box_rect.right - 100, box_rect.y + 25))
            else:
                max_text = self.font_ui.render("MAXED", True, (50, 255, 50))
                self.screen.blit(max_text, (box_rect.right - 120, box_rect.y + 25))

        hint = self.font_small.render("[UP/DOWN] Select   [ENTER] Buy   [ESC] Return to Sky", True, (180, 180, 180))
        self.screen.blit(hint, (50, HEIGHT - 50))