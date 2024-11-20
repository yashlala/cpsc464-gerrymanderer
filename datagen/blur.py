import numpy as np
import csv
from pathlib import Path
from typing import List
from census import CensusBlock, write_census_tree
from datagen import create_tree

EPSILON = 0.5

def _add_laplace_noise(value, epsilon):
    scale = 1 / epsilon
    l_noise = value + np.random.laplace(0, scale)
    return l_noise

def _blur_block(blocks: List[CensusBlock], epsilon=EPSILON):
    for block in blocks:
        block.population = max(0, round(_add_laplace_noise(block.population, epsilon), 2))
        block.jerries = max(0, round(_add_laplace_noise(block.jerries, epsilon), 2))

def blur_tree(root_block, epsilon=EPSILON):
    all_blocks = []
    def collect_blocks(block):
        all_blocks.append(block)
        for child in block.children:
            collect_blocks(child)
    collect_blocks(root_block)

    _blur_block(all_blocks, epsilon)

if __name__ == '__main__':
    treeStruct = create_tree(num_layers=2, fanout=2, total_pop=20, total_jerries=10)
    write_census_tree(treeStruct,
                      adjacency_outfile=Path('adjacency.csv'),
                      demographic_outfile=Path('demographic.csv'),
                      hierarchy_outfile=Path('hierarchy.csv'))

    blur_tree(treeStruct)
    write_census_tree(treeStruct,
        adjacency_outfile=Path('blurred_adjacency.csv'),
        demographic_outfile=Path('blurred_demographic.csv'),
        hierarchy_outfile=Path('blurred_hierarchy.csv'))
