"""
Power-up system for Breakout game.
"""

import pygame
import random
from config import (
    POWERUP_SPEED, POWERUP_DROP_CHANCE, POWERUP_DURATION,
    POWERUP_SLOW, POWERUP_FAST, POWERUP_BULLET,
    SCREEN_HEIGHT
)


class PowerUp(pygame.sprite.Sprite):
    """A falling power-up collectible."""
    
    TYPES = [POWERUP_SLOW, POWERUP_FAST, POWERUP_BULLET]
    
    def __init__(self, x, y, image, powerup_type=None):
        super().__init__()
        self.image = image
        self.rect = self.image.get_rect(center=(x, y))
        self.speed = POWERUP_SPEED
        
        # Random type if not specified
        self.powerup_type = powerup_type or random.choice(self.TYPES)
    
    def update(self, dt=0):
        """Move power-up downward."""
        self.rect.y += self.speed
        
        # Remove if off screen
        if self.rect.top > SCREEN_HEIGHT:
            self.kill()
    
    @staticmethod
    def should_spawn():
        """Determine if a power-up should spawn (random chance)."""
        return random.random() < POWERUP_DROP_CHANCE
    
    def get_duration(self):
        """Get the power-up duration in milliseconds."""
        return POWERUP_DURATION


class PowerUpManager:
    """Manages active power-ups and their effects."""
    
    def __init__(self):
        self.active_powerups = {}  # type -> end_time
        self.powerup_group = pygame.sprite.Group()
    
    def spawn_powerup(self, x, y, star_image):
        """Spawn a power-up at the given position."""
        if PowerUp.should_spawn():
            powerup = PowerUp(x, y, star_image)
            self.powerup_group.add(powerup)
            return powerup
        return None
    
    def update(self, dt, current_time):
        """Update all power-ups and check expirations."""
        self.powerup_group.update(dt)
        
        # Check for expired power-ups
        expired = []
        for ptype, end_time in self.active_powerups.items():
            if current_time >= end_time:
                expired.append(ptype)
        
        for ptype in expired:
            del self.active_powerups[ptype]
        
        return expired  # Return list of expired power-up types
    
    def activate(self, powerup_type, current_time, duration):
        """Activate a power-up effect."""
        self.active_powerups[powerup_type] = current_time + duration
    
    def is_active(self, powerup_type):
        """Check if a power-up type is currently active."""
        return powerup_type in self.active_powerups
    
    def get_active_type(self):
        """Get the currently active power-up type for display."""
        if POWERUP_BULLET in self.active_powerups:
            return POWERUP_BULLET
        elif POWERUP_SLOW in self.active_powerups:
            return POWERUP_SLOW
        elif POWERUP_FAST in self.active_powerups:
            return POWERUP_FAST
        return None
    
    def check_collision(self, paddle_rect, current_time):
        """Check for collision with paddle and return collected power-up."""
        for powerup in self.powerup_group:
            if powerup.rect.colliderect(paddle_rect):
                ptype = powerup.powerup_type
                duration = powerup.get_duration()
                self.activate(ptype, current_time, duration)
                powerup.kill()
                return ptype, duration
        return None, 0
    
    def draw(self, screen):
        """Draw all power-ups."""
        self.powerup_group.draw(screen)
    
    def clear(self):
        """Clear all power-ups."""
        self.powerup_group.empty()
        self.active_powerups.clear()
