# run_multiple_times.py Max Galettis

import subprocess
import time

def run_script_n_times(script_path, n):
    #starting from the 4th run: (3 have already been performed)
    for i in range(4, n + 1): #if starting something new, start from 1, this is to prevent bad headings (cant have 0 at the start of some headings)
        subprocess.run(['python', script_path, str(i)])

if __name__ == "__main__":
    script_path = 'intersect_branch_to_optimise_wk8.py'
    #
    N = 100  # Change this to the desired number of times you want to run the script in total
    #can make this very big, want to be able to get plots of average neuron length etc first...
    
    run_script_n_times(script_path, N)