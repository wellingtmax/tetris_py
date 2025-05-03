import pygame
import random

# Inicializa o pygame
pygame.init()

# Cores
BLACK = (0, 0, 0)
WHITE = (255, 255, 255)
GRAY = (128, 128, 128)
COLORS = [
    (0, 255, 255),  # I - Ciano
    (0, 0, 255),    # J - Azul
    (255, 165, 0),  # L - Laranja
    (255, 255, 0),  # O - Amarelo
    (0, 255, 0),    # S - Verde
    (128, 0, 128),  # T - Roxo
    (255, 0, 0)     # Z - Vermelho
]

# Configurações do jogo
BLOCK_SIZE = 30
GRID_WIDTH = 10
GRID_HEIGHT = 20
SCREEN_WIDTH = BLOCK_SIZE * (GRID_WIDTH + 6)
SCREEN_HEIGHT = BLOCK_SIZE * GRID_HEIGHT
GAME_AREA_LEFT = BLOCK_SIZE
NEXT_PIECE_POS = (GAME_AREA_LEFT + GRID_WIDTH * BLOCK_SIZE + 20, 150)

# Formas das peças (tetrominós)
SHAPES = [
    [[1, 1, 1, 1]],  # I
    
    [[1, 0, 0],
     [1, 1, 1]],     # J
     
    [[0, 0, 1],
     [1, 1, 1]],     # L
     
    [[1, 1],
     [1, 1]],        # O
     
    [[0, 1, 1],
     [1, 1, 0]],     # S
     
    [[0, 1, 0],
     [1, 1, 1]],     # T
     
    [[1, 1, 0],
     [0, 1, 1]]      # Z
]

# Cria a tela
screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
pygame.display.set_caption("Tetris")

clock = pygame.time.Clock()

class Tetris:
    def __init__(self):
        self.grid = [[0 for _ in range(GRID_WIDTH)] for _ in range(GRID_HEIGHT)]
        self.current_piece = None
        self.next_piece = self.create_new_piece()
        self.game_over = False
        self.score = 0
        self.level = 1
        self.fall_speed = 0.5  # segundos
        self.fall_time = 0
        self.new_piece()  # Gera a primeira peça
    
    def create_new_piece(self):
        shape = random.choice(SHAPES)
        color = COLORS[SHAPES.index(shape)]
        return {"shape": shape, "color": color, "x": 0, "y": 0}
    
    def new_piece(self):
        self.current_piece = self.next_piece
        self.next_piece = self.create_new_piece()
        # Posição inicial (centro no topo)
        self.current_piece["x"] = GRID_WIDTH // 2 - len(self.current_piece["shape"][0]) // 2
        self.current_piece["y"] = 0
    
    def valid_move(self, piece, x_offset=0, y_offset=0):
        for y, row in enumerate(piece["shape"]):
            for x, cell in enumerate(row):
                if cell:
                    new_x = piece["x"] + x + x_offset
                    new_y = piece["y"] + y + y_offset
                    
                    if (new_x < 0 or new_x >= GRID_WIDTH or 
                        new_y >= GRID_HEIGHT or 
                        (new_y >= 0 and self.grid[new_y][new_x])):
                        return False
        return True
    
    def rotate_piece(self):
        rotated = [list(row) for row in zip(*self.current_piece["shape"][::-1])]
        old_shape = self.current_piece["shape"]
        self.current_piece["shape"] = rotated
        if not self.valid_move(self.current_piece):
            self.current_piece["shape"] = old_shape
    
    def lock_piece(self):
        for y, row in enumerate(self.current_piece["shape"]):
            for x, cell in enumerate(row):
                if cell:
                    if self.current_piece["y"] + y < 0:
                        self.game_over = True
                    else:
                        self.grid[self.current_piece["y"] + y][self.current_piece["x"] + x] = self.current_piece["color"]
        
        self.clear_lines()
        self.new_piece()
        
        if not self.valid_move(self.current_piece):
            self.game_over = True
    
    def clear_lines(self):
        lines_cleared = 0
        for y in range(GRID_HEIGHT):
            if all(self.grid[y]):
                lines_cleared += 1
                for y2 in range(y, 0, -1):
                    self.grid[y2] = self.grid[y2-1][:]
                self.grid[0] = [0 for _ in range(GRID_WIDTH)]
        
        if lines_cleared == 1:
            self.score += 100 * self.level
        elif lines_cleared == 2:
            self.score += 300 * self.level
        elif lines_cleared == 3:
            self.score += 500 * self.level
        elif lines_cleared == 4:
            self.score += 800 * self.level
        
        self.level = 1 + self.score // 5000
        self.fall_speed = max(0.05, 0.5 - (self.level - 1) * 0.05)
    
    def draw_next_piece(self):
        font = pygame.font.SysFont(None, 24)
        next_text = font.render("Next Piece:", True, WHITE)
        screen.blit(next_text, NEXT_PIECE_POS)
        
        # Calcula posição centralizada
        start_x = NEXT_PIECE_POS[0] + 10
        start_y = NEXT_PIECE_POS[1] + 40
        max_width = max(len(row) for row in self.next_piece["shape"])
        
        for y, row in enumerate(self.next_piece["shape"]):
            for x, cell in enumerate(row):
                if cell:
                    pygame.draw.rect(screen, self.next_piece["color"],
                                    (start_x + x * BLOCK_SIZE,
                                     start_y + y * BLOCK_SIZE,
                                     BLOCK_SIZE - 1, BLOCK_SIZE - 1))
                    pygame.draw.rect(screen, GRAY,
                                    (start_x + x * BLOCK_SIZE,
                                     start_y + y * BLOCK_SIZE,
                                     BLOCK_SIZE, BLOCK_SIZE), 1)
    
    def update(self, delta_time):
        if self.game_over:
            return
        
        self.fall_time += delta_time
        
        if self.fall_time >= self.fall_speed:
            self.fall_time = 0
            if self.valid_move(self.current_piece, 0, 1):
                self.current_piece["y"] += 1
            else:
                self.lock_piece()
    
    def draw(self):
        # Desenha a grade
        for y in range(GRID_HEIGHT):
            for x in range(GRID_WIDTH):
                pygame.draw.rect(screen, GRAY, 
                                (GAME_AREA_LEFT + x * BLOCK_SIZE, y * BLOCK_SIZE, 
                                 BLOCK_SIZE, BLOCK_SIZE), 1)
                if self.grid[y][x]:
                    pygame.draw.rect(screen, self.grid[y][x], 
                                    (GAME_AREA_LEFT + x * BLOCK_SIZE + 1, y * BLOCK_SIZE + 1, 
                                     BLOCK_SIZE - 2, BLOCK_SIZE - 2))
        
        # Desenha a peça atual
        if not self.game_over:
            for y, row in enumerate(self.current_piece["shape"]):
                for x, cell in enumerate(row):
                    if cell:
                        pygame.draw.rect(screen, self.current_piece["color"], 
                                        (GAME_AREA_LEFT + (self.current_piece["x"] + x) * BLOCK_SIZE + 1, 
                                         (self.current_piece["y"] + y) * BLOCK_SIZE + 1, 
                                         BLOCK_SIZE - 2, BLOCK_SIZE - 2))
        
        # Desenha informações
        info_x = GAME_AREA_LEFT + GRID_WIDTH * BLOCK_SIZE + 20
        font = pygame.font.SysFont(None, 36)
        score_text = font.render(f"Score: {self.score}", True, WHITE)
        screen.blit(score_text, (info_x, 50))
        level_text = font.render(f"Level: {self.level}", True, WHITE)
        screen.blit(level_text, (info_x, 100))
        
        # Desenha próxima peça
        self.draw_next_piece()
        
        # Game Over
        if self.game_over:
            game_over_font = pygame.font.SysFont(None, 48)
            game_over_text = game_over_font.render("GAME OVER", True, (255, 0, 0))
            screen.blit(game_over_text, 
                       (GAME_AREA_LEFT + GRID_WIDTH * BLOCK_SIZE // 2 - game_over_text.get_width() // 2, 
                        GRID_HEIGHT * BLOCK_SIZE // 2 - game_over_text.get_height() // 2))

def main():
    game = Tetris()
    running = True
    
    while running:
        delta_time = clock.tick(60) / 1000.0
        
        screen.fill(BLACK)
        
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
            
            if not game.game_over:
                if event.type == pygame.KEYDOWN:
                    if event.key == pygame.K_LEFT and game.valid_move(game.current_piece, -1, 0):
                        game.current_piece["x"] -= 1
                    elif event.key == pygame.K_RIGHT and game.valid_move(game.current_piece, 1, 0):
                        game.current_piece["x"] += 1
                    elif event.key == pygame.K_DOWN and game.valid_move(game.current_piece, 0, 1):
                        game.current_piece["y"] += 1
                    elif event.key == pygame.K_UP:
                        game.rotate_piece()
                    elif event.key == pygame.K_SPACE:
                        while game.valid_move(game.current_piece, 0, 1):
                            game.current_piece["y"] += 1
                        game.lock_piece()
        
        game.update(delta_time)
        game.draw()
        
        pygame.display.flip()
    
    pygame.quit()

if __name__ == "__main__":
    main()