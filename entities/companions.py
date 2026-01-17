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
        
        # Animation Variables
        self.anim_timer = 0
        self.blink_duration = 0.15  
        self.next_blink_time = random.uniform(2.0, 5.0) 
        self.is_blinking = False
        
        # Effect rotation for visual flares
        self.effect_rotation = 0

    def update_behavior(self, dt):
        self.life_timer -= dt
        self.effect_rotation += 180 * dt # Rotate 180 degrees per sec
        
        # Cleanup logic
        if self.life_timer <= 0:
            if isinstance(self, Tine) and hasattr(self.huey, 'is_invincible'):
                self.huey.is_invincible = False
            if isinstance(self, Cici) and hasattr(self.huey, 'heat_system'):
                self.huey.heat_system.apply_cici_boost(False)
            self.kill()

        # Follow distance logic
        offset_x = -80 
        if self.side == "TOP": offset_y = -110
        elif self.side == "BOTTOM": offset_y = 110
        else: offset_y = 0 
        
        target = pygame.Vector2(self.huey.rect.centerx + offset_x, 
                                self.huey.rect.centery + offset_y)
        
        self.hover_angle += 3 * dt
        target.y += math.sin(self.hover_angle) * 20
        self.pos += (target - self.pos) * 5 * dt
        self.rect.center = self.pos

    def draw_circular_flash(self, screen):
        """Visual feedback when the companion is about to expire."""
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
        for i in range(3):
            angle = math.radians(self.effect_rotation + (i * 120))
            dist = 45 + math.sin(pygame.time.get_ticks() * 0.005) * 5
            off_x = math.cos(angle) * dist
            off_y = math.sin(angle) * dist
            core_pos = (self.rect.centerx + off_x, self.rect.centery + off_y)
            pygame.draw.circle(screen, (255, 50, 50), core_pos, 6)
            pygame.draw.circle(screen, (255, 255, 255), core_pos, 3) 
            s = pygame.Surface((20, 20), pygame.SRCALPHA)
            pygame.draw.circle(s, (200, 0, 0, 100), (10, 10), 10)
            screen.blit(s, s.get_rect(center=core_pos), special_flags=pygame.BLEND_RGB_ADD)

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
            self.frame1 = pygame.image.load("assets/sprites/companions/tine_witch.png").convert_alpha()
            self.frame2 = pygame.image.load("assets/sprites/companions/tine_witchframe1.png").convert_alpha()
            self.image = self.frame1
        except:
            self.frame1 = pygame.Surface((50, 50), pygame.SRCALPHA)
            pygame.draw.circle(self.frame1, (150, 50, 255), (25, 25), 20)
            self.frame2 = self.frame1
            self.image = self.frame1

        try:
            self.bolt_img = pygame.image.load("assets/sprites/effects/lightning_bolt.png").convert_alpha()
            self.bolt_img = pygame.transform.scale(self.bolt_img, (40, 80)) 
        except: self.bolt_img = None

        try:
            self.zap_sfx = pygame.mixer.Sound("assets/sfx/tine_lightning.mp3")
            self.zap_sfx.set_volume(0.2)
        except: self.zap_sfx = None

        self.rect = self.image.get_rect()
        self.zap_timer = 0
        self.active_zaps = [] 
        self.aura_particles = [] 

    def update(self, dt, enemies):
        self.update_behavior(dt)
        self.animate(dt)
        self.zap_timer += dt
        self.huey.is_invincible = True
        
        if random.random() < 0.4:
            angle = random.uniform(0, math.pi * 2)
            dist = random.uniform(10, 45)
            self.aura_particles.append({
                'rel_pos': pygame.Vector2(math.cos(angle)*dist, math.sin(angle)*dist),
                'vel': pygame.Vector2(random.uniform(-10, 10), random.uniform(-20, -50)),
                'life': 1.0,
                'color': random.choice([(130, 50, 255), (180, 100, 255), (75, 0, 130)]),
                'size': random.randint(2, 5)
            })

        for p in self.aura_particles:
            p['rel_pos'] += p['vel'] * dt
            p['life'] -= dt * 1.2
        self.aura_particles = [p for p in self.aura_particles if p['life'] > 0]

        self.active_zaps = [z for z in self.active_zaps if z['life'] > 0]
        for z in self.active_zaps: z['life'] -= dt

        if self.zap_timer > 0.5:
            potential_targets = [e for e in enemies if pygame.Vector2(self.rect.center).distance_to(e.rect.center) < 700]
            if potential_targets:
                primary = min(potential_targets, key=lambda e: pygame.Vector2(self.rect.center).distance_to(e.rect.center))
                self.perform_chain_zap(primary, enemies)
                self.zap_timer = 0

    def animate(self, dt):
        self.anim_timer += dt
        if not self.is_blinking:
            if self.anim_timer >= self.next_blink_time:
                self.is_blinking, self.anim_timer, self.image = True, 0, self.frame2
        else:
            if self.anim_timer >= self.blink_duration:
                self.is_blinking, self.anim_timer, self.image = False, 0, self.frame1
                self.next_blink_time = random.uniform(2.0, 6.0)

    def perform_chain_zap(self, target, all_enemies):
        if hasattr(target, 'take_damage'):
            target.take_damage(35)
            self.create_zap_visual(pygame.Vector2(self.rect.center), pygame.Vector2(target.rect.center), target.rect.center)
            chain_target = next((e for e in all_enemies if e != target and pygame.Vector2(target.rect.center).distance_to(e.rect.center) < 250), None)
            if chain_target:
                chain_target.take_damage(15) 
                self.create_zap_visual(pygame.Vector2(target.rect.center), pygame.Vector2(chain_target.rect.center), chain_target.rect.center)
            if self.zap_sfx: self.zap_sfx.play()

    def create_zap_visual(self, start, end, target_pos):
        points = [start]
        for i in range(1, 4):
            points.append(start.lerp(end, i/4) + pygame.Vector2(random.randint(-15, 15), random.randint(-15, 15)))
        points.append(end)
        self.active_zaps.append({'points': points, 'life': 0.15, 'target_pos': target_pos})

    def draw(self, screen):
        for p in self.aura_particles:
            alpha = max(0, min(255, int(p['life'] * 255)))
            draw_pos = self.pos + p['rel_pos']
            glow = pygame.Surface((p['size']*4, p['size']*4), pygame.SRCALPHA)
            pygame.draw.circle(glow, (*p['color'], alpha // 2), (p['size']*2, p['size']*2), p['size']*2)
            screen.blit(glow, glow.get_rect(center=draw_pos), special_flags=pygame.BLEND_RGB_ADD)
            pygame.draw.circle(screen, (*p['color'], alpha), draw_pos, p['size'])

        shield_surf = pygame.Surface((250, 250), pygame.SRCALPHA)
        pulse = 30 + math.sin(pygame.time.get_ticks() * 0.01) * 10
        pygame.draw.circle(shield_surf, (75, 0, 130, int(pulse)), (125, 125), 110)
        pygame.draw.circle(shield_surf, (150, 100, 255, 80), (125, 125), 110, 2)
        screen.blit(shield_surf, shield_surf.get_rect(center=self.huey.rect.center))

        for zap in self.active_zaps:
            pygame.draw.lines(screen, (200, 200, 255), False, zap['points'], 3)
            if self.bolt_img:
                screen.blit(self.bolt_img, self.bolt_img.get_rect(center=zap['target_pos']))

        screen.blit(self.image, self.rect)
        self.draw_circular_flash(screen)

class Cici(Companion):
    def __init__(self, huey):
        super().__init__(huey, "BACK")
        self.life_timer = 10.0  
        try:
            self.frame1 = pygame.image.load("assets/sprites/companions/cici.png").convert_alpha()
            self.frame2 = pygame.image.load("assets/sprites/companions/cici_frame1.png").convert_alpha()
            self.image = self.frame1
        except:
            self.frame1 = pygame.Surface((45, 60), pygame.SRCALPHA)
            pygame.draw.ellipse(self.frame1, (255, 255, 200), (5, 5, 35, 50)) 
            self.frame2 = self.frame1
            self.image = self.frame1
            
        self.rect = self.image.get_rect()
        self.last_huey_hp = self.huey.health 
        self.burst_visuals = [] 
        self.particles = [] 
        
        # APPLY HEAT BUFF IMMEDIATELY
        if hasattr(self.huey, 'heat_system'):
            self.huey.heat_system.apply_cici_boost(True)

    def update(self, dt, enemies):
        self.update_behavior(dt)
        self.animate(dt)
        
        # Passive Heat Reduction while active
        if hasattr(self.huey, 'heat_system'):
            self.huey.heat_system.heat = max(0, self.huey.heat_system.heat - 20 * dt)
            
        # Passive Healing
        if self.huey.health < self.huey.max_health:
            self.huey.health += 3 * dt 
            if random.random() < 0.15: 
                self.spawn_particle(self.huey.rect.center, random.choice([(100, 200, 255), (255, 255, 150)]))
        
        # Defensive Burst if player takes damage
        if self.huey.health < self.last_huey_hp: 
            self.trigger_heal_burst(enemies)
            
        self.last_huey_hp = self.huey.health
        self.update_visual_effects(dt)

    def animate(self, dt):
        self.anim_timer += dt
        if not self.is_blinking:
            if self.anim_timer >= self.next_blink_time:
                self.is_blinking, self.anim_timer, self.image = True, 0, self.frame2
        else:
            if self.anim_timer >= self.blink_duration:
                self.is_blinking, self.anim_timer, self.image = False, 0, self.frame1
                self.next_blink_time = random.uniform(3.0, 7.0)

    def spawn_particle(self, pos, color):
        angle = random.uniform(0, math.pi * 2)
        speed = random.uniform(30, 70)
        self.particles.append({'pos': pygame.Vector2(pos), 'vel': pygame.Vector2(math.cos(angle)*speed, math.sin(angle)*speed), 'life': random.uniform(0.6, 1.2), 'color': color, 'size': random.randint(2, 4)})

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
        if random.random() < 0.2: self.spawn_particle(self.rect.center, (255, 230, 100))

    def trigger_heal_burst(self, enemies):
        self.burst_visuals.append({'radius': 10, 'alpha': 200})
        for _ in range(20): self.spawn_particle(self.huey.rect.center, (255, 255, 100))
        for e in enemies:
            if pygame.Vector2(self.huey.rect.center).distance_to(e.rect.center) < 250:
                if hasattr(e, 'take_damage'): e.take_damage(20)

    def draw(self, screen):
        circle_surf = pygame.Surface((120, 120), pygame.SRCALPHA)
        pygame.draw.circle(circle_surf, (255, 215, 0, 40), (60, 60), 55, 2)
        for i in range(8):
            angle = math.radians(self.effect_rotation + (i * 45))
            tx, ty = 60 + math.cos(angle)*55, 60 + math.sin(angle)*55
            pygame.draw.circle(circle_surf, (255, 255, 150, 100), (int(tx), int(ty)), 3)
        screen.blit(circle_surf, circle_surf.get_rect(center=self.rect.center))

        glow_size = int(self.huey.rect.width * 2.8)
        glow_surf = pygame.Surface((glow_size, glow_size), pygame.SRCALPHA)
        pulse = 15 + math.sin(pygame.time.get_ticks() * 0.005) * 8
        pygame.draw.ellipse(glow_surf, (40, 80, 200, int(pulse)), glow_surf.get_rect())
        screen.blit(glow_surf, glow_surf.get_rect(center=self.huey.rect.center), special_flags=pygame.BLEND_RGB_ADD)

        for p in self.particles:
            alpha = max(0, min(255, int(p['life'] * 255)))
            p_surf = pygame.Surface((p['size']*2, p['size']*2), pygame.SRCALPHA)
            pygame.draw.circle(p_surf, (*p['color'], alpha), (p['size'], p['size']), p['size'])
            screen.blit(p_surf, p['pos'])

        for b in self.burst_visuals:
            s = pygame.Surface((int(b['radius']*2), int(b['radius']*2)), pygame.SRCALPHA)
            pygame.draw.circle(s, (255, 215, 0, max(0, int(b['alpha']))), (int(b['radius']), int(b['radius'])), int(b['radius']), 3)
            screen.blit(s, s.get_rect(center=self.huey.rect.center))

        screen.blit(self.image, self.rect)
        self.draw_circular_flash(screen)

    def update_behavior(self, dt):
        """Cici hovers behind the player."""
        self.life_timer -= dt
        self.effect_rotation += 180 * dt
        
        if self.life_timer <= 0:
            if hasattr(self.huey, 'heat_system'):
                self.huey.heat_system.apply_cici_boost(False)
            self.kill()

        target = pygame.Vector2(self.huey.rect.left - 60, self.huey.rect.centery)
        self.hover_angle += 2 * dt
        target.y += math.sin(self.hover_angle) * 15
        self.pos += (target - self.pos) * 4 * dt
        self.rect.center = self.pos

class CompanionManager:
    def __init__(self, huey):
        self.huey, self.companions = huey, pygame.sprite.Group()

    def summon(self, comp_type):
        # Prevent duplicates
        if any(isinstance(c, Red) for c in self.companions) and comp_type == "RED": return
        if any(isinstance(c, Tine) for c in self.companions) and comp_type == "TINE": return
        if any(isinstance(c, Cici) for c in self.companions) and comp_type == "CICI": return
        
        mapping = {"RED": Red, "TINE": Tine, "CICI": Cici}
        if comp_type in mapping: self.companions.add(mapping[comp_type](self.huey))

    def update(self, dt, enemies):
        # Safety check for invincibility
        if not any(isinstance(c, Tine) for c in self.companions) and hasattr(self.huey, 'is_invincible'):
            self.huey.is_invincible = False
            
        self.companions.update(dt, enemies)

    def draw(self, screen):
        for c in self.companions: c.draw(screen)