"""Run pipeline/train_cell_weights.py for every 5 x 5 degree cell on the global grid.

Cell centres: lat -87.5..87.5, lon -177.5..177.5 (2,592 cells). Cells outside DMSP-OLS
coverage or without any 2012 night lights fail inside the training script and produce no
weight file; 1,011 cells (60S-70N) completed and are deposited on Zenodo.
Existing weight files are skipped, so the run can be resumed.
"""
import numpy as np
from tqdm import tqdm
import os
import concurrent.futures

# Define your lat/lon ranges
lons = np.arange(-177.5, 180, 5)
lats = np.arange(-87.5, 90, 5)


# Total iterations based on lat/lon grid
total_iterations = len(lats) * len(lons)
buffer = 2.5

# Define a function to run the command for a given lat/lon
def run_command(lat, lon):
    lats_, late_ = float(lat) - buffer, float(lat) + buffer
    lons_, lone_ = float(lon) - buffer, float(lon) + buffer
    model_save_path = "best_model_lats_" + str(lats_) + "_late_" + str(late_) + "_lons_" + str(lons_) + "_lone_" + str(lone_) + ".pth"

    # Example system command
    command = "python pipeline/train_cell_weights.py " + str(lat) + " " + str(lon)

    # Skip if the model already exists
    if os.path.exists(model_save_path):
        return

    # Run the command
    os.system(command)

# Use ThreadPoolExecutor to run 10 jobs in parallel
with concurrent.futures.ThreadPoolExecutor(max_workers=10) as executor:
    futures = []
    with tqdm(total=total_iterations, desc="Processing lat/lon pairs") as pbar:
        for lat in lats:
            for lon in lons:
                # Submit each command to the executor for concurrent execution
                futures.append(executor.submit(run_command, lat, lon))

                # Update progress bar after every job is submitted
                pbar.update(1)

    # Ensure all futures are completed
    concurrent.futures.wait(futures)

