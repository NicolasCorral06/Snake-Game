import pygame, random, json, os, time

# Variáveis do jogo
sw, sh = 800, 800  
block_size = 40
normal_speed = 10
current_speed = normal_speed
bg_color = (0, 0, 0)  
grid_color = (50, 50, 50)
snake_color = (0, 255, 0)
text_color = (255, 255, 255)
colisao = False  

red_color = (255, 0, 0)
blue_color = (0, 100, 255)
yellow_color =  (255, 255, 0)
purple_color = (128, 0, 128)

time_boost = 3 # Duração do boost
power_boost = 1.5 # Velocidade adicional 

# Cada maça e seus valores
APPLE_TYPES = {
    "red": {"color": red_color, "points": 1, "effect": None, "spawn_chance": 0.7},
    "blue": {"color": blue_color, "points": 2, "effect": None, "spawn_chance": 0.2},
    "yellow": {"color": yellow_color, "points": 3, "effect": None, "spawn_chance": 0.08},
    "purple": {"color": purple_color, "points": 1, "effect": "speed_boost", "spawn_chance": 0.1}
}

# Carrega a pontuação máxima
def load_high_score(score_file='snake_scores.json'):
    script_dir = os.path.dirname(os.path.abspath(__file__))
    score_path = os.path.join(script_dir, score_file)

    if os.path.exists(score_path):
        with open(score_path, 'r') as f:
            try:
                data = json.load(f)
                return data.get('high_score', 0)
            except json.JSONDecodeError:
                return 0
    return 0

# Salva a pontuação máxima
def save_high_score(score, score_file='snake_scores.json'):
    script_dir = os.path.dirname(os.path.abspath(__file__))
    score_path = os.path.join(script_dir, score_file)

    data = {'high_score': score}
    with open(score_path, 'w') as f:
        json.dump(data, f)

# Classe da cobra
class Snake:
    def __init__(self, sw, sh, block_size):
        self.sw = sw
        self.sh = sh
        self.block_size = block_size
        self.reset()
        
    def reset(self):
        self.x, self.y = self.block_size * 5, self.block_size * 5
        self.xdir, self.ydir = 1, 0
        self.body = []
        self.length = 1
        self.score = 0
        self.high_score = load_high_score()
        self.game_active = True
        self.speed_boost_active = False
        self.speed_boost_end_time = 0
        
    def update(self, colisao):
        if not self.game_active:
            return normal_speed 

        # Verifica se o boost acabou
        if self.speed_boost_active and time.time() > self.speed_boost_end_time:
            self.speed_boost_active = False

        # Atualiza posição da cabeça
        self.x += self.xdir * self.block_size
        self.y += self.ydir * self.block_size

        # Colisão com parede
        if colisao:
            if self.x >= self.sw or self.x < 0 or self.y >= self.sh or self.y < 0:
                self.game_over()
                return normal_speed
        else:
            if self.x >= self.sw:
                self.x = 0
            elif self.x < 0:
                self.x = self.sw - self.block_size
            if self.y >= self.sh:
                self.y = 0
            elif self.y < 0:
                self.y = self.sh - self.block_size

        self.body.append((self.x, self.y))
        if len(self.body) > self.length:
            self.body.pop(0)

        for segment in self.body[:-1]:
            if segment == (self.x, self.y):
                self.game_over()
                return normal_speed

        return int(normal_speed * 1.5) if self.speed_boost_active else normal_speed
            
    def draw(self, surface, snake_color):
        for segment in self.body:
            pygame.draw.rect(surface, snake_color, (*segment, self.block_size, self.block_size))
            pygame.draw.rect(surface, (0, 200, 0), (*segment, self.block_size, self.block_size), 1)
            
    def change_dir(self, x, y):
        # Impede que a cobra vá na direção oposta
        if (self.xdir * -1, self.ydir * -1) != (x, y):
            self.xdir, self.ydir = x, y
            
    def eat(self, food):
        if self.x == food.x and self.y == food.y:
            # Adiciona pontos
            self.score += food.points
            # Cresce de acordo com os pontos da maçã
            self.length += food.points
            
            # Aplica efeitos especiais
            if food.effect == "speed_boost":
                self.speed_boost_active = True
                self.speed_boost_end_time = time.time() + time_boost 
                return int(normal_speed * power_boost)  

            # Verifica recorde
            if self.score > self.high_score:
                self.high_score = self.score
                save_high_score(self.high_score)

            return True
        return False
    
    def game_over(self):
        self.game_active = False

# Classe da comida
class Food:
    def __init__(self, sw, sh, block_size):
        self.sw = sw
        self.sh = sh
        self.block_size = block_size
        self.spawn()
        
    def spawn(self):
        # Escolhe um tipo de maçã baseado nas probabilidades
        rand = random.random()
        cumulative_prob = 0
        
        for apple_type, attributes in APPLE_TYPES.items():
            cumulative_prob += attributes["spawn_chance"]
            if rand < cumulative_prob:
                self.type = apple_type
                self.color = attributes["color"]
                self.points = attributes["points"]
                self.effect = attributes["effect"]
                break
                
        self.x = random.randint(0, (self.sw - self.block_size) // self.block_size) * self.block_size
        self.y = random.randint(0, (self.sh - self.block_size) // self.block_size) * self.block_size
        
    def draw(self, surface):
        pygame.draw.rect(surface, self.color, (self.x, self.y, self.block_size, self.block_size))

# Desenha a grade
def draw_grid(surface, sw, sh, block_size, grid_color):
    for x in range(0, sw, block_size):
        pygame.draw.line(surface, grid_color, (x, 0), (x, sh))
    for y in range(0, sh, block_size):
        pygame.draw.line(surface, grid_color, (0, y), (sw, y))

# Mostra a pontuação e informações
def show_score(surface, snake, sw, text_color):
    font = pygame.font.SysFont('Arial', 25)
    font_small = pygame.font.SysFont('Arial', 20)
    
    score_text = font.render(f'Pontuação: {snake.score}', True, text_color)
    high_score_text = font.render(f'Recorde: {snake.high_score}', True, text_color)

    redApple_text = font_small.render(f'Vermelha: +1 ponto', True, text_color)
    blueApple_text = font_small.render(f'Azul: +2 pontos', True, text_color)
    yellowApple_text = font_small.render(f'Amarela: +3 pontos', True, text_color)
    purpleApple_text = font_small.render(f'Roxa: 1.5% boost', True, text_color)

    surface.blit(score_text, (10, 10))
    surface.blit(high_score_text, (10, 40))

    surface.blit(redApple_text, (10, 70))
    surface.blit(blueApple_text, (10, 100))
    surface.blit(yellowApple_text, (10, 130))
    surface.blit(purpleApple_text, (10, 160))

    # Mostra tempo de boost no canto superior direito
    if snake.speed_boost_active:
        time_left = max(0, snake.speed_boost_end_time - time.time())
        boost_text = font.render(f'Boost: {time_left:.1f}s', True, (128, 0, 128))
        surface.blit(boost_text, (sw - boost_text.get_width() - 10, 40))

# Tela de game over
def game_over_screen(surface, snake, sw, sh, text_color, bg_color):
    surface.fill(bg_color)
    font_large = pygame.font.SysFont('Arial', 50)
    font_medium = pygame.font.SysFont('Arial', 35)
    font_small = pygame.font.SysFont('Arial', 25)
    
    # Novo recorde
    if snake.score == snake.high_score and snake.score > 0:
        record_text = font_large.render('NOVO RECORDE!', True, (255, 215, 0))
        surface.blit(record_text, (sw//2 - record_text.get_width()//2, sh//2 - 150))
    
    # Textos de game over
    game_over_text = font_large.render('GAME OVER', True, text_color)
    score_text = font_medium.render(f'Pontuação: {snake.score}', True, text_color)
    high_score_text = font_medium.render(f'Recorde: {snake.high_score}', True, text_color)
    
    surface.blit(game_over_text, (sw//2 - game_over_text.get_width()//2, sh//2 - 80))
    surface.blit(score_text, (sw//2 - score_text.get_width()//2, sh//2 - 20))
    surface.blit(high_score_text, (sw//2 - high_score_text.get_width()//2, sh//2 + 20))
    
    # Instruções
    continue_text = font_small.render('Pressione ENTER para continuar', True, text_color)
    quit_text = font_small.render('Pressione ESC para sair', True, text_color)
    
    surface.blit(continue_text, (sw//2 - continue_text.get_width()//2, sh - 80))
    surface.blit(quit_text, (sw//2 - quit_text.get_width()//2, sh - 50))
    
    pygame.display.update()
    
    waiting = True
    while waiting:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                return False
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_RETURN:
                    waiting = False
                    return True  # Continuar
                if event.key == pygame.K_ESCAPE:
                    return False
    return False