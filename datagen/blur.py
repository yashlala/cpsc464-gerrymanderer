#!/usr/bin/env python3

import numpy as np
import csv
from pathlib import Path
from typing import List
from census import CensusBlock, write_census_tree
from .datagen import create_tree

def _add_laplace_noise(value, epsilon):
    l_noise = value + np.random.laplace(0, 1 / epsilon)
    return l_noise

def blur_tree(root: CensusBlock, epsilon=0.5):
    root.population = round(_add_laplace_noise(root.population, epsilon), 2)
    root.jerries = round(_add_laplace_noise(root.jerries, epsilon), 2)

    for child in root.children:
        blur_tree(child)

    # y: We can't just add laplace noise and provide block data as-is.
    #    Census data needs some basic invariants to make sense
    #    (eg: population > 0). In the real TopDown, these invariants are
    #    encoded as parts of the noisy optimization problem itself (so the
    #    overall solution is guaranteed to be DP while also adhering to these
    #    invariants). Here, we encode some of them manually, potentially losing
    #    DP in the process.

    # population should be at least as large as the children.
    max_child_pop = max((child.population for child in root.children),
                        default=0)
    root.population = max(root.population, max_child_pop)

    max_child_jerries = max((child.jerries for child in root.children),
                            default=0)
    root.jerries = max(root.jerries, max_child_jerries)

    # population >= 0 ;)
    root.population = max(0, root.population)
    root.jerries = max(0, root.jerries)

    # we target a _subset_ of the population
    root.jerries = min(root.jerries, root.population)

if __name__ == '__main__':
    tree = create_tree(num_layers=2, fanout=2, total_pop=400, total_jerries=10)
    write_census_tree(tree,
                      adjacency_outfile=Path('adjacency.csv'),
                      demographic_outfile=Path('demographic.csv'),
                      hierarchy_outfile=Path('hierarchy.csv'))
    blur_tree(tree)
    write_census_tree(tree,
        adjacency_outfile=Path('blurred_adjacency.csv'),
        demographic_outfile=Path('blurred_demographic.csv'),
        hierarchy_outfile=Path('blurred_hierarchy.csv'))
