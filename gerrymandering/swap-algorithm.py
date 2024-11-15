import pandas as pd
import networkx as nx

def load_data(adjacency_file, demographics_file):
    # Load adjacency as a graph
    adj_df = pd.read_csv(adjacency_file)
    G = nx.Graph()
    for _, row in adj_df.iterrows():
        G.add_edge(row['block1'], row['block2'])
    
    # Load demographic data
    demo_df = pd.read_csv(demographics_file)
    demographics = {row['block']: {'population': row['population'], 'democrats': row['democrats']}
                    for _, row in demo_df.iterrows()}
    
    return G, demographics

def initialize_districts(num_districts, target_population):
    districts = {i: {'blocks': set(), 'population': 0, 'democrats': 0} for i in range(num_districts)}
    return districts

def assign_block_to_district(district, block, demographics):
    district['blocks'].add(block)
    district['population'] += demographics[block]['population']
    district['democrats'] += demographics[block]['democrats']

def gerrymander(adjacency_file, demographics_file, num_districts, party):
    # Step 1: Load data
    G, demographics = load_data(adjacency_file, demographics_file)
    
    # Step 2: Calculate target population per district
    total_population = sum(d['population'] for d in demographics.values())
    target_population = total_population // num_districts

    # Step 3: Initialize districts
    districts = initialize_districts(num_districts, target_population)

    # Step 4: Sort blocks by favorability to the target party
    sorted_blocks = sorted(demographics.keys(), key=lambda b: favorability_score(demographics[b], party), reverse=True)

    # Step 5: Assign blocks to districts based on packing/cracking
    for block in sorted_blocks:
        for district_id, district in districts.items():
            if district['population'] < target_population and is_contiguous(district, block, G):
                assign_block_to_district(district, block, demographics)
                break  # move to next block

    # Step 6: Refinement (if needed to balance populations or enforce contiguity)
    refine_districts(districts, G, target_population)

    return [district['blocks'] for district in districts.values()]

def favorability_score(block_demo, party):
    # Calculate favorability score for a block for the given party
    if party == 'D':
        return block_demo['democrats'] / block_demo['population']
    else:
        return (block_demo['population'] - block_demo['democrats']) / block_demo['population']

def is_contiguous(district, block, G):
    # Check if the block is directly adjacent to any block in the district
    for b in district['blocks']:
        if G.has_edge(b, block):
            return True
    return False

def refine_districts(districts, G, target_population):
    # Further tweak districts to improve population balance and favorability.
    pass  # Implementation detail


