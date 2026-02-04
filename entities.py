"""
Game entities for Breakout: Ball, Paddle, Brick, Particle, and Bullet.
"""

import pygame
import random
import math
from config import (
    SCREEN_WIDTH, SCREEN_HEIGHT, PADDLE_Y, PADDLE_SPEED,
    BALL_SPEED_INITIAL, BALL_SPEED_MIN, BALL_SPEED_MAX,
    BRICK_WIDTH, BRICK_HEIGHT, BRICK_HEALTH_NORMAL,
    SCORE_VALUES, PARTICLE_SPEED, PARTICLE_LIFETIME, PARTICLE_GRAVITY,
    BULLET_SPEED, SLOW_MULTIPLIER, FAST_MULTIPLIER,
    PADDLE_SCORE_DISPLAY_TIME
)


class Ball(pygame.sprite.Sprite):
    """The game ball with physics and collision handling."""
    
    def __init__(self, x, y, image):
        super().__init__()
        self.image = image
        self.rect = self.image.get_rect(center=(x, y))
        self.base_speed = BALL_SPEED_INITIAL
        self.speed = self.base_speed
        self.speed_multiplier = 1.0
        
        # Start with random angle upward
        angle = random.uniform(-60, 60)  # degrees from vertical
        rad = math.radians(angle - 90)  # Convert to radians, -90 for upward
        self.velocity = pygame.math.Vector2(
            math.cos(rad) * self.speed,
            math.sin(rad) * self.speed
        )
        
        self.active = False  # Ball attached to paddle until launched
    
    def update(self, paddle_rect=None):
        """Update ball position and handle wall collisions."""
        if not self.active:
            # Ball follows paddle
            if paddle_rect:
                self.rect.centerx = paddle_rect.centerx
                self.rect.bottom = paddle_rect.top - 5
            return
        
        # Apply speed multiplier
        current_speed = self.speed * self.speed_multiplier
        if self.velocity.length() > 0:
            self.velocity = self.velocity.normalize() * current_speed
        
        # Move ball
        self.rect.x += self.velocity.x
        self.rect.y += self.velocity.y
        
        # Wall collisions
        if self.rect.left <= 0:
            self.rect.left = 0
            self.velocity.x = abs(self.velocity.x)
        elif self.rect.right >= SCREEN_WIDTH:
            self.rect.right = SCREEN_WIDTH
            self.velocity.x = -abs(self.velocity.x)
        
        if self.rect.top <= 0:
            self.rect.top = 0
            self.velocity.y = abs(self.velocity.y)
    
    def launch(self):
        """Launch the ball."""
        self.active = True
        angle = random.uniform(-45, 45)
        rad = math.radians(angle - 90)
        self.velocity = pygame.math.Vector2(
            math.cos(rad) * self.speed,
            math.sin(rad) * self.speed
        )
    
    def collide_paddle(self, paddle_rect):
        """Handle paddle collision with angle reflection."""
        if self.rect.colliderect(paddle_rect) and self.velocity.y > 0:
            # Calculate hit position relative to paddle center (-1 to 1)
            relative_hit = (self.rect.centerx - paddle_rect.centerx) / (paddle_rect.width / 2)
            relative_hit = max(-1, min(1, relative_hit))  # Clamp
            
            # Calculate reflection angle (max 60 degrees from vertical)
            angle = relative_hit * 60
            rad = math.radians(angle - 90)
            
            current_speed = self.velocity.length()
            self.velocity = pygame.math.Vector2(
                math.cos(rad) * current_speed,
                math.sin(rad) * current_speed
            )
            
            # Ensure ball is above paddle
            self.rect.bottom = paddle_rect.top - 1
            return True
        return False
    
    def is_out(self):
        """Check if ball fell off screen."""
        return self.rect.top > SCREEN_HEIGHT
    
    def reset(self, paddle_rect):
        """Reset ball to paddle."""
        self.active = False
        self.rect.centerx = paddle_rect.centerx
        self.rect.bottom = paddle_rect.top - 5
        self.speed_multiplier = 1.0
    
    def set_slow(self):
        """Apply slow effect."""
        self.speed_multiplier = SLOW_MULTIPLIER
    
    def set_fast(self):
        """Apply fast effect."""
        self.speed_multiplier = FAST_MULTIPLIER
    
    def reset_speed(self):
        """Reset to normal speed."""
        self.speed_multiplier = 1.0


class Paddle(pygame.sprite.Sprite):
    """The player-controlled paddle."""
    
    def __init__(self, x, y, assets):
        super().__init__()
        self.assets = assets
        self.image = assets.paddle_default
        self.rect = self.image.get_rect(center=(x, y))
        
        self.speed = PADDLE_SPEED
        
        # Score display state
        self.score_display = None
        self.score_display_timer = 0
        
        # Power-up state
        self.active_powerup = None
        self.powerup_timer = 0
    
    def update(self, dt=0):
        """Update paddle based on mouse position."""
        mouse_x = pygame.mouse.get_pos()[0]
        
        # Smoothly follow mouse
        target_x = mouse_x
        dx = target_x - self.rect.centerx
        
        # Move towards target
        if abs(dx) > self.speed:
            self.rect.centerx += self.speed if dx > 0 else -self.speed
        else:
            self.rect.centerx = target_x
        
        # Keep paddle on screen
        if self.rect.left < 0:
            self.rect.left = 0
        elif self.rect.right > SCREEN_WIDTH:
            self.rect.right = SCREEN_WIDTH
        
        # Update score display timer
        if self.score_display is not None:
            self.score_display_timer -= dt
            if self.score_display_timer <= 0:
                self.score_display = None
        
        # Update power-up timer
        if self.active_powerup is not None:
            self.powerup_timer -= dt
            if self.powerup_timer <= 0:
                self.active_powerup = None
        
        # Update sprite
        self._update_sprite()
    
    def _update_sprite(self):
        """Update paddle sprite based on state."""
        self.image = self.assets.get_paddle_sprite(
            score_display=self.score_display,
            powerup=self.active_powerup
        )
    
    def show_score(self, score):
        """Display score on paddle temporarily."""
        if score >= 500:
            self.score_display = 500
        elif score >= 250:
            self.score_display = 250
        elif score >= 100:
            self.score_display = 100
        else:
            self.score_display = None
        self.score_display_timer = PADDLE_SCORE_DISPLAY_TIME
    
    def activate_powerup(self, powerup_type, duration):
        """Activate a power-up."""
        self.active_powerup = powerup_type
        self.powerup_timer = duration


class Brick(pygame.sprite.Sprite):
    """A destructible brick."""
    
    def __init__(self, x, y, brick_type, assets):
        super().__init__()
        self.brick_type = brick_type
        self.assets = assets
        self.health = BRICK_HEALTH_NORMAL
        
        self.image = assets.get_brick_sprite(brick_type, is_cracked=False)
        self.rect = self.image.get_rect(topleft=(x, y))
        
        self.score = SCORE_VALUES[brick_type] if brick_type < len(SCORE_VALUES) else 50
    
    def hit(self):
        """
        Handle brick being hit.
        Returns True if brick is destroyed, False otherwise.
        """
        self.health -= 1
        
        if self.health <= 0:
            return True  # Destroyed
        else:
            # Show cracked version
            self.image = self.assets.get_brick_sprite(self.brick_type, is_cracked=True)
            return False
    
    def get_particle_type(self):
        """Get the particle type for this brick."""
        return self.brick_type


class Particle(pygame.sprite.Sprite):
    """Particle effect for brick destruction."""
    
    def __init__(self, x, y, image):
        super().__init__()
        self.original_image = image
        self.image = image
        self.rect = self.image.get_rect(center=(x, y))
        
        # Random velocity
        angle = random.uniform(0, 360)
        speed = random.uniform(2, PARTICLE_SPEED)
        self.velocity = pygame.math.Vector2(
            math.cos(math.radians(angle)) * speed,
            math.sin(math.radians(angle)) * speed
        )
        
        self.lifetime = PARTICLE_LIFETIME
        self.age = 0
        self.alpha = 255
    
    def update(self, dt):
        """Update particle position and fade."""
        self.age += dt
        
        if self.age >= self.lifetime:
            self.kill()
            return
        
        # Apply gravity
        self.velocity.y += PARTICLE_GRAVITY
        
        # Move
        self.rect.x += self.velocity.x
        self.rect.y += self.velocity.y
        
        # Fade out
        progress = self.age / self.lifetime
        self.alpha = int(255 * (1 - progress))
        
        # Apply alpha
        self.image = self.original_image.copy()
        self.image.set_alpha(self.alpha)


class Bullet(pygame.sprite.Sprite):
    """Projectile for Super Bullet power-up."""
    
    def __init__(self, x, y, image):
        super().__init__()
        self.image = image
        self.rect = self.image.get_rect(center=(x, y))
        self.speed = BULLET_SPEED
    
    def update(self, dt=0):
        """Move bullet upward."""
        self.rect.y -= self.speed
        
        # Remove if off screen
        if self.rect.bottom < 0:
            self.kill()
