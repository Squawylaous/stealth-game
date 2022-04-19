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

Flags = {"move":False}
Entities = pygame.sprite.Group()
LvlGroup = None

post_event = lambda e:pygame.event.post(pygame.event.Event(e))
group_dict = lambda d:{i:v for k, v in d.items() for i in k}

hold_moves = group_dict({(K_w, K_UP):"up", (K_s, K_DOWN):"down", (K_a, K_LEFT):"left", (K_d, K_RIGHT):"right"})
toggle_moves = group_dict({})

def rect_circle_collide(cpos, csize, rect):
  crect = pygame.rect.Rect((0 ,0), (csize*2, csize*2))
  crect.center = cpos
  if not rect.colliderect(crect):
    return False
  rcenter = vector(rect.center)
  rdist = rcenter.distance_to(rect.topleft)
  dist = rcenter.distance_to(cpos)
  if rdict + csize > dist:
    return False
  if dist <= min(rect.width, rect.height) + csize:
    return True
  return rect.collidepoint(cpos + cpos.angle_to(rect.center)*csize)


class Player(pygame.sprite.Sprite):
  directions = {"up":(0, -1), "down":(0, 1), "left":(-1, 0), "right":(1, 0)}
  isstill = set(directions.keys()).isdisjoint
  
  def __init__(self, pos, angle):
    super().__init__(Entities)
    
    self.prev_pos, self.prev_angle = vector(), vector()
    
    self.pos, self.angle = vector(pos), vector(1, 0).rotate(angle)
    self.prev_pos, self.prev_angle = self.pos, self.angle
    self.speed = 0
    self.accel = 1
    self.max_speed = 5
    self.input, self.prev_input = set(), set()
    self.size = 37.5
    self.base_image = pygame.Surface((self.size*1.5, self.size*1.5))
    self.base_image.fill(background)
    self.base_image.set_colorkey(background)
    triangle = (lambda size:[(0, size*.875), (size*.25, size/2), (0, size*.125), (size, size/2)])(self.size*1.5)
    pygame.draw.polygon(self.base_image, foreground, triangle)
    pygame.draw.polygon(self.base_image, (0, 0, 0), triangle, 5)
  
  @property
  def velocity(self):
    return self.angle * self.speed
  
  def hold_input(self, key, keydown):
    getattr(self.input, ("add" if keydown else "discard"))(key)
  
  def toggle_input(self, key):
    getattr(self.input, ("discard" if key in self.input else "add"))(key)
  
  def update(self, walls):
    if not self.isstill(self.input):
      for dir_ in self.directions:
        if dir_ in self.input:
          self.angle += self.directions[dir_]
      if self.angle:
        self.prev_angle, self.angle = self.angle, self.angle.normalize()
      self.speed += self.accel
    else:
      self.speed -= self.accel
    self.velocity = self.angle * self.speed
    
    self.speed = min(max(self.speed, 0), self.max_speed)
    self.prev_pos, self.pos = self.pos, self.pos + self.velocity
    self.prev_input = self.input.copy()
    
    self.image = pygame.transform.rotate(self.base_image, -vector().angle_to(self.angle))
    self.rect = self.image.get_rect()
    self.rect.center = screen_rect.center


class Level(pygame.sprite.Group):
  def __init__(self, size, walls):
    super().__init__()
    
    self.size = vector(size, size)
    self.background = Wall(self, ((0, 0), self.size), fill=background)
    
    self.walls = [*map(partial(Wall, self), walls)]


class Wall(pygame.sprite.Sprite):
  def __init__(self, lvl, rect, *, fill=foreground):
    super().__init__(lvl)
    
    self.lvl = lvl
    self.base_rect = pygame.rect.Rect(rect)
    self.image = pygame.Surface(self.base_rect.size)
    self.image.fill(fill)
  
  def update(self, pos):
    self.rect = self.base_rect.move(-pos + screen_rect.center)


player = Player((400, 400), -90)
lvl1 = Level(2000, [(100, 100, 200, 200), (500, 100, 200, 200), (100, 500, 200, 200), (500, 500, 200, 200)])
LvlGroup = lvl1

while True:
  clock.tick(60)
  fps = clock.get_fps()
  screen.fill((0, 0, 0))
  
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
  
  
  LvlGroup.update(player.pos)
  LvlGroup.draw(screen)
  Entities.update(LvlGroup.walls)
  Entities.draw(screen)
  
  screen.blit(font.render(str(int(fps)), 0, foreground), (0, 0))
  screen.blit(font.render(str(int(player.collided)), 0, foreground), (50, 0))
  pygame.display.flip()
pygame.quit()
