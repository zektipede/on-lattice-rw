#31/03/2024 Max Galettis
#100by100by100 with 100n was ran 100 times
#100 neurons on a million nopde sim has a density of 0.0001,
#btw, fly brain on google: 590 µm × 340 µm × 120 µm

import os
import matplotlib.pyplot as plt
from collections import Counter


###lattice type###
l=200 #side length of lattice boundary
lattice = 'tetrahedron' #type of lattice
# l=100 #side length of lattice boundary
# lattice = 'cube' #type of lattice
# l=159 #side length of lattice boundary
# lattice = 'octahedron' #type of lattice
###sim information###
num_neurons_in_sim=100
Number_of_runs = 10

folder_path = r'Alternative_computation_results'
file_path_branched = os.path.join(folder_path, f'alt_lengths_branched_cables_{Number_of_runs}r_{lattice}_{l}by{l}by{l}_{num_neurons_in_sim}n.txt')
file_path_terminated = os.path.join(folder_path, f'alt_lengths_terminated_cables_{Number_of_runs}r_{lattice}_{l}by{l}by{l}_{num_neurons_in_sim}n.txt')



# Read data from the text file
with open(file_path_branched, 'r') as file:
    # Read lines from the file and convert them to integers
    lengths_b_cables = [int(line.strip()) for line in file.readlines()]
with open(file_path_terminated, 'r') as file:
    # Read lines from the file and convert them to integers
    lengths_t_cables = [int(line.strip()) for line in file.readlines()]



# Count the frequency of unique cable lengths
length_counts_b = Counter(lengths_b_cables)
length_counts_t = Counter(lengths_t_cables)

unique_lengths_b, counts_b = zip(*length_counts_b.items())
unique_lengths_t, counts_t = zip(*length_counts_t.items())
combined_unique_lengths = sorted(set(unique_lengths_b) | set(unique_lengths_t))
sum_counts = [length_counts_b[length] + length_counts_t[length] for length in combined_unique_lengths]

# Normalize counts by the total number of simulations 
counts_b_norm = [count / Number_of_runs for count in counts_b]
counts_t_norm = [count / Number_of_runs  for count in counts_t]
sum_counts_norm = [count / Number_of_runs  for count in sum_counts]

num_cables_that_branch = len(lengths_b_cables)
num_cables_that_terminate = len(lengths_t_cables)
print('branch:',num_cables_that_branch, 'terminate:', num_cables_that_terminate)
#divide by len(lengths_b_cables) (the number of cables that branch, vs number that terminate) to get the percentage frequencies
counts_b_perc = [count / num_cables_that_branch for count in counts_b]
counts_t_perc = [count / num_cables_that_terminate  for count in counts_t]
sum_counts_perc = [count / (num_cables_that_branch + num_cables_that_terminate)  for count in sum_counts]


#######normalised to number of sims#######
# Create a bar graph, normalised to the number of simulations
# Plot the sum
plt.bar(combined_unique_lengths, sum_counts_norm, color='purple', alpha=1, label='Sum')
# Plot the terminating and branching cables length frequency/counts
plt.bar(unique_lengths_b, counts_b_norm, color='blue', alpha=1, label='Branched Cables')
plt.bar(unique_lengths_t, counts_t_norm, color='red', alpha=1, label='Terminated Cables')
plt.plot( combined_unique_lengths,[(i)**(-2/3) for i in combined_unique_lengths], color='black', linestyle='--', label='y=x^(-2/3)')

# Set y-axis to logarithmic scale for better visualization
plt.yscale('log')
plt.xscale('log') #this is why we plot -2/3 since this allows us to check gradient
# plt.ylim(0,)

# Add title and labels
plt.title('Bar Graph of Lengths Frequency')
plt.xlabel('Branch lengths')
plt.ylabel('Frequency normalised by the number of brains(sims)')
plt.legend()

# Show the bar graph
plt.show()






#######normalised to number of sims, no xlog#######
# Create a bar graph, normalised to the number of simulations
# Plot the sum
plt.bar(combined_unique_lengths, sum_counts_norm, color='purple', alpha=1, label='Sum')
# Plot the terminating and branching cables length frequency/counts
plt.bar(unique_lengths_b, counts_b_norm, color='blue', alpha=1, label='Branched Cables')
plt.bar(unique_lengths_t, counts_t_norm, color='red', alpha=1, label='Terminated Cables')
plt.plot( combined_unique_lengths,[(i)**(-2/3) for i in combined_unique_lengths], color='black', linestyle='--', label='y=x^(-2/3)')

# Set y-axis to logarithmic scale for better visualization
plt.yscale('log')
# plt.ylim(0,)

# Add title and labels
plt.title('Bar Graph of Lengths Frequency')
plt.xlabel('Branch lengths')
plt.ylabel('Frequency normalised by the number of brains(sims)')
plt.legend()

# Show the bar graph
plt.show()






#######normalised to number of cables#######
# Create a bar graph for percents (normalised to the number of cables)
plt.bar(combined_unique_lengths, sum_counts_perc, color='purple', alpha=1, label='Sum')
# Plot the terminating and branching cables length frequency/counts
plt.bar(unique_lengths_b, counts_b_perc, color='blue', alpha=1, label='Branched Cables')
plt.bar(unique_lengths_t, counts_t_perc, color='red', alpha=1, label='Terminated Cables')

#plt.plot( combined_unique_lengths,[i**(-2/3) for i in combined_unique_lengths], color='black', linestyle='--', label='y=x^(-2/3)')

# Set y-axis to logarithmic scale for better visualization
# plt.yscale('log')
# plt.ylim(0,) 

# Add title and labels
plt.title('Bar Graph of Lengths Frequency')
plt.xlabel('Branch lengths')
plt.ylabel('Frequency %')
plt.legend()

# Show the bar graph
plt.show()