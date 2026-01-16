import pygame
import random
import math
from settings import WIDTH, HEIGHT

class Companion(pygame.sprite.Sprite):
    def __init__(self, huey, side="TOP"):
        super().__init__()
        self.huey = huey
        self.side = side
        self.life_timer = 12.0  
        self.pos = pygame.Vector2(huey.rect.center)
        self.hover_angle = random.uniform(0, math.pi * 2)
        
    def update_behavior(self, dt):
        self.life_timer -= dt
        if self.life_timer <= 0:
            if hasattr(self.huey, 'is_invincible'):
                self.huey.is_invincible = False
            self.kill()

        # Movement Logic
        offset_x = -80 
        if self.side == "TOP": offset_y = -110
        elif self.side == "BOTTOM": offset_y = 110
        else: offset_y = 0 # For "BACK" side
        
        target = pygame.Vector2(self.huey.rect.centerx + offset_x, 
                                self.huey.rect.centery + offset_y)
        
        self.hover_angle += 3 * dt
        target.y += math.sin(self.hover_angle) * 20
        self.pos += (target - self.pos) * 5 * dt
        self.rect.center = self.pos

    def draw_circular_flash(self, screen):
        if self.life_timer < 1.0:
            alpha = int(self.life_timer * 255) 
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
                self.attack_cooldown = 0.8 

    def find_target(self, enemies):
        visible = [e for e in enemies if 50 < e.rect.x < WIDTH]
        return min(visible, key=lambda e: e.rect.x) if visible else None

    def fire_railgun(self, target):
        self.lasers.append({'start': self.rect.center, 'end': target.rect.center, 'life': 0.2})
        if self.shoot_sfx: self.shoot_sfx.play()
        if hasattr(target, 'take_damage'): target.take_damage(60)

    def draw(self, screen):
        for laser in self.lasers:
            thickness = int(laser['life'] * 25)
            pygame.draw.line(screen, (255, 0, 0), laser['start'], laser['end'], thickness)
            pygame.draw.line(screen, (255, 255, 255), laser['start'], laser['end'], thickness // 2)
        screen.blit(self.image, self.rect)
        self.draw_circular_flash(screen)

class Tine(Companion):
    def __init__(self, huey):
        super().__init__(huey, "BOTTOM")
        try:
            self.image = pygame.image.load("assets/sprites/companions/tine_witch.png").convert_alpha()
        except:
            self.image = pygame.Surface((50, 50), pygame.SRCALPHA)
            pygame.draw.circle(self.image, (150, 50, 255), (25, 25), 20)

        # Re-loading the lightning bolt asset
        try:
            self.bolt_img = pygame.image.load("assets/sprites/effects/lightning_bolt.png").convert_alpha()
            # Scale it down slightly so it fits the enemies better
            self.bolt_img = pygame.transform.scale(self.bolt_img, (40, 80)) 
        except:
            self.bolt_img = None

        try:
            self.zap_sfx = pygame.mixer.Sound("assets/sfx/tine_lightning.mp3")
            self.zap_sfx.set_volume(0.2)
        except:
            self.zap_sfx = None

        self.rect = self.image.get_rect()
        self.zap_timer = 0
        self.active_zaps = [] 

    def update(self, dt, enemies):
        self.update_behavior(dt)
        self.zap_timer += dt
        self.huey.is_invincible = True
        
        self.active_zaps = [z for z in self.active_zaps if z['life'] > 0]
        for z in self.active_zaps: z['life'] -= dt

        if self.zap_timer > 0.5:
            potential_targets = [e for e in enemies if pygame.Vector2(self.rect.center).distance_to(e.rect.center) < 700]
            if potential_targets:
                primary = min(potential_targets, key=lambda e: pygame.Vector2(self.rect.center).distance_to(e.rect.center))
                self.perform_chain_zap(primary, enemies)
                self.zap_timer = 0

    def perform_chain_zap(self, target, all_enemies):
        if hasattr(target, 'take_damage'):
            target.take_damage(35)
            # Added target_pos to the zap data for the bolt drawing
            self.create_zap_visual(pygame.Vector2(self.rect.center), pygame.Vector2(target.rect.center), target.rect.center)
            
            chain_target = None
            for e in all_enemies:
                if e != target:
                    dist = pygame.Vector2(target.rect.center).distance_to(e.rect.center)
                    if dist < 250:
                        chain_target = e
                        break
            
            if chain_target:
                chain_target.take_damage(15) 
                self.create_zap_visual(pygame.Vector2(target.rect.center), pygame.Vector2(chain_target.rect.center), chain_target.rect.center)

            if self.zap_sfx: self.zap_sfx.play()

    def create_zap_visual(self, start, end, target_pos):
        points = [start]
        mid_points = 3
        for i in range(1, mid_points + 1):
            fraction = i / (mid_points + 1)
            base = start.lerp(end, fraction)
            offset = pygame.Vector2(random.randint(-15, 15), random.randint(-15, 15))
            points.append(base + offset)
        points.append(end)
        # We store 'target_pos' so the draw method knows where to put the bolt sprite
        self.active_zaps.append({'points': points, 'life': 0.15, 'target_pos': target_pos})

    def draw(self, screen):
        shield_surf = pygame.Surface((250, 250), pygame.SRCALPHA)
        pulse = 30 + math.sin(pygame.time.get_ticks() * 0.01) * 10
        pygame.draw.circle(shield_surf, (75, 0, 130, int(pulse)), (125, 125), 110)
        pygame.draw.circle(shield_surf, (150, 100, 255, 80), (125, 125), 110, 2)
        screen.blit(shield_surf, shield_surf.get_rect(center=self.huey.rect.center))

        for zap in self.active_zaps:
            # Draw the electricity lines
            pygame.draw.lines(screen, (200, 200, 255), False, zap['points'], 3)
            pygame.draw.lines(screen, (255, 255, 255), False, zap['points'], 1)
            
            # Draw the bolt sprite at the impact point
            if self.bolt_img:
                bolt_rect = self.bolt_img.get_rect(center=zap['target_pos'])
                # Add a little jitter for the lightning effect
                bolt_rect.x += random.randint(-5, 5)
                screen.blit(self.bolt_img, bolt_rect)

        screen.blit(self.image, self.rect)
        self.draw_circular_flash(screen)

class Cici(Companion):
    def __init__(self, huey):
        super().__init__(huey, "BACK")
        self.life_timer = 10.0  
        try:
            self.image = pygame.image.load("assets/sprites/companions/cici.png").convert_alpha()
        except:
            self.image = pygame.Surface((45, 60), pygame.SRCALPHA)
            pygame.draw.ellipse(self.image, (255, 255, 200), (5, 5, 35, 50)) 
            
        self.rect = self.image.get_rect()
        self.last_huey_hp = self.huey.health 
        self.burst_visuals = [] 
        self.particles = [] 
        
        if hasattr(self.huey, 'heat_system'):
            self.original_cool_rate = self.huey.heat_system.base_cool_rate
            # NERF: Lowered to 80.0 so heat still builds during heavy firing
            self.huey.heat_system.base_cool_rate = 80.0 
        else:
            self.original_cool_rate = 35

    def update(self, dt, enemies):
        self.update_behavior(dt)
        
        # 1. Heat Drain NERF: Lowered to -20 per second (gentle cooling)
        if hasattr(self.huey, 'heat_system'):
            self.huey.heat_system.heat = max(0, self.huey.heat_system.heat - 20 * dt)
            
        # 2. Passive Auto-Heal
        if self.huey.health < self.huey.max_health:
            self.huey.health += 3 * dt 
            # Blue and Yellow motes
            if random.random() < 0.15:
                color = random.choice([(100, 200, 255), (255, 255, 150)])
                self.spawn_particle(self.huey.rect.center, color)

        # 3. Heal Burst Logic
        if self.huey.health < self.last_huey_hp:
            self.trigger_heal_burst(enemies)
        self.last_huey_hp = self.huey.health

        self.update_visual_effects(dt)

    def spawn_particle(self, pos, color):
        angle = random.uniform(0, math.pi * 2)
        speed = random.uniform(30, 70)
        self.particles.append({
            'pos': pygame.Vector2(pos),
            'vel': pygame.Vector2(math.cos(angle) * speed, math.sin(angle) * speed),
            'life': random.uniform(0.6, 1.2),
            'color': color,
            'size': random.randint(2, 4)
        })

    def update_visual_effects(self, dt):
        for b in self.burst_visuals:
            b['radius'] += 400 * dt
            b['alpha'] -= 500 * dt
        self.burst_visuals = [b for b in self.burst_visuals if b['alpha'] > 0]

        for p in self.particles:
            p['pos'] += p['vel'] * dt
            p['life'] -= dt
            p['vel'] *= 0.95 
        self.particles = [p for p in self.particles if p['life'] > 0]

        if random.random() < 0.2:
            self.spawn_particle(self.rect.center, (255, 230, 100))

    def trigger_heal_burst(self, enemies):
        self.burst_visuals.append({'radius': 10, 'alpha': 200})
        burst_range = 250
        for _ in range(20):
            self.spawn_particle(self.huey.rect.center, (255, 255, 100))
            
        for e in enemies:
            if pygame.Vector2(self.huey.rect.center).distance_to(e.rect.center) < burst_range:
                if hasattr(e, 'take_damage'):
                    e.take_damage(20)

    def draw(self, screen):
        # 1. Fainter Blue Glow with Gold Accent
        glow_size = int(self.huey.rect.width * 2.8)
        glow_surf = pygame.Surface((glow_size, glow_size), pygame.SRCALPHA)
        pulse = 15 + math.sin(pygame.time.get_ticks() * 0.005) * 8
        
        # Outer Blue (Faint)
        pygame.draw.ellipse(glow_surf, (40, 80, 200, int(pulse)), glow_surf.get_rect())
        # Inner Gold Ring Accent
        inner_rect = glow_surf.get_rect().inflate(-glow_size*0.4, -glow_size*0.4)
        pygame.draw.ellipse(glow_surf, (255, 215, 0, int(pulse * 1.5)), inner_rect, 2)
        
        screen.blit(glow_surf, glow_surf.get_rect(center=self.huey.rect.center), special_flags=pygame.BLEND_RGB_ADD)

        # 2. Draw Yellow and Blue Particles (FIXED COLOR ARGUMENT)
        for p in self.particles:
            # Safety check for alpha to prevent ValueError
            alpha = max(0, min(255, int(p['life'] * 255)))
            p_surf = pygame.Surface((p['size']*2, p['size']*2), pygame.SRCALPHA)
            # Use the protected alpha value
            pygame.draw.circle(p_surf, (*p['color'], alpha), (p['size'], p['size']), p['size'])
            screen.blit(p_surf, p['pos'])

        # 3. Draw Burst Visuals
        for b in self.burst_visuals:
            b_alpha = max(0, min(255, int(b['alpha'])))
            s = pygame.Surface((int(b['radius']*2), int(b['radius']*2)), pygame.SRCALPHA)
            pygame.draw.circle(s, (255, 215, 0, b_alpha), (int(b['radius']), int(b['radius'])), int(b['radius']), 3)
            screen.blit(s, s.get_rect(center=self.huey.rect.center))

        screen.blit(self.image, self.rect)
        self.draw_circular_flash(screen)

    def update_behavior(self, dt):
        self.life_timer -= dt
        if self.life_timer <= 0:
            if hasattr(self.huey, 'heat_system'):
                self.huey.heat_system.base_cool_rate = self.original_cool_rate
            self.kill()

        target = pygame.Vector2(self.huey.rect.left - 60, self.huey.rect.centery)
        self.hover_angle += 2 * dt
        target.y += math.sin(self.hover_angle) * 15
        self.pos += (target - self.pos) * 4 * dt
        self.rect.center = self.pos

class CompanionManager:
    def __init__(self, huey):
        self.huey = huey
        self.companions = pygame.sprite.Group()

    def summon(self, companion_type):
        # Check if already active
        for c in self.companions:
            if isinstance(c, Red) and companion_type == "RED": return
            if isinstance(c, Tine) and companion_type == "TINE": return
            if isinstance(c, Cici) and companion_type == "CICI": return

        if companion_type == "RED":
            self.companions.add(Red(self.huey))
        elif companion_type == "TINE":
            self.companions.add(Tine(self.huey))
        elif companion_type == "CICI":
            self.companions.add(Cici(self.huey))

    def update(self, dt, enemies):
        tine_present = any(isinstance(c, Tine) for c in self.companions)
        if not tine_present and hasattr(self.huey, 'is_invincible'):
            self.huey.is_invincible = False
            
        self.companions.update(dt, enemies)

    def draw(self, screen):
        for c in self.companions:
            c.draw(screen)