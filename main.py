import threading
import pygame
from Sudoku import Sudoku

A = 50
pygame.init()
display = pygame.display.set_mode((A * 9, A * 9 + 60))
pygame.display.set_caption('Судоку: генерация и поиск решения')
font = pygame.font.Font(pygame.font.match_font('dejavuserif'), A - 10)
fontText = pygame.font.Font(pygame.font.match_font('arial'), 20)
info_surf = pygame.image.load('info.png')

m = [[0] * 9 for _ in range(9)]

sudoku = Sudoku(m)

ways = {pygame.K_LEFT: (0, -1), pygame.K_RIGHT: (0, 1), pygame.K_UP: (-1, 0), pygame.K_DOWN: (1, 0)}
game, select, cons, process, show_info = True, [], '', [], False
while game:
    display.fill((200, 200, 200))

    y, x = pygame.mouse.get_pos()
    for i in range(9):
        for j in range(9):
            color = (170, 170, 170) if i * A < x < (i + 1) * A and j * A < y < (j + 1) * A else (200, 200, 200)
            if select and sudoku.a[select[0]][select[1]] != 0 and sudoku.a[i][j] == sudoku.a[select[0]][select[1]]:
                color = (170, 170, 170)
            if select and select == [i, j]:
                color = (170, 130, 50)
            pygame.draw.rect(display, color, (A * j, A * i, 50, 50))
            if sudoku.a[i][j]:
                text_surface = font.render(str(sudoku.a[i][j]), True, (0, 0, 0))
                display.blit(text_surface, (j * A + A // 4, i * A + 3))

    for i in range(1, 10):
        w = 2 if i % 3 == 0 else 1
        pygame.draw.line(display, (0, 0, 0), (0, i * A), (A * 9, i * A), w)
        pygame.draw.line(display, (0, 0, 0), (i * A, 0), (i * A, A * 9), w)

    if show_info:
        pygame.draw.rect(display, (0, 0, 0), (98, 98, A * 9 - 196, A * 9 - 136))
        pygame.draw.rect(display, (190, 190, 190), (100, 100, A * 9 - 200, A * 9 - 140))
        for i, t in enumerate(['g - Генерация поля', 'f - Поиск решения', 'Enter - Заполнить клетку',
                               'Shift - Возможные цифры', 'Del - Очистить поле']):
            txt = fontText.render(t, True, (0, 0, 0))
            display.blit(txt, (110, 110 + i * 30))

    txt = fontText.render(str(cons), True, (0, 0, 0))
    display.blit(txt, (10, A * 9 + 20))

    if str(cons)[-3:] == '...' and sudoku.status != 'run':
        cons = sudoku.status

    display.blit(info_surf, (A * 8 - 5, A * 9 + 5))

    pygame.display.flip()

    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            game = False

        if event.type == pygame.MOUSEBUTTONDOWN:
            y, x = pygame.mouse.get_pos()
            select = [(x - x % A) // A, (y - y % A) // A]
            if not (0 <= select[0] < 9 and 0 <= select[1] < 9):
                select = []

            show_info = A * 8 - 5 < y < A * 8 + 105 and A * 9 + 5 < x < A * 9 + 95
            if not sudoku.status:
                cons = ''

        if select and event.type == pygame.KEYDOWN and pygame.K_0 <= event.key <= pygame.K_9:
            sudoku.a[select[0]][select[1]] = int(event.key) - 48

        if select and event.type == pygame.KEYDOWN and event.key in [pygame.K_SPACE, pygame.K_BACKSPACE]:
            sudoku.a[select[0]][select[1]] = 0

        if event.type == pygame.KEYDOWN and event.key == pygame.K_p:
            print(sudoku.a)

        if select and event.type == pygame.KEYDOWN and event.key in ways:
            new = select[0] + ways[event.key][0], select[1] + ways[event.key][1]
            select[0] = new[0] if 0 <= new[0] < 9 else (new[0] + 9) % 9
            select[1] = new[1] if 0 <= new[1] < 9 else (new[1] + 9) % 9
            if sudoku.status:
                cons = ''

        if select and event.type == pygame.KEYDOWN and event.key == pygame.K_RSHIFT:
            app = sudoku.applicants(select)
            cons = 'Возможные цифры: ' + ', '.join(str(e) for e in app) if app else ''

        if select and event.type == pygame.KEYDOWN and event.key == pygame.K_RETURN:
            if not sudoku.a[select[0]][select[1]]:
                pr = sudoku.predict(select, autofill=True)
                if not pr:
                    cons = 'Не удалось заполнить'

        if event.type == pygame.KEYDOWN and event.key == pygame.K_g:
            threading.Thread(target=sudoku.generate_map).start()
            cons = 'Генерация...'

        if event.type == pygame.KEYDOWN and event.key == pygame.K_f:
            threading.Thread(target=sudoku.fill_map).start()
            cons = 'Поиск решения...'

        if event.type == pygame.KEYDOWN and event.key == pygame.K_DELETE:
            sudoku.a = [[0] * 9 for _ in range(9)]
