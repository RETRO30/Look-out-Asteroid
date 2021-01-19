import pygame
import sys
import os
import random
import json

fps = 60
player_spaceship = 'player_1'


def load_data():
    with open("data/config.json", "r") as read_file:
        data_ = json.load(read_file)
    with open("data/scoreboard.json", "r") as read_file:
        scoreboard_data_ = json.load(read_file)
    return data_, scoreboard_data_


def save_data(data_, scoreboard_data_):
    with open("data/config.json", "w") as write_file:
        json.dump(data_, write_file)
    with open("data/scoreboard.json", "w") as write_file:
        json.dump(scoreboard_data_, write_file)


def terminate():
    pygame.quit()
    sys.exit()


def load_image(name):
    fullname = os.path.join('data', name)
    # если файл не существует, то выходим
    if not os.path.isfile(fullname):
        print(f"Файл с изображением '{fullname}' не найден")
        sys.exit()
    image = pygame.image.load(fullname)
    return image


class CoinCounter:
    def __init__(self):
        self.count = data["COINS"]

    def draw(self):
        self.count = data["COINS"]
        font = pygame.font.Font('data/font.ttf', 26)
        text = font.render(str(self.count), True, (255, 255, 255))
        text_x = 110
        text_y = 17
        return text, (text_x, text_y)


class Score:
    def __init__(self, count):
        self.count = count

    def draw(self):
        font = pygame.font.Font('data/font.ttf', 26)
        text = font.render(str(self.count), True, (255, 255, 255))
        text_x = 120
        text_y = 52
        return text, (text_x, text_y)


class ShipInStore(pygame.sprite.Sprite):
    def __init__(self, name, x, y):
        global data
        super(ShipInStore, self).__init__(all_sprites)
        self.name = name
        self.name_image = self.name
        self.add(store_sprites)
        self.sold = data[self.name]
        if self.sold:
            self.name_image += '_SOLD'
        self.image = load_image(f'{self.name_image}.png')
        self.x = x
        self.y = y
        self.rect = self.image.get_rect().move(x - 24, y - 24)

    def update(self, *args):
        global data, scoreboard_data, player_spaceship
        self.image = load_image(f'{self.name_image}.png')
        self.rect = self.image.get_rect().move(self.x - 24, self.y - 24)
        if args and args[0].type == pygame.MOUSEMOTION and self.rect.collidepoint(args[0].pos):
            self.image = load_image(f'{self.name_image}_SELECTED.png')
            self.rect = self.image.get_rect().move(self.x, self.y)
        if args and args[0].type == pygame.MOUSEBUTTONDOWN \
                and self.rect.collidepoint(args[0].pos) and args[0].button == 1:
            if self.sold:
                player_spaceship = f'player_{self.name.split("_")[1]}'
            elif data["COINS"] >= 100:
                data["COINS"] -= 100
                self.sold = 1
                data[self.name] = 1
                self.name_image += '_SOLD'
                save_data(data, scoreboard_data)


class Player(pygame.sprite.Sprite):
    def __init__(self):
        super(Player, self).__init__(all_sprites)
        self.add(player_sprite)
        self.image = load_image(f'{player_spaceship}.png')
        self.rect = self.image.get_rect()
        self.mask = pygame.mask.from_surface(self.image)
        self.rect.centerx = width / 2
        self.rect.bottom = height - 25
        self.speedx = 0
        self.charge = 0

    def update(self):
        global in_play

        self.speedx = 0
        keystate = pygame.key.get_pressed()
        if keystate[pygame.K_LEFT]:
            self.speedx = -8
        if keystate[pygame.K_RIGHT]:
            self.speedx = 8
        self.rect.x += self.speedx
        if self.rect.right > width:
            self.rect.right = width
        if self.rect.left < 0:
            self.rect.left = 0

        if keystate[pygame.K_SPACE] and self.charge >= 100:
            bullet = Bullet(self.rect.centerx, self.rect.top)
            bullet.add(player_sprite)
            bullet.add(all_sprites)
            pygame.mixer.Sound.play(shoot_sound)
            self.charge = 0

        if self.charge < 100:
            self.charge += 1


class Bullet(pygame.sprite.Sprite):
    image = load_image('rocket.png')

    def __init__(self, x, y):
        pygame.sprite.Sprite.__init__(self)
        self.image = Bullet.image
        self.rect = self.image.get_rect()
        self.rect.bottom = y
        self.rect.centerx = x
        self.speedy = -10

    def update(self):
        self.rect.y += self.speedy
        if self.rect.bottom < 0:
            self.kill()
        if pygame.sprite.spritecollide(self, meteor_sprites, True):
            self.kill()
            MeteorPlay()


class CoinsPlay(pygame.sprite.Sprite):
    def __init__(self):
        super(CoinsPlay, self).__init__(all_sprites)
        self.add(coins_sprites)
        self.image = load_image('Coin.png')
        self.rect = self.image.get_rect()
        self.rect.x = random.randrange(width - self.rect.width)
        self.rect.y = random.randrange(-1000, -200)
        self.speedy = 2

    def update(self):
        self.rect.y += self.speedy
        if self.rect.top > height + 10 or self.rect.left < -self.rect.width or self.rect.right > width + self.rect.width:
            self.rect.x = random.randrange(width - self.rect.width)
            self.rect.y = random.randrange(-1000, -200)
            self.speedy = 2

        if player_sprite.sprites():
            if pygame.sprite.collide_mask(self, player_sprite.sprites()[0]):
                data['COINS'] += len(pygame.sprite.spritecollide(self, coins_sprites, True))
                CoinsPlay()
                pygame.mixer.Sound.play(collect_coin_sound)


class MeteorMenu(pygame.sprite.Sprite):
    def __init__(self):
        super(MeteorMenu, self).__init__(all_sprites)
        self.add(meteor_sprites)
        self.image = load_image(random.choice(['meteor_1.png', 'meteor_2.png', 'meteor_3.png']))
        self.rect = self.image.get_rect()
        self.rect.x = random.randrange(width - self.rect.width)
        self.rect.y = random.randrange(-100, -40)
        self.speedy = random.randrange(1, 5)
        self.speedx = random.randrange(-2, 2)

    def update(self):
        self.rect.x += self.speedx
        self.rect.y += self.speedy
        if self.rect.top > height + 10 or self.rect.left < -self.rect.width or self.rect.right > width + self.rect.width:
            self.rect.x = random.randrange(width - self.rect.width)
            self.rect.y = random.randrange(-100, -40)
            self.speedy = random.randrange(1, 8)


class MeteorPlay(pygame.sprite.Sprite):
    def __init__(self):
        super(MeteorPlay, self).__init__(all_sprites)
        self.add(meteor_sprites)
        self.image = load_image(random.choice(['meteor_1.png', 'meteor_2.png', 'meteor_3.png']))
        self.rect = self.image.get_rect()
        self.mask = pygame.mask.from_surface(self.image)
        self.rect.x = random.randrange(width - self.rect.width)
        self.rect.y = random.randrange(-100, -40)
        self.speedy = random.randrange(1, 5)

    def update(self):
        global in_play, in_game_over
        self.rect.y += self.speedy
        if self.rect.top > height + 10 or self.rect.left < -self.rect.width or self.rect.right > width + self.rect.width:
            self.rect.x = random.randrange(width - self.rect.width)
            self.rect.y = random.randrange(-100, -40)
            self.speedy = random.randrange(3, 6)

        if player_sprite.sprites():
            if pygame.sprite.collide_mask(self, player_sprite.sprites()[0]):
                pygame.mixer.Sound.play(crash_sound)
                in_play = False
                in_game_over = True


class ButtonPlay(pygame.sprite.Sprite):
    image = load_image('PLAY_BUTTON.png')
    image_selected = load_image('PLAY_BUTTON_SELECTED.png')

    def __init__(self):
        super(ButtonPlay, self).__init__(all_sprites)
        self.add(menu_sprites)
        self.image = ButtonPlay.image
        self.rect = self.image.get_rect().move(285 - 24, 116 - 24)

    def update(self, *args):
        global in_menu, in_play
        self.image = ButtonPlay.image
        self.rect = self.image.get_rect().move(285 - 24, 116 - 24)
        if args and args[0].type == pygame.MOUSEMOTION and self.rect.collidepoint(args[0].pos):
            self.image = ButtonPlay.image_selected
            self.rect = self.image.get_rect().move(285, 116)
        if args and args[0].type == pygame.MOUSEBUTTONDOWN \
                and self.rect.collidepoint(args[0].pos) and args[0].button == 1:
            in_menu = False
            in_play = True


class ButtonStore(pygame.sprite.Sprite):
    image = load_image('STORE_BUTTON.png')
    image_selected = load_image('STORE_BUTTON_SELECTED.png')

    def __init__(self):
        super(ButtonStore, self).__init__(all_sprites)
        self.add(menu_sprites)
        self.image = ButtonStore.image
        self.rect = self.image.get_rect().move(285 - 24, 232 - 24)

    def update(self, *args):
        global in_menu, in_store
        self.image = ButtonStore.image
        self.rect = self.image.get_rect().move(285 - 24, 232 - 24)
        if args and args[0].type == pygame.MOUSEMOTION and self.rect.collidepoint(args[0].pos):
            self.image = ButtonStore.image_selected
            self.rect = self.image.get_rect().move(285, 232)
        if args and args[0].type == pygame.MOUSEBUTTONDOWN \
                and self.rect.collidepoint(args[0].pos) and args[0].button == 1:
            in_menu = False
            in_store = True


class ButtonScoreboard(pygame.sprite.Sprite):
    image = load_image('SCOREBOARD_BUTTON.png')
    image_selected = load_image('SCOREBOARD_BUTTON_SELECTED.png')

    def __init__(self):
        super(ButtonScoreboard, self).__init__(all_sprites)
        self.add(menu_sprites)
        self.image = ButtonScoreboard.image
        self.rect = self.image.get_rect().move(285 - 24, 348 - 24)

    def update(self, *args):
        global in_menu, in_scoreboard
        self.image = ButtonScoreboard.image
        self.rect = self.image.get_rect().move(285 - 24, 348 - 24)
        if args and args[0].type == pygame.MOUSEMOTION and self.rect.collidepoint(args[0].pos):
            self.image = ButtonScoreboard.image_selected
            self.rect = self.image.get_rect().move(285, 348)
        if args and args[0].type == pygame.MOUSEBUTTONDOWN \
                and self.rect.collidepoint(args[0].pos) and args[0].button == 1:
            in_menu = False
            in_scoreboard = True


class ButtonExit(pygame.sprite.Sprite):
    image = load_image('EXIT_BUTTON.png')
    image_selected = load_image('EXIT_BUTTON_SELECTED.png')

    def __init__(self):
        super(ButtonExit, self).__init__(all_sprites)
        self.add(menu_sprites)
        self.image = ButtonExit.image
        self.rect = self.image.get_rect().move(285 - 24, 464 - 24)

    def update(self, *args):
        self.image = ButtonExit.image
        self.rect = self.image.get_rect().move(285 - 24, 464 - 24)
        if args and args[0].type == pygame.MOUSEMOTION and self.rect.collidepoint(args[0].pos):
            self.image = ButtonExit.image_selected
            self.rect = self.image.get_rect().move(285, 464)
        if args and args[0].type == pygame.MOUSEBUTTONDOWN \
                and self.rect.collidepoint(args[0].pos) and args[0].button == 1:
            terminate()


class ButtonBack(pygame.sprite.Sprite):
    image = load_image('BACK_BUTTON.png')
    image_selected = load_image('BACK_BUTTON_SELECTED.png')

    def __init__(self):
        super(ButtonBack, self).__init__(all_sprites)
        self.image = ButtonBack.image
        self.rect = self.image.get_rect().move(0, 531 - 24)

    def update(self, *args):
        global in_menu, in_store, in_scoreboard, in_game_over
        self.image = ButtonBack.image
        self.rect = self.image.get_rect().move(0, 531 - 24)
        if args and args[0].type == pygame.MOUSEMOTION and self.rect.collidepoint(args[0].pos):
            self.image = ButtonBack.image_selected
            self.rect = self.image.get_rect().move(14, 531)
        if args and args[0].type == pygame.MOUSEBUTTONDOWN \
                and self.rect.collidepoint(args[0].pos) and args[0].button == 1:
            in_menu = True
            in_store = False
            in_scoreboard = False
            in_game_over = False


class InputBox:
    def __init__(self):
        self.text = ''

    def draw(self):
        font = pygame.font.Font('data/font.ttf', 36)
        text = font.render(self.text, True, (255, 255, 255))
        text_x = width // 2 - text.get_rect().width // 2
        text_y = 361
        return text, (text_x, text_y)

    def update(self, *args):
        if args and args[0].type == pygame.KEYDOWN:
            if args[0].key == pygame.K_BACKSPACE:
                self.text = self.text[:-1]
            elif len(self.text) <= 15:
                if args[0].unicode.upper() in 'ABCDEFGHIJKLMNOPQRSTUVWXYZ' or args[0].unicode.isdigit():
                    self.text += args[0].unicode.upper()


class ScoreboardRow(pygame.sprite.Sprite):
    def __init__(self, name, score, x, y):
        super(ScoreboardRow, self).__init__(all_sprites)
        self.add(scoreboard_sprites)
        self.image = load_image("row scoreboard.png")
        self.rect = self.image.get_rect()
        self.rect.x = x
        self.rect.y = y
        self.text = f'{name} - {score}'
        font = pygame.font.Font('data/font.ttf', 26)
        text = font.render(self.text, True, (0, 0, 0))
        self.image.blit(text, (
            self.rect.width // 2 - text.get_rect().width // 2, self.rect.height // 2 - text.get_rect().height // 2))


class Indicator:
    def __init__(self, value):
        self.value = value

    def draw(self):
        font = pygame.font.Font('data/font.ttf', 26)
        text = font.render(str(self.value), True, (255, 255, 255))
        text_x = 140
        text_y = 87
        return text, (text_x, text_y)


def rockers():
    music_pos = pygame.mixer.music.get_pos()
    pygame.mixer.music.stop()
    delay = 10
    s = pygame.Surface((800, 600))
    s.fill('black')
    for i in range(0, 255, 15):
        s.set_alpha(i)
        screen.blit(s, (0, 0))
        pygame.display.flip()
        pygame.time.delay(delay)
    for i in range(255, 0, -15):
        s.set_alpha(i)
        screen.blit(s, (0, 0))
        pygame.display.flip()
        pygame.time.delay(delay)
    pygame.mixer.music.play(-1, music_pos)


def start_menu():
    coins_counter = CoinCounter()
    for _ in range(8):
        MeteorMenu()
    play_btn = ButtonPlay()
    store_btn = ButtonStore()
    scoreboard_btn = ButtonScoreboard()
    exit_btn = ButtonExit()
    while in_menu:
        screen.fill('black')
        screen.blit(load_image('background_menu.png'), (0, 0))
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                terminate()
            menu_sprites.update(event)
        meteor_sprites.update()
        all_sprites.draw(screen)
        screen.blit(*coins_counter.draw())
        pygame.display.flip()
        clock.tick(fps)
    for meteor in meteor_sprites:
        meteor.remove(all_sprites, meteor_sprites)
    store_btn.remove(all_sprites, menu_sprites)
    play_btn.remove(all_sprites, menu_sprites)
    scoreboard_btn.remove(all_sprites, menu_sprites)
    exit_btn.remove(all_sprites, menu_sprites)
    rockers()


def game_over(score_count):
    global data, scoreboard_data

    screen.blit(load_image('GAME OVER.png'), (0, 0))
    input_box = InputBox()
    btn_back = ButtonBack()
    btn_back.add(game_over_sprites)
    coins_counter = CoinCounter()
    score = Score(score_count)
    while in_game_over:
        screen.blit(load_image('GAME OVER.png'), (0, 0))
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                terminate()
            game_over_sprites.update(event)
            input_box.update(event)
        all_sprites.draw(screen)
        screen.blit(*input_box.draw())
        screen.blit(*coins_counter.draw())
        screen.blit(*score.draw())
        pygame.display.flip()
        clock.tick(fps)
    if input_box.text:
        for btn in game_over_sprites:
            btn.remove(all_sprites, game_over_sprites)
        flag = False
        for i, user in enumerate(scoreboard_data["scoreboard"]):
            if user["name"] == input_box.text:
                if user["score"] < score_count:
                    scoreboard_data["scoreboard"][i]["score"] = score_count
                flag = True
        if not flag:
            scoreboard_data["scoreboard"].append({"name": input_box.text, "score": score_count})
    scoreboard_data["scoreboard"] = sorted(scoreboard_data["scoreboard"], key=lambda x: x["score"], reverse=True)[:11]
    save_data(data, scoreboard_data)
    btn_back.remove(all_sprites)


def play():
    pygame.mixer.music.load('data/in game.mp3')
    pygame.mixer.music.set_volume(0.2)
    pygame.mixer.music.play(-1)

    for _ in range(10):
        MeteorPlay()
    for _ in range(4):
        CoinsPlay()

    player = Player()
    coins_counter = CoinCounter()
    indicator = Indicator(player.charge)
    score = Score(0)
    while in_play:
        screen.fill('black')
        screen.blit(load_image('background_play.png'), (0, 0))
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                terminate()
        player_sprite.update()
        meteor_sprites.update()
        coins_sprites.update()
        coins_counter.count = data['COINS']
        screen.blit(*coins_counter.draw())
        screen.blit(*score.draw())
        screen.blit(*indicator.draw())
        indicator.value = player.charge
        all_sprites.draw(screen)
        pygame.display.flip()
        clock.tick(fps)
        score.count += 1
    for player in player_sprite:
        player.remove(all_sprites, player_sprite)
    for meteor in meteor_sprites:
        meteor.remove(all_sprites, meteor_sprites)
    for coin in coins_sprites:
        coin.remove(all_sprites, coins_sprites)
    rockers()
    pygame.mixer.music.load('data/background.mp3')
    pygame.mixer.music.set_volume(1)
    pygame.mixer.music.play(-1)
    game_over(score.count)
    rockers()


def store_menu():
    back_btn = ButtonBack()
    back_btn.add(store_sprites)
    coins_counter = CoinCounter()
    for _ in range(4):
        ShipInStore(f'SHIP_{_ + 1}', 122 + 150 * _, 244)
    while in_store:
        screen.fill('black')
        screen.blit(load_image('background_store.png'), (0, 0))
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                terminate()
            store_sprites.update(event)
        all_sprites.draw(screen)
        screen.blit(*coins_counter.draw())
        pygame.display.flip()
        clock.tick(fps)
    for btn in store_sprites:
        btn.remove(store_sprites, all_sprites)
    rockers()


def scoreboard():
    back_btn = ButtonBack()
    coins_counter = CoinCounter()
    y = height // 2 - (len(scoreboard_data["scoreboard"]) - 1) * 24
    for user in scoreboard_data["scoreboard"]:
        ScoreboardRow(user["name"], user["score"], 148, y)
        y += 44
    while in_scoreboard:
        screen.fill('black')
        screen.blit(load_image('background_scoreboard.png'), (0, 0))
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                terminate()
            back_btn.update(event)
        scoreboard_sprites.update()
        all_sprites.draw(screen)
        screen.blit(*coins_counter.draw())
        pygame.display.flip()
        clock.tick(fps)
    for row in scoreboard_sprites:
        row.remove(all_sprites, scoreboard_sprites)
    back_btn.remove(scoreboard_sprites, all_sprites)
    rockers()


if __name__ == '__main__':
    data, scoreboard_data = load_data()
    pygame.init()
    pygame.display.set_caption('Look out! Asteroid!')
    size = width, height = 800, 600
    screen = pygame.display.set_mode(size)
    pygame.mixer.music.load('data/background.mp3')
    pygame.mixer.music.set_volume(1)
    pygame.mixer.music.play(-1)

    collect_coin_sound = pygame.mixer.Sound('data/coin_collect.mp3')
    shoot_sound = pygame.mixer.Sound('data/shoot.mp3')
    crash_sound = pygame.mixer.Sound('data/crash.mp3')
    crash_sound.set_volume(0.2)

    all_sprites = pygame.sprite.Group()
    menu_sprites = pygame.sprite.Group()
    meteor_sprites = pygame.sprite.Group()
    player_sprite = pygame.sprite.Group()
    store_sprites = pygame.sprite.Group()
    scoreboard_sprites = pygame.sprite.Group()
    coins_sprites = pygame.sprite.Group()
    game_over_sprites = pygame.sprite.Group()

    clock = pygame.time.Clock()

    in_menu = True
    in_play = False
    in_store = False
    in_scoreboard = False
    in_game_over = False

    start_menu()

    while True:
        if in_menu:
            start_menu()
        if in_play:
            play()
        if in_store:
            store_menu()
        if in_scoreboard:
            scoreboard()
