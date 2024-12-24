import pygame
import sys
from utils import *
from particle import Particle, Spring

pygame.init()
display = pygame.display.set_mode((W_SIZE, W_SIZE))
clock = pygame.time.Clock()

# Initialize the particle matrix (cloth)
particle_matrix = [[Particle(j * SPACING + SPACING, i * SPACING + SPACING, BLACK, 10, 4) for j in range(1, 57)] for i in range(1, 15)]
particles = []
springs = []

selected_particle = None

GRID_SIZE = 50  # Grid cell size for spatial partitioning

# Grid dictionary to store particles by their grid cell index
grid = {}

def make_spring(par1: Particle, par2: Particle):
    s = Spring(par1, par2, (par1.pos - par2.pos).length(), 3, 1.5)
    springs.append(s)


def connect_row(row: list[Particle], fixed: bool = False):
    for par1, par2 in zip(row, row[1:]):
        if fixed:
            par1.fixed = True
            par2.fixed = True
        make_spring(par1, par2)

def connect_vertical(row1: list[Particle], row2: list[Particle]):
    for par1, par2 in zip(row1, row2):
        make_spring(par1, par2)


def make_cloth():
    for i, (row1, row2) in enumerate(zip(particle_matrix, particle_matrix[1:])):

        if i == 0: 
            particles.extend(row1)
            connect_row(row1, fixed=True)

        particles.extend(row2)
        connect_row(row2)

        connect_vertical(row1, row2)

make_cloth()

def keep_within_screen(particle):
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

def get_grid_cell(particle):
    """Return the grid cell for the particle."""
    return (int(particle.pos.x) // GRID_SIZE, int(particle.pos.y) // GRID_SIZE)

def handle_collisions():
    """Handle collision between particles using spatial partitioning."""
    # Clear grid and reset particle groupings
    grid.clear()

    # Assign particles to grid cells
    for particle in particles:
        cell = get_grid_cell(particle)
        if cell not in grid:
            grid[cell] = []
        grid[cell].append(particle)

    # For each particle, check neighboring grid cells for collisions
    for particle in particles:
        cell = get_grid_cell(particle)

        # Check the particle in its cell and neighboring cells
        neighboring_cells = [
            (cell[0], cell[1]), (cell[0] + 1, cell[1]), (cell[0] - 1, cell[1]),
            (cell[0], cell[1] + 1), (cell[0], cell[1] - 1)
        ]

        for neighbor in neighboring_cells:
            if neighbor in grid:
                # Only check particles that are in neighboring cells
                for other_particle in grid[neighbor]:
                    if particle != other_particle:  # Avoid checking the same particle

                        # Calculate the distance only if necessary
                        distance = particle.pos.distance_to(other_particle.pos)
                        min_distance = particle.radius + other_particle.radius

                        if distance < min_distance:  # Check if particles are colliding
                            overlap = min_distance - distance
                            collision_vector = other_particle.pos - particle.pos

                            # Avoid zero-length vectors by checking the magnitude
                            if collision_vector.length() > 0.001:
                                collision_normal = collision_vector.normalize()

                                # Apply a simple elastic collision response (repulsion)
                                particle.pos -= collision_normal * overlap * 0.5
                                other_particle.pos += collision_normal * overlap * 0.5

                                # Apply damping to velocities (simulate energy loss)
                                damping_factor = 0.8
                                particle.velocity *= damping_factor
                                other_particle.velocity *= damping_factor


while True:
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            sys.exit()

        elif event.type == pygame.MOUSEBUTTONDOWN:
            mouse_pos = pygame.mouse.get_pos()

            for particle in particles:
                if particle.is_hovered(mouse_pos):
                    selected_particle = particle
                    particle.moving = True

        elif event.type == pygame.MOUSEBUTTONUP:
            if selected_particle:
                selected_particle.moving = False
                selected_particle = None

    if selected_particle:
        selected_particle.set_position(pygame.mouse.get_pos())

    display.fill(GRAY)

    # region Update
    for s in springs:
        s.update()
    for particle in particles:
        particle.update()
        keep_within_screen(particle)
    # handle_collisions()  # Check for collisions after updates
    # endregion

    # region Draw
    for s in springs:
        s.draw(display)
    for particle in particles:
        particle.draw(display)
    # endregion

    pygame.display.flip()
    clock.tick(FPS)
