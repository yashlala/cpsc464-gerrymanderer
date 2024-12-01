import pandas as pd
import networkx as nx
from pathlib import Path

def _load_data(adjacency_file, demographics_file, hierarchy_file):
    """Given a census tree as CSV input, returns useful information about the leaf nodes.

    Returns:
        - The adjacency graph of the leaf nodes.
        - A dictionary with demographics of the leaf nodes
    """

    #Load heirarchy as a graph
    hier_df = pd.read_csv(hierarchy_file)
    H = nx.from_pandas_edgelist(hier_df, source='parent_block',
                                target='child_block', create_using=nx.DiGraph())

    leaves = set()
    for node in H.nodes:
        if H.out_degree(node) == 0:
            leaves.add(node)
    
    # Load adjacency as a graph
    adj_df = pd.read_csv(adjacency_file)
    G = nx.Graph()
    for _, row in adj_df.iterrows():
        if(row['blockA'] in leaves and row['blockB'] in leaves):
            G.add_edge(int(row['blockA']), int(row['blockB']))  # Convert to integers
   
    # Load demographic data
    demo_df = pd.read_csv(demographics_file)
    demographics = {
        int(row['block']): {
            'population': float(row['population']), 
            'democrats': float(row['num_positive'])
        }
        for _, row in demo_df.iterrows() if int(row['block'] in leaves)
    }
    
    return G, demographics

def _initialize_districts(num_districts, target_population):
    districts = {i: {'blocks': set(), 'population': 0, 'democrats': 0} for i in range(num_districts)}
    return districts

def _assign_block_to_district(district, block, demographics):
    district['blocks'].add(block)
    district['population'] += demographics[block]['population']
    district['democrats'] += demographics[block]['democrats']

def gerrymander(adjacency_file, demographics_file, hierarchy_file, num_districts, party):
    """Create a set of legislative districts designed to favor a party.

    Arguments:
        - adjacency_file: path to a CSV of district adjacency data.
          see README.
        - num_districts: the number of districts to produce in the output.
        - party: the party to gerrymander _for_.
    Returns:
        - A list of districts. Each district is a set of block IDs.
    """
    # Step 1: Load data
    G, demographics = _load_data(adjacency_file, demographics_file, hierarchy_file)

    # Step 2: Calculate target population per district
    total_population = sum(d['population'] for d in demographics.values())
    target_population = total_population / num_districts

    # Step 3: Initialize districts
    districts = _initialize_districts(num_districts, target_population)

    # Step 4: Sort blocks by favorability to the target party
    sorted_blocks = sorted(demographics.keys(),
                           key=lambda b: _favorability_score(demographics[b], party),
                           reverse=True)

    # Step 5: Assign blocks to districts based on packing/cracking strategy
    for block in sorted_blocks:
        assigned = False
        for district in districts.values():
            # Ensure the block does not exceed target population
            if district['population'] + demographics[block]['population'] <= target_population:
                if _is_contiguous(district, block, G) or district['population'] == 0:
                    _assign_block_to_district(district, block, demographics)
                    assigned = True
                    break
        if not assigned:
            print(f"Block {block} could not be assigned due to population/contiguity constraints.")

    # Step 6: Refinement to balance populations across districts
    # refine_districts(districts, G, target_population, demographics)

    return [district['blocks'] for district in districts.values()]

def _favorability_score(block_demo, party):
    # Calculate favorability score for a block for the given party
    if party == 'D':
        return block_demo['democrats'] / block_demo['population']
    else:
        if block_demo['population'] == 0:
            return 0
        return (block_demo['population'] - block_demo['democrats']) / block_demo['population']

def _is_contiguous(district, block, G):
    # Check if the block is directly adjacent to any block in the district
    for b in district['blocks']:
        if G.has_edge(b, block):
            return True
    return False

def _refine_districts(districts, G, target_population, demographics):
    for district in districts.values():
        while district['population'] > target_population:
            # Find a block to move out
            for block in list(district['blocks']):
                # Temporarily remove the block
                district['blocks'].remove(block)
                district['population'] -= demographics[block]['population']
                district['democrats'] -= demographics[block]['democrats']

                if not _is_contiguous(district, block, G):
                    # Revert if contiguity is broken
                    district['blocks'].add(block)
                    district['population'] += demographics[block]['population']
                    district['democrats'] += demographics[block]['democrats']
                    continue

                # Move block to underpopulated district
                for other_district in districts.values():
                    if other_district['population'] + demographics[block]['population'] <= target_population:
                        _assign_block_to_district(other_district, block, demographics)
                        break
                break
    
    # print(f"Refining Districts...")
    # for district_id, district in enumerate(districts.values()):
    #     print(f"Before Refinement - District {district_id}: Population: {district['population']}, Blocks: {district['blocks']}")
    _refine_districts(districts, G, target_population, demographics)
    # for district_id, district in enumerate(districts.values()):
    #     print(f"After Refinement - District {district_id}: Population: {district['population']}, Blocks: {district['blocks']}")

if __name__ == "__main__":
    # Input file paths
    adjacency_file = "blurred_adjacency_debug-epsilon1.csv"
    demographics_file = "blurred_demographic_debug-epsilon1.csv"
    hierarchy_file = "blurred_hierarchy_debug-epsilon1.csv"

    # Number of districts and party to favor
    num_districts = 7
    party = 'R'  # 'R' for Republicans, 'D' for Democrats

    # Run the debugging version of the gerrymander algorithm
    results = gerrymander(adjacency_file, demographics_file, hierarchy_file, num_districts, party)

    # Load demographics to calculate statistics
    _, demographics = _load_data(adjacency_file, demographics_file, hierarchy_file)

    # Print results for each district
    print("\nGerrymandering Results:")
    for district_id, blocks in enumerate(results):
        total_population = sum(demographics[block]['population'] for block in blocks)
        total_democrats = sum(demographics[block]['democrats'] for block in blocks)
        total_republicans = total_population - total_democrats

        print(f"\nDistrict {district_id}:")
        print(f"  Total Population: {total_population}")
        print(f"  Democrats: {total_democrats}")
        print(f"  Republicans: {total_republicans}")
        print(f"  Blocks: {sorted(blocks)}")
