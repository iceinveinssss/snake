from abc import ABC, abstractmethod
import pygame
import random
import sys

# Константы для размеров поля и сетки:
SCREEN_WIDTH, SCREEN_HEIGHT = 640, 480
GRID_SIZE = 20
GRID_WIDTH = 32  # 32 ячейки по горизонтали
GRID_HEIGHT = 24  # 24 ячейки по вертикали

# Направления движения:
UP = (0, -1)
DOWN = (0, 1)
LEFT = (-1, 0)
RIGHT = (1, 0)

# Цвета:
BOARD_BACKGROUND_COLOR = (0, 0, 0)
BORDER_COLOR = (93, 216, 228)
APPLE_COLOR = (255, 0, 0)
SNAKE_COLOR = (0, 255, 0)

# Скорость игры:
SPEED = 15

# Настройка игрового окна:
screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT), 0, 32)
pygame.display.set_caption('Змейка')
clock = pygame.time.Clock()

class GameObject():
    def __init__(self, body_color=None, position=None):
        self.body_color = body_color if body_color else (0, 0, 0)  # По умолчанию черный цвет
        self._position = position if position else (0, 0)  # По умолчанию (0, 0)
    
    @property
    def position(self):
        return self._position
    
    @position.setter
    def position(self, value):
        self._position = value
    
    @abstractmethod
    def draw(self):
        """Абстрактный метод для рисования объекта."""


class Apple(GameObject):
    def __init__(self):
        super().__init__(APPLE_COLOR, (random.randint(0, GRID_WIDTH-1) * GRID_SIZE, random.randint(0, GRID_HEIGHT-1) * GRID_SIZE))
    
    def randomize_position(self, snake_positions):
        """Перемещает яблоко в случайное место, проверяя, чтобы оно не попало на тело змейки."""
        while True:
            self.position = (random.randint(0, GRID_WIDTH-1) * GRID_SIZE, random.randint(0, GRID_HEIGHT-1) * GRID_SIZE)
            if self.position not in snake_positions:
                break

    def draw(self):
        rect = pygame.Rect(self.position, (GRID_SIZE, GRID_SIZE))
        pygame.draw.rect(screen, self.body_color, rect)
        pygame.draw.rect(screen, BORDER_COLOR, rect, 1)


class Snake(GameObject):
    def __init__(self):
        # Инициализация с передачей позиции как списка
        super().__init__(SNAKE_COLOR, [(GRID_WIDTH // 2 * GRID_SIZE, GRID_HEIGHT // 2 * GRID_SIZE)])
        self.positions = [(GRID_WIDTH // 2 * GRID_SIZE, GRID_HEIGHT // 2 * GRID_SIZE)]  # Инициализируем список позиций
        self.direction = RIGHT
        self.next_direction = RIGHT
        self.last = None
        self.growing = False
    
    @property
    def position(self):
        return self.positions[0]  # Возвращаем первую позицию как 'позицию' головы змейки

    @position.setter
    def position(self, value):
        self.positions[0] = value

    def get_head_position(self):
        return self.positions[0]

    def move(self):
        head_x, head_y = self.positions[0]
        new_head = (head_x + self.direction[0] * GRID_SIZE, head_y + self.direction[1] * GRID_SIZE)
        new_head = (new_head[0] % SCREEN_WIDTH, new_head[1] % SCREEN_HEIGHT)
        self.positions.insert(0, new_head)

        if not self.growing:
            self.positions.pop()
        else:
            self.growing = False
    
    def reset(self):
        self.positions = [(GRID_WIDTH // 2 * GRID_SIZE, GRID_HEIGHT // 2 * GRID_SIZE)]
        self.direction = RIGHT
        self.next_direction = RIGHT
        self.growing = False
    
    def update_direction(self):
        if self.next_direction:
            self.direction = self.next_direction
            self.next_direction = None

    def draw(self):
        for position in self.positions[:-1]:
            rect = pygame.Rect(position, (GRID_SIZE, GRID_SIZE))
            pygame.draw.rect(screen, self.body_color, rect)
            pygame.draw.rect(screen, BORDER_COLOR, rect, 1)
        
        head_rect = pygame.Rect(self.positions[0], (GRID_SIZE, GRID_SIZE))
        pygame.draw.rect(screen, self.body_color, head_rect)
        pygame.draw.rect(screen, BORDER_COLOR, head_rect, 1)


def handle_keys(game):
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            pygame.quit()
            sys.exit()
        elif event.type == pygame.KEYDOWN:
            if event.key == pygame.K_UP and game.snake.direction != DOWN:
                game.snake.next_direction = UP
            elif event.key == pygame.K_DOWN and game.snake.direction != UP:
                game.snake.next_direction = DOWN
            elif event.key == pygame.K_LEFT and game.snake.direction != RIGHT:
                game.snake.next_direction = LEFT
            elif event.key == pygame.K_RIGHT and game.snake.direction != LEFT:
                game.snake.next_direction = RIGHT


class Game:
    def __init__(self):
        self.snake = Snake()
        self.apple = Apple()
        self.score = 0
        self.game_over = False
    
    def update(self):
        if self.game_over:
            return
        
        self.snake.update_direction()
        self.snake.move()
        
        # Проверка на столкновение с яблоком:
        if self.snake.get_head_position() == self.apple.position:
            self.snake.growing = True  # Увеличиваем длину змейки
            self.apple.randomize_position(self.snake.positions)  # Перемещаем яблоко
            self.score += 1
        
        # Проверка на столкновение с самим собой:
        if len(self.snake.positions) != len(set(self.snake.positions)):
            self.game_over = True
    
    def game_over_screen(self):
        font = pygame.font.Font(None, 36)
        text = font.render(f"Game Over! Score: {self.score}", True, (255, 255, 255))
        screen.blit(text, (SCREEN_WIDTH // 4, SCREEN_HEIGHT // 2))
        pygame.display.flip()
        pygame.time.wait(2000)
    
    def draw(self):
        screen.fill(BOARD_BACKGROUND_COLOR)
        self.snake.draw()
        self.apple.draw()
        
        # Отображение счета:
        font = pygame.font.Font(None, 36)
        score_text = font.render(f"Score: {self.score}", True, (255, 255, 255))
        screen.blit(score_text, (10, 10))
        
        pygame.display.flip()


def main():
    pygame.init()
    game = Game()

    while True:
        clock.tick(SPEED)
        handle_keys(game)
        game.update()

        if game.game_over:
            game.game_over_screen()
            break

        game.draw()


if __name__ == '__main__':
    main()
