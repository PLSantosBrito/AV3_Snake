import pygame
import sys
import random

# Configurações do jogo
WIDTH, HEIGHT = 800, 600
GRID_SIZE = 20
FPS = 10

# Cores
colors = {
    'white': (255, 255, 255),
    'green': (0, 255, 0),
    'red': (255, 0, 0),
}

maybe_score = lambda score: 1 if score == None else score
adjust_speed = lambda score:lambda mult: FPS + maybe_score(score) * mult #crescimento de velocidade esta estrapolado para que dê para notar

class Snake:
    def __init__(self):
        self.body = [(400, 300), (400 - GRID_SIZE, 300)]
        self.direction = (1, 0)

    def move(self, food):
        head = self.body[0]
        new_head = (head[0] + self.direction[0] * GRID_SIZE, head[1] + self.direction[1] * GRID_SIZE)
        self.body.insert(0, new_head)

        if new_head == food.position:
            food.spawn()
            return True
        else:
            self.body.pop()
            return False

    def check_collision(self, obstacles):
        head = self.body[0]
        if (
            head[0] < 0 or head[0] >= WIDTH or head[1] < 0 or head[1] >= HEIGHT or
            head in obstacles or
            head in self.body[1:]  # Verifica se a cabeça colide com o corpo
        ):
            return True  # Colisão com as bordas da tela, com as pedras ou com a própria cobra
        return False

    def set_direction(self, direction):
        # Verificar se a nova direção não é oposta à direção atual
        if (direction[0] * -1, direction[1] * -1) != self.direction:
            self.direction = direction

    def draw(self, screen):
        for segment in self.body:
            pygame.draw.rect(screen, colors['green'], (*segment, GRID_SIZE, GRID_SIZE))

class Food:
    def __init__(self, obstacles):
        self.position = (400, 200)
        self.obstacles = obstacles  # Armazena a lista de obstáculos

    def spawn(self):
        while True:
            self.position = (
                random.randint(0, (WIDTH - GRID_SIZE) // GRID_SIZE) * GRID_SIZE,
                random.randint(0, (HEIGHT - GRID_SIZE) // GRID_SIZE) * GRID_SIZE
            )
            if self.position not in self.obstacles:
                break

    def draw(self, screen):
        pygame.draw.rect(screen, colors['red'], (*self.position, GRID_SIZE, GRID_SIZE))

def draw_grid(screen, obstacles):
    for x in range(0, WIDTH, GRID_SIZE):
        pygame.draw.line(screen, colors['white'], (x, 0), (x, HEIGHT))
    for y in range(0, HEIGHT, GRID_SIZE):
        pygame.draw.line(screen, colors['white'], (0, y), (WIDTH, y))
    for obstacle in obstacles:
        pygame.draw.rect(screen, colors['white'], (*obstacle, GRID_SIZE, GRID_SIZE))

def draw_score(screen, score):
    font = pygame.font.SysFont(None, 36)
    text = font.render(f"Score: {score}", True, colors['white'])
    screen.blit(text, (10, 10))

def ler_mapas_do_arquivo(nome_arquivo):
    with open(nome_arquivo, 'r') as file:
        conteudo = file.read()

    mapas = {}
    mapas_em_texto = conteudo.split('\n\n')

    for mapa_em_texto in mapas_em_texto:
        linhas = mapa_em_texto.strip().split('\n')
        nome_mapa = linhas[0].strip()
        matriz_mapa = [list(map(int, linha.split())) for linha in linhas[1:]]
        mapas[nome_mapa] = matriz_mapa

    return mapas

def trocar_mapa(mapas, mapa_atual):
    mapas_disponiveis = list(mapas.keys())
    indice_mapa_atual = mapas_disponiveis.index(mapa_atual)
    proximo_indice = (indice_mapa_atual + 1) % len(mapas_disponiveis)
    return mapas_disponiveis[proximo_indice]

def mostrar_tela_vitoria(screen):
    font = pygame.font.SysFont(None, 48)
    text = font.render("Vitória!", True, colors['green'])
    text_rect = text.get_rect(center=(WIDTH // 2, HEIGHT // 2))
    screen.blit(text, text_rect)

def main(mapas_selecionados):
    pygame.init()
    screen = pygame.display.set_mode((WIDTH, HEIGHT))
    pygame.display.set_caption("Snake Game")

    clock = pygame.time.Clock()

    # Ler mapas do arquivo
    mapas = ler_mapas_do_arquivo('C:\\Users\\ogarf\\Desktop\\Faculdade\\Prog_Func\\AV3_Func\\Sprint4\\mapas.txt')

    # Inicializar variáveis
    mapas_disponiveis = list(mapas.keys())
    mapa_atual = mapas_selecionados.pop(0)
    map_matrix = mapas[mapa_atual]
    obstacles = [(j * GRID_SIZE, i * GRID_SIZE) for i, row in enumerate(map_matrix) for j, value in enumerate(row) if value == 1]

    snake = Snake()
    food = Food(obstacles)
    score = 0
    mapa_atual = None
    while True:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()
            elif event.type == pygame.KEYDOWN:
                if event.key == pygame.K_UP:
                    snake.set_direction((0, -1))
                elif event.key == pygame.K_DOWN:
                    snake.set_direction((0, 1))
                elif event.key == pygame.K_LEFT:
                    snake.set_direction((-1, 0))
                elif event.key == pygame.K_RIGHT:
                    snake.set_direction((1, 0))

        if snake.move(food):
            score += 1

        if snake.check_collision(obstacles):
            pygame.quit()
            sys.exit()

        screen.fill((0, 0, 0))
        draw_grid(screen, obstacles)
        snake.draw(screen)
        food.draw(screen)
        draw_score(screen, score)

        pygame.display.flip()
        clock.tick(adjust_speed(score)(30))

        # Verificar se o score atingiu 2 e trocar de mapa
        if score == 5:
            if mapas_selecionados:
                mapa_atual = mapas_selecionados.pop(0)
                map_matrix = mapas[mapa_atual]
                obstacles = [(j * GRID_SIZE, i * GRID_SIZE) for i, row in enumerate(map_matrix) for j, value in enumerate(row) if value == 1]
                snake = Snake()  # Reiniciar a posição da cobra
                food = Food(obstacles)  # Recolocar a comida em um novo local
                score = 0  # Reiniciar o score
            else:
                # Exibir mensagem de vitória na tela
                mostrar_tela_vitoria(screen)
                pygame.display.flip()  # Atualizar a tela para exibir a mensagem
                pygame.time.delay(2000)  # Esperar 2 segundos
                pygame.quit()
                sys.exit()

            pygame.display.flip()
        clock.tick(FPS)


if __name__ == "__main__":
    mapas_selecionados = ['mapa1', 'mapa2', 'mapa3']
    main(mapas_selecionados)



