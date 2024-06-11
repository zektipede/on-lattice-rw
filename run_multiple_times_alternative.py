# run_multiple_times.py

import subprocess
import time

def run_script_n_times(script_path, n):
    #starting from the 1st run:
    for i in range(1, n + 1): #if starting something new, start from 1, this is to prevent bad headings (cant have 0 at the start of some headings)
        subprocess.run(['python', script_path, str(i)])

if __name__ == "__main__":
    script_path = 'non_intersect_branch_alternative_growth_rule.py'
    N = 10  # Change this to the desired number of times you want to run the script
    
    run_script_n_times(script_path, N)