#!/usr/bin/env python3

import random
import numpy as np
from random import randint
from dataclasses import dataclass, field
from typing import List, Optional
from pprint import pprint

from .census import CensusBlock

def _split_population(total: int, num_parts: int) -> List[int]:
    """Randomly splits a total into `num_parts` values that sum to `total`"""

    splits = [randint(0, total) for _ in range(num_parts - 1)]
    splits = [0] + sorted(splits) + [total]
    splits = [splits[i+1] - splits[i] for i in range(num_parts)]

    assert(sum(splits) == total)
    return splits

def _distribute_jerries(num_jerries: int, pops: List[int]) -> List[int]:
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
        if jerries[i] <= pops[i] - 1:
            jerries[i] += 1
            discrepancy -= 1
        i = (i + 1) % num_children

    assert(sum(jerries) == num_jerries)
    return jerries

def _create_adjacency_lists(layer: List[CensusBlock]) -> List[List[CensusBlock]]:
    if len(layer) <= 1:
        return [[]]
    ret = []
    for node in layer:
        possible_neighbors = [n for n in layer if n != node]
        num_neighbors = randint(1, len(possible_neighbors))
        ret.append(random.sample(possible_neighbors, num_neighbors))

    return ret

def _create_tree_leaves(num_leaves: int, total_pop: int, total_jerries: int) -> List[CensusBlock]:
    pops = _split_population(total_pop, num_leaves)
    jerries = _distribute_jerries(total_jerries, pops)

    leaves = []
    for pop, jerry in zip(pops, jerries):
        leaves.append(CensusBlock(population=pop, jerries=jerry))

    for leaf, adj in zip(leaves, _create_adjacency_lists(leaves)):
        leaf.siblings = adj

    return leaves


def _create_tree_layer(num_in_layer: int, leaves: List[CensusBlock]) -> List[CensusBlock]:
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

    # Add adjacency lists _within the layer_ only.
    for parent, adj in zip(new_parents, _create_adjacency_lists(new_parents)):
        parent.siblings = adj
    return new_parents

def create_tree(num_layers: int, fanout: int, total_pop: int, total_jerries: int) -> CensusBlock:
    """Run a mock census, storing the output as a tree of census blocks.

    Arguments:
        - `num_layers`: how many layers should be in the tree?
        - `fanout`: the degree of the tree (number of children per node)
        - `total_pop`: the total population to be distributed among census
          blocks.
        - `total_jerries`: the total number of people that should be
          "positive" for a trait. Our end-to-end system will gerrymander on
          this trait. Examples: `total_positive=4` for 4 total Latinos in the
          census results.
    """

    leaves = _create_tree_leaves(fanout ** num_layers, total_pop, total_jerries)

    layers = [leaves]
    for layer_num in reversed(range(num_layers)):
        nodes_in_layer = fanout ** layer_num
        layer = _create_tree_layer(nodes_in_layer, layers[-1])
        layers.append(layer)

    assert(len(layers[-1]) == 1)
    return layers[-1][0]

if __name__ == '__main__':
    root = create_tree(num_layers=2, fanout=2, total_pop=20, total_jerries=10)
    root.subtree_to_csv()
