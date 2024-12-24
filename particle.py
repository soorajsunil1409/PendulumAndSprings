import pygame
import math
from utils import *

class Particle:
    def __init__(self, x: int, y: int, color: tuple, mass: int = 10, radius: int = 10, fixed: bool = False):
        self.pos = pygame.Vector2(x, y)
        self.color = color
        self.mass = mass
        self.radius = radius
        self.fixed = fixed
        self.moving = False

        self.force = pygame.Vector2(0, 0)
        self.acceleration = pygame.Vector2(0, 0)
        self.velocity = pygame.Vector2(0, 0)
        self.additional_force = pygame.Vector2(0, 0)

    def update(self):
        if not self.fixed and not self.moving:
            damping_force = -self.velocity * AIR_DRAG
            self.force = pygame.Vector2(0, 0)
            self.force = pygame.Vector2(0, GRAVITY) * self.mass
            self.force += self.additional_force + damping_force
            self.update_pos()
        else:
            self.force = pygame.Vector2(0, 0)
            self.acceleration = pygame.Vector2(0, 0)
            self.velocity = pygame.Vector2(0, 0)
        self.additional_force = pygame.Vector2(0, 0)

    def update_pos(self):
        self.acceleration = self.force / self.mass
        self.velocity += self.acceleration
        self.pos += self.velocity

    def draw(self, screen: pygame.Surface):
        pygame.draw.circle(screen, self.color, self.pos, self.radius)

    def add_force(self, force):
        if not self.fixed and not self.moving:
            self.additional_force += force

    def is_hovered(self, mouse_pos):
        distance = math.sqrt((self.pos.x - mouse_pos[0])**2 + (self.pos.y - mouse_pos[1])**2)
        return distance <= self.radius
        
    def set_position(self, mouse_pos):
        self.pos = pygame.Vector2(mouse_pos)
            
class Spring:
    def __init__(self, p1: Particle, p2: Particle, rest_length: int, spring_constant: int, damping_constant: int = 0):
        self.p1 = p1
        self.p2 = p2
        self.length = rest_length
        self.k = spring_constant
        self.c = damping_constant

    def update(self):
        direction = (self.p2.pos - self.p1.pos)
        curr_dist = direction.length()
        direction = direction.normalize()

        spring_force = direction * self.k * (curr_dist - self.length)

        # Damping
        relative_vel = self.p2.velocity - self.p1.velocity
        damping_force = direction * self.c * relative_vel.dot(direction)

        total_force = spring_force + damping_force

        self.p1.add_force(total_force)
        self.p2.add_force(-total_force)

    def draw(self, screen: pygame.Surface):
        pygame.draw.aaline(screen, BLACK, self.p1.pos, self.p2.pos)

