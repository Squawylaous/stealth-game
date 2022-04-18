import math
import operator as op
from functools import partial, reduce
from itertools import chain
import pygame
from pygame.locals import *
from pygame.math import Vector2 as vector

pygame.init()

clock = pygame.time.Clock()
font = pygame.font.SysFont("Arial", 25)
background = Color(161, 161, 161)
foreground = Color(255, 255, 255)
screen = pygame.display.set_mode((0, 0), FULLSCREEN)
screen_rect = screen.get_rect()
fps = 0

entities = pygame.sprite.Group()

group_dict = lambda d:{i:v for k, v in d.items() for i in k}

hold_moves = group_dict({(K_w, K_UP):"up", (K_s, K_DOWN):"down", (K_a, K_LEFT):"left", (K_d, K_RIGHT):"right"})
toggle_moves = group_dict({})


class Player(pygame.sprite.Sprite):
  directions = {"up":(0, -1), "down":(0, 1), "left":(-1, 0), "right":(1, 0)}
  isstill = set(directions.keys()).isdisjoint
  
  def __init__(self, pos, angle):
    super().__init__(entities)
    
    self.pos, self.angle = vector(pos), vector(1, 0).rotate(angle)
    self.speed = 0
    self.accel = 1
    self.max_speed = 12.5
    self.input, self.prev_input = set(), set()
    self.size = 50
    self.base_image = pygame.Surface((self.size, self.size))
    self.base_image.set_colorkey((0, 0, 0))
    pygame.draw.aalines(self.base_image, foreground, 1, [(0, 0), (self.size, self.size/2), (0, self.size)])
  
  @property
  def velocity(self):
    return self.angle * self.speed
  
  def hold_input(self, key, keydown):
    getattr(self.input, ("add" if keydown else "discard"))(key)
  
  def toggle_input(self, key):
    getattr(self.input, ("discard" if key in self.input else "add"))(key)
  
  def update(self):
    if not self.isstill(self.input):
      for dir_ in self.directions:
        if dir_ in self.input:
          self.angle += self.directions[dir_]
      self.angle.normalize_ip()
      self.speed += self.accel
    else:
      self.speed -= self.accel
    
    self.speed = min(max(self.speed, 0), self.max_speed)
    self.pos += self.velocity
    self.prev_input = self.input.copy()
    
    self.image = pygame.transform.rotate(self.base_image, vector().angle_to(self.angle))
    self.rect = self.image.get_rect()
    self.rect.center = self.pos

player = Player((0, 0), -90)

while True:
  clock.tick(60)
  fps = clock.get_fps()
  screen.fill(background)
  
  if pygame.event.get(QUIT):
    break
  for event in pygame.event.get():
    if event.type == KEYDOWN:
      if event.key == K_ESCAPE:
        pygame.event.post(pygame.event.Event(QUIT))
      elif event.key in hold_moves:
        player.hold_input(hold_moves[event.key], 1)
    elif event.type == KEYUP:
      if event.key in hold_moves:
        player.hold_input(hold_moves[event.key], 0)
      elif event.key in toggle_moves:
        player.toggle_input(toggle_moves[event.key])
  
  entities.update()
  entities.draw(screen)
  
  screen.blit(font.render(str(int(fps)), 0, foreground), (0, 0))
  pygame.display.flip()
pygame.quit()
