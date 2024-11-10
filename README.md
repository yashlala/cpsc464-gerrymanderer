# CPSC 464 Group 5: Gerrymandering

## Environment Setup

1. Ensure [Anaconda](https://www.anaconda.com/products/distribution) or [Miniconda](https://docs.conda.io/en/latest/miniconda.html) is installed on your system.
2. Run `conda env create -f environment.yml` to create a new Conda environment
   with all the required dependencies.
3. Activate the environment with `conda activate cpsc464-gerrymandering`. 
4. Run the programs you want. Eg: `python3 datagen/datagen.py`. 

## Data Pipeline

Census data (both pre and post DP) is represented as three CSVs. 

- `adjacency.csv`: represents census block adjacency. Schema:
  `(blockA,blockB)`. 
- `demographic.csv`: represents votes and population of each block. 
  Schema: `(block,population,num_positive)`. 
- `hierarchy.csv`: represents the logical hierarchy of census blocks. 
  Schema: `(Parent Block, Child Block)`. 

## Code Map

- `datagen/`: code that creates synthetic census data. 
  - `census.py`: a helper module that contains useful data structures + CSV
    conversion functions. 
  - `datagen.py`: the main program of the data generator. provides
    `create_tree()` as main entry point. 
