import pygame
import random

# Инициализация Pygame
pygame.init()

# Размеры окна и поля
WIDTH, HEIGHT = 400, 600
GRID_SIZE = 8
CELL_SIZE = 40
BOARD_WIDTH = GRID_SIZE * CELL_SIZE
BOARD_HEIGHT = GRID_SIZE * CELL_SIZE

# Цвета
WHITE = (255, 255, 255)
BLACK = (0, 0, 0)
GRAY = (200, 200, 200)
BLUE = (0, 102, 204)
RED = (255, 0, 0)

# Создание экрана
screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("Block Blast")

# Шрифт
font = pygame.font.Font(None, 36)

# Игровое поле
board = [[0 for _ in range(GRID_SIZE)] for _ in range(GRID_SIZE)]

# Позиция игрового поля по центру экрана
BOARD_OFFSET_X = (WIDTH - BOARD_WIDTH) // 2
BOARD_OFFSET_Y = (HEIGHT - BOARD_HEIGHT) // 2

# Генерация случайного блока, который можно поставить на поле
def generate_block():
    # Генерация случайного размера блока (от 1x1 до 4x4)
    width = random.randint(1, 4)
    height = random.randint(1, 4)
    block = [[1 for _ in range(width)] for _ in range(height)]
    return block

# Проверка на возможность размещения блока на сетке
def can_place_block(board, block, x, y):
    for i, row in enumerate(block):
        for j, cell in enumerate(row):
            if cell:
                board_x = x + j
                board_y = y + i
                if board_x < 0 or board_x >= GRID_SIZE or board_y < 0 or board_y >= GRID_SIZE or board[board_y][board_x] != 0:
                    return False
    return True

# Размещение блока на поле
def place_block(board, block, x, y):
    for i, row in enumerate(block):
        for j, cell in enumerate(row):
            if cell:
                board[y + i][x + j] = 1

# Удаление заполненных линий
def clear_lines(board):
    cleared = 0
    # Проверка строк
    for i in range(GRID_SIZE):
        if all(board[i]):
            cleared += 1
            board.pop(i)
            board.insert(0, [0] * GRID_SIZE)

    # Проверка столбцов
    for j in range(GRID_SIZE):
        if all(row[j] for row in board):
            cleared += 1
            for row in board:
                row[j] = 0

    return cleared

# Главное меню
def main_menu():
    menu_font = pygame.font.Font(None, 48)
    title_text = menu_font.render("Block Blast", True, BLUE)
    start_text = font.render("Нажмите SPACE чтобы начать", True, BLACK)

    while True:
        screen.fill(WHITE)
        screen.blit(title_text, (WIDTH // 2 - title_text.get_width() // 2, HEIGHT // 3))
        screen.blit(start_text, (WIDTH // 2 - start_text.get_width() // 2, HEIGHT // 2))

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                return False  # Возвращаем False, чтобы выйти из игры
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_SPACE:
                    return True  # Возвращаем True, чтобы начать игру

        pygame.display.flip()

# Экран окончания игры
def game_over_screen(score):
    menu_font = pygame.font.Font(None, 48)
    game_over_text = menu_font.render("Игра Окончена", True, RED)
    score_text = font.render(f"Счет: {score}", True, BLACK)
    restart_text = font.render("Нажмите SPACE чтобы начать заново", True, BLACK)

    while True:
        screen.fill(WHITE)
        screen.blit(game_over_text, (WIDTH // 2 - game_over_text.get_width() // 2, HEIGHT // 3))
        screen.blit(score_text, (WIDTH // 2 - score_text.get_width() // 2, HEIGHT // 2))
        screen.blit(restart_text, (WIDTH // 2 - restart_text.get_width() // 2, HEIGHT * 2 // 3))

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                return False  # Возвращаем False, чтобы выйти из игры
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_SPACE:
                    return True  # Возвращаем True, чтобы начать игру заново

        pygame.display.flip()

# Основной игровой цикл
def main():
    running = True
    clock = pygame.time.Clock()

    # Переменные игры
    blocks = [generate_block() for _ in range(3)]
    active_block_index = -1
    dragging = False
    score = 0
    multiplier = 1  # Множитель очков
    no_clear_counter = 0  # Счетчик ходов без уничтожения линий

    # Позиции для блоков
    block_positions = [(WIDTH // 4 * i + 30, HEIGHT - 100) for i in range(3)]

    while running:
        screen.fill(WHITE)

        # Обработка событий
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
            elif event.type == pygame.MOUSEBUTTONDOWN:
                mouse_x, mouse_y = event.pos
                for i, (block, pos) in enumerate(zip(blocks, block_positions)):
                    bx, by = pos
                    block_width = len(block[0]) * CELL_SIZE
                    block_height = len(block) * CELL_SIZE
                    if bx <= mouse_x < bx + block_width and by <= mouse_y < by + block_height:
                        active_block_index = i
                        dragging = True
                        break
            elif event.type == pygame.MOUSEBUTTONUP:
                if dragging and active_block_index != -1:
                    dragging = False
                    mouse_x, mouse_y = event.pos
                    # Преобразуем координаты в сетку
                    grid_x = (mouse_x - BOARD_OFFSET_X) // CELL_SIZE
                    grid_y = (mouse_y - BOARD_OFFSET_Y) // CELL_SIZE
                    if can_place_block(board, blocks[active_block_index], grid_x, grid_y):
                        place_block(board, blocks[active_block_index], grid_x, grid_y)
                        # Увеличиваем счет на количество клеток в блоке, умноженное на множитель
                        for row in blocks[active_block_index]:
                            score += sum(row) * multiplier
                        # Проверяем, уничтожаются ли линии
                        cleared_lines = clear_lines(board)
                        if cleared_lines > 0:
                            score += cleared_lines * 10 * multiplier  # Дополнительные очки за линии
                            multiplier += 1  # Увеличиваем множитель
                            no_clear_counter = 0  # Сбрасываем счетчик
                        else:
                            no_clear_counter += 1
                            if no_clear_counter >= 2:
                                multiplier = 1  # Сбрасываем множитель
                        blocks[active_block_index] = generate_block()
                        block_positions[active_block_index] = (WIDTH // 4 * active_block_index + 30, HEIGHT - 100)
                    else:
                        # Если блок нельзя поставить, игра завершается
                        running = False
                    active_block_index = -1
            elif event.type == pygame.MOUSEMOTION and dragging and active_block_index != -1:
                mouse_x, mouse_y = event.pos
                block_positions[active_block_index] = (mouse_x - (CELL_SIZE * len(blocks[active_block_index][0]) // 2),
                                                      mouse_y - (CELL_SIZE * len(blocks[active_block_index]) // 2))

        # Отрисовка поля
        for i in range(GRID_SIZE):
            for j in range(GRID_SIZE):
                rect = pygame.Rect(BOARD_OFFSET_X + j * CELL_SIZE, BOARD_OFFSET_Y + i * CELL_SIZE, CELL_SIZE, CELL_SIZE)
                pygame.draw.rect(screen, BLUE if board[i][j] else WHITE, rect)
                pygame.draw.rect(screen, BLACK, rect, 1)

        # Отрисовка блоков
        for i, (block, pos) in enumerate(zip(blocks, block_positions)):
            bx, by = pos
            for row_index, row in enumerate(block):
                for col_index, cell in enumerate(row):
                    if cell:
                        rect = pygame.Rect(bx + col_index * CELL_SIZE, by + row_index * CELL_SIZE, CELL_SIZE, CELL_SIZE)
                        pygame.draw.rect(screen, BLUE, rect)
                        pygame.draw.rect(screen, BLACK, rect, 1)

        # Отображение счета и множителя
        score_text = font.render(f"Score: {score}", True, BLACK)
        screen.blit(score_text, (10, 10))

        multiplier_text = font.render(f"Multiplier: x{multiplier}", True, BLACK)
        screen.blit(multiplier_text, (WIDTH - 150, 10))

        pygame.display.flip()
        clock.tick(30)

    return score

if __name__ == "__main__":
    while True:
        if not main_menu():  # Если в главном меню нажали на выход
            break  # Выход из игры
        score = main()  # Запуск игры
        if not game_over_screen(score):  # Если на экране окончания игры нажали на выход
            break  # Выход из игры