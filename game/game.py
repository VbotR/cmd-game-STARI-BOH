import os
import msvcrt
import time
import random
import pygame

GRID_SIZE = 10
SHIP_SYMBOL = '^'
EMPTY_SYMBOL = ' '
BORDER_SYMBOL = '#'
MONSTER_SYMBOL = 'M'
INITIAL_SPEED = 0.2
SCORE_PER_SECOND = 10
BEST_SCORE_FILE = "best_score.txt"
MUSIC_FILE = "music.mp3"

def initialize_grid(size):
    # Инициализировать сетку заданного размера символами EMPTY_SYMBOL
    return [[EMPTY_SYMBOL for _ in range(size)] for _ in range(size)]

def place_ship(grid, position):
    # Разместить корабль в начальной позиции
    grid[position[0]][position[1]] = SHIP_SYMBOL

def place_monsters(grid, num_monsters):
    # Разместить монстров в сетке в случайных колонках
    positions = []
    cols = set()  # Отслеживание колонок, в которых уже есть монстры
    for _ in range(num_monsters):
        line = random.randint(0, GRID_SIZE - 1)
        col = random.randint(0, GRID_SIZE - 1)
        while col in cols:  # Обеспечить, чтобы в каждой колонке был не более одного монстра
            col = random.randint(0, GRID_SIZE - 1)
        cols.add(col)
        pos = [line, col]
        positions.append(pos)
        grid[pos[0]][pos[1]] = MONSTER_SYMBOL
    return positions

def display_grid(grid, score):
    # Очистить экран и вывести текущую сетку и счет
    os.system('cls' if os.name == 'nt' else 'clear')
    term_width = os.get_terminal_size().columns
    
    # Рассчитать количество пробелов для центровки сетки по горизонтали
    grid_width = len(grid[0]) + 2  # Добавить 2 для символов границы
    left_padding = (term_width - grid_width) // 2
    right_padding = term_width - grid_width - left_padding
    
    # Отобразить верхнюю границу
    print(" " * left_padding + BORDER_SYMBOL * (GRID_SIZE + 2))
    # Отобразить каждую строку сетки с границами слева и справа
    for row in grid:
        print(" " * left_padding + BORDER_SYMBOL + ''.join(row) + BORDER_SYMBOL)
    # Отобразить нижнюю границу
    print(" " * left_padding + BORDER_SYMBOL * (GRID_SIZE + 2))
    # Отобразить текущий счет
    print(" " * left_padding + "Score: ", score)

def move_ship(grid, position, direction):
    # Переместить корабль в указанном направлении, если это возможно
    new_position = position.copy()
    if direction == b'w' and position[0] > 0:
        new_position[0] -= 1
    elif direction == b's' and position[0] < GRID_SIZE - 1:
        new_position[0] += 1
    elif direction == b'a' and position[1] > 0:
        new_position[1] -= 1
    elif direction == b'd' and position[1] < GRID_SIZE - 1:
        new_position[1] += 1

    # Проверить, попал ли корабль на монстра
    if grid[new_position[0]][new_position[1]] == MONSTER_SYMBOL:
        return None

    # Переместить корабль в новую позицию, если она отличается от текущей
    if new_position != position:
        grid[position[0]][position[1]] = EMPTY_SYMBOL
        grid[new_position[0]][new_position[1]] = SHIP_SYMBOL
        return new_position
    return position

def move_monsters(grid, monsters):
    # Переместить монстров вниз по сетке
    new_monsters = []
    for pos in monsters:
        grid[pos[0]][pos[1]] = EMPTY_SYMBOL
        if pos[0] < GRID_SIZE - 1:
            pos[0] += 1
            new_monsters.append(pos)
            if grid[pos[0]][pos[1]] == SHIP_SYMBOL:
                return None
            grid[pos[0]][pos[1]] = MONSTER_SYMBOL
        else:
            new_pos = [0, random.randint(0, GRID_SIZE - 1)]
            new_monsters.append(new_pos)
            grid[new_pos[0]][new_pos[1]] = MONSTER_SYMBOL
    return new_monsters

def load_best_scores():
    # Загрузить лучшие результаты из файла
    best_scores = []
    if os.path.exists(BEST_SCORE_FILE):
        with open(BEST_SCORE_FILE, "r") as file:
            best_scores = [int(score) for score in file.readlines()]
    return sorted(best_scores, reverse=True)[:3]

def save_best_scores(scores):
    # Сохранить лучшие результаты в файл
    with open(BEST_SCORE_FILE, "w") as file:
        file.write("\n".join(map(str, sorted(scores, reverse=True)[:3])))

def main():
    # Инициализация микшера pygame
    pygame.mixer.init()
    
    # Загрузка и воспроизведение музыки
    if os.path.exists(MUSIC_FILE):
        pygame.mixer.music.load(MUSIC_FILE)
        pygame.mixer.music.play(-1)  # -1 означает, что музыка будет играть в бесконечном цикле

    # Инициализация сетки и размещение корабля
    grid = initialize_grid(GRID_SIZE)
    ship_position = [GRID_SIZE // 2, GRID_SIZE // 2]
    place_ship(grid, ship_position)

    # Загрузка лучших результатов
    best_scores = load_best_scores()

    # Вывод заголовка
    title = """
~####~~######~~####~~#####~~######
##~~~~~~~##~~~##~~##~##~~##~~~##
~####~~~~##~~~######~#####~~~~##
~~~~##~~~##~~~##~~##~##~~##~~~##
~####~~~~##~~~##~~##~##~~##~######

#####~~~####~~##~~##
##~~##~##~~##~##~~##
#####~~##~~##~######
##~~##~##~~##~##~~##
#####~~~####~~##~~##
    """
    print(title)
    
    # Вывод лучших результатов
    print("Лучшие результаты:")
    for i, score in enumerate(best_scores):
        print(f"{i+1}. {score}")

    # Ожидание нажатия Enter для начала игры
    print("\nНажмите Enter для начала игры...")
    while True:
        if msvcrt.getch() == b'\r':
            break

    monsters = []
    start_time = time.time()

    # Ожидание одной секунды перед началом спавна монстров
    while True:
        if time.time() - start_time >= 1:
            monsters = place_monsters(grid, 5)
            break

    # Инициализация счета и скорости игры
    score = 0
    speed = INITIAL_SPEED
    last_time = time.time()
    
    # Основной цикл игры
    while True:
        # Отображение сетки и текущего счета
        display_grid(grid, score)
        
        # Проверка нажатия клавиш
        if msvcrt.kbhit():
            key = msvcrt.getch()
            if key == b'q':
                break
            elif key in [b'w', b's', b'a', b'd']:
                new_position = move_ship(grid, ship_position, key)
                if new_position is None:
                    print("Игра окончена! Вы столкнулись с монстром!")
                    break
                ship_position = new_position

        # Обновление позиции монстров и счета через определенные интервалы
        current_time = time.time()
        if current_time - last_time >= speed:
            monsters = move_monsters(grid, monsters)
            if monsters is None:
                print("Игра окончена! Монстр вас поймал!")
                break
            last_time = current_time
            score += SCORE_PER_SECOND

        time.sleep(0.01)
    
    # Обновление и сохранение лучших результатов
    if score > (best_scores[-1] if best_scores else 0):
        best_scores.append(score)
        best_scores = sorted(best_scores, reverse=True)[:3]
        save_best_scores(best_scores)

    # Остановка музыки
    pygame.mixer.music.stop()

if __name__ == "__main__":
    main()
