import pygame
import random
import math
from settings import WIDTH, HEIGHT, GROUND_LINE

class Companion(pygame.sprite.Sprite):
    def __init__(self, huey, side="TOP"):
        super().__init__()
        self.huey = huey
        self.side = side
        self.life_timer = 12.0  # Duration of the companion
        self.pos = pygame.Vector2(huey.rect.center)
        self.hover_angle = random.uniform(0, math.pi * 2)
        
    def update_behavior(self, dt):
        self.life_timer -= dt
        if self.life_timer <= 0:
            # Ensure invincibility is cleared if Tine expires
            if hasattr(self.huey, 'is_invincible'):
                self.huey.is_invincible = False
            self.kill()

        # Movement Logic
        offset_x = -80 
        offset_y = -110 if self.side == "TOP" else 110
        target = pygame.Vector2(self.huey.rect.centerx + offset_x, 
                                self.huey.rect.centery + offset_y)
        
        self.hover_angle += 3 * dt
        target.y += math.sin(self.hover_angle) * 20
        self.pos += (target - self.pos) * 5 * dt
        self.rect.center = self.pos

    def draw_circular_flash(self, screen):
        # Circular white flash fade out when life < 1.0s
        if self.life_timer < 1.0:
            alpha = int(self.life_timer * 255) # Fades OUT
            radius = int(self.rect.width * 0.8)
            flash_surf = pygame.Surface((radius*2, radius*2), pygame.SRCALPHA)
            pygame.draw.circle(flash_surf, (255, 255, 255, alpha), (radius, radius), radius)
            screen.blit(flash_surf, flash_surf.get_rect(center=self.rect.center))

class Red(Companion):
    def __init__(self, huey):
        super().__init__(huey, "TOP")
        try:
            self.image = pygame.image.load("assets/sprites/companions/red_mount.png").convert_alpha()
        except:
            self.image = pygame.Surface((60, 50), pygame.SRCALPHA)
            pygame.draw.rect(self.image, (200, 50, 50), (0, 10, 60, 30))
            
        # --- SFX LOAD ---
        try:
            self.shoot_sfx = pygame.mixer.Sound("assets/sfx/Red_Laser.mp3")
            self.shoot_sfx.set_volume(0.25)
        except:
            self.shoot_sfx = None
        
        self.rect = self.image.get_rect()
        self.attack_cooldown = 0
        self.lasers = []

    def update(self, dt, enemies):
        self.update_behavior(dt)
        self.attack_cooldown -= dt
        self.lasers = [l for l in self.lasers if l['life'] > 0]
        for l in self.lasers: l['life'] -= dt

        if self.attack_cooldown <= 0:
            target = self.find_target(enemies)
            if target:
                self.fire_railgun(target)
                self.attack_cooldown = 1.0

    def find_target(self, enemies):
        # Find closest enemy in front of player
        visible = [e for e in enemies if 50 < e.rect.x < WIDTH - 50]
        return min(visible, key=lambda e: e.rect.x) if visible else None

    def fire_railgun(self, target):
        self.lasers.append({'start': self.rect.center, 'end': target.rect.center, 'life': 0.2})
        
        if self.shoot_sfx:
            self.shoot_sfx.play()

        if hasattr(target, 'take_damage'):
            target.take_damage(60)

    def draw(self, screen):
        for laser in self.lasers:
            thickness = int(laser['life'] * 25)
            # Red Core
            pygame.draw.line(screen, (255, 0, 0), laser['start'], laser['end'], thickness)
            # White Inner Beam
            pygame.draw.line(screen, (255, 255, 255), laser['start'], laser['end'], thickness // 2)
            
        screen.blit(self.image, self.rect)
        self.draw_circular_flash(screen)

class Tine(Companion):
    def __init__(self, huey):
        super().__init__(huey, "BOTTOM")
        try:
            self.image = pygame.image.load("assets/sprites/companions/tine_witch.png").convert_alpha()
            self.lightning_img = pygame.image.load("assets/sprites/effects/lightning_bolt.png").convert_alpha()
        except:
            self.image = pygame.Surface((50, 50), pygame.SRCALPHA)
            pygame.draw.circle(self.image, (150, 50, 255), (25, 25), 20)
            self.lightning_img = None

        # --- SFX LOAD ---
        try:
            self.zap_sfx = pygame.mixer.Sound("assets/sfx/tine_lightning.mp3")
            self.zap_sfx.set_volume(0.3)
        except:
            self.zap_sfx = None

        self.rect = self.image.get_rect()
        self.zap_timer = 0
        self.active_zaps = [] # List of {'end_pos': Vec2, 'life': float}

    def update(self, dt, enemies):
        self.update_behavior(dt)
        self.zap_timer += dt
        
        # Invincibility Logic
        self.huey.is_invincible = True
        
        # Clean up zap visuals
        self.active_zaps = [z for z in self.active_zaps if z['life'] > 0]
        for z in self.active_zaps: z['life'] -= dt

        if self.zap_timer > 0.4:
            for enemy in enemies:
                dist = pygame.Vector2(self.rect.center).distance_to(enemy.rect.center)
                # INCREASED RANGE HERE (350 -> 650)
                if dist < 650:
                    self.perform_zap(enemy)
                    self.zap_timer = 0
                    break 

    def perform_zap(self, enemy):
        if hasattr(enemy, 'take_damage'):
            enemy.take_damage(30)
            self.active_zaps.append({'end': pygame.Vector2(enemy.rect.center), 'life': 0.15})
            
            if self.zap_sfx:
                self.zap_sfx.play()

    def draw(self, screen):
        # 1. Indigo Glowing Translucent Shield
        shield_radius = 120
        shield_surf = pygame.Surface((shield_radius*2.5, shield_radius*2.5), pygame.SRCALPHA)
        pulse = 40 + math.sin(pygame.time.get_ticks() * 0.01) * 10
        
        # Indigo color: (75, 0, 130)
        pygame.draw.circle(shield_surf, (75, 0, 130, int(pulse)), (int(shield_radius*1.25), int(shield_radius*1.25)), shield_radius)
        pygame.draw.circle(shield_surf, (150, 100, 255, 100), (int(shield_radius*1.25), int(shield_radius*1.25)), shield_radius, 3)
        screen.blit(shield_surf, shield_surf.get_rect(center=self.huey.rect.center))

        # 2. Draw Lightning Bolts
        for zap in self.active_zaps:
            start_pos = pygame.Vector2(self.rect.center)
            end_pos = zap['end']
            
            # Create a jagged multi-point lightning line for better visual at long range
            points = [start_pos]
            mid_points = 3 # Number of jagged breaks
            for i in range(1, mid_points + 1):
                fraction = i / (mid_points + 1)
                base_point = start_pos.lerp(end_pos, fraction)
                offset = pygame.Vector2(random.randint(-20, 20), random.randint(-20, 20))
                points.append(base_point + offset)
            points.append(end_pos)
            
            # Draw the main bolt
            pygame.draw.lines(screen, (200, 200, 255), False, points, 3)
            # Draw a thinner white core for "brightness"
            pygame.draw.lines(screen, (255, 255, 255), False, points, 1)
            
            # Blit lightning asset impact if available
            if self.lightning_img:
                bolt_scaled = pygame.transform.rotozoom(self.lightning_img, random.randint(0, 360), 0.5)
                screen.blit(bolt_scaled, bolt_scaled.get_rect(center=end_pos))

        screen.blit(self.image, self.rect)
        self.draw_circular_flash(screen)

class CompanionManager:
    def __init__(self, huey):
        self.huey = huey
        self.companions = pygame.sprite.Group()

    def summon(self, companion_type):
        for c in self.companions:
            if isinstance(c, Red) and companion_type == "RED": return
            if isinstance(c, Tine) and companion_type == "TINE": return

        if companion_type == "RED":
            self.companions.add(Red(self.huey))
        elif companion_type == "TINE":
            self.companions.add(Tine(self.huey))

    def update(self, dt, enemies):
        # Default invincibility to false, let Tine set it to True if she exists
        tine_present = any(isinstance(c, Tine) for c in self.companions)
        if not tine_present and hasattr(self.huey, 'is_invincible'):
            self.huey.is_invincible = False
            
        self.companions.update(dt, enemies)

    def draw(self, screen):
        for c in self.companions:
            c.draw(screen)