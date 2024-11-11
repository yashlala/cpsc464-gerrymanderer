import numpy as np
import csv
from pathlib import Path
from typing import List
from census import CensusBlock, write_census_tree
from datagen import create_tree

EPSILON = 0.5

def add_laplace_noise(value, epsilon):
    scale = 1 / epsilon
    l_noise = value + np.random.laplace(0, scale)
    return l_noise

def apply_blurring(blocks: List[CensusBlock], epsilon=EPSILON):
    for block in blocks:
        block.population = max(0, round(add_laplace_noise(block.population, epsilon), 2))
        block.jerries = max(0, round(add_laplace_noise(block.jerries, epsilon), 2))

def save_to_csv(blocks: List[CensusBlock], adj_file, demo_file, hier_file):
    with open(adj_file, mode="w", newline="") as file:
        writer = csv.writer(file)
        writer.writerow(["blockA", "blockB"])
        for block in blocks:
            for sibling in block.siblings:
                writer.writerow([block.id, sibling.id])

    with open(demo_file, mode="w", newline="") as file:
        writer = csv.writer(file)
        writer.writerow(["block", "population", "num_positive"])
        for block in blocks:
            writer.writerow([block.id, block.population, block.jerries])

    with open(hier_file, mode="w", newline="") as file:
        writer = csv.writer(file)
        writer.writerow(["parent_block", "child_block"])
        
        def write_hierarchy(block):
            for child in block.children:
                writer.writerow([block.id, child.id])
                write_hierarchy(child)

        for block in blocks:
            write_hierarchy(block)

def blur_and_save_census_data(root_block, epsilon=EPSILON):
    def collect_blocks(block):
        all_blocks.append(block)
        for child in block.children:
            collect_blocks(child)

    all_blocks = []
    collect_blocks(root_block)

    apply_blurring(all_blocks, epsilon)

    save_to_csv(
        all_blocks, 
        adj_file=Path('blurred_adjacency.csv'),
        demo_file=Path('blurred_demographic.csv'),
        hier_file=Path('blurred_hierarchy.csv')
    )

if __name__ == '__main__':
    treeStruct = create_tree(num_layers=2, fanout=2, total_pop=20, total_jerries=10)
    write_census_tree(treeStruct)
    blur_and_save_census_data(treeStruct)

#this was created with both human code and generated content and is still a work in progress
