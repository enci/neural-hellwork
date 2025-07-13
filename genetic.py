import time

import pygad
from pygame import Vector2
import math
from talakat import TokenType
from talakat_evaluator import TalakatEvaluator

target_avg_bullets = 10
n_fitness_call = 0

def fitness_func(ga_instance, solution, solution_idx):  # solution = [count, angle, spread, speed, size, loop, wait]
    global n_fitness_call
    n_fitness_call += 1
    pattern = [
        (TokenType.COUNT, solution[0]),
        (TokenType.ANGLE, solution[1]),
        (TokenType.SPREAD, solution[2]),
        (TokenType.SPEED, solution[3]),  # Scaled down speed
        (TokenType.SIZE, solution[4]),  # Scaled down size
        (TokenType.LOOP, solution[5]),
        (TokenType.WAIT, solution[6])
    ]
    enemy_pos = Vector2(0, 270)
    # Create evaluator with bounds
    evaluator = TalakatEvaluator(
        pattern=pattern,
        enemy_position=enemy_pos,
        bounds=(-270, 270, -360, 360)
    )
    n_frames = 300
    evaluator.simulate(n_frames)
    # min_x, max_x, min_y, max_y = evaluator.get_coverage_area()
    # area = (max_x - min_x) * (max_y - min_y)
    average_bullets = evaluator.get_total_bullets_spawned()/n_frames
    # difficulty = average number of bullets
    # always maximize bullets coverage
    return -(average_bullets - target_avg_bullets)**2 #+ (area / (520*720))



fitness_function = fitness_func
gene_space = [
        list(range(1, 51)),      # count
        {'low': 0, 'high': 360},      # angle
        {'low': 0, 'high': 360},      # spread
        {'low': 0.1, 'high': 5},      # speed
        {'low': 0.1, 'high': 5},      # size
        list(range(0, 51)),      # loop
        list(range(0, 2)),      # wait
    ]

num_generations = 20
num_parents_mating = 4

sol_per_pop = 8
num_genes = 7

parent_selection_type = "sss"
keep_parents = -1

crossover_type = "uniform"

mutation_type = "random"
mutation_probability = 0.1

ga_instance = pygad.GA(num_generations=num_generations,
                       num_parents_mating=num_parents_mating,
                       fitness_func=fitness_function,
                       gene_space=gene_space,
                       sol_per_pop=sol_per_pop,
                       num_genes=num_genes,
                       parent_selection_type=parent_selection_type,
                       keep_parents=keep_parents,
                       crossover_type=crossover_type,
                       mutation_type=mutation_type,
                       mutation_probability=mutation_probability,
                       save_best_solutions=True)
t = time.time()
ga_instance.run()
# ga_instance.plot_fitness()
# print(ga_instance.solutions_fitness)
print(ga_instance.best_solution())
print(ga_instance.best_solutions)
print(time.time() - t)
print(n_fitness_call)