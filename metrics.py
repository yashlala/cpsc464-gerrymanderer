# Function to calculate the efficiency gap
def calculate_efficiency_gap_verified(file_path):
    import re

    # Helper function to extract data from a single district
    def extract_district_data(lines):
        data = {"Democrats": 0, "Republicans": 0}
        for line in lines:
            if "Democrats:" in line:
                data["Democrats"] = float(re.search(r"Democrats:\s*([\d.]+)", line).group(1))
            elif "Republicans:" in line:
                data["Republicans"] = float(re.search(r"Republicans:\s*([\d.]+)", line).group(1))
        return data

    # Parse districts from the file
    districts = []
    with open(file_path, 'r') as f:
        lines = f.readlines()

    current_district = []
    for line in lines:
        if line.startswith("District"):
            if current_district:  # Save previous district's data
                districts.append(extract_district_data(current_district))
                current_district = []
        current_district.append(line)
    if current_district:  # Save the final district's data
        districts.append(extract_district_data(current_district))

    # Initialize totals for wasted votes
    total_dem_wasted = 0
    total_rep_wasted = 0
    detailed_results = []

    # Step 1: Calculate wasted votes for each district
    for idx, district in enumerate(districts):
        dem_votes = district["Democrats"]
        rep_votes = district["Republicans"]
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
    total_votes_cast = sum(d["Democrats"] + d["Republicans"] for d in districts)
    efficiency_gap = net_wasted_votes / total_votes_cast

    return efficiency_gap, detailed_results
