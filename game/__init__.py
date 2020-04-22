import os
import pygame
import random
from pygame.locals import *

from game.lib.dino import Dino
from game.lib.scenario import Scenario
from game.lib.cloud import Cloud
from game.lib.constants import Constants


class Game:
    def __init__(self):
        self.tileset = pygame.image.load(Constants.TILESET_DIR)

        self.dino = Dino(self.tileset)
        self.dino_group = pygame.sprite.Group(self.dino)

        self.scenario_group = pygame.sprite.Group(
            Scenario(self.tileset, 0),
            Scenario(self.tileset, 1199),
        )

        self.cloud_group = pygame.sprite.Group(Cloud(self.tileset))

        self.display = pygame.display.set_mode(Constants.SIZE)
        self.clock = pygame.time.Clock()
        self.running = True


    def run(self):
        pygame.init()

        while self.running:
            self.clock.tick(45)
            self.display.fill(Constants.WHITE_COLOR)

            for event in pygame.event.get():
                if event.type == QUIT:
                    self.running = False

                if event.type == KEYDOWN:
                    if event.key == K_DOWN:
                        self.dino.turn_down()
                    
                    if event.key in [K_SPACE, K_UP]:
                        self.dino.jumping = True

                if event.type == KEYUP:
                    if event.key == K_DOWN:
                        self.dino.turn_standing()

                    if event.key in [K_SPACE, K_UP]:
                        self.dino.jumping = False

            self.scenario_group.draw(self.display)
            self.scenario_group.update()

            first_scenario = self.scenario_group.sprites()[0]
            last_scenario = self.scenario_group.sprites()[1]

            if first_scenario.rect.right < 0:
                self.scenario_group.add(Scenario(self.tileset, last_scenario.rect.right - 2))
                self.scenario_group.remove(first_scenario)

            self.cloud_group.draw(self.display)
            self.cloud_group.update()

            for cloud in self.cloud_group.sprites():
                if cloud.rect.right == 300:
                    self.cloud_group.add(Cloud(self.tileset))
                if cloud.rect.right < 0:
                    self.cloud_group.remove(cloud)

            self.dino_group.draw(self.display)
            self.dino_group.update()
            self.dino.move()

            pygame.display.flip()

        pygame.quit()
