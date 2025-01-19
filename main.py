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

# Создание экрана
screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("Block Blast")

# Шрифт
font = pygame.font.Font(None, 36)

# Игровое поле
board = [[0 for _ in range(GRID_SIZE)] for _ in range(GRID_SIZE)]

# Генерация случайного блока
def generate_block():
    shapes = [
        [[1, 1],
         [1, 1]],

        [[1, 1, 1],
         [0, 1, 0]],

        [[1, 1, 1]],

        [[1],
         [1],
         [1]]
    ]
    shape = random.choice(shapes)
    return shape

# Проверка на возможность размещения блока
def can_place_block(board, block, x, y):
    for i, row in enumerate(block):
        for j, cell in enumerate(row):
            if cell:
                if (x + j >= GRID_SIZE or y + i >= GRID_SIZE or
                        board[y + i][x + j] != 0):
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
    block_positions = [(50, BOARD_HEIGHT + i * 120) for i in range(3)]
    dragging = [False, False, False]
    score = 0

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
                    if bx <= mouse_x < bx + len(block[0]) * CELL_SIZE and by <= mouse_y < by + len(block) * CELL_SIZE:
                        dragging[i] = True
            elif event.type == pygame.MOUSEBUTTONUP:
                for i, drag in enumerate(dragging):
                    if drag:
                        dragging[i] = False
                        mouse_x, mouse_y = event.pos
                        grid_x = (mouse_x - mouse_x % CELL_SIZE) // CELL_SIZE
                        grid_y = (mouse_y - mouse_y % CELL_SIZE) // CELL_SIZE
                        if can_place_block(board, blocks[i], grid_x, grid_y):
                            place_block(board, blocks[i], grid_x, grid_y)
                            score += clear_lines(board)
                            blocks[i] = generate_block()
                            block_positions[i] = (50, BOARD_HEIGHT + i * 120)
            elif event.type == pygame.MOUSEMOTION:
                for i, drag in enumerate(dragging):
                    if drag:
                        block_positions[i] = (event.pos[0] - CELL_SIZE, event.pos[1] - CELL_SIZE)

        # Отрисовка поля
        for i in range(GRID_SIZE):
            for j in range(GRID_SIZE):
                rect = pygame.Rect(j * CELL_SIZE, i * CELL_SIZE, CELL_SIZE, CELL_SIZE)
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

        # Отображение счета
        score_text = font.render(f"Score: {score}", True, BLACK)
        screen.blit(score_text, (10, BOARD_HEIGHT + 10))

        pygame.display.flip()
        clock.tick(30)

    pygame.quit()

if __name__ == "__main__":
    main()
