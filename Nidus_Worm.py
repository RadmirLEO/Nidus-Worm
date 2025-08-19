import pygame
import sys
import random

#Настройки 
WIDTH, HEIGHT = 600, 600
GRID_SIZE = 20
GRID_WIDTH = WIDTH // GRID_SIZE
GRID_HEIGHT = HEIGHT // GRID_SIZE

#Цвета
WHITE = (255, 255, 255)
GRAY = (120, 120, 120)
BLACK = (0, 0, 0)
RED = (255, 50, 50)
GREEN = (0, 255, 0)
DARK_GREEN = (15, 56, 15)
DANGER_RED = (120, 0, 0)
YELLOW = (255, 255, 0)
FOOD_COLOR = (255, 50, 50)

#  Pygame 
pygame.init()
screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("Червь Нидуса")
font = pygame.font.SysFont('arial', 24)
clock = pygame.time.Clock()

#  Таймер 
GAME_DURATION = 60000  # 60 сек
TIME_BONUS = 5000      # +5 сек за еду

# Направления 
UP = (0, -1)
DOWN = (0, 1)
LEFT = (-1, 0)
RIGHT = (1, 0)

# Меню
def draw_text(text, size, color, x, y, center=True):
    fnt = pygame.font.SysFont("arial", size)
    txt = fnt.render(text, True, color)
    rect = txt.get_rect()
    rect.center = (x, y) if center else (x, y)
    screen.blit(txt, rect)

def show_rules():
    running = True
    while running:
        screen.fill(BLACK)
        rules = [
            "Цель: набрать 200 очков",
            "E — телепорт (раз в 30 сек)",
            "Клик мышью — место телепорта",
            "Красные клетки — опасны",
            "Еда даёт +5 секунд",
            "↑ ↓ ← → — движение, ESC — выход"
        ]
        draw_text("ПРАВИЛА", 36, YELLOW, WIDTH//2, 50)
        for i, line in enumerate(rules):
            draw_text(line, 22, WHITE, WIDTH//2, 120 + i * 40)
        draw_text("Нажмите любую клавишу", 20, GRAY, WIDTH//2, HEIGHT - 40)
        pygame.display.update()
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit(); sys.exit()
            elif event.type == pygame.KEYDOWN:
                running = False

def main_menu():
    while True:
        screen.fill(BLACK)
        draw_text("ЧЕРВЬ НИДУСА", 48, GREEN, WIDTH//2, HEIGHT//4)
        draw_text("1. Начать игру", 28, WHITE, WIDTH//2, HEIGHT//2 - 30)
        draw_text("2. Правила", 28, WHITE, WIDTH//2, HEIGHT//2 + 10)
        draw_text("3. Выход", 28, WHITE, WIDTH//2, HEIGHT//2 + 50)
        pygame.display.update()

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit(); sys.exit()
            elif event.type == pygame.KEYDOWN:
                if event.key == pygame.K_1:
                    return
                elif event.key == pygame.K_2:
                    show_rules()
                elif event.key == pygame.K_3 or event.key == pygame.K_ESCAPE:
                    pygame.quit(); sys.exit()

#  Классы 
class Snake:
    def __init__(self):
        self.positions = [(GRID_WIDTH//2, GRID_HEIGHT//2)]
        self.direction = random.choice([UP, DOWN, LEFT, RIGHT])
        self.grow_to = 3
        self.score = 0
        self.last_teleport = -30000
        self.waiting_for_click = False

    def head(self):
        return self.positions[0]

    def move(self):
        x, y = self.direction
        hx, hy = self.head()
        new_pos = ((hx + x) % GRID_WIDTH, (hy + y) % GRID_HEIGHT)
        if new_pos in self.positions[1:]:
            return False
        self.positions.insert(0, new_pos)
        if len(self.positions) > self.grow_to:
            self.positions.pop()
        return True

    def draw(self):
        for i, (x, y) in enumerate(self.positions):
            color = GREEN if i == 0 else (0, 200, 0)
            pygame.draw.rect(screen, color, (x * GRID_SIZE, y * GRID_SIZE, GRID_SIZE, GRID_SIZE))

    def change_direction(self, d):
        if (d[0]*-1, d[1]*-1) != self.direction:
            self.direction = d

    def start_teleport(self, current_time):
        if current_time - self.last_teleport >= 30000:
            self.waiting_for_click = True

    def do_teleport(self, pos, safe_margin):
        x, y = pos
        if (safe_margin <= x < GRID_WIDTH - safe_margin and
            safe_margin <= y < GRID_HEIGHT - safe_margin):
            self.positions[0] = (x, y)
            self.last_teleport = pygame.time.get_ticks()
        self.waiting_for_click = False

class Food:
    def __init__(self, snake):
        self.snake = snake
        self.position = (0, 0)
        self.place(0)

    def place(self, safe_margin):
        while True:
            x = random.randint(safe_margin, GRID_WIDTH - safe_margin - 1)
            y = random.randint(safe_margin, GRID_HEIGHT - safe_margin - 1)
            if (x, y) not in self.snake.positions:
                self.position = (x, y)
                break

    def draw(self):
        rect = pygame.Rect((self.position[0]*GRID_SIZE, self.position[1]*GRID_SIZE), (GRID_SIZE, GRID_SIZE))
        pygame.draw.rect(screen, FOOD_COLOR, rect)
        pygame.draw.circle(screen, WHITE, rect.center, 5)

#  Вспомогательные функции 
def draw_grid():
    for x in range(0, WIDTH, GRID_SIZE):
        pygame.draw.line(screen, GRAY, (x, 0), (x, HEIGHT))
    for y in range(0, HEIGHT, GRID_SIZE):
        pygame.draw.line(screen, GRAY, (0, y), (WIDTH, y))

def draw_restricted_zone(safe_margin):
    for x in range(GRID_WIDTH):
        for y in range(GRID_HEIGHT):
            if x < safe_margin or x >= GRID_WIDTH - safe_margin or y < safe_margin or y >= GRID_HEIGHT - safe_margin:
                pygame.draw.rect(screen, DANGER_RED, (x * GRID_SIZE, y * GRID_SIZE, GRID_SIZE, GRID_SIZE))

def draw_score_and_timer(score, time_left):
    draw_text(f"Очки: {score}", 20, WHITE, 40, 20, center=False)
    draw_text(f"Время: {max(0, time_left // 1000)}", 20, WHITE, WIDTH - 450, 20, center=False)

#  Игровой цикл 
def run_game():
    snake = Snake()
    food = Food(snake)
    safe_margin = 0

    game_start = pygame.time.get_ticks()
    zone_update_time = pygame.time.get_ticks()

    while True:
        current_time = pygame.time.get_ticks()
        time_left = GAME_DURATION - (current_time - game_start)
        if time_left <= 0:
            return "Время вышло!"

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit(); sys.exit()
            elif event.type == pygame.KEYDOWN:
                if event.key == pygame.K_UP: snake.change_direction(UP)
                if event.key == pygame.K_DOWN: snake.change_direction(DOWN)
                if event.key == pygame.K_LEFT: snake.change_direction(LEFT)
                if event.key == pygame.K_RIGHT: snake.change_direction(RIGHT)
                if event.key == pygame.K_e:
                    snake.start_teleport(current_time)
            elif event.type == pygame.MOUSEBUTTONDOWN and snake.waiting_for_click:
                mx, my = pygame.mouse.get_pos()
                gx, gy = mx // GRID_SIZE, my // GRID_SIZE
                snake.do_teleport((gx, gy), safe_margin)

        if not snake.waiting_for_click:
            if not snake.move():
                return "Вы врезались в себя!"

        if snake.head() == food.position:
            snake.grow_to += 1
            snake.score += 10
            game_start += TIME_BONUS
            food.place(safe_margin)

        hx, hy = snake.head()
        if hx < safe_margin or hx >= GRID_WIDTH - safe_margin or hy < safe_margin or hy >= GRID_HEIGHT - safe_margin:
            return "Вы зашли в красную зону!"

        if current_time - zone_update_time > 10000:
            safe_margin += 1
            zone_update_time = current_time

        # Обновить если еда на красной зоне
        fx, fy = food.position
        if fx < safe_margin or fx >= GRID_WIDTH - safe_margin or fy < safe_margin or fy >= GRID_HEIGHT - safe_margin:
            food.place(safe_margin)

        screen.fill(DARK_GREEN)
        draw_restricted_zone(safe_margin)
        draw_grid()
        snake.draw()
        food.draw()
        draw_score_and_timer(snake.score, time_left)
        pygame.display.update()
        clock.tick(10)

        if snake.score >= 200:
            return "Ты победил!"

# === Запуск ===
if __name__ == "__main__":
    
    main_menu()
    while True:
            result = run_game()
            screen.fill(BLACK)
            draw_text(result, 36, RED, WIDTH//2, HEIGHT//2)
            draw_text("Нажмите R чтобы начать заново", 22, WHITE, WIDTH//2, HEIGHT//2 + 50)
            draw_text("Нажмите ESC чтобы выйти", 22, WHITE, WIDTH//2, HEIGHT//2 + 80)
            pygame.display.update()

            waiting = True
            while waiting:
                for event in pygame.event.get():
                    if event.type == pygame.QUIT:
                        pygame.quit(); sys.exit()
                    elif event.type == pygame.KEYDOWN:
                        if event.key == pygame.K_r:
                            waiting = False  # Запустим игру заново
                        elif event.key == pygame.K_ESCAPE:
                            pygame.quit(); sys.exit()