import pygame
import random
import math
from settings import WIDTH, HEIGHT, WHITE, BLACK, LUMEN_GOLD, HEAT_RED

class MenuParticle:
    def __init__(self):
        self.reset()

    def reset(self):
        self.x = random.randint(0, WIDTH)
        self.y = random.randint(0, HEIGHT)
        self.size = random.randint(2, 4)
        self.speed = random.uniform(15, 40)
        self.alpha = random.randint(50, 180)
        self.fade_dir = random.choice([-1, 1])

    def update(self, dt):
        self.y -= self.speed * dt
        self.alpha += self.fade_dir * 100 * dt
        if self.alpha <= 0 or self.alpha >= 200:
            self.fade_dir *= -1
        if self.y < -10:
            self.reset()
            self.y = HEIGHT + 10

    def draw(self, screen):
        s = pygame.Surface((self.size * 2, self.size * 2), pygame.SRCALPHA)
        pygame.draw.circle(s, (255, 255, 180, int(max(0, self.alpha))), (self.size, self.size), self.size)
        screen.blit(s, (self.x, self.y))

class MainMenu:
    def __init__(self, screen):
        self.screen = screen
        self.font_path = "assets/fonts/8-bitanco.ttf"
        
        # Assets
        try:
            self.bg1 = pygame.transform.scale(pygame.image.load("assets/backgrounds/skyfall_bg1.jpeg").convert(), (WIDTH, HEIGHT))
            self.bg2 = pygame.transform.scale(pygame.image.load("assets/backgrounds/skyfall_bg2.jpeg").convert(), (WIDTH, HEIGHT))
        except:
            self.bg1 = pygame.Surface((WIDTH, HEIGHT))
            self.bg1.fill((30, 30, 50))
            self.bg2 = self.bg1.copy()

        # Intro State
        self.menu_state = "SPLASH"
        self.intro_timer = 0
        self.splash_alpha = 0
        self.title_text_full = "ZETHIA"
        self.title_text_current = ""
        self.typewriter_index = 0
        self.typewriter_timer = 0
        
        # Animations
        self.fade_alpha = 0
        self.bg_switch = False
        self.particles = [MenuParticle() for _ in range(40)]
        self.pulse_timer = 0
        
        # STREAMLINED OPTIONS
        self.options = ["Start Game", "Workshop", "Exit"]
        self.selected_index = 0
        self.button_alphas = [0] * len(self.options)

        # Start Music
        try:
            if not pygame.mixer.music.get_busy():
                pygame.mixer.music.load("assets/sfx/menu_theme-ShiningDays.mp3")
                pygame.mixer.music.set_volume(0.2)
                pygame.mixer.music.play(-1)
        except:
            pass

    def update(self, dt):
        self.intro_timer += dt
        
        if self.menu_state == "SPLASH":
            if self.intro_timer < 2.0:
                self.splash_alpha = min(255, self.splash_alpha + 150 * dt)
            elif self.intro_timer > 4.0:
                self.splash_alpha = max(0, self.splash_alpha - 200 * dt)
                if self.splash_alpha <= 0:
                    self.menu_state = "TITLE_WRITE"
                    self.intro_timer = 0

        elif self.menu_state == "TITLE_WRITE":
            self.typewriter_timer += dt
            if self.typewriter_timer > 0.1 and self.typewriter_index < len(self.title_text_full):
                self.typewriter_index += 1
                self.title_text_current = self.title_text_full[:self.typewriter_index]
                self.typewriter_timer = 0
            
            if self.typewriter_index >= len(self.title_text_full) and self.intro_timer > 1.0:
                self.menu_state = "READY"

        elif self.menu_state == "READY":
            self.pulse_timer += dt * 5
            for i in range(len(self.button_alphas)):
                self.button_alphas[i] = min(255, self.button_alphas[i] + 400 * dt)

            # BG Carousel
            if not self.bg_switch:
                self.fade_alpha = min(255, self.fade_alpha + 30 * dt)
                if self.fade_alpha >= 255: self.bg_switch = True
            else:
                self.fade_alpha = max(0, self.fade_alpha - 30 * dt)
                if self.fade_alpha <= 0: self.bg_switch = False

        for p in self.particles:
            p.update(dt)

    def draw(self):
        if self.menu_state == "SPLASH":
            self.screen.fill(BLACK)
            try:
                splash_font = pygame.font.Font(self.font_path, 30)
                splash_surf = splash_font.render("Hyu Wei Productions", True, (200, 200, 200))
                splash_surf.set_alpha(self.splash_alpha)
                self.screen.blit(splash_surf, (WIDTH//2 - splash_surf.get_width()//2, HEIGHT//2))
            except: pass
            return

        self.screen.blit(self.bg1, (0, 0))
        self.bg2.set_alpha(self.fade_alpha)
        self.screen.blit(self.bg2, (0, 0))

        for p in self.particles:
            p.draw(self.screen)

        if self.menu_state in ["TITLE_WRITE", "READY"]:
            box_w, box_h = 700, 160
            box_surf = pygame.Surface((box_w, box_h), pygame.SRCALPHA)
            pygame.draw.rect(box_surf, (255, 253, 208, 180), (0, 0, box_w, box_h), border_radius=15)
            pygame.draw.rect(box_surf, LUMEN_GOLD, (0, 0, box_w, box_h), width=3, border_radius=15)
            self.screen.blit(box_surf, (WIDTH//2 - box_w//2, 80))

            try:
                title_font = pygame.font.Font(self.font_path, 90)
                main_title = title_font.render(self.title_text_current, True, (60, 60, 60))
                self.screen.blit(main_title, (WIDTH//2 - main_title.get_width()//2, 105))
                
                if self.menu_state == "READY":
                    sub_font = pygame.font.Font(self.font_path, 25)
                    sub_title = sub_font.render("SCRAPJET SKYWAYS", True, (100, 90, 0))
                    self.screen.blit(sub_title, (WIDTH//2 - sub_title.get_width()//2, 190))
            except: pass

        if self.menu_state == "READY":
            try:
                opt_font = pygame.font.Font(self.font_path, 35)
                for i, option in enumerate(self.options):
                    is_sel = (i == self.selected_index)
                    color = list(LUMEN_GOLD) if is_sel else [255, 255, 255]
                    
                    if is_sel:
                        glow = (math.sin(self.pulse_timer) + 1) * 20
                        color[1] = min(255, color[1] + glow)
                    
                    text = f"> {option} <" if is_sel else option
                    surf = opt_font.render(text, True, color)
                    surf.set_alpha(self.button_alphas[i])
                    
                    x_pos = WIDTH//2 - surf.get_width()//2
                    if is_sel: x_pos += math.sin(self.pulse_timer * 2) * 5
                    
                    # Vertical spacing for 3 buttons
                    self.screen.blit(surf, (x_pos, 350 + i * 80))
            except: pass

    def handle_input(self, event):
        if self.menu_state != "READY":
            if event.type == pygame.KEYDOWN:
                if event.key in [pygame.K_RETURN, pygame.K_SPACE, pygame.K_ESCAPE]:
                    self.menu_state = "READY"
                    self.title_text_current = self.title_text_full
                    self.typewriter_index = len(self.title_text_full)
                    self.button_alphas = [255] * len(self.options)
            return None
        
        if event.type == pygame.KEYDOWN:
            if event.key == pygame.K_UP:
                self.selected_index = (self.selected_index - 1) % len(self.options)
            elif event.key == pygame.K_DOWN:
                self.selected_index = (self.selected_index + 1) % len(self.options)
            elif event.key == pygame.K_RETURN:
                return self.options[self.selected_index]
        return None

class GameOverScreen:
    def __init__(self, screen):
        self.screen = screen
        self.font_path = "assets/fonts/8-bitanco.ttf"
        self.options = ["Retry", "Main Menu", "Exit"]
        self.selected_index = 0
        self.timer = 0

    def update(self, dt):
        self.timer += dt

    def draw(self, distance, score):
        overlay = pygame.Surface((WIDTH, HEIGHT), pygame.SRCALPHA)
        overlay.fill((20, 0, 0, 180)) 
        self.screen.blit(overlay, (0, 0))

        try:
            title_font = pygame.font.Font(self.font_path, 80)
            off_x = random.randint(-2, 2)
            title_surf = title_font.render("SYSTEM FAILURE", True, HEAT_RED)
            self.screen.blit(title_surf, (WIDTH//2 - title_surf.get_width()//2 + off_x, 150))

            stat_font = pygame.font.Font(self.font_path, 24)
            dist_surf = stat_font.render(f"DISTANCE TRAVELED: {int(distance)}m", True, WHITE)
            scrap_surf = stat_font.render(f"SCRAP RECOVERED: {score}", True, LUMEN_GOLD)
            
            self.screen.blit(dist_surf, (WIDTH//2 - dist_surf.get_width()//2, 280))
            self.screen.blit(scrap_surf, (WIDTH//2 - scrap_surf.get_width()//2, 320))

            opt_font = pygame.font.Font(self.font_path, 30)
            for i, opt in enumerate(self.options):
                is_sel = (i == self.selected_index)
                color = HEAT_RED if is_sel else (150, 150, 150)
                
                if is_sel:
                    alpha = 155 + math.sin(self.timer * 10) * 100
                    color = (int(alpha), 50, 50)
                
                text = f"> {opt} <" if is_sel else opt
                surf = opt_font.render(text, True, color)
                self.screen.blit(surf, (WIDTH//2 - surf.get_width()//2, 450 + i * 60))

        except Exception as e:
            print(f"Menu Draw Error: {e}")

    def handle_input(self, event):
        if event.type == pygame.KEYDOWN:
            if event.key == pygame.K_UP:
                self.selected_index = (self.selected_index - 1) % len(self.options)
            elif event.key == pygame.K_DOWN:
                self.selected_index = (self.selected_index + 1) % len(self.options)
            elif event.key == pygame.K_RETURN:
                return self.options[self.selected_index]
        return None