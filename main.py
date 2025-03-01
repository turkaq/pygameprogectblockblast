import pygame
import random
import os

# ---------- НАСТРОЙКИ ОКНА И ПОЛЯ ----------
WIDTH, HEIGHT = 600, 700
GRID_SIZE = 8
CELL_SIZE = 40
BOARD_WIDTH = GRID_SIZE * CELL_SIZE
BOARD_HEIGHT = GRID_SIZE * CELL_SIZE
BOARD_OFFSET_X = (WIDTH - BOARD_WIDTH) // 2
BOARD_OFFSET_Y = (HEIGHT - BOARD_HEIGHT) // 2

WHITE = (255, 255, 255)
BLACK = (0, 0, 0)
BLUE = (0, 102, 204)
RED = (255, 0, 0)
GREEN = (0, 255, 0)

SCORES_FILE = "scores.txt"

pygame.init()
screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("Block Blast")
font = pygame.font.Font(None, 36)

# Игровое поле: 8×8, 0 — пустая клетка
board = [[0]*GRID_SIZE for _ in range(GRID_SIZE)]


# ---------- ВСПОМОГАТЕЛЬНЫЕ ФУНКЦИИ ДЛЯ ПОЛЯ ----------
def reset_board():
    global board
    board = [[0]*GRID_SIZE for _ in range(GRID_SIZE)]

def draw_board():
    for row in range(GRID_SIZE):
        for col in range(GRID_SIZE):
            rect = pygame.Rect(
                BOARD_OFFSET_X + col*CELL_SIZE,
                BOARD_OFFSET_Y + row*CELL_SIZE,
                CELL_SIZE, CELL_SIZE
            )
            color = BLUE if board[row][col] else WHITE
            pygame.draw.rect(screen, color, rect)
            pygame.draw.rect(screen, BLACK, rect, 1)

def clear_lines(board):
    cleared = 0
    # Удаляем заполненные строки
    i = 0
    while i < GRID_SIZE:
        if all(board[i]):
            cleared += 1
            board.pop(i)
            board.insert(0, [0]*GRID_SIZE)
        else:
            i += 1
    # Удаляем заполненные столбцы
    j = 0
    while j < GRID_SIZE:
        if all(row[j] for row in board):
            cleared += 1
            for row in board:
                row[j] = 0
        j += 1
    return cleared

def can_place_any_block(board, blocks):
    """
    Проверяем, можно ли поставить хотя бы один блок из списка blocks.
    blocks — список объектов класса Block (описан ниже).
    """
    for block in blocks:
        for row in range(GRID_SIZE):
            for col in range(GRID_SIZE):
                if block.can_place(board, col, row):
                    return True
    return False


# ---------- КЛАСС ДЛЯ БЛОКА ----------
class Block:
    """
    Хранит:
    - shape: матрицу (обрезанную по краям), где 1 — занятая клетка
    - w, h: размеры shape
    - color: цвет блока
    - x, y: координаты ЛЕВОГО ВЕРХНЕГО угла bounding box на экране
    - (cx_cells, cy_cells): центр тяжести в координатах shape (в клетках)
    """
    def __init__(self, shape, color):
        trimmed = self.trim_shape(shape)
        self.shape = trimmed
        self.h = len(trimmed)
        self.w = len(trimmed[0]) if self.h else 0
        self.color = color

        # Координаты левого верхнего угла bounding box (в пикселях)
        self.x = 0
        self.y = 0

        # Считаем центр тяжести в координатах матрицы
        self.cx_cells, self.cy_cells = self.get_shape_center_in_cells()

    @staticmethod
    def trim_shape(shape):
        """
        Убирает пустые строки/столбцы по краям, возвращает «обрезанную» матрицу.
        """
        rows = len(shape)
        cols = max(len(row) for row in shape) if rows > 0 else 0

        min_row, max_row = rows, 0
        min_col, max_col = cols, 0

        for r in range(rows):
            for c in range(len(shape[r])):
                if shape[r][c] == 1:
                    if r < min_row:
                        min_row = r
                    if r > max_row:
                        max_row = r
                    if c < min_col:
                        min_col = c
                    if c > max_col:
                        max_col = c

        if max_row < min_row or max_col < min_col:
            # Нет ни одной клетки, вернём 1x1 пустую
            return [[0]]

        trimmed = []
        for r in range(min_row, max_row+1):
            row_slice = shape[r][min_col:max_col+1]
            trimmed.append(row_slice)
        return trimmed

    def get_shape_center_in_cells(self):
        """
        Находим «центр тяжести» фигуры в координатах матрицы (r, c).
        Например, если shape[r][c] == 1, добавляем (r, c) в список.
        Возвращаем (center_r, center_c), обычно вещественные числа.
        """
        total_r = 0
        total_c = 0
        count = 0
        for r in range(self.h):
            for c in range(self.w):
                if self.shape[r][c] == 1:
                    total_r += r
                    total_c += c
                    count += 1
        if count == 0:
            return 0.0, 0.0
        return (total_r / count, total_c / count)

    def draw(self, surface):
        """Рисует блок по координатам (self.x, self.y)."""
        for r in range(self.h):
            for c in range(self.w):
                if self.shape[r][c] == 1:
                    rect = pygame.Rect(
                        self.x + c*CELL_SIZE,
                        self.y + r*CELL_SIZE,
                        CELL_SIZE, CELL_SIZE
                    )
                    pygame.draw.rect(surface, self.color, rect)
                    pygame.draw.rect(surface, BLACK, rect, 1)

    def can_place(self, board, x, y):
        """
        Проверяет, можно ли разместить фигуру, если
        левый верхний угол bounding box в координатах поля = (x, y).
        """
        for r in range(self.h):
            for c in range(self.w):
                if self.shape[r][c] == 1:
                    bx = x + c
                    by = y + r
                    if (bx < 0 or bx >= GRID_SIZE or
                            by < 0 or by >= GRID_SIZE or
                            board[by][bx] != 0):
                        return False
        return True

    def place(self, board, x, y):
        """Фактически размещает блок в board, если can_place == True."""
        for r in range(self.h):
            for c in range(self.w):
                if self.shape[r][c] == 1:
                    board[y + r][x + c] = 1

    def get_shape_center_in_pixels(self):
        """
        Суммируем пиксельные координаты всех занятых клеток
        и берём среднее. Так получаем «реальный» центр тяжести
        в системе координат экрана.
        """
        total_x = 0
        total_y = 0
        count = 0
        for r in range(self.h):
            for c in range(self.w):
                if self.shape[r][c] == 1:
                    # Центр клетки в пикселях
                    cell_center_x = self.x + c*CELL_SIZE + CELL_SIZE/2
                    cell_center_y = self.y + r*CELL_SIZE + CELL_SIZE/2
                    total_x += cell_center_x
                    total_y += cell_center_y
                    count += 1
        if count == 0:
            return self.x, self.y
        return (total_x / count, total_y / count)

    def set_center_bounding_box(self, cx, cy):
        """
        Перемещает bounding box так, чтобы его ЦЕНТР (в пикселях)
        совпадал с (cx, cy).
        """
        box_w = self.w * CELL_SIZE
        box_h = self.h * CELL_SIZE
        self.x = cx - box_w//2
        self.y = cy - box_h//2


# ---------- ГЕНЕРАЦИЯ НЕСКОЛЬКИХ БЛОКОВ ----------
def generate_block():
    shapes = [
        [[1]],
        [[1, 1]],
        [[1, 1, 1]],
        [[1, 1, 1, 1]],
        [[1, 1], [1, 1]],
        [[1, 1, 1], [0, 1, 0]],
        [[1, 1, 0], [0, 1, 1]],
    ]
    return random.choice(shapes)

def generate_3_blocks():
    shapes = [generate_block() for _ in range(3)]
    possible_colors = [
        (255, 0, 0),
        (0, 255, 0),
        (0, 0, 255),
        (255, 255, 0),
        (255, 165, 0),
        (128, 0, 128)
    ]
    used_colors = random.sample(possible_colors, 3)
    blocks = []
    for i in range(3):
        block = Block(shapes[i], used_colors[i])
        blocks.append(block)
    return blocks

def init_block_positions(blocks):
    """
    Ставим 3 блока внизу, достаточно разнесённо, чтобы не налезали друг на друга.
    """
    starts = [(60, 550), (260, 550), (460, 550)]
    for block, (sx, sy) in zip(blocks, starts):
        block.x = sx
        block.y = sy


# ---------- СОХРАНЕНИЕ И ЗАГРУЗКА ОЧКОВ ----------
def save_score(score):
    with open(SCORES_FILE, "a", encoding="utf-8") as f:
        f.write(str(score) + "\n")

def get_last_scores(n=5):
    if not os.path.exists(SCORES_FILE):
        return []
    with open(SCORES_FILE, "r", encoding="utf-8") as f:
        lines = f.read().splitlines()
    scores = [int(line) for line in lines if line.isdigit()]
    return scores[-n:]


# ---------- МЕНЮ И ФИНАЛ ----------
def main_menu():
    menu_font = pygame.font.Font(None, 48)
    title_text = menu_font.render("Block Blast", True, (0, 102, 204))
    start_text = font.render("Нажмите SPACE, чтобы начать", True, BLACK)

    last_scores = get_last_scores(n=5)

    while True:
        screen.fill(WHITE)
        screen.blit(title_text, (WIDTH//2 - title_text.get_width()//2, HEIGHT//5))
        screen.blit(start_text, (WIDTH//2 - start_text.get_width()//2, HEIGHT//2))

        score_y = HEIGHT//2 + 50
        if last_scores:
            last_scores_text = font.render("Последние результаты:", True, BLACK)
            screen.blit(last_scores_text, (WIDTH//2 - last_scores_text.get_width()//2, score_y))
            score_y += 40
            for sc in reversed(last_scores):
                line = font.render(str(sc), True, BLACK)
                screen.blit(line, (WIDTH//2 - line.get_width()//2, score_y))
                score_y += 30

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                return False
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_SPACE:
                    return True
        pygame.display.flip()

def game_over_screen(score):
    menu_font = pygame.font.Font(None, 48)
    game_over_text = menu_font.render("Игра Окончена", True, RED)
    score_text = font.render(f"Счёт: {score}", True, BLACK)
    restart_text = font.render("Нажмите SPACE, чтобы начать заново", True, BLACK)

    while True:
        screen.fill(WHITE)
        screen.blit(game_over_text, (WIDTH//2 - game_over_text.get_width()//2, HEIGHT//3))
        screen.blit(score_text, (WIDTH//2 - score_text.get_width()//2, HEIGHT//2))
        screen.blit(restart_text, (WIDTH//2 - restart_text.get_width()//2, HEIGHT*2//3))

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                return False
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_SPACE:
                    return True
        pygame.display.flip()


# ---------- ОСНОВНОЙ ЦИКЛ ----------
def draw_score_and_multiplier(score, multiplier):
    score_text = font.render(f"Score: {score}", True, BLACK)
    screen.blit(score_text, (10, 10))
    multiplier_text = font.render(f"Multiplier: x{multiplier}", True, BLACK)
    screen.blit(multiplier_text, (WIDTH - 200, 10))

def main():
    running = True
    clock = pygame.time.Clock()

    blocks = generate_3_blocks()
    init_block_positions(blocks)

    active_index = -1
    dragging = False
    offset_x, offset_y = 0, 0

    score = 0
    multiplier = 1
    no_clear_counter = 0

    while running:
        screen.fill(WHITE)

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False

            elif event.type == pygame.MOUSEBUTTONDOWN:
                mx, my = event.pos
                # Проверяем, попали ли в один из 3 блоков
                for i, block in enumerate(blocks):
                    box_w = block.w * CELL_SIZE
                    box_h = block.h * CELL_SIZE
                    if block.x <= mx < block.x + box_w and block.y <= my < block.y + box_h:
                        active_index = i
                        dragging = True
                        # Центр bounding box
                        center_x = block.x + box_w//2
                        center_y = block.y + box_h//2
                        offset_x = mx - center_x
                        offset_y = my - center_y
                        break

            elif event.type == pygame.MOUSEBUTTONUP:
                if dragging and active_index != -1:
                    dragging = False
                    block = blocks[active_index]

                    # Находим «центр тяжести» всех занятых клеток (в пикселях)
                    shape_center_x, shape_center_y = block.get_shape_center_in_pixels()
                    # Определяем, какая клетка поля под этим центром
                    grid_cx = (shape_center_x - BOARD_OFFSET_X)//CELL_SIZE
                    grid_cy = (shape_center_y - BOARD_OFFSET_Y)//CELL_SIZE

                    # В матрице shape у блока «центр тяжести» = (cx_cells, cy_cells)
                    # Если мы хотим, чтобы этот центр оказался в клетке (grid_cx, grid_cy),
                    # то левый верхний угол блока в координатах поля:
                    place_x = int(round(grid_cx - block.cy_cells))
                    place_y = int(round(grid_cy - block.cx_cells))

                    if block.can_place(board, place_x, place_y):
                        block.place(board, place_x, place_y)
                        # Подсчитываем занятые клетки
                        block_cells = 0
                        for row in block.shape:
                            block_cells += sum(row)
                        score += block_cells * multiplier

                        cleared = clear_lines(board)
                        if cleared > 0:
                            score += cleared * 10 * multiplier
                            multiplier += 1
                            no_clear_counter = 0
                        else:
                            no_clear_counter += 1
                            if no_clear_counter >= 2:
                                multiplier = 1

                        # Удаляем блок из списка
                        blocks.pop(active_index)
                        active_index = -1

                        # Если все 3 блока расставлены, генерируем новые
                        if not blocks:
                            blocks = generate_3_blocks()
                            init_block_positions(blocks)
                    else:
                        # Если нельзя поставить, проверяем остальные
                        if not can_place_any_block(board, blocks):
                            running = False
                    active_index = -1

            elif event.type == pygame.MOUSEMOTION:
                if dragging and active_index != -1:
                    mx, my = event.pos
                    block = blocks[active_index]
                    box_w = block.w * CELL_SIZE
                    box_h = block.h * CELL_SIZE
                    # Новый центр bounding box
                    new_center_x = mx - offset_x
                    new_center_y = my - offset_y
                    # Смещаем левый верхний угол, чтобы центр совпал
                    block.x = new_center_x - box_w//2
                    block.y = new_center_y - box_h//2

        # Отрисовка
        draw_board()
        for block in blocks:
            block.draw(screen)
        draw_score_and_multiplier(score, multiplier)

        pygame.display.flip()
        clock.tick(30)

    return score


# ---------- ЗАПУСК ----------
if __name__ == "__main__":
    while True:
        if not main_menu():
            break
        reset_board()
        final_score = main()
        save_score(final_score)
        if not game_over_screen(final_score):
            break

    pygame.quit()
