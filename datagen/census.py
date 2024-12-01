from dataclasses import dataclass, field
from typing import List
import csv
from pathlib import Path

id_counter: int = 0

def _assign_id() -> int:
    """Every block is assigned a unique ID"""
    global id_counter
    id_counter += 1
    return id_counter

class CensusBlock:
    def __init__(self, id=None, population=0, jerries=0, children=None, siblings=None):
        self.id: int = id if id is not None else _assign_id()
        self.population = population
        self.jerries = jerries
        self.children: List['CensusBlock'] = children if children is not None else []
        self.siblings: List['CensusBlock'] = siblings if siblings is not None else []

    def subtree_to_csv(self,
                       adjacency_outfile: Path = Path('adjacency.csv'),
                       demographic_outfile: Path = Path('demographic.csv'),
                       hierarchy_outfile: Path = Path('hierarchy.csv')):
        """Writes the tree rooted on this node to a set of CSV files"""

        flat_tree = _gather_all_blocks(self)
        _write_adjacency_csv(flat_tree, adjacency_outfile)
        _write_demographic_csv(flat_tree, demographic_outfile)
        _write_hierarchy_csv(flat_tree, hierarchy_outfile)

    def node_to_string(self):
        """Generate a string representation of this CensusBlock (no children)"""
        return f"Blk(id={self.id}, pop={self.population}, jerries={self.jerries})"

    def _subtree_to_string_list(self):
        ret = [f"Blk(id={self.id}, pop={self.population}, jerries={self.jerries})"]
        for child in self.children:
            ret.extend(child._subtree_to_string_list())
        return ret

    def subtree_to_string(self):
        """Generate a string representation of the tree rooted at this CensusBlock."""
        return "\n".join(self._subtree_to_string_list())

    def get_leaf_nodes(self):
        """Return a list with all the leaf nodes"""
        if len(self.children) == 0:
            return [self]

        # y: I can't shake the feeling there's a way more elegant way to do this...
        ret = []
        for child in self.children:
            ret.extend(child.get_leaf_nodes())
        return ret


    def __str__(self) -> str:
        return self.subtree_to_string()

def _write_adjacency_csv(blocks: List[CensusBlock], filename):
    with open(filename, mode="w", newline="") as file:
        file.seek(0)
        file.truncate(0)

        writer = csv.writer(file)
        writer.writerow(["blockA", "blockB"])
        
        for block in blocks:
            for sibling in block.siblings:
                writer.writerow([block.id, sibling.id])

def _write_demographic_csv(blocks: List[CensusBlock], filename):
    with open(filename, mode="w", newline="") as file:
        file.seek(0)
        file.truncate(0)

        writer = csv.writer(file)
        writer.writerow(["block", "population", "num_positive"])
        for block in blocks:
            writer.writerow([block.id, block.population, block.jerries])

def _write_hierarchy_csv(blocks: List[CensusBlock], filename):
    with open(filename, mode="w", newline="") as file:
        file.seek(0)
        file.truncate(0)
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
