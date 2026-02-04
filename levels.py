"""
Level definitions for Breakout game.
"""

from config import (
    BRICK_COLS, BRICK_ROWS, BRICK_WIDTH, BRICK_HEIGHT,
    BRICK_PADDING, BRICK_TOP_OFFSET, BRICK_LEFT_OFFSET
)


# Level patterns - each number represents a brick type (0-9), -1 means empty
LEVEL_PATTERNS = [
    # Level 1 - Simple rows
    [
        [0, 0, 0, 0, 0, 0, 0, 0, 0],
        [1, 1, 1, 1, 1, 1, 1, 1, 1],
        [2, 2, 2, 2, 2, 2, 2, 2, 2],
        [3, 3, 3, 3, 3, 3, 3, 3, 3],
        [4, 4, 4, 4, 4, 4, 4, 4, 4],
    ],
    
    # Level 2 - Checkerboard
    [
        [0, -1, 1, -1, 2, -1, 1, -1, 0],
        [-1, 3, -1, 4, -1, 4, -1, 3, -1],
        [2, -1, 5, -1, 6, -1, 5, -1, 2],
        [-1, 3, -1, 4, -1, 4, -1, 3, -1],
        [0, -1, 1, -1, 2, -1, 1, -1, 0],
    ],
    
    # Level 3 - Diamond
    [
        [-1, -1, -1, -1, 7, -1, -1, -1, -1],
        [-1, -1, -1, 5, 6, 5, -1, -1, -1],
        [-1, -1, 3, 4, 5, 4, 3, -1, -1],
        [-1, 1, 2, 3, 4, 3, 2, 1, -1],
        [0, 1, 2, 3, 4, 3, 2, 1, 0],
        [-1, 1, 2, 3, 4, 3, 2, 1, -1],
        [-1, -1, 3, 4, 5, 4, 3, -1, -1],
    ],
    
    # Level 4 - Fortress
    [
        [8, 8, 8, -1, 9, -1, 8, 8, 8],
        [7, -1, 7, -1, 9, -1, 7, -1, 7],
        [6, -1, 6, 6, 6, 6, 6, -1, 6],
        [5, -1, -1, -1, -1, -1, -1, -1, 5],
        [4, 4, 4, 4, 4, 4, 4, 4, 4],
        [3, 3, 3, 3, 3, 3, 3, 3, 3],
    ],
    
    # Level 5 - Final Challenge
    [
        [9, 9, 9, 9, 9, 9, 9, 9, 9],
        [8, 8, 8, 8, 8, 8, 8, 8, 8],
        [7, 7, -1, 7, 7, 7, -1, 7, 7],
        [6, 6, -1, 6, 6, 6, -1, 6, 6],
        [5, 5, 5, 5, 5, 5, 5, 5, 5],
        [4, -1, 4, -1, 4, -1, 4, -1, 4],
        [3, 3, 3, 3, 3, 3, 3, 3, 3],
        [2, 2, 2, 2, 2, 2, 2, 2, 2],
    ],
]


class LevelManager:
    """Manages level loading and progression."""
    
    def __init__(self, assets):
        self.assets = assets
        self.current_level = 0
        self.total_levels = len(LEVEL_PATTERNS)
    
    def get_level_bricks(self, level_num=None):
        """
        Generate bricks for a level.
        Returns a list of Brick objects.
        """
        from entities import Brick
        
        if level_num is not None:
            self.current_level = level_num
        
        if self.current_level >= self.total_levels:
            return []  # No more levels
        
        pattern = LEVEL_PATTERNS[self.current_level]
        bricks = []
        
        for row_idx, row in enumerate(pattern):
            for col_idx, brick_type in enumerate(row):
                if brick_type < 0:  # -1 means empty space
                    continue
                
                x = BRICK_LEFT_OFFSET + col_idx * (BRICK_WIDTH + BRICK_PADDING)
                y = BRICK_TOP_OFFSET + row_idx * (BRICK_HEIGHT + BRICK_PADDING)
                
                brick = Brick(x, y, brick_type, self.assets)
                bricks.append(brick)
        
        return bricks
    
    def next_level(self):
        """Advance to next level. Returns True if successful, False if no more levels."""
        self.current_level += 1
        return self.current_level < self.total_levels
    
    def reset(self):
        """Reset to first level."""
        self.current_level = 0
    
    def get_current_level_num(self):
        """Get current level number (1-indexed for display)."""
        return self.current_level + 1
    
    def is_final_level(self):
        """Check if this is the final level."""
        return self.current_level >= self.total_levels - 1
