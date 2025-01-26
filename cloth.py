import pygame
import sys
import random
from utils import *
from particle import Particle, Spring
from ui import UI, Menu


class Sim:
    def __init__(self):
        pygame.init()
        self.screen = pygame.display.set_mode((W_SIZE, W_SIZE))
        self.clock = pygame.time.Clock()

        self.xpoints = 57
        self.ypoints = 15
        self.spacing = 10
        self.k = 2
        self.c = 1

        self.particle_matrix = [[Particle(j * self.spacing + self.spacing, i * self.spacing + CLOTH_Y, BLACK, 10, 4) for j in range(1, self.xpoints)] for i in range(1, self.ypoints)]

        self.selected_particle = None

        self.GRID_SIZE = 50
        self.grid = {}

        self.init_particles()
        self.make_cloth()

        UI.init(self)
        self.menu = Menu(self)

    def init_particle_matrix(self):
        self.particle_matrix = []
        for i in range(1, self.ypoints):
            row = []
            for j in range(0, self.xpoints):
                if j == 0:
                    row.append(Particle(j * self.spacing, i * self.spacing + CLOTH_Y, BLACK, 10, 4))
                else:
                    row.append(Particle(j * self.spacing + self.spacing, i * self.spacing + CLOTH_Y, BLACK, 10, 4))

            self.particle_matrix.append(row)

    def init_particles(self):
        self.particles = []
        self.springs = []

    def change_xpoints(self, newx):
        self.xpoints = int(newx)
        self.init_particle_matrix()
        self.init_particles()
        self.make_cloth()

    def change_ypoints(self, newy):
        self.ypoints = int(newy)
        self.init_particle_matrix()
        self.init_particles()
        self.make_cloth()

    def change_spacing(self, news):
        self.spacing = news
        self.init_particle_matrix()
        self.init_particles()
        self.make_cloth()

    def change_spring_constant(self, newk):
        self.k = newk
        self.init_particle_matrix()
        self.init_particles()
        self.make_cloth()

    def change_damp_constant(self, newc):
        self.c = newc
        self.init_particle_matrix()
        self.init_particles()
        self.make_cloth()

    def make_spring(self, par1: Particle, par2: Particle):
        # if random.randint(0, 20):
            s = Spring(par1, par2, (par1.pos - par2.pos).length(), self.k, self.c)
            self.springs.append(s)


    def connect_row(self, row: list[Particle], fixed: bool = False):
        for par1, par2 in zip(row, row[1:]):
            if fixed:
                par1.fixed = True
                par2.fixed = True
            self.make_spring(par1, par2)

    def connect_vertical(self, row1: list[Particle], row2: list[Particle]):
        for par1, par2 in zip(row1, row2):
            self.make_spring(par1, par2)


    def make_cloth(self):
        for i, (row1, row2) in enumerate(zip(self.particle_matrix, self.particle_matrix[1:])):

            if i == 0: 
                self.particles.extend(row1)
                self.connect_row(row1, fixed=True)

            self.particles.extend(row2)
            self.connect_row(row2)

            self.connect_vertical(row1, row2)

    def keep_within_screen(self, particle):
        """Ensure the particle stays within the screen bounds."""
        damping_factor = 1
        
        # Check left or right bounds
        if particle.pos.x - particle.radius < 0:
            particle.pos.x = particle.radius
            particle.velocity.x *= -damping_factor
        elif particle.pos.x + particle.radius > W_SIZE:
            particle.pos.x = W_SIZE - particle.radius
            particle.velocity.x *= -damping_factor
        
        # Check top or bottom bounds
        if particle.pos.y - particle.radius < 0:
            particle.pos.y = particle.radius
            particle.velocity.y *= -damping_factor
        elif particle.pos.y + particle.radius > W_SIZE:
            particle.pos.y = W_SIZE - particle.radius
            particle.velocity.y *= -damping_factor

    def get_grid_cell(self, particle):
        return (int(self.particle.pos.x) // self.GRID_SIZE, int(self.particle.pos.y) // self.GRID_SIZE)

    def handle_collisions(self):
        self.grid.clear()

        for particle in self.particles:
            cell = self.get_grid_cell(particle)
            if cell not in self.grid:
                self.grid[cell] = []
            self.grid[cell].append(particle)

        for particle in self.particles:
            cell = self.get_grid_cell(particle)

            neighboring_cells = [
                (cell[0], cell[1]), (cell[0] + 1, cell[1]), (cell[0] - 1, cell[1]),
                (cell[0], cell[1] + 1), (cell[0], cell[1] - 1)
            ]

            for neighbor in neighboring_cells:
                if neighbor in self.grid:
                    for other_particle in self.grid[neighbor]:
                        if particle != other_particle:

                            distance = particle.pos.distance_to(other_particle.pos)
                            min_distance = particle.radius + other_particle.radius

                            if distance < min_distance:
                                overlap = min_distance - distance
                                collision_vector = other_particle.pos - particle.pos

                                if collision_vector.length() > 0.001:
                                    collision_normal = collision_vector.normalize()

                                    particle.pos -= collision_normal * overlap * 0.5
                                    other_particle.pos += collision_normal * overlap * 0.5

                                    damping_factor = 0.8
                                    particle.velocity *= damping_factor
                                    other_particle.velocity *= damping_factor


    def run(self):
        while True:
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    sys.exit()

                elif event.type == pygame.MOUSEBUTTONDOWN:
                    mouse_pos = pygame.mouse.get_pos()

                    for particle in self.particles:
                        if particle.is_hovered(mouse_pos):
                            self.selected_particle = particle
                            particle.moving = True

                elif event.type == pygame.MOUSEBUTTONUP:
                    if self.selected_particle:
                        self.selected_particle.moving = False
                        self.selected_particle = None

            if self.selected_particle:
                self.selected_particle.set_position(pygame.mouse.get_pos())

            self.screen.fill(GRAY)

            self.menu.run()

            # region Update
            for s in self.springs:
                s.update()
            for particle in self.particles:
                particle.update()
                self.keep_within_screen(particle)
            # handle_collisions()
            # endregion

            # region Draw
            for s in self.springs:
                s.draw(self.screen)
            for particle in self.particles:
                particle.draw(self.screen)
            # endregion

            pygame.display.flip()
            self.clock.tick(FPS)


if __name__ == '__main__':
    s = Sim()
    s.run()