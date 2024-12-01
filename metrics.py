import re
from dataclasses import dataclass
from typing import Set, List, Dict, Tuple
from datagen import CensusBlock

def efficiency_gap(tree: CensusBlock, districts: List[Set[int]]) -> Tuple[float, List]:
    leaves = tree.get_leaf_nodes()
    leaves = { leaf.id: leaf for leaf in leaves }

    @dataclass
    class DistrictResult:
        republicans: float = 0
        democrats: float = 0

    results: List[DistrictResult] = []
    for district in districts:
        result = DistrictResult()
        for block_id in district:
            result.democrats += leaves[block_id].jerries
            result.republicans += leaves[block_id].population - leaves[block_id].jerries
        results.append(result)

    # Initialize totals for wasted votes
    total_dem_wasted = 0
    total_rep_wasted = 0
    detailed_results = []

    # Step 1: Calculate wasted votes for each district
    for idx, district in enumerate(results):
        dem_votes = district.democrats
        rep_votes = district.republicans
        total_votes = dem_votes + rep_votes
        winning_threshold = (total_votes / 2) + 1

        if dem_votes > rep_votes:  # Democrats win
            dem_wasted = dem_votes - winning_threshold
            rep_wasted = rep_votes
        else:  # Republicans win
            rep_wasted = rep_votes - winning_threshold
            dem_wasted = dem_votes

        total_dem_wasted += max(0, dem_wasted)  # Ensure no negative wasted votes
        total_rep_wasted += max(0, rep_wasted)

        # Record details for verification
        detailed_results.append({
            "District": idx,
            "Dem Votes": dem_votes,
            "Rep Votes": rep_votes,
            "Dem Wasted": max(0, dem_wasted),
            "Rep Wasted": max(0, rep_wasted),
            "Net Wasted": max(0, dem_wasted) - max(0, rep_wasted)
        })

    # Step 2: Calculate net wasted votes
    net_wasted_votes = total_dem_wasted - total_rep_wasted

    # Step 3: Calculate the efficiency gap
    total_votes_cast = sum(r.democrats + r.republicans for r in results)

    efficiency_gap = net_wasted_votes / total_votes_cast
    return efficiency_gap, detailed_results
