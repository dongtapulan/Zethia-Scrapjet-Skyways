import pygame
from settings import WIDTH, HEIGHT, GROUND_LINE

class ParallaxLayer:
    def __init__(self, image_path, internal_speed, y_pos=0, initial_alpha=0, fade_speed=60, is_ground=False):
        self.image = pygame.image.load(image_path).convert_alpha()
        self.width = self.image.get_width()
        self.height = self.image.get_height()
        
        self.internal_speed = internal_speed 
        self.is_ground = is_ground
        
        # ANCHOR FIX: If it's ground, it MUST start at GROUND_LINE
        # Otherwise, use the provided y_pos
        self.y_pos = GROUND_LINE if is_ground else y_pos
            
        self.x = 0
        self.alpha = initial_alpha
        self.fade_speed = fade_speed
        self.image.set_alpha(self.alpha)

    def update(self, dt):
        if self.alpha < 255:
            self.alpha = min(255, self.alpha + (self.fade_speed * dt))
            self.image.set_alpha(int(self.alpha))

        # Autonomous movement
        self.x -= self.internal_speed * dt
        
        # Reset x to keep it within the bounds of the image width for seamless tiling
        if self.x <= -self.width:
            self.x += self.width

    def draw(self, screen):
        # Calculate how many tiles we need to cover the screen width
        # This handles cases where the image is narrower than the screen
        tiles = (WIDTH // self.width) + 2
        for i in range(tiles):
            screen.blit(self.image, (self.x + (i * self.width), self.y_pos))

class ParallaxBackground:
    def __init__(self):
        # Layer 1: Distant Clouds (Slowest)
        self.clouds = ParallaxLayer("assets/backgrounds/cloud.png", 
                                   internal_speed=15, y_pos=30, initial_alpha=255)
        
        # Layer 2: Mountains (Mid-speed, lowered y_pos to meet the ground)
        # Positioned at 300 to ensure it overlaps with the ground line
        self.mountains = ParallaxLayer("assets/backgrounds/mountain.png", 
                                      internal_speed=50, y_pos=300, initial_alpha=0)
        
        # Layer 3: The Ground (Fastest, anchored to GROUND_LINE)
        self.ground = ParallaxLayer("assets/backgrounds/ground.png", 
                                   internal_speed=200, is_ground=True, initial_alpha=255)

    def update(self, unused_speed, dt):
        self.clouds.update(dt)
        self.mountains.update(dt)
        self.ground.update(dt)

    def draw(self, screen):
        self.clouds.draw(screen)
        self.mountains.draw(screen)
        self.ground.draw(screen)