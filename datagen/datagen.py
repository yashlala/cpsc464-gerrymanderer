#!/usr/bin/env python3

import numpy as np
import random
from random import randint
from dataclasses import dataclass, field
from typing import List, Optional

id_counter: int = 0

def _assign_id():
    """Every block is assigned a unique ID"""
    global id_counter
    id_counter += 1
    return id_counter

@dataclass
class CensusBlock:
    id: int = field(default_factory=_assign_id)
    population: int = 0
    jerries: int = 0
    children: List['CensusBlock'] = field(default_factory=list)
    siblings: List['CensusBlock'] = field(default_factory=list)


def split_population(total: int, num_parts: int) -> List[int]:
    """Randomly splits a total into `num_parts` values that sum to `total`"""

    splits = [randint(0, total) for _ in range(num_parts - 1)]
    splits = [0] + sorted(splits) + [total]
    return [splits[i+1] - splits[i] for i in range(num_parts)]

def distribute_jerries(num_jerries: int, pops: List[int]) -> List[int]:
    """Distribute jerries among census blocks"""
    num_children = len(pops)

    zipf_weights = np.random.zipf(1.5, num_children)
    zipf_weights = zipf_weights / zipf_weights.sum()

    jerries = []
    for i in range(num_children):
        max_allowed_jerries = min(int(num_jerries * zipf_weights[i]), pops[i] - 1)
        jerries.append(max(0, max_allowed_jerries))

    # Adjust rounding errors.
    discrepancy = num_jerries - sum(jerries)
    i = 0
    while discrepancy > 0:
        if jerries[i] < pops[i] - 1:
            jerries[i] += 1
            discrepancy -= 1
        i = (i + 1) % num_children

    return jerries

def create_tree_leaves(num_leaves: int, total_pop: int, total_jerries: int) -> List[CensusBlock]:
    pops = split_population(total_pop, num_leaves)
    jerries = distribute_jerries(total_jerries, pops)

    leaves = []
    for pop, jerry in zip(pops, jerries):
        leaves.append(CensusBlock(id=_assign_id(), population=pop, jerries=jerry))
    return leaves


def create_tree_layer(num_in_layer: int, leaves: List[CensusBlock]) -> List[CensusBlock]:
    """Equally assign child leaves to parent leaves"""

    children_per_parent = len(leaves) // num_in_layer
    extra_children = len(leaves) % num_in_layer

    # shallow copy -> don't mess up input list
    leaves = list(leaves)

    new_parents = []
    for i in range(num_in_layer):
        num_children = children_per_parent
        if i == 0:
            num_children += extra_children

        children = []
        for _ in range(num_children):
            children.append(leaves.pop())

        parent_pop = sum(child.population for child in children)
        parent_jerries = sum(child.jerries for child in children)
        new_parents.append(CensusBlock(population=parent_pop,
                             jerries=parent_jerries,
                             children=children))

    assert(len(leaves) == 0)

    return new_parents



def create_tree(num_layers: int, total_pop: int, total_jerries: int):
    pass # TODO

def main():
    pass # TODO



if __name__ == '__main__':
    main()
