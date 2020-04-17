from random import random

import numpy as np
import tensorflow as tf

from solution import solve
from utils import grid2values, values2grid


def grid_generate(fraction=0.2, solvable=True):
    """Generate a random sudoku grid

    Parameters
    ----------
    fraction(float) - percentage of squares that are originally filled
    solvable(bool)  - if the output must be a solvable sudoku puzzle

    Returns
    -------
        a string representing a sudoku grid.
        Ex. '2.............62....1....7...6..8...3...9...7...6..4...4....8....52.............3'
    """
    output = ''
    for i in range(9*9):
        if random() > fraction: output += '.'
        else:                   output += str(int(random()*10))

    if solvable and not solve(grid2values(output)):
        return grid_generate(fraction, solvable)
    else:
        return output


def one_hot_encode(number: str) -> np.array:
    if number == '.': number = 11
    output = np.zeros((11,))
    output[int(number)] = 1
    return output


def one_hot_decode(onehot: np.array) -> str:
    return str(np.argmax(onehot))


def grid2onehot(grid: str) -> np.array:
    output = (
        np.vectorize(one_hot_encode)(
            np.array(list(grid))
        )
        .reshape(9,9,11)
    )
    return output


def grid_generator(fraction=0.2, solvable=True, limit: int=None) -> np.array:
    count = 0
    while not limit or count <= limit:
        count += 1
        yield grid_generate(fraction, solvable)


def onehot_solved_generator(fraction=0.2, solvable=True, limit: int=None)  -> (np.array, np.array):
    for grid in grid_generator(fraction, solvable, limit):
        onehot = grid2onehot(grid)
        solved = solve(grid)
        solved = grid2onehot(values2grid(solved))
        yield onehot, solved


def dataset():
    input_shape  = (9,9,11)
    output_shape = (9,9,10)
    dataset = (
        tf.data.Dataset.from_generator(
            onehot_solved_generator,
            (tf.float32, tf.float32, tf.float32),
            (tf.TensorShape([output_shape[0]]), tf.TensorShape([output_shape[1]]), tf.TensorShape([output_shape[2]]))
        )
        .batch(128)
        .prefetch(16)
    )
    return dataset
