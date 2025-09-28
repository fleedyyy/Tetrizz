import pygame
import random
import sys
import math

# Initialize Pygame
pygame.init()

# Constants
GRID_WIDTH = 10
GRID_HEIGHT = 20
CELL_SIZE = 32
GRID_X_OFFSET = 60
GRID_Y_OFFSET = 60

WINDOW_WIDTH = GRID_WIDTH * CELL_SIZE + 2 * GRID_X_OFFSET + 350
WINDOW_HEIGHT = GRID_HEIGHT * CELL_SIZE + 2 * GRID_Y_OFFSET + 40

# Modern color palette
BACKGROUND = (15, 15, 23)
GRID_BG = (25, 25, 35)
GRID_LINE = (45, 45, 60)
UI_BG = (30, 30, 40)
UI_BORDER = (60, 60, 80)
TEXT_PRIMARY = (220, 220, 230)
TEXT_SECONDARY = (160, 160, 180)
ACCENT = (100, 200, 255)
SUCCESS = (80, 200, 120)
WARNING = (255, 180, 80)
DANGER = (255, 100, 100)
BOSS_COLOR = (150, 50, 200)
CORRUPTION_COLOR = (100, 50, 50)

# Enhanced Tetromino colors with gradients
TETROMINO_COLORS = {
    'I': (0, 240, 255),      # Bright cyan
    'O': (255, 220, 0),      # Golden yellow
    'T': (160, 80, 255),     # Purple
    'S': (80, 255, 80),      # Bright green
    'Z': (255, 80, 80),      # Bright red
    'J': (80, 120, 255),     # Blue
    'L': (255, 160, 0)       # Orange
}

# Shadow colors (darker versions)
SHADOW_COLORS = {
    'I': (0, 180, 200),
    'O': (200, 170, 0),
    'T': (120, 60, 200),
    'S': (60, 200, 60),
    'Z': (200, 60, 60),
    'J': (60, 90, 200),
    'L': (200, 120, 0)
}

# Tetromino shapes
TETROMINOES = {
    'I': [['.....',
           '..#..',
           '..#..',
           '..#..',
           '..#..'],
          ['.....',
           '.....',
           '####.',
           '.....',
           '.....']],
    
    'O': [['.....',
           '.....',
           '.##..',
           '.##..',
           '.....']],
    
    'T': [['.....',
           '.....',
           '..#..',
           '.###.',
           '.....'],
          ['.....',
           '.....',
           '.#...',
           '.##..',
           '.#...'],
          ['.....',
           '.....',
           '.....',
           '.###.',
           '..#..'],
          ['.....',
           '.....',
           '.#...',
           '##...',
           '.#...']],
    
    'S': [['.....',
           '.....',
           '..##.',
           '.##..',
           '.....'],
          ['.....',
           '.#...',
           '.##..',
           '..#..',
           '.....']],
    
    'Z': [['.....',
           '.....',
           '##...',
           '.##..',
           '.....'],
          ['.....',
           '..#..',
           '.##..',
           '.#...',
           '.....']],
    
    'J': [['.....',
           '..#..',
           '..#..',
           '.##..',
           '.....'],
          ['.....',
           '.....',
           '#....',
           '###..',
           '.....'],
          ['.....',
           '.##..',
           '.#...',
           '.#...',
           '.....'],
          ['.....',
           '.....',
           '###..',
           '..#..',
           '.....']],
    
    'L': [['.....',
           '..#..',
           '..#..',
           '..##.',
           '.....'],
          ['.....',
           '.....',
           '###..',
           '#....',
           '.....'],
          ['.....',
           '##...',
           '.#...',
           '.#...',
           '.....'],
          ['.....',
           '.....',
           '..#..',
           '###..',
           '.....']]
}

class ParticleEffect:
    def __init__(self, x, y, color, velocity_scale=1.0):
        self.particles = []
        particle_count = 12 if velocity_scale > 1 else 8
        for _ in range(particle_count):
            self.particles.append({
                'x': x,
                'y': y,
                'vx': random.uniform(-3, 3) * velocity_scale,
                'vy': random.uniform(-5, -1) * velocity_scale,
                'life': int(30 * velocity_scale),
                'color': color,
                'size': random.randint(2, 4)
            })
    
    def update(self):
        for particle in self.particles[:]:
            particle['x'] += particle['vx']
            particle['y'] += particle['vy']
            particle['vy'] += 0.2  # gravity
            particle['life'] -= 1
            if particle['life'] <= 0:
                self.particles.remove(particle)
    
    def draw(self, screen):
        for particle in self.particles:
            alpha = particle['life'] / 30.0
            size = max(1, int(3 * alpha))
            pygame.draw.circle(screen, particle['color'], 
                             (int(particle['x']), int(particle['y'])), size)
class Boss:
    def __init__(self):
        self.max_health = 100
        self.health = self.max_health
        self.phase = 1
        self.attack_timer = 0
        self.attack_cooldown = 5000  # milliseconds
        self.is_stunned = False
        self.stun_timer = 0
        self.animation_time = 0
        self.shake_intensity = 0
        self.shake_timer = 0
        self.last_attack = None
        
        # Boss attacks
        self.attacks = {
            1: ['garbage_lines', 'speed_boost'],
            2: ['garbage_lines', 'speed_boost', 'grid_shake'],
            3: ['garbage_lines', 'speed_boost', 'grid_shake', 'piece_theft', 'time_pressure']
        }
    
    def take_damage(self, damage):
        if not self.is_stunned:
            self.health -= damage
            self.health = max(0, self.health)
            
            # Phase transitions
            if self.health <= 66 and self.phase == 1:
                self.phase = 2
                self.attack_cooldown = 2500
            elif self.health <= 33 and self.phase == 2:
                self.phase = 3
                self.attack_cooldown = 2000
            
            # Stun on big damage
            if damage >= 20:  # Tetris damage
                self.is_stunned = True
                self.stun_timer = 1500
    
    def update(self, dt):
        self.animation_time += dt
        
        if self.is_stunned:
            self.stun_timer -= dt
            if self.stun_timer <= 0:
                self.is_stunned = False
        
        if self.shake_timer > 0:
            self.shake_timer -= dt
            self.shake_intensity = max(0, self.shake_intensity - dt * 0.01)
        
        if not self.is_stunned:
            self.attack_timer += dt
    
    def should_attack(self):
        return self.attack_timer >= self.attack_cooldown and not self.is_stunned
    
    def get_random_attack(self):
        available_attacks = self.attacks.get(self.phase, self.attacks[1])
        # Avoid repeating the same attack
        if self.last_attack and len(available_attacks) > 1:
            available_attacks = [a for a in available_attacks if a != self.last_attack]
        return random.choice(available_attacks)
    
    def execute_attack(self):
        attack = self.get_random_attack()
        self.last_attack = attack
        self.attack_timer = 0
        return attack
    
    def draw(self, screen, x, y, width, height):
        # Boss health bar background
        health_bg = pygame.Rect(x, y, width, 20)
        pygame.draw.rect(screen, (50, 50, 50), health_bg, border_radius=10)
        
        # Health bar
        health_width = int((self.health / self.max_health) * width)
        health_color = DANGER if self.health < 30 else WARNING if self.health < 60 else SUCCESS
        if health_width > 0:
            health_bar = pygame.Rect(x, y, health_width, 20)
            pygame.draw.rect(screen, health_color, health_bar, border_radius=10)
        
        # Boss name and phase
        font = pygame.font.Font(None, 24)
        boss_text = font.render(f"TETRIS OVERLORD - Phase {self.phase}", True, BOSS_COLOR)
        screen.blit(boss_text, (x, y - 47))
        
        # Health text
        health_text = font.render(f"{self.health}/{self.max_health}", True, TEXT_PRIMARY)
        screen.blit(health_text, (x + width - 60, y - 25))
        
        # Boss avatar (animated)
        avatar_rect = pygame.Rect(x + width + 10, y - 15, 50, 50)
        
        # Boss face color based on health/stun
        if self.is_stunned:
            boss_face_color = (100, 100, 200)
        elif self.health < 30:
            boss_face_color = DANGER
        else:
            boss_face_color = BOSS_COLOR
        
        # Animated boss face
        pulse = abs(math.sin(self.animation_time * 0.005)) * 0.2 + 0.8
        face_color = tuple(int(c * pulse) for c in boss_face_color)
        
        pygame.draw.rect(screen, face_color, avatar_rect, border_radius=8)
        pygame.draw.rect(screen, TEXT_PRIMARY, avatar_rect, 2, border_radius=8)
        
        # Boss eyes
        eye_size = 6 if not self.is_stunned else 4
        eye_y = avatar_rect.y + 15
        pygame.draw.circle(screen, (255, 0, 0), (avatar_rect.x + 15, eye_y), eye_size)
        pygame.draw.circle(screen, (255, 0, 0), (avatar_rect.x + 35, eye_y), eye_size)
        
        # Boss mouth
        if self.is_stunned:
            # Dizzy mouth
            pygame.draw.arc(screen, TEXT_PRIMARY, (avatar_rect.x + 15, avatar_rect.y + 25, 20, 15), 0, math.pi, 2)
        else:
            # Evil grin
            pygame.draw.arc(screen, TEXT_PRIMARY, (avatar_rect.x + 15, avatar_rect.y + 30, 20, 10), math.pi, 2 * math.pi, 2)

class Tetromino:
    def __init__(self, shape, color):
        self.shape = shape
        self.color = color
        self.shadow_color = SHADOW_COLORS[shape]
        self.x = GRID_WIDTH // 2 - 2
        self.y = 0
        self.rotation = 0
        self.animation_offset = 0
        self.pulse = 0
        self.is_corrupted = False
    
    def get_rotated_shape(self):
        return TETROMINOES[self.shape][self.rotation]
    
    def get_cells(self):
        cells = []
        shape = self.get_rotated_shape()
        for i, row in enumerate(shape):
            for j, cell in enumerate(row):
                if cell == '#':
                    cells.append((self.x + j, self.y + i))
        return cells

class TetrisGame:
    def __init__(self, boss_mode=False):
        self.grid = [[None for _ in range(GRID_WIDTH)] for _ in range(GRID_HEIGHT)]
        self.corrupted_grid = [[False for _ in range(GRID_WIDTH)] for _ in range(GRID_HEIGHT)]
        
        # Initialize boss mode first
        self.boss_mode = boss_mode
        self.boss = Boss() if boss_mode else None
        self.boss_attacks_active = []
        self.speed_boost_timer = 0
        self.time_pressure_timer = 0
        self.game_won = False

        # Safely call get_new_piece
        self.current_piece = self.get_new_piece()
        self.next_piece = self.get_new_piece()

        self.score = 0
        self.level = 1
        self.lines_cleared = 0
        self.fall_time = 0
        self.fall_speed = 500
        self.base_fall_speed = 500
        self.particles = []
        self.line_clear_animation = []
        self.animation_time = 0
        self.grid_shake_x = 0
        self.grid_shake_y = 0
        self.pending_line_clears = []
        self.line_clear_timer = 0
        
    def get_new_piece(self):
        shape = random.choice(list(TETROMINOES.keys()))
        piece = Tetromino(shape, TETROMINO_COLORS[shape])
        # Boss attack: make some pieces corrupted
        if self.boss_mode and 'piece_corruption' in self.boss_attacks_active and random.random() < 0.3:
            piece.is_corrupted = True
            piece.color = CORRUPTION_COLOR
        
        return piece
    
    def is_valid_position(self, piece, dx=0, dy=0, rotation=None):
        if rotation is None:
            rotation = piece.rotation
        
        old_rotation = piece.rotation
        piece.rotation = rotation
        
        for x, y in piece.get_cells():
            x += dx
            y += dy
            
            if x < 0 or x >= GRID_WIDTH or y >= GRID_HEIGHT:
                piece.rotation = old_rotation
                return False
            
            if y >= 0 and self.grid[y][x] is not None:
                piece.rotation = old_rotation
                return False
        
        piece.rotation = old_rotation
        return True
    
    def place_piece(self, piece):
        for x, y in piece.get_cells():
            if y >= 0:
                self.grid[y][x] = piece.color
                if piece.is_corrupted: # Mark corrupted Cells
                    self.corrupted_grid[y][x] = True

        lines_to_clear = []
        for y in range(GRID_HEIGHT):
            if all(cell is not None for cell in self.grid[y]):
                lines_to_clear.append(y)
        
        # Add line clear animation
        if lines_to_clear:
            self.line_clear_animation = lines_to_clear[:]
            self.pending_line_clears = lines_to_clear[:]
            self.line_clear_timer = 0 
            # Add particles for line clear effect
            for y in lines_to_clear:
                for x in range(GRID_WIDTH):
                    px = GRID_X_OFFSET + x * CELL_SIZE + CELL_SIZE // 2 + self.grid_shake_x
                    py = GRID_Y_OFFSET + y * CELL_SIZE + CELL_SIZE // 2 + self.grid_shake_y
                    self.particles.append(ParticleEffect(px, py, self.grid[y][x], 1.5))

    def move_piece(self, dx, dy):
        if self.is_valid_position(self.current_piece, dx, dy):
            self.current_piece.x += dx
            self.current_piece.y += dy
            return True
        return False
    
    def rotate_piece(self):
        rotations = len(TETROMINOES[self.current_piece.shape])
        new_rotation = (self.current_piece.rotation + 1) % rotations
        
        if self.is_valid_position(self.current_piece, 0, 0, new_rotation):
            self.current_piece.rotation = new_rotation
            return True
        return False
    
    def add_garbage_lines(self, count=1):
        """Boss attack: add garbage lines from bottom"""
        for _ in range(count):
            # Remove top line
            self.grid.pop(0)
            self.corrupted_grid.pop(0)
            
            # Add garbage line at bottom
            garbage_line = [CORRUPTION_COLOR if random.random() < 0.8 else None for _ in range(GRID_WIDTH)]
            # Ensure there's at least one gap
            gap_pos = random.randint(0, GRID_WIDTH - 1)
            garbage_line[gap_pos] = None
            
            self.grid.append(garbage_line)
            self.corrupted_grid.append([cell is not None for cell in garbage_line])
        
        # Add particles for garbage lines
        for x in range(GRID_WIDTH):
            if self.grid[-1][x] is not None:
                px = GRID_X_OFFSET + x * CELL_SIZE + CELL_SIZE // 2
                py = GRID_Y_OFFSET + (GRID_HEIGHT - 1) * CELL_SIZE + CELL_SIZE // 2
                self.particles.append(ParticleEffect(px, py, CORRUPTION_COLOR, 0.5))
    
    def execute_boss_attack(self, attack):
        """Execute a boss attack"""
        if attack == 'garbage_lines':
            self.add_garbage_lines(random.randint(1, 2))
            
        elif attack == 'speed_boost':
            self.speed_boost_timer = 5000  # 5 seconds of fast fall
            
        elif attack == 'piece_corruption':
            if 'piece_corruption' not in self.boss_attacks_active:
                self.boss_attacks_active.append('piece_corruption')
            
        elif attack == 'grid_shake':
            self.boss.shake_intensity = 3
            self.boss.shake_timer = 2000
            
        elif attack == 'piece_theft':
            # Steal next piece and give a bad one (random)
            self.next_piece = self.get_new_piece()
            
        elif attack == 'time_pressure':
            self.time_pressure_timer = 10000  # 10 seconds of extreme speed
    
    def update(self, dt):
        self.animation_time += dt
        
        # Update boss
        if self.boss_mode and self.boss and not self.game_won:
            self.boss.update(dt)
            
            # Execute boss attacks
            if self.boss.should_attack():
                attack = self.boss.execute_attack()
                self.execute_boss_attack(attack)
        
        # Update boss attack timers
        if self.speed_boost_timer > 0:
            self.speed_boost_timer -= dt
        
        if self.time_pressure_timer > 0:
            self.time_pressure_timer -= dt
        else:
            # Remove piece corruption when time pressure ends
            if 'piece_corruption' in self.boss_attacks_active:
                self.boss_attacks_active.remove('piece_corruption')
        
        # Update grid shake
        if self.boss and self.boss.shake_timer > 0:
            shake_amount = int(self.boss.shake_intensity)
            self.grid_shake_x = random.randint(-shake_amount, shake_amount)
            self.grid_shake_y = random.randint(-shake_amount, shake_amount)
        else:
            self.grid_shake_x = 0
            self.grid_shake_y = 0
        
        # Calculate current fall speed with boss effects
        current_fall_speed = self.base_fall_speed
        if self.speed_boost_timer > 0:
            current_fall_speed //= 2
        if self.time_pressure_timer > 0:
            current_fall_speed //= 4
        
        self.fall_speed = current_fall_speed

        # Update particles
        for particle_effect in self.particles[:]:
            particle_effect.update()
            if not particle_effect.particles:
                self.particles.remove(particle_effect)
        """"""
        # Update line clear timer
        if self.line_clear_animation:
            self.line_clear_timer += dt
        # Clear line clear animation
        if self.line_clear_animation and self.animation_time > 300:
            if self.pending_line_clears:
                # Clear lines (clear from bottom to top to avoid index shifting issues)
                clear_effect = pygame.mixer.Sound('sfx/dropop.wav')
                clear_effect.play()
                lines_cleared = len(self.pending_line_clears)
                for y in sorted(self.pending_line_clears, reverse=True):
                    del self.grid[y]
                    del self.corrupted_grid[y]
                for _ in range(lines_cleared):
                    self.grid.insert(0, [None for _ in range(GRID_WIDTH)])
                    self.corrupted_grid.insert(0, [False for _ in range(GRID_WIDTH)])
            
                lines_cleared = len(self.pending_line_clears)
                self.lines_cleared += lines_cleared
                
                # Enhanced scoring
                score_values = {0: 0, 1: 100, 2: 300, 3: 500, 4: 800}
                line_score = score_values.get(lines_cleared, 0) * self.level
                self.score += line_score
                
                # Boss damage
                if self.boss_mode and self.boss and lines_cleared > 0:
                    damage = lines_cleared * 5
                    if lines_cleared == 4:  # Tetris
                        damage = 25
                    self.boss.take_damage(damage)
                    
                    # Check win condition
                    if self.boss.health <= 0:
                        self.game_won = True
                
                # Level progression
                self.level = self.lines_cleared // 10 + 1
                self.base_fall_speed = max(50, 500 - (self.level - 1) * 25)

                self.pending_line_clears = []

            self.line_clear_animation = []
            self.line_clear_timer = 0
        
        self.fall_time += dt
        
        if self.fall_time >= self.fall_speed:
            if not self.move_piece(0, 1):
                self.place_piece(self.current_piece)
                self.current_piece = self.next_piece
                self.next_piece = self.get_new_piece()
                
                # Check game over
                if not self.is_valid_position(self.current_piece):
                    return False
            
            self.fall_time = 0
        
        return True
    
    def hard_drop(self):
        drop_effect = pygame.mixer.Sound('sfx/dblock.mp3')
        drop_effect.play()
        drop_distance = 0
        while self.move_piece(0, 1):
            drop_distance += 1
            self.score += 2
        
        # Add drop effect
        if drop_distance > 0:
            # fixed bug placed block moved yippeeeeeeee
            self.place_piece(self.current_piece)
            self.current_piece = self.next_piece
            self.next_piece = self.get_new_piece()
            self.fall_time = 0  # Reset fall timer
            for x, y in self.current_piece.get_cells():
                px = GRID_X_OFFSET + x * CELL_SIZE + CELL_SIZE // 2
                py = GRID_Y_OFFSET + y * CELL_SIZE + CELL_SIZE // 2
                self.particles.append(ParticleEffect(px, py, self.current_piece.color))
    
    def draw_rounded_rect(self, screen, color, rect, radius=4):
        """Draw a rounded rectangle"""
        pygame.draw.rect(screen, color, rect, border_radius=radius)
    
    def draw_cell_with_gradient(self, screen, x, y, color, shadow_color, highlight=False, corrupted=False):
        adjusted_x = x + self.grid_shake_x // 2
        adjusted_y = y + self.grid_shake_y // 2
        
        """Draw a cell with gradient effect"""
        rect = pygame.Rect(
            GRID_X_OFFSET + adjusted_x * CELL_SIZE + 1,
            GRID_Y_OFFSET + adjusted_y * CELL_SIZE + 1,
            CELL_SIZE - 2,
            CELL_SIZE - 2
        )
        
        # Corrupted blocks have special color
        if corrupted:
            # Flickering corruption effect
            flicker = abs(math.sin(self.animation_time * 0.01)) * 0.5 + 0.5
            corruption_color = tuple(int(c * flicker) for c in CORRUPTION_COLOR)
            self.draw_rounded_rect(screen, corruption_color, rect, 3)
            
            # Corruption overlay
            overlay_rect = pygame.Rect(rect.x + 4, rect.y + 4, rect.width - 8, rect.height - 8)
            pygame.draw.rect(screen, (150, 0, 0), overlay_rect, 1)
        else:
            # Normal block rendering
            self.draw_rounded_rect(screen, color, rect, 3)
        
            # Highlight effect
            if highlight:
                pulse = abs(math.sin(self.animation_time * 0.01)) * 0.3 + 0.7
                highlight_color = tuple(min(255, max(0, int(c * pulse))) for c in color)
                self.draw_rounded_rect(screen, highlight_color, rect, 3)
        
        # Inner highlight
        if not corrupted:
            inner_rect = pygame.Rect(rect.x + 2, rect.y + 2, rect.width - 8, 4)
            highlight_color = tuple(min(255, max(0, c + 40)) for c in color)
            self.draw_rounded_rect(screen, highlight_color, inner_rect, 2)
        
            # Shadow - ensure no negative values
            shadow_rect = pygame.Rect(rect.x + 2, rect.bottom - 6, rect.width - 4, 4)
            safe_shadow_color = tuple(max(0, min(255, c)) for c in shadow_color)
            self.draw_rounded_rect(screen, safe_shadow_color, shadow_rect, 2)
    
    def draw_grid(self, screen):
        # Draw background
        grid_bg_rect = pygame.Rect(
            GRID_X_OFFSET - 5 + self.grid_shake_x, 
            GRID_Y_OFFSET - 5 + self.grid_shake_y,
            GRID_WIDTH * CELL_SIZE + 10, 
            GRID_HEIGHT * CELL_SIZE + 10
        )
        self.draw_rounded_rect(screen, GRID_BG, grid_bg_rect, 8)
        
        # Draw grid lines
        for x in range(GRID_WIDTH + 1):
            start_pos = (GRID_X_OFFSET + x * CELL_SIZE + self.grid_shake_x, GRID_Y_OFFSET + self.grid_shake_y)
            end_pos = (GRID_X_OFFSET + x * CELL_SIZE + self.grid_shake_x, GRID_Y_OFFSET + GRID_HEIGHT * CELL_SIZE + self.grid_shake_y)
            pygame.draw.line(screen, GRID_LINE, start_pos, end_pos, 1)
        
        for y in range(GRID_HEIGHT + 1):
            start_pos = (GRID_X_OFFSET + self.grid_shake_x, GRID_Y_OFFSET + y * CELL_SIZE + self.grid_shake_y)
            end_pos = (GRID_X_OFFSET + GRID_WIDTH * CELL_SIZE + self.grid_shake_x, GRID_Y_OFFSET + y * CELL_SIZE + self.grid_shake_y)
            pygame.draw.line(screen, GRID_LINE, start_pos, end_pos, 1)
        
        # Draw placed pieces
        for y in range(GRID_HEIGHT):
            for x in range(GRID_WIDTH):
                if self.grid[y][x] is not None:
                    # Check if this line is being cleared
                    highlight = y in self.line_clear_animation
                    shadow_color = tuple(max(0, c - 60) for c in self.grid[y][x])
                    self.draw_cell_with_gradient(screen, x, y, self.grid[y][x], shadow_color, highlight, self.corrupted_grid[y][x])
    
    def draw_piece(self, screen, piece, ghost=False):
        alpha = 0.3 if ghost else 1.0
        
        for x, y in piece.get_cells():
            if y >= 0:
                if ghost:
                    # Draw ghost piece
                    rect = pygame.Rect(
                        GRID_X_OFFSET + x * CELL_SIZE + 1 + self.grid_shake_x,
                        GRID_Y_OFFSET + y * CELL_SIZE + 1 + self.grid_shake_y,
                        CELL_SIZE - 2,
                        CELL_SIZE - 2
                    )
                    ghost_color = tuple(max(0, c // 3) for c in piece.color)
                    pygame.draw.rect(screen, ghost_color, rect, 2, border_radius=3)
                else:
                    shadow_color = tuple(max(0, c - 60) for c in piece.color)
                    self.draw_cell_with_gradient(screen, x, y, piece.color, piece.shadow_color, True, piece.is_corrupted)
    
    def draw_ghost_piece(self, screen):
        if not self.current_piece:
            return
        """Draw the ghost piece showing where the current piece will land"""
        ghost_piece = Tetromino(self.current_piece.shape, self.current_piece.color)
        ghost_piece.x = self.current_piece.x
        ghost_piece.y = self.current_piece.y
        ghost_piece.rotation = self.current_piece.rotation
        
        # Move ghost piece down until it can't move anymore
        while self.is_valid_position(ghost_piece, 0, 1):
            ghost_piece.y += 1
        
        # Only draw if ghost is below current piece
        if ghost_piece.y > self.current_piece.y:
            self.draw_piece(screen, ghost_piece, ghost=True)
    
    def draw_ui_panel(self, screen, x, y, width, height, title):
        """Draw a styled UI panel"""
        panel_rect = pygame.Rect(x, y, width, height)
        self.draw_rounded_rect(screen, UI_BG, panel_rect, 8)
        pygame.draw.rect(screen, UI_BORDER, panel_rect, 2, border_radius=8)
        
        if title:
            font = pygame.font.Font(None, 24)
            title_text = font.render(title, True, TEXT_PRIMARY)
            screen.blit(title_text, (x + 10, y + 8))
        
        return panel_rect
    
    def draw_next_piece(self, screen):
        ui_x = GRID_X_OFFSET + GRID_WIDTH * CELL_SIZE + 20
        ui_y = GRID_Y_OFFSET
        
        panel = self.draw_ui_panel(screen, ui_x, ui_y, 150, 125, "Next")
        
        # Draw next piece
        if self.next_piece:
            shape = self.next_piece.get_rotated_shape()
            piece_width = len(shape[0])
            piece_height = len(shape)

            start_x = ui_x + 5 + (150 - piece_width * 20) // 2
            start_y = ui_y + 20 + (80 - piece_height * 20) // 2
            
            for i, row in enumerate(shape):
                for j, cell in enumerate(row):
                    if cell == '#':
                        mini_rect = pygame.Rect(
                            start_x + j * 20,
                            start_y + i * 20,
                            18,
                            18
                        )
                        color = self.next_piece.color
                        if self.next_piece.is_corrupted:
                            # Flickering corruption effect
                            flicker = abs(math.sin(self.animation_time * 0.01)) * 0.5 + 0.5
                            color = tuple(int(c * flicker) for c in CORRUPTION_COLOR)
                        
                        self.draw_rounded_rect(screen, color, mini_rect, 3)
    
    def draw_score_panel(self, screen):
        ui_x = GRID_X_OFFSET + GRID_WIDTH * CELL_SIZE + 20
        ui_y = GRID_Y_OFFSET + 140
        
        panel_rect = self.draw_ui_panel(screen, ui_x, ui_y, 150, 200, "STATS")
        
        font = pygame.font.Font(None, 20)
        y_offset = ui_y + 35
        
        # Score
        score_text = font.render(f"Score: {self.score:,}", True, TEXT_PRIMARY)
        screen.blit(score_text, (ui_x + 10, y_offset))
        y_offset += 25
        
        # Level
        level_text = font.render(f"Level: {self.level}", True, TEXT_PRIMARY)
        screen.blit(level_text, (ui_x + 10, y_offset))
        y_offset += 25
        
        # Lines
        lines_text = font.render(f"Lines: {self.lines_cleared}", True, TEXT_PRIMARY)
        screen.blit(lines_text, (ui_x + 10, y_offset))
        y_offset += 35
        
        # Boss mode indicators
        if self.boss_mode:
            # Active effects
            if self.speed_boost_timer > 0:
                effect_text = font.render("SPEED BOOST!", True, WARNING)
                screen.blit(effect_text, (ui_x + 10, y_offset))
                y_offset += 20
            
            if self.time_pressure_timer > 0:
                effect_text = font.render("TIME PRESSURE!", True, DANGER)
                screen.blit(effect_text, (ui_x + 10, y_offset))
                y_offset += 20
            
            if 'piece_corruption' in self.boss_attacks_active:
                effect_text = font.render("CORRUPTION!", True, CORRUPTION_COLOR)
                screen.blit(effect_text, (ui_x + 10, y_offset))
                y_offset += 20
            
            if self.boss and self.boss.is_stunned:
                effect_text = font.render("BOSS STUNNED", True, SUCCESS)
                screen.blit(effect_text, (ui_x + 10, y_offset))
                y_offset += 20

    def draw_boss_panel(self, screen):
        if not self.boss_mode or not self.boss:
            return
        
        ui_x = GRID_X_OFFSET + GRID_WIDTH * CELL_SIZE + 20
        ui_y = GRID_Y_OFFSET + 400
        
        # Boss health and info
        self.boss.draw(screen, ui_x, ui_y, 200, 20)
        
        # Attack warning
        if self.boss.attack_timer > self.boss.attack_cooldown * 0.8 and not self.boss.is_stunned:
            warning_y = ui_y + 70
            font = pygame.font.Font(None, 24)
            warning_text = font.render("INCOMING ATTACK!", True, DANGER)
            # Blinking effect
            if int(self.animation_time / 100) % 2:
                screen.blit(warning_text, (ui_x, warning_y))
    
    def draw_victory_screen(self, screen):
        if not self.game_won:
            return
        
        # Victory overlay
        overlay = pygame.Surface((WINDOW_WIDTH, WINDOW_HEIGHT))
        overlay.set_alpha(200)
        overlay.fill((0, 0, 0))
        screen.blit(overlay, (0, 0))
        
        # Victory text
        font_large = pygame.font.Font(None, 72)
        font_medium = pygame.font.Font(None, 36)
        
        victory_text = font_large.render("VICTORY!", True, SUCCESS)
        victory_rect = victory_text.get_rect(center=(WINDOW_WIDTH // 2, WINDOW_HEIGHT // 2 - 50))
        screen.blit(victory_text, victory_rect)
        
        score_text = font_medium.render(f"Final Score: {self.score:,}", True, TEXT_PRIMARY)
        score_rect = score_text.get_rect(center=(WINDOW_WIDTH // 2, WINDOW_HEIGHT // 2 + 20))
        screen.blit(score_text, score_rect)
        
        restart_text = font_medium.render("Press R to restart or ESC to quit", True, TEXT_SECONDARY)
        restart_rect = restart_text.get_rect(center=(WINDOW_WIDTH // 2, WINDOW_HEIGHT // 2 + 60))
        screen.blit(restart_text, restart_rect)
    
    def draw_controls(self, screen):
        ui_x = GRID_X_OFFSET + GRID_WIDTH * CELL_SIZE + 20
        ui_y = GRID_Y_OFFSET + 355
        
        panel = self.draw_ui_panel(screen, ui_x, ui_y, 150, 200, "Controls")
        
        font = pygame.font.Font(None, 16)
        
        controls = [
            "Arrow Key Also Works",
            "A/D Move",
            "S Soft Drop",
            "W Rotate",
            "\"Space Bar\" Hard Drop",
            "",
            "R Restart",
            "ESC Quit"
        ]
        
        for i, control in enumerate(controls):
            if control:
                color = TEXT_SECONDARY if control else TEXT_PRIMARY
                text = font.render(control, True, color)
                screen.blit(text, (ui_x + 10, ui_y + 30 + i * 18))

    def draw(self, screen):
        # Clear screen
        screen.fill(BACKGROUND)
        
        # Draw grid and pieces
        self.draw_grid(screen)
        self.draw_ghost_piece(screen)
        
        if self.current_piece:
            self.draw_piece(screen, self.current_piece)
        
        # Draw UI
        self.draw_next_piece(screen)
        self.draw_score_panel(screen)
        if not self.boss_mode:
            self.draw_controls(screen)
        
        if self.boss_mode:
            self.draw_boss_panel(screen)
        
        # Draw particles
        for particle_effect in self.particles:
            particle_effect.draw(screen)
        
        # Draw victory screen
        self.draw_victory_screen(screen)

def main():
    screen = pygame.display.set_mode((WINDOW_WIDTH, WINDOW_HEIGHT))
    pygame.display.set_caption("Tetrizz")
    clock = pygame.time.Clock()
    pygame.mixer.music.load('music/menutet.mp3')
    pygame.mixer.music.play(-1)
    pygame.mixer.music.set_volume(0.4)
    
    # Show mode selection
    font = pygame.font.Font(None, 48)
    title_font = pygame.font.Font(None, 72)
    
    mode_selected = False
    boss_mode = False
    
    while not mode_selected:
        screen.fill(BACKGROUND)
        
        # Title
        title_text = title_font.render("TETRIZZ", True, ACCENT)
        title_rect = title_text.get_rect(center=(WINDOW_WIDTH // 2, 150))
        screen.blit(title_text, title_rect)
        
        # Mode options
        classic_text = font.render("1 - Classic Mode", True, TEXT_PRIMARY)
        classic_rect = classic_text.get_rect(center=(WINDOW_WIDTH // 2, 250))
        screen.blit(classic_text, classic_rect)
        
        boss_text = font.render("2 - Boss Fight Mode", True, BOSS_COLOR)
        boss_rect = boss_text.get_rect(center=(WINDOW_WIDTH // 2, 300))
        screen.blit(boss_text, boss_rect)
        
        instruction_text = font.render("Press 1 or 2 to select mode", True, TEXT_SECONDARY)
        instruction_rect = instruction_text.get_rect(center=(WINDOW_WIDTH // 2, 400))
        screen.blit(instruction_text, instruction_rect)
        
        pygame.display.flip()
        
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()
            elif event.type == pygame.KEYDOWN:
                if event.key == pygame.K_1:
                    pygame.mixer.music.load('music/tetrizz.mp3')
                    pygame.mixer.music.play(-1)
                    pygame.mixer.music.set_volume(0.5)
                    boss_mode = False
                    mode_selected = True
                elif event.key == pygame.K_2:
                    pygame.mixer.music.load('music/TETrizzz.mp3')
                    pygame.mixer.music.play(-1)
                    pygame.mixer.music.set_volume(0.5)
                    boss_mode = True
                    mode_selected = True
                elif event.key == pygame.K_ESCAPE:
                    pygame.quit()
                    sys.exit()
    
    # Initialize game
    game = TetrisGame(boss_mode)
    running = True
    game_over = False
    
    while running:
        dt = clock.tick(60)
        
        # Handle events
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
            
            elif event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE:
                    running = False
                
                elif game_over or game.game_won:
                    if event.key == pygame.K_r:
                        # Restart game
                        game = TetrisGame(boss_mode)
                        game_over = False
                
                else:  # Game is active
                    if event.key == pygame.K_LEFT or event.key == pygame.K_a:
                        game.move_piece(-1, 0)
                    elif event.key == pygame.K_RIGHT or event.key == pygame.K_d:
                        game.move_piece(1, 0)
                    elif event.key == pygame.K_DOWN or event.key == pygame.K_s:
                        if game.move_piece(0, 1):
                            game.score += 1
                    elif event.key == pygame.K_UP or event.key == pygame.K_w:
                        game.rotate_piece()
                    elif event.key == pygame.K_SPACE:
                        game.hard_drop()
        
        # Update game
        if not game_over and not game.game_won:
            if not game.update(dt):
                game_over = True
        
        # Draw everything
        game.draw(screen)
        
        # Game over screen
        if game_over and not game.game_won:
            overlay = pygame.Surface((WINDOW_WIDTH, WINDOW_HEIGHT))
            overlay.set_alpha(200)
            overlay.fill((0, 0, 0))
            screen.blit(overlay, (0, 0))
            
            font_large = pygame.font.Font(None, 72)
            font_medium = pygame.font.Font(None, 36)
            
            game_over_text = font_large.render("GAME OVER", True, DANGER)
            game_over_rect = game_over_text.get_rect(center=(WINDOW_WIDTH // 2, WINDOW_HEIGHT // 2 - 50))
            screen.blit(game_over_text, game_over_rect)
            
            if boss_mode and game.boss and game.boss.health > 0:
                boss_health_text = font_medium.render(f"Boss Health Remaining: {game.boss.health}/100", True, BOSS_COLOR)
                boss_health_rect = boss_health_text.get_rect(center=(WINDOW_WIDTH // 2, WINDOW_HEIGHT // 2))
                screen.blit(boss_health_text, boss_health_rect)
            
            score_text = font_medium.render(f"Final Score: {game.score:,}", True, TEXT_PRIMARY)
            score_rect = score_text.get_rect(center=(WINDOW_WIDTH // 2, WINDOW_HEIGHT // 2 + 40))
            screen.blit(score_text, score_rect)
            
            restart_text = font_medium.render("Press R to restart or ESC to quit", True, TEXT_SECONDARY)
            restart_rect = restart_text.get_rect(center=(WINDOW_WIDTH // 2, WINDOW_HEIGHT // 2 + 80))
            screen.blit(restart_text, restart_rect)
        
        pygame.display.flip()
    
    pygame.quit()
    sys.exit()

if __name__ == "__main__":
    main()