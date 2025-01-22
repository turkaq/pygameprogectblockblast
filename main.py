import pygame
import random

# Инициализация Pygame
pygame.init()

# Размеры окна и поля
WIDTH, HEIGHT = 400, 700
GRID_SIZE = 8
CELL_SIZE = 40
BOARD_WIDTH = GRID_SIZE * CELL_SIZE
BOARD_HEIGHT = GRID_SIZE * CELL_SIZE
MARGIN_TOP = 50  # Отступ сверху для счётчика

# Цвета
WHITE = (255, 255, 255)
BLACK = (0, 0, 0)
GRAY = (200, 200, 200)
BLUE = (0, 102, 204)

# Создание экрана
screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("Block Blast")

# Шрифт
font = pygame.font.Font(None, 36)

# Игровое поле
board = [[0 for _ in range(GRID_SIZE)] for _ in range(GRID_SIZE)]

# Генерация случайного блока
def generate_block():
    width = random.randint(1, 3)  # Ширина от 1 до 3 клеток
    height = random.randint(1, 3)  # Высота от 1 до 3 клеток
    block = [[random.choice([0, 1]) for _ in range(width)] for _ in range(height)]

    # Гарантируем, что хотя бы одна клетка блока будет заполнена
    if not any(cell for row in block for cell in row):
        block[random.randint(0, height - 1)][random.randint(0, width - 1)] = 1

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

# Основной игровой цикл
def main():
    running = True
    clock = pygame.time.Clock()

    # Переменные игры
    blocks = [generate_block() for _ in range(3)]
    active_block_index = -1
    dragging = False
    score = 0

    # Позиции для блоков
    block_positions = [(WIDTH // 4 * i + 30, BOARD_HEIGHT + MARGIN_TOP + 20) for i in range(3)]

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
                    grid_x = (mouse_x - (CELL_SIZE * len(blocks[active_block_index][0]) // 2)) // CELL_SIZE
                    grid_y = (mouse_y - MARGIN_TOP - (CELL_SIZE * len(blocks[active_block_index]) // 2)) // CELL_SIZE
                    if can_place_block(board, blocks[active_block_index], grid_x, grid_y):
                        place_block(board, blocks[active_block_index], grid_x, grid_y)
                        score += clear_lines(board)
                        blocks[active_block_index] = generate_block()
                    block_positions[active_block_index] = (WIDTH // 4 * active_block_index + 30, BOARD_HEIGHT + MARGIN_TOP + 20)
                    active_block_index = -1
            elif event.type == pygame.MOUSEMOTION and dragging and active_block_index != -1:
                mouse_x, mouse_y = event.pos
                block_positions[active_block_index] = (mouse_x - (CELL_SIZE * len(blocks[active_block_index][0]) // 2),
                                                      mouse_y - (CELL_SIZE * len(blocks[active_block_index]) // 2))

        # Отрисовка поля
        for i in range(GRID_SIZE):
            for j in range(GRID_SIZE):
                rect = pygame.Rect(j * CELL_SIZE, i * CELL_SIZE + MARGIN_TOP, CELL_SIZE, CELL_SIZE)
                pygame.draw.rect(screen, GRAY if board[i][j] else WHITE, rect)
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

        # Отображение счета (по центру над полем)
        score_text = font.render(f"Score: {score}", True, BLACK)
        score_x = (WIDTH - score_text.get_width()) // 2
        screen.blit(score_text, (score_x, 10))

        pygame.display.flip()
        clock.tick(30)

    pygame.quit()

if __name__ == "__main__":
    main()
