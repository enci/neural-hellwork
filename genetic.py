import pygad

target_difficulty = 0


def fitness_func(ga_instance, solution, solution_idx):  # solution = [count, angle, spread, speed, size, loop, wait]
    bullets_distribution = 0
    min_bullets = 0
    # evaluate these by initializing a game with these parameters
    # return -(difficulty_eval(bullets_distribution, min_bullets) - target_difficulty) ** 2
    return sum(-solution)


def difficulty_eval(bullets_distribution, min_bullets):
    return 0


fitness_function = fitness_func
gene_space = [
        list(range(1, 51)),      # count
        {'low': 0, 'high': 360},      # angle
        {'low': 0, 'high': 360},      # spread
        {'low': 0.1, 'high': 5},      # speed
        {'low': 0.1, 'high': 5},      # size
        list(range(0, 51)),      # loop
        list(range(0, 51)),      # wait
    ]

num_generations = 500
num_parents_mating = 4

sol_per_pop = 8
num_genes = 7

parent_selection_type = "sss"
keep_parents = -1

crossover_type = "uniform"

mutation_type = "random"
mutation_probability = 0.2

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
                       mutation_probability=mutation_probability)
ga_instance.run()
# ga_instance.plot_fitness()
# print(ga_instance.solutions_fitness)
print(ga_instance.best_solution())