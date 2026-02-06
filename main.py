"""
Breakout Game - Main Entry Point
A fully-featured Brick Breaker game with power-ups and particle effects.
"""

import pygame
import sys
from config import (
    SCREEN_WIDTH, SCREEN_HEIGHT, FPS, TITLE,
    BLACK, WHITE, DARK_GRAY, NEON_BLUE, NEON_PINK,
    PADDLE_Y, INITIAL_LIVES, HEART_SPACING, HEART_Y, HEART_SIZE,
    PARTICLE_COUNT, BULLET_COOLDOWN,
    STATE_MENU, STATE_PLAYING, STATE_PAUSED, STATE_GAME_OVER,
    STATE_LEVEL_COMPLETE, STATE_WIN,
    POWERUP_SLOW, POWERUP_FAST, POWERUP_BULLET
)
from assets import AssetManager
from entities import Ball, Paddle, Particle, Bullet
from powerups import PowerUpManager
from levels import LevelManager


class Game:
    """Main game class."""
    
    def __init__(self):
        pygame.init()
        pygame.mixer.init()
        
        self.screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
        pygame.display.set_caption(TITLE)
        
        self.clock = pygame.time.Clock()
        self.running = True
        self.fullscreen = False
        
        # Load assets
        self.assets = AssetManager()
        
        # Start background music
        if self.assets.bg_music:
            try:
                pygame.mixer.music.load(self.assets.bg_music)
                pygame.mixer.music.play(-1)  # Loop indefinitely
                pygame.mixer.music.set_volume(0.5)  # Set volume to 50%
            except pygame.error as e:
                print(f"Error playing music: {e}")
        
        # Initialize managers
        self.level_manager = LevelManager(self.assets)
        self.powerup_manager = PowerUpManager()
        
        # Fonts
        self.font_large = pygame.font.Font(None, 72)
        self.font_medium = pygame.font.Font(None, 48)
        self.font_small = pygame.font.Font(None, 36)
        
        # Game state
        self.state = STATE_MENU
        self.score = 0
        self.lives = INITIAL_LIVES
        self.combo = 0
        
        # Sprite groups
        self.all_sprites = pygame.sprite.Group()
        self.bricks = pygame.sprite.Group()
        self.particles = pygame.sprite.Group()
        self.bullets = pygame.sprite.Group()
        
        # Game objects
        self.paddle = None
        self.ball = None
        
        # Bullet timing
        self.last_bullet_time = 0
        
        # Background
        self.bg_surface = self._create_background()
    
    def _create_background(self):
        """Create a gradient background."""
        surface = pygame.Surface((SCREEN_WIDTH, SCREEN_HEIGHT))
        for y in range(SCREEN_HEIGHT):
            # Gradient from dark top to slightly lighter bottom
            ratio = y / SCREEN_HEIGHT
            color = (
                int(20 + 15 * ratio),
                int(20 + 15 * ratio),
                int(35 + 20 * ratio)
            )
            pygame.draw.line(surface, color, (0, y), (SCREEN_WIDTH, y))
        return surface
    
    def _toggle_fullscreen(self):
        """Toggle between fullscreen and windowed mode."""
        self.fullscreen = not self.fullscreen
        if self.fullscreen:
            self.screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT), pygame.FULLSCREEN)
        else:
            self.screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))

    
    def new_game(self):
        """Start a new game."""
        self.score = 0
        self.lives = INITIAL_LIVES
        self.combo = 0
        self.level_manager.reset()
        self.powerup_manager.clear()
        self._setup_level()
        self.state = STATE_PLAYING
    
    def _setup_level(self):
        """Set up the current level."""
        # Clear existing sprites
        self.all_sprites.empty()
        self.bricks.empty()
        self.particles.empty()
        self.bullets.empty()
        self.powerup_manager.clear()
        
        # Create paddle
        self.paddle = Paddle(SCREEN_WIDTH // 2, PADDLE_Y, self.assets)
        self.all_sprites.add(self.paddle)
        
        # Create ball
        self.ball = Ball(
            SCREEN_WIDTH // 2,
            PADDLE_Y - 30,
            self.assets.ball
        )
        self.all_sprites.add(self.ball)
        
        # Load bricks for current level
        bricks = self.level_manager.get_level_bricks()
        for brick in bricks:
            self.bricks.add(brick)
            self.all_sprites.add(brick)
    
    def run(self):
        """Main game loop."""
        while self.running:
            dt = self.clock.tick(FPS)
            current_time = pygame.time.get_ticks()
            
            self._handle_events()
            self._update(dt, current_time)
            self._draw()
            
            pygame.display.flip()
        
        pygame.quit()
        sys.exit()
    
    def _handle_events(self):
        """Handle input events."""
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                self.running = False
            
            elif event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE:
                    if self.state == STATE_PLAYING:
                        self.state = STATE_PAUSED
                    elif self.state == STATE_PAUSED:
                        self.state = STATE_PLAYING
                    elif self.state in (STATE_MENU, STATE_GAME_OVER, STATE_WIN):
                        self.running = False
                
                elif event.key == pygame.K_SPACE:
                    if self.state == STATE_MENU:
                        self.new_game()
                    elif self.state == STATE_PLAYING and not self.ball.active:
                        self.ball.launch()
                    elif self.state == STATE_PAUSED:
                        self.state = STATE_PLAYING
                    elif self.state == STATE_LEVEL_COMPLETE:
                        if self.level_manager.next_level():
                            self._setup_level()
                            self.state = STATE_PLAYING
                        else:
                            self.state = STATE_WIN
                    elif self.state in (STATE_GAME_OVER, STATE_WIN):
                        self.new_game()
                
                elif event.key == pygame.K_r and self.state in (STATE_GAME_OVER, STATE_WIN):
                    self.new_game()
                
                elif event.key == pygame.K_f:
                    self._toggle_fullscreen()
            
            elif event.type == pygame.MOUSEBUTTONDOWN:
                if event.button == 1:  # Left click
                    if self.state == STATE_MENU:
                        self.new_game()
                    elif self.state == STATE_PLAYING and not self.ball.active:
                        self.ball.launch()
    
    def _update(self, dt, current_time):
        """Update game state."""
        if self.state != STATE_PLAYING:
            return
        
        # Update paddle
        self.paddle.update(dt)
        
        # Update ball
        self.ball.update(self.paddle.rect, self.assets.thud_sound)
        
        # Handle power-up speed effects on ball
        active_powerup = self.powerup_manager.get_active_type()
        if active_powerup == POWERUP_SLOW:
            self.ball.set_slow()
        elif active_powerup == POWERUP_FAST:
            self.ball.set_fast()
        else:
            self.ball.reset_speed()
        
        # Update paddle power-up display
        self.paddle.active_powerup = active_powerup
        
        # Ball-paddle collision
        if self.ball.collide_paddle(self.paddle.rect):
            if self.assets.thud_sound:
                self.assets.thud_sound.play()
            self.combo = 0  # Reset combo on paddle hit
        
        # Ball-brick collisions
        self._handle_brick_collisions(current_time)
        
        # Ball out of bounds
        if self.ball.is_out():
            self.lives -= 1
            self.combo = 0
            if self.lives <= 0:
                self.state = STATE_GAME_OVER
            else:
                self.ball.reset(self.paddle.rect)
        
        # Update power-ups
        expired = self.powerup_manager.update(dt, current_time)
        
        # Check power-up collection
        collected, duration = self.powerup_manager.check_collision(
            self.paddle.rect, current_time
        )
        if collected:
            self.paddle.activate_powerup(collected, duration)
        
        # Update particles
        self.particles.update(dt)
        
        # Handle bullet firing
        if self.powerup_manager.is_active(POWERUP_BULLET):
            if pygame.mouse.get_pressed()[0]:
                if current_time - self.last_bullet_time > BULLET_COOLDOWN:
                    self._fire_bullet()
                    self.last_bullet_time = current_time
        
        # Update bullets
        self.bullets.update(dt)
        self._handle_bullet_collisions(current_time)
        
        # Check level complete
        if len(self.bricks) == 0:
            self.state = STATE_LEVEL_COMPLETE
    
    def _handle_brick_collisions(self, current_time):
        """Handle ball-brick collisions."""
        for brick in self.bricks:
            if self.ball.rect.colliderect(brick.rect):
                # Calculate collision response
                self._resolve_brick_collision(brick)
                
                # Handle brick hit
                destroyed = brick.hit()
                
                if destroyed:
                    self.combo += 1
                    points = brick.score * (1 + self.combo // 5)  # Combo bonus
                    self.score += points
                    self.paddle.show_score(points)
                    
                    # Spawn particles
                    self._spawn_particles(brick)
                    
                    # Maybe spawn power-up
                    self.powerup_manager.spawn_powerup(
                        brick.rect.centerx,
                        brick.rect.centery,
                        self.assets.star
                    )
                    
                    brick.kill()
                
                break  # Only handle one collision per frame
    
    def _resolve_brick_collision(self, brick):
        """Resolve ball-brick collision with proper reflection."""
        ball_rect = self.ball.rect
        brick_rect = brick.rect
        
        # Determine collision side
        dx = ball_rect.centerx - brick_rect.centerx
        dy = ball_rect.centery - brick_rect.centery
        
        # Width and height of combined rects
        w = (ball_rect.width + brick_rect.width) / 2
        h = (ball_rect.height + brick_rect.height) / 2
        
        # Calculate overlap
        cross_w = w * dy
        cross_h = h * dx
        
        if abs(dx) <= w and abs(dy) <= h:
            if cross_w > cross_h:
                if cross_w > -cross_h:
                    # Bottom collision
                    self.ball.velocity.y = abs(self.ball.velocity.y)
                    self.ball.rect.top = brick_rect.bottom + 1
                else:
                    # Left collision
                    self.ball.velocity.x = -abs(self.ball.velocity.x)
                    self.ball.rect.right = brick_rect.left - 1
            else:
                if cross_w > -cross_h:
                    # Right collision
                    self.ball.velocity.x = abs(self.ball.velocity.x)
                    self.ball.rect.left = brick_rect.right + 1
                else:
                    # Top collision
                    self.ball.velocity.y = -abs(self.ball.velocity.y)
                    self.ball.rect.bottom = brick_rect.top - 1
    
    def _spawn_particles(self, brick):
        """Spawn particles when a brick is destroyed."""
        particle_img = self.assets.get_particle_sprite(brick.get_particle_type())
        
        for _ in range(PARTICLE_COUNT):
            particle = Particle(
                brick.rect.centerx,
                brick.rect.centery,
                particle_img
            )
            self.particles.add(particle)
    
    def _fire_bullet(self):
        """Fire a bullet from the paddle."""
        bullet = Bullet(
            self.paddle.rect.centerx,
            self.paddle.rect.top - 20,
            self.assets.bullet
        )
        self.bullets.add(bullet)
    
    def _handle_bullet_collisions(self, current_time):
        """Handle bullet-brick collisions."""
        for bullet in self.bullets:
            for brick in self.bricks:
                if bullet.rect.colliderect(brick.rect):
                    bullet.kill()
                    
                    # Bullets destroy bricks instantly
                    self.combo += 1
                    points = brick.score * (1 + self.combo // 5)
                    self.score += points
                    self.paddle.show_score(points)
                    
                    self._spawn_particles(brick)
                    brick.kill()
                    
                    break
    
    def _draw(self):
        """Render the game."""
        # Draw background
        self.screen.blit(self.bg_surface, (0, 0))
        
        if self.state == STATE_MENU:
            self._draw_menu()
        elif self.state in (STATE_PLAYING, STATE_PAUSED):
            self._draw_game()
            if self.state == STATE_PAUSED:
                self._draw_overlay("PAUSED", "Press SPACE to continue")
        elif self.state == STATE_GAME_OVER:
            self._draw_game()
            self._draw_overlay("GAME OVER", f"Final Score: {self.score}", "Press SPACE to restart")
        elif self.state == STATE_LEVEL_COMPLETE:
            self._draw_game()
            self._draw_overlay(
                f"LEVEL {self.level_manager.get_current_level_num()} COMPLETE!",
                f"Score: {self.score}",
                "Press SPACE for next level"
            )
        elif self.state == STATE_WIN:
            self._draw_game()
            self._draw_overlay("YOU WIN!", f"Final Score: {self.score}", "Press SPACE to play again")
    
    def _draw_menu(self):
        """Draw the main menu."""
        # Title
        title = self.font_large.render("BRICK BREAKER", True, NEON_BLUE)
        title_rect = title.get_rect(center=(SCREEN_WIDTH // 2, SCREEN_HEIGHT // 3))
        self.screen.blit(title, title_rect)
        
        # Subtitle with glow effect
        subtitle = self.font_medium.render("Press SPACE or CLICK to Start", True, WHITE)
        subtitle_rect = subtitle.get_rect(center=(SCREEN_WIDTH // 2, SCREEN_HEIGHT // 2))
        self.screen.blit(subtitle, subtitle_rect)
        
        # Instructions
        instructions = [
            "Mouse - Move paddle",
            "SPACE - Launch ball",
            "Left Click - Shoot (when power-up active)",
            "F - Toggle Fullscreen",
            "ESC - Pause"
        ]
        
        y = SCREEN_HEIGHT * 2 // 3
        for instruction in instructions:
            text = self.font_small.render(instruction, True, (150, 150, 170))
            rect = text.get_rect(center=(SCREEN_WIDTH // 2, y))
            self.screen.blit(text, rect)
            y += 35
    
    def _draw_game(self):
        """Draw the game elements."""
        # Draw bricks
        self.bricks.draw(self.screen)
        
        # Draw particles
        self.particles.draw(self.screen)
        
        # Draw power-ups
        self.powerup_manager.draw(self.screen)
        
        # Draw bullets
        self.bullets.draw(self.screen)
        
        # Draw paddle
        self.screen.blit(self.paddle.image, self.paddle.rect)
        
        # Draw ball
        self.screen.blit(self.ball.image, self.ball.rect)
        
        # Draw UI
        self._draw_ui()
    
    def _draw_ui(self):
        """Draw the game UI (score, lives, level)."""
        # Score
        score_text = self.font_medium.render(f"Score: {self.score}", True, WHITE)
        self.screen.blit(score_text, (20, 20))
        
        # Level
        level_text = self.font_small.render(
            f"Level {self.level_manager.get_current_level_num()}",
            True, NEON_BLUE
        )
        level_rect = level_text.get_rect(center=(SCREEN_WIDTH // 2, 25))
        self.screen.blit(level_text, level_rect)
        
        # Lives (hearts)
        for i in range(self.lives):
            x = SCREEN_WIDTH - HEART_SPACING * (i + 1)
            self.screen.blit(self.assets.heart, (x, HEART_Y))
        
        # Combo indicator
        if self.combo > 0:
            combo_text = self.font_small.render(f"Combo: {self.combo}x", True, NEON_PINK)
            combo_rect = combo_text.get_rect(topright=(SCREEN_WIDTH - 20, 60))
            self.screen.blit(combo_text, combo_rect)
        
        # Power-up indicator
        active = self.powerup_manager.get_active_type()
        if active:
            powerup_text = self.font_small.render(
                f"Power: {active.upper()}", True, (255, 255, 0)
            )
            self.screen.blit(powerup_text, (20, 70))
    
    def _draw_overlay(self, title, *lines):
        """Draw a semi-transparent overlay with text."""
        # Semi-transparent overlay
        overlay = pygame.Surface((SCREEN_WIDTH, SCREEN_HEIGHT), pygame.SRCALPHA)
        overlay.fill((0, 0, 0, 180))
        self.screen.blit(overlay, (0, 0))
        
        # Title
        title_surf = self.font_large.render(title, True, NEON_BLUE)
        title_rect = title_surf.get_rect(center=(SCREEN_WIDTH // 2, SCREEN_HEIGHT // 3))
        self.screen.blit(title_surf, title_rect)
        
        # Additional lines
        y = SCREEN_HEIGHT // 2
        for line in lines:
            text_surf = self.font_medium.render(line, True, WHITE)
            text_rect = text_surf.get_rect(center=(SCREEN_WIDTH // 2, y))
            self.screen.blit(text_surf, text_rect)
            y += 50


def main():
    """Entry point."""
    game = Game()
    game.run()


if __name__ == "__main__":
    main()
