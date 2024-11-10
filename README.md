# CPSC 464 Group 5: Gerrymandering


## Data Pipeline

Census data (both pre and post DP) is represented as three CSVs. 


- `adjacency.csv`: represents census block adjacency. Schema:
  `(blockA,blockB)`. 
- `demographic.csv`: represents votes and population of each block. 
  Schema: `(block,population,num_positive)`. 
- `hierarchy.csv`: represents the logical hierarchy of census blocks. 
  Schema: `(Parent Block, Child Block)`. 
