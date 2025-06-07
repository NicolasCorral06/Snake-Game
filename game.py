import pygame
import sys
from gameClass import Snake, Food, draw_grid, show_score, game_over_screen, show_fps

# Inicialização do pygame
pygame.init()

# Variáveis do jogo
sw, sh = 800, 800  
block_size = 40 # tamanho de cada bloco
normal_speed = 10 
current_speed = normal_speed
bg_color = (0, 0, 0)  
grid_color = (50, 50, 50)
snake_color = (0, 255, 0)
text_color = (255, 255, 255)
colisao = False  

# Configuração da tela
screen = pygame.display.set_mode((sw, sh))
pygame.display.set_caption('Jogo da Cobrinha')
clock = pygame.time.Clock()

# Função principal
def main():
    global colisao, current_speed
    
    # as classes do outro arquivo
    snake = Snake(sw, sh, block_size)
    food = Food(sw, sh, block_size)
    
    # loop do jogo
    while True:
        #show_fps(clock)

        # checa os botões
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE:
                    pygame.quit()
                    sys.exit()
                if snake.game_active:
                    if event.key == pygame.K_UP:
                        snake.change_dir(0, -1)
                    if event.key == pygame.K_DOWN:
                        snake.change_dir(0, 1)
                    if event.key == pygame.K_LEFT:
                        snake.change_dir(-1, 0)
                    if event.key == pygame.K_RIGHT:
                        snake.change_dir(1, 0)
                    if event.key == pygame.K_c:  # Tecla C para alternar modo colisão/portal
                        colisao = not colisao
                else:
                    if event.key == pygame.K_RETURN:
                        snake.reset()
                        current_speed = normal_speed
        
        # inicia tudo
        if snake.game_active:
            screen.fill(bg_color)
            draw_grid(screen, sw, sh, block_size, grid_color)
            
            # Atualiza a cobra e verifica se houve mudança de velocidade
            speed_change = snake.update(colisao)
            if speed_change:
                current_speed = speed_change
                
            if snake.eat(food): 
                food.spawn()
                while (food.x, food.y) in snake.body:  # Garante q a comida n aparece na cobra
                    food.spawn()
            
            # desenha a comida, cobra e a pontuação
            food.draw(screen)
            snake.draw(screen, snake_color)
            show_score(screen, snake, sw, text_color)
            
            pygame.display.update()
            clock.tick(current_speed)
        else:
            if not game_over_screen(screen, snake, sw, sh, text_color, bg_color):
                pygame.quit()
                sys.exit()
            snake.reset()
            current_speed = normal_speed

# inicia o jogo
if __name__ == "__main__":
    main()