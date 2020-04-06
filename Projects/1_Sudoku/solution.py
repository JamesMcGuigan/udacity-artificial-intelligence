#!/usr/bin/env python3

from utils import *
import re


row_units    = [cross(r, cols) for r in rows]
column_units = [cross(rows, c) for c in cols]
square_units = [cross(rs, cs) for rs in ('ABC','DEF','GHI') for cs in ('123','456','789')]
unitlist     = row_units + column_units + square_units

# TODO: Update the unit list to add the new diagonal units
diagonals    = [
    [ rows[i] + cols[i]      for i in range(len(rows)) ],
    [ rows[i] + cols[-(i+1)] for i in range(len(rows)) ],
]
unitlist     = unitlist + diagonals


# Must be called after all units (including diagonals) are added to the unitlist
units = extract_units(unitlist, boxes)
peers = extract_peers(units, boxes)


def hash_values(values):
    return str(sorted(values.items()))

def is_singleton(values):
    return all(map(lambda value: len(value) == 1, values.values()))

def is_valid(values):
    if not all(map(len, values.values())):  # check for empty cells
        return False
    for unit in unitlist:
        singles = [ values[peer] for peer in unit if len(values[peer]) == 1 ]
        if len(singles) != len(set(singles)):
            return False
    return True

def is_solved(values):
    return is_singleton(values) and is_valid(values)



def naked_twins(values):
    """Eliminate values using the naked twins strategy.

    The naked twins strategy says that if you have two or more unallocated boxes
    in a unit and there are only two digits that can go in those two boxes, then
    those two digits can be eliminated from the possible assignments of all other
    boxes in the same unit.

    Parameters
    ----------
    values(dict)
        a dictionary of the form {'box_name': '123456789', ...}

    Returns
    -------
    dict
        The values dictionary with the naked twins eliminated from peers

    Notes
    -----
    Your solution can either process all pairs of naked twins from the input once,
    or it can continue processing pairs of naked twins until there are no such
    pairs remaining -- the project assistant test suite will accept either
    convention. However, it will not accept code that does not process all pairs
    of naked twins from the original input. (For example, if you start processing
    pairs of twins and eliminate another pair of twins before the second pair
    is processed then your code will fail the PA test suite.)

    The first convention is preferred for consistency with the other strategies,
    and because it is simpler (since the reduce_puzzle function already calls this
    strategy repeatedly).

    See Also
    --------
    Pseudocode for this algorithm on github:
    https://github.com/udacity/artificial-intelligence/blob/master/Projects/1_Sudoku/pseudocode.md
    """
    original = values.copy()
    for unit in unitlist:
        # Build inverted index: { value: [cells] }
        twins = { original[cell]: [] for cell in unit }
        for cell in unit:
            twins[ original[cell] ].append(cell)

        # Search for naked twins and eliminate
        for value, cells in twins.items():
            if len(value) == 2 and len(value) == len(cells):         # should also work with triplets or greater
                for peer in unit:
                    if peer in cells: continue                       # ignore self

                    ### Optimize: Slower (10ms)
                    ### DOCS: https://stackoverflow.com/questions/3939361/remove-specific-characters-from-a-string-in-python
                    # values[peer] = values.get(peer,'').translate({ord(c): None for c in value})

                    ### Optimize: Faster (7ms)
                    values[peer] = set(values[peer]) - set(value)
                    values[peer] = "".join(values[peer])     # cast back to string

    # assert is_valid(values)
    return values


def eliminate(values):
    """Apply the eliminate strategy to a Sudoku puzzle

    The eliminate strategy says that if a box has a value assigned, then none
    of the peers of that box can have the same value.

    Parameters
    ----------
    values(dict)
        a dictionary of the form {'box_name': '123456789', ...}

    Returns
    -------
    dict
        The values dictionary with the assigned values eliminated from peers
    """
    original = values.copy()               # unit tests require not eliminating later values
    for cell, value in original.items():
        if len(value) != 1:  continue      # still has multiple choice
        for peer in peers[cell]:
            if peer == cell: continue      # unsure if peers includes cell
            if value == values[peer]:
                return original            # invalid grid
            if value in values[peer]:
                values[peer] = values[peer].replace(value, '')

    # assert is_valid(values)
    return values


def only_choice(values):
    """Apply the only choice strategy to a Sudoku puzzle

    The only choice strategy says that if only one box in a unit allows a certain
    digit, then that box must be assigned that digit.

    Parameters
    ----------
    values(dict)
        a dictionary of the form {'box_name': '123456789', ...}

    Returns
    -------
    dict
        The values dictionary with all single-valued boxes assigned

    Notes
    -----
    You should be able to complete this function by copying your code from the classroom
    """
    for unit in unitlist:
        for cell in unit:
            if len(values[cell]) == 1: continue   # already solved
            ### Optimize: Slower (39ms)
            # options   = values[cell]
            # others    = set("".join([ values[peer] for peer in unit if peer != cell ]))
            # remaining = options.translate({ord(c): None for c in others})

            ### Optimize: Faster (33ms)
            options   = set(values[cell])
            others    = set([ values[peer] for peer in unit if peer != cell ])
            remaining = options - others
            if len(options) == 1:
                values[cell] = "".join(sorted(remaining))  # cast to string

    # assert is_valid(values)
    return values


def reduce_puzzle(values):
    """Reduce a Sudoku puzzle by repeatedly applying all constraint strategies

    Parameters
    ----------
    values(dict)
        a dictionary of the form {'box_name': '123456789', ...}

    Returns
    -------
    dict or False
        The values dictionary after continued application of the constraint strategies
        no longer produces any changes, or False if the puzzle is unsolvable
    """
    original = values.copy()               # unit tests require not eliminating later values

    values = eliminate(values)
    values = only_choice(values)
    values = naked_twins(values)

    if hash_values(values) != hash_values(original):
        return reduce_puzzle(values)
    else:
        return values


def search(values, verbose=False):
    """Apply depth first search to solve Sudoku puzzles in order to solve puzzles
    that cannot be solved by repeated reduction alone.

    Parameters
    ----------
    values(dict)
        a dictionary of the form {'box_name': '123456789', ...}

    Returns
    -------
    dict or False
        The values dictionary with all boxes assigned or False

    Notes
    -----
    You should be able to complete this function by copying your code from the classroom
    and extending it to call the naked twins strategy.
    """
    values = reduce_puzzle(values)
    if verbose: display(values)

    if values == False:      return False   # unsolvable
    if is_solved(values):    return values  # solved

    unsolved = sorted([
        (len(value), cell, values[cell])
        for cell, value in values.items()
        if len(value) > 1
    ])
    if len(unsolved) == 0:   return False   # BUGFIX: udacity submit unit tests

    length, cell, options = min(unsolved)
    for option in options:
        if verbose: print('solve', cell, option, options)
        clone       = values.copy()
        clone[cell] = option

        if not is_valid(clone): continue
        solution    = search(clone)
        if solution:
            return solution
    else:
        return False



def solve(grid):
    """Find the solution to a Sudoku puzzle using search and constraint propagation

    Parameters
    ----------
    grid(string)
        a string representing a sudoku grid.

        Ex. '2.............62....1....7...6..8...3...9...7...6..4...4....8....52.............3'

    Returns
    -------
    dict or False
        The dictionary representation of the final sudoku grid or False if no solution exists.
    """
    values = grid2values(grid)
    values = search(values)
    return values


if __name__ == "__main__":
    diag_sudoku_grid = '2.............62....1....7...6..8...3...9...7...6..4...4....8....52.............3'
    display(grid2values(diag_sudoku_grid))
    result = solve(diag_sudoku_grid)
    display(result)

    try:
        import PySudoku
        PySudoku.play(grid2values(diag_sudoku_grid), result, history)

    except SystemExit:
        pass
    except:
        print('We could not visualize your board due to a pygame issue. Not a problem! It is not a requirement.')
