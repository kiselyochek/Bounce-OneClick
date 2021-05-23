import pygame
from os import path
import random
import sys

# инициализируем pygame
pygame.init()

clock = pygame.time.Clock()
fps = 60

# параметры экрана
screen_width = 1000
screen_height = 500

screen = pygame.display.set_mode((screen_width, screen_height))
pygame.display.set_caption('Bounce 2.0')

# шрифт
font_score = \
    pygame.font.SysFont('sitkasmallsitkatextboldsitkasubheadingboldsitkaheadingboldsitkadisplayboldsitkabannerbold', 30)
text_color = (255, 255, 255)

# параметры игры
tile_size = 50
game_over = 0
main_menu = True
score = 0
sky_color = (80, 217, 254)
# текстуры
restart_img = pygame.image.load('assets/restart_btn.png')
start_img = pygame.image.load('assets/start_btn.png')
exit_img = pygame.image.load('assets/exit_btn.png')
start_screen = pygame.image.load('assets/start_screen.png')

font = pygame.font.Font(None, 50)
game_over_screen = font.render('Game Over', True, (64, 47, 3))
game_over_x = 1000 // 2 - game_over_screen.get_width() // 2


def load_image(name, colorkey=None):
    fullname = path.join('assets/', name)
    if not path.isfile(fullname):
        print(f"Файл с изображением '{fullname}' не найден")
        sys.exit()
    image = pygame.image.load(fullname)
    if colorkey is not None:
        image = image.convert()
        if colorkey == -1:
            colorkey = image.get_at((15, 0))
        image.set_colorkey(colorkey)
    else:
        image = image.convert_alpha()
    return image


def create_spike(spike):
    new_spike = spike.get_rect(left=random.choice([i for i in range(500, 1000)]), top=420)

    return new_spike, spike.get_rect(bottom=550, top=420)


def move_spikes(spikes):
    for p in spikes:
        p[0].centerx -= 3
    return spikes


def draw_spikes(spikes, screen, spike):
    for p in spikes:
        screen.blit(spike, p[0])


# отрисовываем текст
def draw_text(text, font, text_color, x, y):
    img = font.render(text, True, text_color)
    screen.blit(img, (x, y))


# класс кнопок
class Button:
    def __init__(self, x, y, image):
        self.image = image
        self.rect = self.image.get_rect()
        self.rect.x = x
        self.rect.y = y
        self.clicked = False

    def draw(self):
        action = False

        # считываем координаты мыши
        pos = pygame.mouse.get_pos()

        # проверка наведение и нажатие
        if self.rect.collidepoint(pos):
            if pygame.mouse.get_pressed()[0] == 1 and not self.clicked:
                action = True
                self.clicked = True

        if pygame.mouse.get_pressed()[0] == 0:
            self.clicked = False

        # отрисовка кнопки
        screen.blit(self.image, self.rect)

        return action


ground = load_image('ground.png')
ground = pygame.transform.scale(ground, (1080, 50))
ground_rect = ground.get_rect()
ground_rect.top = screen_height - ground_rect.bottom

spike = load_image('spike.png', -1)
spike = pygame.transform.scale(spike, (15, 35))

spikeSPAWNEVENT = pygame.USEREVENT + 1
pygame.time.set_timer(spikeSPAWNEVENT, 1500)
spikes_group = []


# класс игрока
class Player(pygame.sprite.Sprite):
    def __init__(self, x, y, *groups):
        super().__init__(*groups)
        self.reset(x, y)
        self.count = 1

    # обновление координат и состояний игрока
    def update(self, game_over):
        dx = 0
        dy = 0
        # считывание нажатий клавиш
        if game_over == 0:
            key = pygame.key.get_pressed()
            if key[pygame.K_SPACE] and self.on_the_ground:
                self.vel_y = -15
            if not key[pygame.K_SPACE]:
                self.jumped = False
                self.on_the_ground = False
        self.on_the_ground = False

        self.vel_y += 1
        if self.vel_y > 10:
            self.vel_y = 10
        dy += self.vel_y

        # проверка на коллизии
        for i in range(1000 // 50):
            # проверка на коллизии в оси x
            if ground_rect.colliderect(self.rect.x + dx, self.rect.y, self.width, self.height):
                dx = 0
            # проверка на коллизии в оси у
            if ground_rect.colliderect(self.rect.x, self.rect.y + dy, self.width, self.height):
                if self.vel_y < 0:
                    dy = ground_rect.bottom - self.rect.top
                    self.vel_y = 0
                elif self.vel_y >= 0:
                    dy = ground_rect.top - self.rect.bottom
                    self.vel_y = 0
                    self.on_the_ground = True

        # обновление координат
        self.rect.x += dx
        self.rect.y += dy

        if self.rect.bottom > screen_height:
            self.rect.bottom = screen_height
            dy = 0

        screen.blit(self.image, self.rect)

        return game_over

    # сброс при проигрыше
    def reset(self, x, y):
        img = pygame.image.load('assets/ball.png')
        self.image = pygame.transform.scale(img, (40, 40))
        self.rect = self.image.get_rect()
        self.rect.x = x
        self.rect.y = y
        self.width = self.image.get_width()
        self.height = self.image.get_height()
        self.vel_y = 0
        self.jumped = False
        self.on_the_ground = True

    def get_rec(self):
        return self.rect


player = Player(50, screen_height - 130)


def is_collide(spikes, counter, p_rect):
    for i in spikes:
        if p_rect.colliderect(i[0]) or p_rect.colliderect(i[1]):
            return False, counter
        if i[0].right + 2 > p_rect.left > i[0].right - 2:
            counter += 10
    return True, counter


# отрисовка кнопок
restart_button = Button(screen_width // 2 - 50, screen_height // 2 + 100, restart_img)
start_button = Button(screen_width // 2 + 100, 100, start_img)
exit_button = Button(screen_width // 2 - 30 + 150, 300, exit_img)

# игровой цикл
running = True
while running:
    clock.tick(fps)

    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False
        if event.type == spikeSPAWNEVENT and game_over == 0:
            spikes_group.append(create_spike(spike))

    if main_menu:
        screen.fill(sky_color)
        screen.blit(start_screen, (0, 0))
        if exit_button.draw():
            running = False
        if start_button.draw():
            main_menu = False

    else:
        screen.fill(sky_color)
        ground_rect.left -= 3
        if ground_rect.right <= screen_width:
            ground_rect.left = 0
        if score != 0 and score // 10 == 0:
            fps += 2
        if score == 1000:
            game_over = 1
        score_count = font.render(str(score), True, (64, 47, 3))
        score_x = 1000 // 2 - score_count.get_width() // 2
        screen.blit(score_count, (score_x, 100))
        screen.blit(ground, ground_rect)

        game_over = player.update(game_over)

        if game_over == -1:
            screen.fill(sky_color)
            screen.blit(game_over_screen, (game_over_x, 100))
            if restart_button.draw():
                player.reset(100, screen_height - 130)

                game_over = 0
                score = 0
                fps = 60

        if game_over == 1:
            score = 0
            screen.fill(sky_color)
            win = font.render("You won!", True, (64, 47, 3))
            screen.blit(win, (430, 100))
            if restart_button.draw():
                player.reset(100, screen_height - 130)

        if game_over == 0:
            spikes_group = move_spikes(spikes_group)
            draw_spikes(spikes_group, screen, spike)
            collision, score = is_collide(spikes_group, score, player.get_rec())
            if not collision:
                game_over = -1
                spikes_group = []
                score = 0
    pygame.display.update()

pygame.quit()
