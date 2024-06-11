#! /bin/usr/env python3

#31/03/2024 Max Galettis

#lacking: counter for unocupied nodes
#the alternative growth rule, is:
#1. don't self interect, 
#2. if you tried to grow into an occupied neighbour, go elsewhere (unocupied node)
#3. if you had to go else where after attempting to enter a non-self neuron occupied point
#       record that point as a branch point
#4. if you are a branch point, grow as described above, twice
#Notes: in growing the second time, the attempted point is removed, should it?






#####################################
### some nomenclature notes:      ###
#####################################
##
# -Everything is a point, not a node.
# -Points are only ever spatial.
##
# -The lattice is called a box at all times since it
# behaves more like a box that we put stuff in than a lattice
##
#####################################
#optimisations yet to implement
#migrate to c++ and fix the memory allocation of the dictionaries and stuff
#convert tuples to integers via formula x + (max(x)+1)*y +...
#so for a tuple (x,y,z) you get:  x + X*y + X*Y*z 
#then use modulo to work back...
#####################################




#import numpy as np
import matplotlib.pyplot as plt
from mpl_toolkits.mplot3d import Axes3D
import time
import statistics #use for getting mean std dev etc from cables_lengths
from collections import Counter #use for creating a bar graph

######'essential' imports#####
import sys          #command line control
import os           #file paths
import pickle       #the .lat file
import csv          #output
import random       #gotta have random
from Tree_Node import TreeNode 
from Neuron import Neuron 



##############################Global variables###############################
# Dimensions of your "box", 
# 1mil for _  lattice is:
#     tetrahedron       : 200by200by200
#        cube           : 100by100by100 
#     octahedron        : 159by159by159
# #aproximatly 158/159 for octahedral lattice to get 1 million nodes.  (unit cell has 2 nodes, our unit cells are 2x2x2, so divide 8...
# gives 1/4 nodes per unit m^3 cell in normal counting system, and the cube root of 4 is 1.5874...)
############ S = {(1,1,0), (0,1,1), (1,0,1), (1,1,1)} union S_c works aswell (intersections only occur at ), however it isnt as nice since the sum of all directions in S doesnt add to 0, and this should be another requirement for niceness, if you add the negative diagonals you may get intersections of edges without meeting at a vertex
############ write that the niceness conditions are determined by user the simulation... (user choice...?)
############ though the above S can work if like the tetrahedron, you add a type of node, however this still unevenly distributes movement

########################################################
### To make any change to the simulations, these are ###
############# THE ONLY VARIABLES TO CHANGE #############
########################################################
X = 159 # 200, 100, 159
Y = 159
Z = 159 
lattice_type ='octahedron' #'tetrahedron', 'cube', 'octahedron'
time_steps = 10000
num_neurons_in_sim = 100
total_runs = 10 #number of runs of the code there will be dictated by another script
#############################################################################


#up to standards, independent of sim
def pick_random_colour(alpha=0.8):
    # Generate random values for RGB
    red = random.random()
    green = random.random()
    blue = random.random()

    # Return the random RGBA color
    return (red, green, blue, alpha)
#up to standards, independent of sim
def read_csv(file_path):
    data = []
    try:
        with open(file_path, 'r') as file:
            reader = csv.reader(file)
            data = list(reader)
    except FileNotFoundError:
        pass  # File doesn't exist yet

    return data
#up to standards, independent of sim
def write_csv(file_path, data):
    with open(file_path, 'w', newline='') as file:
        writer = csv.writer(file)
        writer.writerows(data)
#up to standards, independent of sim
def update_and_save_csv(file_path, new_data):
    existing_data = read_csv(file_path)

    # Update existing data or add new data
    # For example, appending new rows
    existing_data.extend(new_data)

    # Save the updated data
    write_csv(file_path, existing_data)


#not to standard re:naming conventions
#goes to folder ... variation_of_num_neurons
def export_n_branch_sim(new_data):
    # Example usage:
    #csv_file_path = 'data.csv'
    #new_data = [('John', 25), ('Alice', 30)]
    #update_and_save_csv(csv_file_path, new_data)
    folder_name = 'variation_of_num_neurons'
    file_name = f'data_{X}by{Y}by{Z}_{num_neurons_in_sim}.csv'
    csv_file_path = os.path.join(folder_name, file_name)
    update_and_save_csv(csv_file_path, new_data)


#not to standard
#goes to folder .... very specific
def export(neurons, run_name, box):
    folder_name = 'complete_neuron_point_runs_10000t_100n'
    #file_name = f'neuron_point_data_{X}by{Y}by{Z}_{num_neurons_in_sim}.csv'
    file_name = f'neuron_point_data_run{run_name}_{X}by{Y}by{Z}_{num_neurons_in_sim}.csv' #remove run name from the export, can add titles to the csv
    #file_name = #please choose appropriate export method(per box, or per box constraints)
    csv_file_path = os.path.join(folder_name, file_name)

    
    ##could incorparate into other methods to speed it up but doing it in isolation is clear satisfying
    #print(f'number_of_neurons: {len(neurons)}, Box dimensions X:{X}, Y:{Y}, Z:{Z}, Timesteps: {time_steps}')
    #print('other notes: ...')
    #print()
    ##the next line can be added to the csv but only if done on a per_neuron_basis as this means it can be included as the heading
    #print('run_name, neuron_name(arbitrary number), neuron_id, x,y,z, parent_x, parent_y, parent_z, time_added_to_neuron, is_root, is_childless, is_branch, is_intersection')

    arbitrary_neuron_name = 0
    all_points_data = [('run_name', 'neuron_name(arbitrary number)', 'neuron_id', 'x','y','z', 'parent_x', 'parent_y', 'parent_z', 'time_added_to_neuron', 'is_root', 'is_childless', 'is_branch', 'is_intersection')]
    for neuron in neurons:
        arbitrary_neuron_name += 1 #must be non zero for some pandas analysis

        #terminating_points = neuron.branch_nodes_points.union(neuron.child_nodes_points)
        interesection_points_with_all_other_neurons = neuron.nodes_points & set().union(*(neuron2.nodes_points for neuron2 in neurons if neuron2 != neuron))
        
        neuron_id = neuron.neuron_id
        for point in neuron.nodes_points:
            x, y, z = point
            parent_x, parent_y, parent_z = box[point].neurons[neuron_id][0]
            time_added_to_neuron = box[point].neurons[neuron_id][1]
            #0 is false, 1 is true
            is_root = 1 if point == neuron.root else 0
            is_childless = 1 if point in neuron.child_nodes_points else 0
            is_branch = 1 if point in neuron.branch_nodes_points else 0
            is_intersection = 1 if point in interesection_points_with_all_other_neurons else 0
            one_points_data = (run_name, arbitrary_neuron_name, x, y, z, parent_x, parent_y, parent_z, time_added_to_neuron, is_root, is_childless, is_branch, is_intersection)
            all_points_data.append(one_points_data) #note, one_points_data is a tuple, this is important to get each point as a seperate row
    update_and_save_csv(csv_file_path, all_points_data)
        # run_name, neuron_name(arbitrary number), x,y,z, parent_x, parent_y, parent_z, time_added_to_neuron, is_root, is_childless, is_branch, is_intersection,
#not to standard
def plot(neurons, box): #####pass the list of neurons to this method so that iterating through them allows for the counting of branches, lengths (you can avoid the need for neuron.get_cables())
    # Create a figure and a 3D subplot
    fig = plt.figure()
    ax = fig.add_subplot(111, projection='3d')

    #going from 
    for neuron in neurons:
        colour = pick_random_colour()
        #this is a repeat of the get_cables method
        terminating_points = neuron.branch_nodes_points.union(neuron.child_nodes_points)
        neuron_id = neuron.neuron_id
        for point in terminating_points:
            end_point = point
            start_point = box[end_point].neurons[neuron_id][0] #0 is the (x, y, z) of the parent
            while start_point not in terminating_points and start_point != neuron.root:
                ax.plot(*zip(start_point, end_point), color=colour)
                end_point = start_point
                start_point = box[end_point].neurons[neuron_id][0] #0 is the (x, y, z) of the parent
            ax.plot(*zip(start_point, end_point), color=colour)
        for point in neuron.intersection_nodes: #not currently calculated
            ax.scatter(*point, c='g', s=10, marker='o') #c='b' sets the marker to blue, s=5 sets the marker sizes to 5
        ax.scatter(*neuron.root, c='r', s=20, marker='o')
    # Set labels for the axes
    ax.set_xlabel('X')
    ax.set_ylabel('Y')
    ax.set_zlabel('Z')

    # Show the 3D plot
    plt.show()


#up to initial week 7 standards, 27/03/2024
def generate_starting_positions(number_of_neurons_to_initialise, box):
    point_list = list(box)
    starting_points = set() #using sets ensures no duplicates
    while len(starting_points) < number_of_neurons_to_initialise:
        starting_points.add(random.choice(point_list))
    return starting_points


#up to initial week 7 standards, 27032024 until:
##############################################
### Export calculations that I plan to do ###
# to avoid recomputing these things later ###
#############################################
#UNTIL ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
def main():
    #######################################
    ### run style and loading/importing ###
    #######################################

    #run from a script
    if len(sys.argv) != 2:
        print("Usage: python myscript.py <count>")
        sys.exit(1)
    run_name = int(sys.argv[1])

    ### method for loading the lattice of interconnected custom classes ###
    file_name = f'{lattice_type}_{X}by{Y}by{Z}.lat'
    folder='lattices' #'' is current directory
    file_path = os.path.join(folder, file_name)

    box = None # {(0,0,0) : TreeNode((0,0,0),{(0,0,1),(0,1,0),(1,0,0)}),...} for cubic lattice
    with open(file_path, 'rb') as f:
        box = pickle.load(f)
    #except: sys.exit(1)

    #######################################
    ### actual generation methods below ###
    #######################################
    #sym variable initialisation
    code_time = 0 #time tracking
    total_branch_points = 0 #tracking the total number of branch points, for a per neuron basis, use len(neuron.branch_nodes_points)
    starting_points = generate_starting_positions(number_of_neurons_to_initialise=num_neurons_in_sim, box=box) 
    neurons = [ Neuron(box, starting_point, local_time=code_time) for starting_point in starting_points ]


    #######################################
    ### grow the neurons in the lattice ###
    #######################################
    while code_time < time_steps:
        #method for chosing which direction to go
        for neuron in neurons:
            #track branch points or synapses? synapses are at the taking of alternative direciotn, branch points are the point after
            for point in neuron.fresh_points:
                #not_neuron_id replaces_neighbours available_neighbours, 
                #this removes the restriction on the max number of neuron_ids per point
                attempt_directions = box[point].not_neuron_id_neighbours(box, neuron.neuron_id)
                unoccupied_directions = box[point].unoccupied_neighbours(box, neuron.neuron_id) #passing the neuron_id is unecessary but I havent got arround to modifying it
                if unoccupied_directions: #empty lists automatically evaluate false
                    attempt_direction = random.choice(attempt_directions)
                    ######doing the following line is debatable################
                    attempt_directions.remove(attempt_direction) ####################################doing this is debatable
                    if attempt_direction in unoccupied_directions: #can grow in the attempted direction
                        unoccupied_directions.remove(attempt_direction)
                        
                        box[attempt_direction].assign_to_neuron(neuron, parent_point=point, local_time=code_time) #assign the next point with this point as parent 
                        
                        box[point].assign_child_for(neuron.neuron_id)
                    else: #grow to an unoccupied point and branch at the next time step(on the next iteration of the while loop)
                        branch_direction = random.choice(unoccupied_directions) #generate the next point from unocupied directions
                        unoccupied_directions.remove(branch_direction)

                        box[branch_direction].assign_to_neuron(neuron, parent_point=point, local_time=code_time) #assign the next point with this point as parent 
                        box[branch_direction].assign_branch_for(neuron.neuron_id)
                        neuron.record_branch_point(branch_direction)

                        box[point].assign_child_for(neuron.neuron_id)
                    #maybe after growing we should update the branching status of every other nearby point
                if point in neuron.branch_points and unoccupied_directions:#grow again if there is somewhere to grow to
                    #identical copy of above, just without any removals
                    attempt_direction = random.choice(attempt_directions)
                    if attempt_direction in unoccupied_directions: #can grow in the attempted direction                        
                        box[attempt_direction].assign_to_neuron(neuron, parent_point=point, local_time=code_time) #assign the next point with this point as parent 
                        
                        box[point].assign_child_for(neuron.neuron_id)
                    else: #grow to an unoccupied point and branch at the next time step(on the next iteration of the while loop)
                        branch_direction = random.choice(unoccupied_directions) #generate the next point from unocupied directions

                        box[branch_direction].assign_to_neuron(neuron, parent_point=point, local_time=code_time) #assign the next point with this point as parent 
                        box[branch_direction].assign_branch_for(neuron.neuron_id)
                        neuron.record_branch_point(branch_direction)

                        box[point].assign_child_for(neuron.neuron_id)
            #reminder that order of neurons in the neuron list must be randomised to remove bias here over many simulations...
            neuron.migrate_fresh_points(box)
            neuron.migrate_future_points()
        code_time+=1
        #if code_time % 10 == 0: print('time:', code_time)
    #print('halfway')
    






    ##########################################################
    ### complete the non-specific information about neurons###
    ##########################################################

    #complete the current data
    for neuron in neurons:
        neuron.migrate_fresh_points(box) #freshnodes cannot be used for calculating the number of branches due to terminating nodes being covered up
        neuron.get_points_with_no_children(box) #typically executres a million statements per neuron
        neuron.get_cables(box) #when doing the complete box same times as above
    
    #print('all non-specific preprocessing done')

    #######################################
    ### Export the results              ###
    #######################################
    #export(neurons, run_name)
    #include headings in csv's, preconvert???



    #############################################
    ### Export calculations that I plan to do ###
    # to avoid recomputing these things later ###
    #############################################
    #obtain final calculations, must be done after neurons individual values are completed
    
    folder_path = r'Alternative_computation_results'
    file_path_branched = os.path.join(folder_path, f'alt_lengths_branched_cables_{total_runs}r_{lattice_type}_{X}by{Y}by{Z}_{num_neurons_in_sim}n.txt')
    file_path_terminated = os.path.join(folder_path, f'alt_lengths_terminated_cables_{total_runs}r_{lattice_type}_{X}by{Y}by{Z}_{num_neurons_in_sim}n.txt')

    lengths_branched_cables = []
    lengths_terminated_cables = []
    for neuron in neurons:
        lengths_branched_cables += [neuron.cables[branched_cable][1] for branched_cable in neuron.branch_points] #[1] gives the length
        lengths_terminated_cables += [neuron.cables[terminated_cable][1] for terminated_cable in neuron.child_points] #[1] gives the length
        #cables_lengths = sorted(cables_lengths)
        #cables_bar_root_lengths = cables_lengths[:-1] #removed the longest cable, probably the one to the root
    with open(file_path_branched, 'a') as file:
        for length in lengths_branched_cables:
            file.write(f'{length}\n')
    with open(file_path_terminated, 'a') as file:
        for length in lengths_terminated_cables:
            file.write(f'{length}\n')









    print(f'finished run {run_name}')
    ###################################################
    ### the void - things that I dont want to touch ###
    ###################################################
    ################## NO CODE BELOW ##################
    ###################################################

    #record data and parameters to optomise the plot for
    #total_new_data = []
    #for neuron in neurons:
      # I should add length of root(assumed to be max(cable_lengths)), so the calculation len(neuron.nodes_points) - length of root can be plotte against len(neuron.branch_nodes_points) or len(intersectino points with all other neurons)
        ###### this is what daniel plotted ^^^^ #####
        #interesection_points_with_all_other_neurons = neuron.nodes_points & set().union(*(neuron2.nodes_points for neuron2 in neurons if neuron2 != neuron))
        #neuron counter, length, number of branches, number of intersections
        #new_data = (f'{run_name}_{len(total_new_data)+1}', len(neuron.nodes_points), len(neuron.branch_nodes_points), len(interesection_points_with_all_other_neurons))
        #total_new_data.append(new_data)
    #export_n_branch_sim(total_new_data)

    # print(f'finished run {run_name}')

    #print and plot values
    #num_neurons_with_no_branching = 0
    #for neuron in neurons:
    #    if len(neuron.branch_nodes_points) == 0: num_neurons_with_no_branching += 1
    #print(f'number of neurons with no branching is {num_neurons_with_no_branching}')
    
    # for neuron in neurons:
    #     interesection_points_with_all_other_neurons = neuron.nodes_points & set().union(*(neuron2.nodes_points for neuron2 in neurons if neuron2 != neuron))
        
    #     print(f'neuron {neuron.neuron_id}: length: {len(neuron.nodes_points)}, number of branches: {len(neuron.branch_nodes_points)}, number of intersections with other neurons: {len(interesection_points_with_all_other_neurons)}')

    #     #could cables_lengths in the neuron class but it would have to be a list and so method is left outside
    #     cables_lengths = [cable_length for _, cable_length in neuron.cables.values()]
    #     cables_lengths = sorted(cables_lengths)
    #     cables_bar_root_lengths = cables_lengths[:-1] #removed the longest cable, probably the one to the root
    #     if len(neuron.branch_nodes_points) >= 2: #self terminating branches caused problems
    #         print(f'cable properties, mean, median, variance, standard deviation: {statistics.mean(cables_lengths)}, {statistics.median(cables_lengths)}, {statistics.variance(cables_lengths)}, {statistics.stdev(cables_lengths)}') #add the desired statistices.....
    #         print(f'cable properties without the largest cable, mean, median, variance, standard deviation: {statistics.mean(cables_bar_root_lengths)}, {statistics.median(cables_bar_root_lengths)}, {statistics.variance(cables_bar_root_lengths)}, {statistics.stdev(cables_bar_root_lengths)}') #add the desired statistices.....
        
    #         ###create the bar graph### only for ones that did some branching
    #         length_counts = Counter(cables_bar_root_lengths)
    #         # Separate the counts and lengths for plotting
    #         unique_lengths, counts = zip(*length_counts.items())

    #         # Create a bar graph
    #         plt.bar(unique_lengths, counts, color='blue')
    #         # Add a title and labels
    #         plt.yscale('log')
    #         plt.title('Bar Graph of Lengths Frequency')
    #         plt.xlabel('Branch lengths')
    #         plt.ylabel('Frequency')
    #         # Show the bar graph
    #         plt.show()



    # #8/03 plots, saving cumulative plots
    # folder_path = r'C:\Users\maxga\Desktop\Uni work\undergraduate honours year\han\code 2024\T1Wk4\cable_length_vs_frequency'
    # file_path = os.path.join(folder_path, f'global_lengths_100000r_{X}by{Y}by{Z}_{num_neurons_in_sim}n.txt')
    # global_lengths = []
    # for neuron in neurons:
    #     #interesection_points_with_all_other_neurons = neuron.nodes_points & set().union(*(neuron2.nodes_points for neuron2 in neurons if neuron2 != neuron))
        
    #     #print(f'neuron {neuron.neuron_id}: length: {len(neuron.nodes_points)}, number of branches: {len(neuron.branch_nodes_points)}, number of intersections with other neurons: {len(interesection_points_with_all_other_neurons)}')

    #     #could cables_lengths in the neuron class but it would have to be a list and so method is left outside
    #     cables_lengths = [cable_length for _, cable_length in neuron.cables.values()]
    #     global_lengths+=cables_lengths
    #     #cables_lengths = sorted(cables_lengths)
    #     #cables_bar_root_lengths = cables_lengths[:-1] #removed the longest cable, probably the one to the root
    # with open(file_path, 'a') as file:
    #     for length in global_lengths:
    #         file.write(f'{length}\n')

    # '''length_counts = Counter(global_lengths)
    # unique_lengths, counts = zip(*length_counts.items())
    # # Create a bar graph
    # plt.bar(unique_lengths, counts, color='blue')
    # # Add a title and labels
    # plt.yscale('log')
    # plt.title('Bar Graph of Lengths Frequency')
    # plt.xlabel('Branch lengths')
    # plt.ylabel('Frequency')
    # # Show the bar graph
    # plt.show()'''
    
    # print(f'finished run {run_name}')

    #print('finished printing, onto plotting')
    #plot(neurons)



if __name__ == "__main__":
    main()