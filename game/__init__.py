import os
import pygame
import random
from pygame.locals import *

from game.lib.dino import Dino
from game.lib.scenario import Scenario
from game.lib.cloud import Cloud
from game.lib.obstacle import Obstacle
from game.lib.constants import Constants

class Game:
    def __init__(self):
        pygame.display.set_caption('Dino')
        pygame.font.init()

        self.frame_number = 0
        self.score = 0
        self.display = pygame.display.set_mode(Constants.SIZE)
        self.tileset = pygame.image.load(Constants.TILESET_DIR)

        self.clock = pygame.time.Clock()
        self.score_font = pygame.font.Font(Constants.FONTS_DIR, 12)
        self.game_over_font = pygame.font.Font(Constants.FONTS_DIR, 34)
        self.over = False
        self.velocity = 7
        self.allow_pterodactyl = False
        self.fps = 60

        self.dino = Dino(self.tileset)
        self.dino_group = pygame.sprite.Group(self.dino)

        self.scenario_group = pygame.sprite.Group(
            Scenario(self.tileset, 0, self.velocity),
            Scenario(self.tileset, 1199, self.velocity),
        )

        self.cloud_group = pygame.sprite.Group(Cloud(self.tileset))

        self.obstacle = Obstacle(self.tileset, 600, self.velocity)
        self.obstacle_group = pygame.sprite.Group(self.obstacle)

    def handle_input_events(self):
        for event in pygame.event.get():
            if event.type == QUIT:
                self.over = True
                pygame.quit()

            if event.type == KEYDOWN:
                if event.key == K_DOWN:
                    self.dino.turn_down()

                if event.key in [K_SPACE, K_UP]:
                    self.dino.jumping = True
                    if self.over:
                        self.over = False
                        self.__init__()

            if event.type == KEYUP:
                if event.key == K_DOWN:
                    self.dino.turn_standing()

                if event.key in [K_SPACE, K_UP]:
                    self.dino.jumping = False


    def handle_sprites_events(self):
        self.score_text = self.score_font.render(f"{self.score:05d}", True, Constants.PRIMARY_COLOR)
        self.display.blit(self.score_text, (530, 10))

        self.cloud_group.draw(self.display)
        self.cloud_group.update()

        self.scenario_group.draw(self.display)
        self.scenario_group.update()

        self.dino_group.draw(self.display)
        self.dino_group.update()
        self.dino.move()

        first_scenario = self.scenario_group.sprites()[0]
        last_scenario = self.scenario_group.sprites()[1]

        if first_scenario.rect.right < 0:
            self.scenario_group.add(Scenario(self.tileset, last_scenario.rect.right - 2, self.velocity))
            self.scenario_group.remove(first_scenario)

        for cloud in self.cloud_group.sprites():
            if cloud.rect.right == 300:
                self.cloud_group.add(Cloud(self.tileset))
            if cloud.rect.right < 0:
                self.cloud_group.remove(cloud)

        self.obstacle_group.draw(self.display)
        self.obstacle_group.update()

        if self.frame_number % 60 == 0:
            last_obstacle = self.obstacle_group.sprites()[-1]
            self.obstacle_group.add(Obstacle(self.tileset, last_obstacle.rect.right, self.velocity, self.allow_pterodactyl))

        for obstacle in self.obstacle_group.sprites():
            if obstacle.rect.right <= 0:
                self.obstacle_group.remove(obstacle)

            if pygame.sprite.collide_mask(self.dino, obstacle):
                self.over = 0 #True

        if self.score > 150:
            self.allow_pterodactyl = True

        self.fps = 60 + self.score//40
        self.score = self.frame_number // 8

    def run(self):
        pygame.init()

        while True:
            self.handle_input_events()
            self.clock.tick(self.fps)

            if not self.over:
                self.display.fill(Constants.WHITE_COLOR)
                self.handle_sprites_events()
                
                self.frame_number += 1

                print(
                    self.obstacle_group.sprites()[0].rect.left,
                    self.obstacle_group.sprites()[0].rect.width,
                    self.obstacle_group.sprites()[0].rect.height
                )

                print(self.obstacle_group.sprites().__len__())
            else:
                game_over_text = self.game_over_font.render('GAME OVER', True, Constants.PRIMARY_COLOR)
                game_over_rect = game_over_text.get_rect(center=(Constants.WIDTH/2, Constants.HEIGHT/2))
                self.display.blit(game_over_text, game_over_rect)

            pygame.display.flip()

        pygame.quit()
