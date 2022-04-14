import math
import operator as op
from functools import partial
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
update_rects = [[]]
fps = 0

moves = [(K_w, K_UP), (K_s, K_DOWN), (K_a, K_LEFT), (K_d, K_RIGHT)]
moves = {key:2**i for i in range(len(moves)) for key in moves[i]}

def intVector(v):
  return (*map(int, map(round, v)),)


class Player:
  def __init__(self, pos, angle):
    self.pos, self.angle = vector(pos), vector(1, 0).rotate(angle)
    self.speed = 0
    self.top_speed = 12.5
  
  @property
  def velocity(self):
    return self.angle * self.speed
  
  def input(self, key, keydown=True):
    if keydown:
      self.input |= key
    else:
      self.input &= ~key
  
  def move(self):
    # {1: (0, -1), 2: (0, 1), 4: (-1, 0), 8: (1, 0)}
    self.input = 0


screen.fill(background)
pygame.display.flip()

player = Player((0, 0), -90)

while True:
  clock.tick(60)
  fps = clock.get_fps()
  update_rects = [update_rects[1:]]
  screen.fill(background)
  
  if pygame.event.get(QUIT):
    break
  for event in pygame.event.get():
    if event.type == KEYDOWN:
      if event.key == K_ESCAPE:
        pygame.event.post(pygame.event.Event(QUIT))
      if event.key in moves:
        player.input(moves[event.key])
  
  player.move()
  
  screen.blit(font.render(str(int(fps)), 0, foreground), (0,0))
  update_rects.append(pygame.rect.Rect((0,0), font.size(str(int(fps)))))
  pygame.display.update(update_rects[0]+update_rects[1:])
pygame.quit()
