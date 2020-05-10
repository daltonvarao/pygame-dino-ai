import os
import pygame
import random
from pygame.locals import *
from pprint import pprint as print

from game.lib.dino import Dino
from game.lib.scenario import Scenario
from game.lib.cloud import Cloud
from game.lib.obstacle import Obstacle
from game.lib.constants import Constants
from game.lib.population import Population
from game.lib.ga2 import GeneticAlgorithm


tileset = pygame.image.load(Constants.TILESET_DIR)
allow_save=False

genetic_algorithm = GeneticAlgorithm(Constants.CR, Constants.MR, Constants.BESTS_NUM)
population = Population(
    *(Dino(tileset, Constants.NET_LAYERS) for _ in range(Constants.POP_SIZE)), 
    allow_save=allow_save
)

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
        self.velocity = 7
        self.allow_pterodactyl = False
        self.fps = 60
        self.obstacles = 0

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
                population.save_weights()
                pygame.quit()

    def handle_sprites_events(self):
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

        if len(self.obstacle_group.sprites()) < 3:
            last_obstacle = self.obstacle_group.sprites()[-1]
            self.obstacle_group.add(Obstacle(self.tileset, last_obstacle.rect.right, self.velocity, self.allow_pterodactyl))

        for obstacle in self.obstacle_group.sprites():
            if obstacle.rect.right <= 0:
                self.obstacle_group.remove(obstacle)
                self.obstacles += 1

        if self.score > 150:
            self.allow_pterodactyl = True

        self.fps = 60 + self.score//40
        self.score = self.frame_number // 8

        for dino in population:
            if pygame.sprite.spritecollideany(dino, self.obstacle_group):
                dino.kill()

        population.activate(self.obstacle_group.sprites(), self.fps)

    def render_updates(self):
        self.scenario_group.draw(self.display)
        self.scenario_group.update()

        self.obstacle_group.draw(self.display)
        self.obstacle_group.update()

        self.score_text = self.score_font.render(f"{self.score:05d}", True, Constants.PRIMARY_COLOR)
        self.display.blit(self.score_text, (530, 10))

        self.cloud_group.draw(self.display)
        self.cloud_group.update()

        population.draw(self.display)
        population.update()
        population.set_score(self.obstacles)

    def run(self):
        pygame.init()

        try:
            while True:
                self.handle_input_events()
                self.clock.tick(self.fps)

                if not population.over():
                    self.display.fill(Constants.WHITE_COLOR)

                    self.handle_sprites_events()
                    self.render_updates()

                    self.frame_number += 1
                else:
                    evaluated_population = population.avaliate()
                    new_population = genetic_algorithm.evolve(evaluated_population)
                    population.set_population(new_population)
                    self.__init__()

                pygame.display.flip()

        except KeyboardInterrupt:
            population.save_weights()
            pygame.quit()
