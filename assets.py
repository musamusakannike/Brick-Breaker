"""
Asset Manager for Breakout game.
Handles loading and caching all game sprites.
"""

import pygame
import os
from config import (
    BRICK_WIDTH, BRICK_HEIGHT, BALL_SIZE, PADDLE_WIDTH, PADDLE_HEIGHT,
    PARTICLE_SIZE, HEART_SIZE, POWERUP_SIZE
)


class AssetManager:
    """Centralized asset loading and management."""
    
    def __init__(self):
        self.sprites_dir = os.path.join(os.path.dirname(__file__), "Sprites")
        
        # Brick sprites: 10 types, each with complete and cracked versions
        self.bricks_complete = []  # Indices 0-9 for brick types
        self.bricks_cracked = []   # Corresponding cracked versions
        
        # Particle sprites for each brick type
        self.particles = []
        
        # Paddle sprites
        self.paddle_default = None      # +50 (asset 31)
        self.paddle_100_anim = []       # Animation frames (assets 32-37)
        self.paddle_100 = None          # +100 centered (asset 38)
        self.paddle_250 = None          # +250 (asset 39)
        self.paddle_500 = None          # +500 (asset 40)
        self.paddle_slow = None         # Slow indicator (asset 41)
        self.paddle_fast = None         # Fast indicator (asset 42)
        self.paddle_bullet = None       # Super bullet (asset 48)
        
        # Other sprites
        self.ball = None
        self.heart = None
        self.star = None
        self.bullet = None
        
        self._load_all_assets()
    
    def _load_sprite(self, filename, scale_to=None):
        """Load a single sprite and optionally scale it."""
        path = os.path.join(self.sprites_dir, filename)
        try:
            image = pygame.image.load(path).convert_alpha()
            if scale_to:
                image = pygame.transform.smoothscale(image, scale_to)
            return image
        except pygame.error as e:
            print(f"Error loading {filename}: {e}")
            # Return a placeholder surface
            surface = pygame.Surface(scale_to or (32, 32))
            surface.fill((255, 0, 255))  # Magenta for missing textures
            return surface
    
    def _load_all_assets(self):
        """Load all game assets."""
        # Load bricks (assets 1-20)
        # Odd numbers are complete, even are cracked
        for i in range(10):
            complete_idx = i * 2 + 1
            cracked_idx = i * 2 + 2
            
            complete_img = self._load_sprite(
                f"{complete_idx:02d}-Breakout-Tiles.png",
                (BRICK_WIDTH, BRICK_HEIGHT)
            )
            cracked_img = self._load_sprite(
                f"{cracked_idx:02d}-Breakout-Tiles.png",
                (BRICK_WIDTH, BRICK_HEIGHT)
            )
            
            self.bricks_complete.append(complete_img)
            self.bricks_cracked.append(cracked_img)
        
        # Load particles (assets 21-30)
        for i in range(21, 31):
            particle_img = self._load_sprite(
                f"{i:02d}-Breakout-Tiles.png",
                (PARTICLE_SIZE, PARTICLE_SIZE)
            )
            self.particles.append(particle_img)
        
        # Load paddle sprites
        paddle_size = (PADDLE_WIDTH, PADDLE_HEIGHT)
        
        self.paddle_default = self._load_sprite("31-Breakout-Tiles.png", paddle_size)
        
        # +100 animation frames (32-37)
        for i in range(32, 38):
            frame = self._load_sprite(f"{i:02d}-Breakout-Tiles.png", paddle_size)
            self.paddle_100_anim.append(frame)
        
        self.paddle_100 = self._load_sprite("38-Breakout-Tiles.png", paddle_size)
        self.paddle_250 = self._load_sprite("39-Breakout-Tiles.png", paddle_size)
        self.paddle_500 = self._load_sprite("40-Breakout-Tiles.png", paddle_size)
        self.paddle_slow = self._load_sprite("41-Breakout-Tiles.png", paddle_size)
        self.paddle_fast = self._load_sprite("42-Breakout-Tiles.png", paddle_size)
        self.paddle_bullet = self._load_sprite("48-Breakout-Tiles.png", paddle_size)
        
        # Load other sprites
        self.ball = self._load_sprite("ball.png", (BALL_SIZE, BALL_SIZE))
        self.heart = self._load_sprite("heart.png", (HEART_SIZE, HEART_SIZE))
        self.star = self._load_sprite("star.png", (POWERUP_SIZE, POWERUP_SIZE))
        self.bullet = self._load_sprite("vertical-bullet.png", (19, 41))
    
    def get_brick_sprite(self, brick_type, is_cracked=False):
        """Get the appropriate brick sprite."""
        if is_cracked:
            return self.bricks_cracked[brick_type]
        return self.bricks_complete[brick_type]
    
    def get_particle_sprite(self, brick_type):
        """Get the particle sprite for a brick type."""
        return self.particles[brick_type]
    
    def get_paddle_sprite(self, score_display=None, powerup=None):
        """Get the appropriate paddle sprite based on state."""
        if powerup == "slow":
            return self.paddle_slow
        elif powerup == "fast":
            return self.paddle_fast
        elif powerup == "bullet":
            return self.paddle_bullet
        elif score_display == 500:
            return self.paddle_500
        elif score_display == 250:
            return self.paddle_250
        elif score_display == 100:
            return self.paddle_100
        return self.paddle_default
