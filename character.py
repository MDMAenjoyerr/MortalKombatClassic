import pygame

# Класс для определения действий бойца
class Actions:
    IDLE = 0
    RUN = 1
    JUMP = 2
    ATTACK1 = 3
    ATTACK2 = 4
    HIT = 5
    DEATH = 6

# Класс бойца
class Fighter:
    def __init__(self, player, x, y, flip, data, sprite_sheet, animation_steps, sound):
        # Инициализация бойца
        self.player = player
        self.size = data[0]
        self.image_scale = data[1]
        self.offset = data[2]
        self.flip = flip
        self.animation_list = self.load_images(sprite_sheet, animation_steps)
        self.action = 0  # 0:idle #1:run #2:jump #3:attack1 #4: attack2 #5:hit #6:death
        self.frame_index = 0
        self.image = self.animation_list[self.action][self.frame_index]
        self.update_time = pygame.time.get_ticks()
        self.rect = pygame.Rect((x, y, 80, 100))
        self.vel_y = 0
        self.running = False
        self.jump = False
        self.attacking = False
        self.attack_type = 0
        self.attack_cooldown = 0
        self.attack_sound = sound
        self.hit = False
        self.health = 100
        self.alive = True

    def load_images(self, sprite_sheet, animation_steps):
        # Загрузка изображений для анимаций перса
        animation_list = []
        for y, animation in enumerate(animation_steps):
            temp_img_list = []
            for x in range(animation):
                temp_img = sprite_sheet.subsurface(x * self.size, y * self.size, self.size, self.size)
                temp_img_list.append(pygame.transform.scale(temp_img, (self.size * self.image_scale, self.size * self.image_scale)))
            animation_list.append(temp_img_list)
        return animation_list

    def move(self, screen_width, screen_height, surface, target, round_over):
        # Функция для перемещения перса
        SPEED = 12
        GRAVITY = 2
        dx, dy = 0, 0
        self.running, self.attack_type = False, 0

        key = pygame.key.get_pressed()

        if not (self.attacking or not self.alive or round_over):
            if self.player == 1:
                if key[pygame.K_a]:
                    dx = -SPEED
                    self.running = True
                elif key[pygame.K_d]:
                    dx = SPEED
                    self.running = True
                elif key[pygame.K_w] and not self.jump:
                    self.vel_y = -30
                    self.jump = True
                elif key[pygame.K_r] or key[pygame.K_t]:
                    self.attack(target)
                    self.attack_type = 1 if key[pygame.K_r] else 2

            elif self.player == 2:
                if key[pygame.K_LEFT]:
                    dx = -SPEED
                    self.running = True
                elif key[pygame.K_RIGHT]:
                    dx = SPEED
                    self.running = True
                elif key[pygame.K_UP] and not self.jump:
                    self.vel_y = -30
                    self.jump = True
                elif key[pygame.K_n] or key[pygame.K_m]:
                    self.attack(target)
                    self.attack_type = 1 if key[pygame.K_n] else 2

        self.vel_y += GRAVITY
        dy += self.vel_y

        if self.rect.left + dx < 0:
            dx = -self.rect.left
        if self.rect.right + dx > screen_width:
            dx = screen_width - self.rect.right
        if self.rect.bottom + dy > screen_height - 110:
            self.vel_y = 0
            self.jump = False
            dy = screen_height - 110 - self.rect.bottom

        if target.rect.centerx > self.rect.centerx:
            self.flip = False
        else:
            self.flip = True

        if self.attack_cooldown > 0:
            self.attack_cooldown -= 1

        self.rect.x += dx
        self.rect.y += dy

    def update(self):
        # Функция для обновления состояния перса
        if self.health <= 0:
            self.health = 0
            self.alive = False
            self.update_action(Actions.DEATH)
        elif self.hit:
            self.update_action(Actions.HIT)
        elif self.attacking:
            self.update_action(Actions.ATTACK1 if self.attack_type == 1 else Actions.ATTACK2)
        elif self.jump:
            self.update_action(Actions.JUMP)
        elif self.running:
            self.update_action(Actions.RUN)
        else:
            self.update_action(Actions.IDLE)

        animation_cooldown = 50

        self.image = self.animation_list[self.action][self.frame_index]

        if pygame.time.get_ticks() - self.update_time > animation_cooldown:
            self.frame_index += 1
            self.update_time = pygame.time.get_ticks()

        if self.frame_index >= len(self.animation_list[self.action]):
            if not self.alive:
                self.frame_index = len(self.animation_list[self.action]) - 1
            else:
                self.frame_index = 0

                if self.action == Actions.ATTACK1 or self.action == Actions.ATTACK2:
                    self.attacking = False
                    self.attack_cooldown = 20

                if self.action == Actions.HIT:
                    self.hit = False
                    self.attacking = False
                    self.attack_cooldown = 20

    def attack(self, target):
        # Функция для атаки бойца
        if self.attack_cooldown == 0:
            self.attacking = True
            self.attack_sound.play()
            attacking_rect = pygame.Rect(self.rect.centerx - (2 * self.rect.width * self.flip), self.rect.y, 2 * self.rect.width, self.rect.height)
            if attacking_rect.colliderect(target.rect):
                target.health -= 10
                target.hit = True

    def update_action(self, new_action):
        # Функция для обновления текущего действия перса
        if new_action != self.action:
            self.action = new_action
            self.frame_index = 0
            self.update_time = pygame.time.get_ticks()

    def draw(self, surface):
        # Функция для отрисовки перса
        img = pygame.transform.flip(self.image, self.flip, False)
        surface.blit(img, (self.rect.x - (self.offset[0] * self.image_scale), self.rect.y - (self.offset[1] * self.image_scale)))