"""# PSO/Mochila con NUMPY"""


def init_mochila():
    global pv_file
    global bs_file
    global rs_file

    pv_file = np.loadtxt('pv.csv', delimiter=',')
    rs_file = np.loadtxt('rs.csv', delimiter=',')
    bs_file = np.loadtxt('bs.csv', delimiter=',')


def mochila_res(X):
    Peso = np.sum(pv_file, axis=0)

    PR = np.matmul(X, pv_file)

    G = np.matmul(rs_file, X.transpose()).transpose()
    # Transpongo para cumplir con (k,j),(j,i)->(k,i)

    VIO = np.add(G, -1 * bs_file)  # Esto esta perfecto

    VIO = np.where(VIO < 0.0, 0.0, VIO)

    PNLTY = np.sum(VIO, axis=1)

    FI = np.add(PR, -1 * (Peso * PNLTY))

    return FI, VIO


def mochila(X):
    FI, VIO = mochila_res(X)

    return -FI


def activation(x, function=1):
    if (function == 1):  # Sigmoid
        return 1 / (1 + np.exp(-x))
    elif (function == 2):  # Softmax
        expo = np.exp(x)
        expo_sum = np.sum(np.exp(x))
        return expo / expo_sum
    elif (function == 3):  # ReLu
        return np.maximum(0, x)


def toDiscrete(x):
    return np.where(x < 0.5, 0, 1)


def convert_to_discrete(x):
    x_sigmoid = 1 / (1 + np.exp(-x))
    discrete_position = np.where(x_sigmoid < 0.5, 0, 1)
    return discrete_position


def calculate_velocity(w, particles_velocity, c1, c2, r1, r2, best_particle_position,
                       particles_position, best_global_position):
    inertia = w * particles_velocity
    best_particle_pos_component = r1 * (best_particle_position - particles_position)
    best_global_pos_component = r2 * (best_global_position - particles_position)

    new_velocity = inertia + c1 * best_particle_pos_component + c2 * best_global_pos_component
    return new_velocity


def calculate_best_position(objective_values, best_particle_cost, particles_position, best_particle_position, particles,
                            dimensions):
    bests = np.less(objective_values, best_particle_cost)
    reshape = np.reshape(bests, np.array([particles, 1]))
    bests_reshape = np.broadcast_to(reshape, np.array([particles, dimensions]))
    pos = np.where(bests_reshape, particles_position, best_particle_position)
    return pos


def runDiscretePSO_np(user_options, algorithm_options):
    # For each particle, initialize position and velocity
    particles_position = np.random.uniform(-1, 1, (algorithm_options['particles'], algorithm_options['dimensions']))
    particles_velocity = np.random.uniform(-1, 1, (algorithm_options['particles'], algorithm_options['dimensions']))

    # particles_position = convert_to_discrete(particles_position)
    particles_position = toDiscrete(activation(particles_velocity))

    particles = algorithm_options['particles']
    dimensions = algorithm_options['dimensions']
    best_global = None  # Best swarm cost
    best_global_position = np.empty((particles, dimensions))  # Best swarm position
    best_particle_position = particles_position
    best_particle_cost = algorithm_options['objective'](best_particle_position)  # obj_fuction(best_particle_position)

    for k in range(0, algorithm_options['iterations']):
        # while k < algorithm_options['iterations']:
        objective_values = algorithm_options['objective'](best_particle_position)  # obj_fuction(particles_position)
        best_index = np.argmin(objective_values)
        best_value = objective_values[best_index]

        # 150 x 20 !!!
        best_particle_position = calculate_best_position(objective_values, best_particle_cost, particles_position,
                                                         best_particle_position, particles, dimensions)

        if best_global is None or best_value < best_global:
            # Update best swarm cost and position
            best_global = best_value
            best_global_position = particles_position[best_index]

        r1 = np.random.uniform(0, 1, (algorithm_options['particles'], algorithm_options['dimensions']))
        r2 = np.random.uniform(0, 1, (algorithm_options['particles'], algorithm_options['dimensions']))

        particles_velocity = calculate_velocity(user_options['w'], particles_velocity, user_options['c1'],
                                                user_options['c2'], r1, r2, best_particle_position,
                                                particles_position, best_global_position)

        # new_particle_positions = particles_position + particles_velocity
        particles_position = toDiscrete(activation(particles_position + particles_velocity))

        best_particle_position = particles_position

    return best_global, best_global_position


"""# PSO/Mochila con JAX.NUMPY"""

from datetime import datetime

import jax.numpy as npj
import numpy as np
from jax import random, jit


@jit
def mochila_res(X):
    # P = len(X)
    # M = nro_restricciones

    Peso = npj.sum(pv_file, axis=0)

    PR = npj.matmul(X, pv_file)

    G = npj.matmul(rs_file, X.transpose()).transpose()
    # Transpongo para cumplir con (k,j),(j,i)->(k,i)

    VIO = npj.add(G, -1 * bs_file)  # Esto esta perfecto

    VIO = npj.where(VIO < 0.0, 0.0, VIO)

    PNLTY = npj.sum(VIO, axis=1)

    FI = npj.add(PR, -1 * (Peso * PNLTY))

    return FI, VIO


@jit
def mochila(X):
    FI, VIO = mochila_res(X)

    return -FI


@jit
def activation(x, function=1):
    if (function == 1):  # Sigmoid
        return 1 / (1 + npj.exp(-x))
    elif (function == 2):  # Softmax
        expo = npj.exp(x)
        expo_sum = npj.sum(npj.exp(x))
        return expo / expo_sum
    elif (function == 3):  # ReLu
        return npj.maximum(0, x)


@jit
def toDiscrete(x):
    return npj.where(x < 0.5, 0, 1)


@jit
def convert_to_discrete(x):
    x_sigmoid = 1 / (1 + npj.exp(-x))
    discrete_position = npj.where(x_sigmoid < 0.5, 0, 1)
    return discrete_position


@jit
def calculate_velocity(w, particles_velocity, c1, c2, r1, r2, best_particle_position,
                       particles_position, best_global_position):
    inertia = w * particles_velocity
    best_particle_pos_component = r1 * (best_particle_position - particles_position)
    best_global_pos_component = r2 * (best_global_position - particles_position)

    new_velocity = inertia + c1 * best_particle_pos_component + c2 * best_global_pos_component
    return new_velocity


def calculate_best_position(objective_values, best_particle_cost, particles_position, best_particle_position, particles,
                            dimensions):
    bests = npj.less(objective_values, best_particle_cost)
    reshape = npj.reshape(bests, npj.array([particles, 1]))
    bests_reshape = npj.broadcast_to(reshape, npj.array([particles, dimensions]))
    pos = npj.where(bests_reshape, particles_position, best_particle_position)
    return pos


def runDiscretePSO_jax(user_options, algorithm_options):
    # For each particle, initialize position and velocity
    particles_position = random.uniform(random.PRNGKey(datetime.now().microsecond),
                                        (algorithm_options['particles'], algorithm_options['dimensions']), None, -1, 1)
    particles_velocity = random.uniform(random.PRNGKey(datetime.now().microsecond),
                                        (algorithm_options['particles'], algorithm_options['dimensions']), None, -1, 1)

    # particles_position = convert_to_discrete(particles_position)
    particles_position = toDiscrete(activation(particles_velocity))

    particles = algorithm_options['particles']
    dimensions = algorithm_options['dimensions']
    best_global = None  # Best swarm cost
    best_global_position = npj.empty((particles, dimensions))  # Best swarm position
    best_particle_position = particles_position
    best_particle_cost = algorithm_options['objective'](best_particle_position)  # obj_fuction(best_particle_position)

    for k in range(0, algorithm_options['iterations']):
        # while k < algorithm_options['iterations']:
        objective_values = algorithm_options['objective'](best_particle_position)  # obj_fuction(particles_position)
        best_index = npj.argmin(objective_values)
        best_value = objective_values[best_index]

        # 150 x 20 !!!
        best_particle_position = calculate_best_position(objective_values, best_particle_cost, particles_position,
                                                         best_particle_position, particles, dimensions)

        if best_global is None or best_value < best_global:
            # Update best swarm cost and position
            best_global = best_value
            best_global_position = particles_position[best_index]

        r1 = random.uniform(random.PRNGKey(datetime.now().microsecond),
                            (algorithm_options['particles'], algorithm_options['dimensions']), None, 0, 1)
        r2 = random.uniform(random.PRNGKey(datetime.now().microsecond),
                            (algorithm_options['particles'], algorithm_options['dimensions']), None, 0, 1)

        particles_velocity = calculate_velocity(user_options['w'], particles_velocity, user_options['c1'],
                                                user_options['c2'], r1, r2, best_particle_position,
                                                particles_position, best_global_position)

        # new_particle_positions = particles_position + particles_velocity
        particles_position = toDiscrete(activation(particles_position + particles_velocity))

        best_particle_position = particles_position

        # best_cost_yet_found = npj.min(best_particle_cost)
        # relative_measure = algorithm_options['ftol'] * (1 + npj.abs(best_cost_yet_found))
        # if (npj.any(npj.abs(best_particle_cost - best_cost_yet_found) < relative_measure)):
        #     break

    return best_global, best_global_position


"""# Comparar Soluciones"""

import time
import pyswarms as ps


def generar_instancia(nro_items, nro_restricciones, alfa=0.75):
    rs = np.random.randint(1000, size=(nro_restricciones, nro_items))
    bs = alfa * np.sum(rs, axis=1)
    q = np.random.random_sample((nro_items))
    pv = np.sum(rs, axis=0) / nro_restricciones
    pv = np.add(pv, 500 * q)

    return pv, rs, bs


def imprimir_solucion(solX):
    solPru = np.random.randint(2, size=(1, nro_items))
    for k in range(0, nro_items):
        solPru[0, k] = solX[k]

    print(solX)
    print(solPru)

    [f, vio] = mochila_res(solPru)
    print(vio)


def solucion_nuestra_np(num_particles, iterations, dim, ftol, options):
    global solX_NumPy
    user_options = {'c1': options['c1'], 'c2': options['c2'], 'w': options['w']}
    algorithm_options = {'particles': num_particles, 'dimensions': dim,
                         'iterations': iterations, 'objective': mochila, 'ftol': ftol}

    # Perform optimization
    start = time.time()
    solFO, solX_NumPy = runDiscretePSO_np(user_options, algorithm_options)
    wall_time = time.time() - start

    return solFO, wall_time


def solucion_nuestra_jax(num_particles, iterations, dim, ftol, options):
    global solX_NumPyJAX
    user_options = {'c1': options['c1'], 'c2': options['c2'], 'w': options['w']}
    algorithm_options = {'particles': num_particles, 'dimensions': dim,
                         'iterations': iterations, 'objective': mochila, 'ftol': ftol}

    # Perform optimization
    start = time.time()
    solFO, solX_NumPyJAX = runDiscretePSO_jax(user_options, algorithm_options)
    wall_time = time.time() - start

    return solFO, wall_time


def solucion_pyswarm(num_particles, iteraciones, dimensiones, ftol, options):
    global solX_PySwarms
    optimizer = ps.discrete.binary.BinaryPSO(n_particles=num_particles,
                                             dimensions=dimensiones,
                                             options=options,
                                             init_pos=None,
                                             velocity_clamp=None,
                                             vh_strategy='unmodified', ftol=ftol)

    # Perform optimization
    start = time.time()
    [solFO, solX_PySwarms] = optimizer.optimize(mochila, iters=iteraciones)
    wall_time = time.time() - start

    return solFO, wall_time


def comparar_solciones():
    # function particular variables
    global pv_file
    global bs_file
    global rs_file
    global nro_items
    global nro_restricciones

    nro_items = 20
    nro_restricciones = 5

    [pv_temp, rs_temp, bs_temp] = generar_instancia(nro_items, nro_restricciones)
    np.savetxt('pv.csv', pv_temp, delimiter=',')
    np.savetxt('rs.csv', rs_temp, delimiter=',')
    np.savetxt('bs.csv', bs_temp, delimiter=',')

    dimensiones = nro_items
    iteraciones = 100
    num_particles = 15

    prom_iters = 30
    ftol = -np.inf

    wall_times = [0, 0, 0]
    solFOs = [0, 0, 0]
    # Item 0: Solucion Pyswarms
    # Item 1: Solucion Nuestra con Numpy
    # Item 2: Solucion Nuestra con JAX

    init_mochila()

    for i in range(prom_iters):
        [solFO, wall_time] = solucion_pyswarm(num_particles, iteraciones, dimensiones, ftol,
                                              options={'c1': 0.5, 'c2': 0.3, 'w': 0.9, 'k': num_particles, 'p': 1})
        wall_times[0] += wall_time
        solFOs[0] += solFO

        [solFO, wall_time] = solucion_nuestra_np(num_particles, iteraciones, dimensiones, ftol,
                                                 options={'c1': 0.5, 'c2': 0.3, 'w': 0.9, 'k': num_particles, 'p': 1})
        wall_times[1] += wall_time
        solFOs[1] += solFO

        [solFO, wall_time] = solucion_nuestra_jax(num_particles, iteraciones, dimensiones, ftol,
                                                  options={'c1': 0.5, 'c2': 0.3, 'w': 0.9, 'k': num_particles, 'p': 1})
        wall_times[2] += wall_time
        solFOs[2] += solFO

    print("\nwall_time pyswarms: {:0.2f}ms".format(1000 * wall_times[0] / prom_iters))
    print("wall_time nuestro: {:0.2f}ms (con NumPy)".format(1000 * wall_times[1] / prom_iters))
    print("wall_time nuestro: {:0.2f}ms (con JAX.NumPy)".format(1000 * wall_times[2] / prom_iters))

    print("\nSolucion Pyswarms: {:0.2f}".format(-solFOs[
        0] / prom_iters))  # Los valores los pasamos a positivo ya que fueron tomados directamente de la mochila.
    print("Solucion Numpy: {:0.2f}".format(-solFOs[1] / prom_iters))
    print("Solucion JAX: {:0.2f}".format(-solFOs[2] / prom_iters))

    # Imprime la última mochila ejecutada.
    print("\nSolución PySwarms:")
    imprimir_solucion(solX_PySwarms)
    print("\nSolución NumPy:")
    imprimir_solucion(solX_NumPy)
    print("\nSolución JAX.NumPy:")
    imprimir_solucion(solX_NumPyJAX)


if __name__ == '__main__':
    comparar_solciones()
