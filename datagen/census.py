from dataclasses import dataclass, field
from typing import List
import csv
from pathlib import Path

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


def _write_adjacency_csv(blocks: List[CensusBlock], filename):
    with open(filename, mode="w", newline="") as file:
        writer = csv.writer(file)
        writer.writerow(["blockA", "blockB"])
        
        for block in blocks:
            for sibling in block.siblings:
                writer.writerow([block.id, sibling.id])

def _write_demographic_csv(blocks: List[CensusBlock], filename):
    with open(filename, mode="w", newline="") as file:
        writer = csv.writer(file)
        writer.writerow(["block", "population", "num_positive"])

        for block in blocks:
            writer.writerow([block.id, block.population, block.jerries])

def _write_hierarchy_csv(blocks: List[CensusBlock], filename):
    with open(filename, mode="w", newline="") as file:
        writer = csv.writer(file)
        writer.writerow(["parent_block", "child_block"])

        def write_hierarchy(block):
            for child in block.children:
                writer.writerow([block.id, child.id])
                write_hierarchy(child)

        for block in blocks:
            write_hierarchy(block)

def _gather_all_blocks(root: CensusBlock) -> List[CensusBlock]:
    all_blocks = []

    def traverse(block):
        all_blocks.append(block)
        for child in block.children:
            traverse(child)

    traverse(root)
    return all_blocks



def write_census_tree(root: CensusBlock,
                      adjacency_outfile: Path = Path('adjacency.csv'),
                      demographic_outfile: Path = Path('demographic.csv'),
                      hierarchy_outfile: Path = Path('hierarchy.csv')):
    flat_tree = _gather_all_blocks(root)
    _write_adjacency_csv(flat_tree, adjacency_outfile)
    _write_demographic_csv(flat_tree, demographic_outfile)
    _write_hierarchy_csv(flat_tree, hierarchy_outfile)
