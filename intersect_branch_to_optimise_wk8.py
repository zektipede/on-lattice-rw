#! /bin/usr/env python3

#11/06/2024 Max Galettis
#refined comments for the sake of sharing, not one piece of outdated code was left in.
#  for all outdated code see non_intersect_branch_alternative_growth_rule.py
#note: last major changes occured on 02/04/2024


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
X = 159
Y = 159
Z = 159
lattice_type ='octahedron' #'tetrahedron', 'cube', 'octahedron'
time_steps = 10000
num_neurons_in_sim = 100
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


#up to standards 2/04/2024
def export(neurons, run_name, box):
    #export a file with the run name and
    #heading [('neuron_name(arbitrary number)', 'x','y','z', 'parent_x', 'parent_y', 'parent_z', 'time_added_to_neuron', 'is_root', 'is_childless', 'is_branch', 'is_intersection')]
    folder_name = 'Computation_results'
    file_name = f'neuron_collection_data_{lattice_type}lattice_run{run_name}_{X}by{Y}by{Z}_{num_neurons_in_sim}n.csv' #remove run name from the export, can add titles to the csv
    csv_file_path = os.path.join(folder_name, file_name)

    
    arbitrary_neuron_name = 0
    all_points_data = [('neuron_name(arbitrary number)', 'x','y','z', 'parent_x', 'parent_y', 'parent_z', 'time_added_to_neuron', 'is_root', 'is_childless', 'is_branch', 'is_intersection')]
    for neuron in neurons:
        arbitrary_neuron_name += 1 #must be non zero for some pandas analysis

        #terminating_points = neuron.branch_nodes_points.union(neuron.child_nodes_points)
        interesection_points_with_all_other_neurons = neuron.points & set().union(*(neuron2.points for neuron2 in neurons if neuron2 != neuron))
        
        neuron_id = neuron.neuron_id
        for point in neuron.points:
            x, y, z = point[:3]
            parent_x, parent_y, parent_z = box[point].neurons[neuron_id][0][:3]
            time_added_to_neuron = box[point].neurons[neuron_id][1]
            #0 is false, 1 is true
            is_root = 1 if point == neuron.root else 0
            is_childless = 1 if point in neuron.child_points else 0
            is_branch = 1 if point in neuron.branch_points else 0
            is_intersection = 1 if point in interesection_points_with_all_other_neurons else 0
            one_points_data = (arbitrary_neuron_name, x, y, z, parent_x, parent_y, parent_z, time_added_to_neuron, is_root, is_childless, is_branch, is_intersection)
            all_points_data.append(one_points_data) #note, one_points_data is a tuple, this is important to get each point as a seperate row
    update_and_save_csv(csv_file_path, all_points_data)
        # run_name, neuron_name(arbitrary number), x,y,z, parent_x, parent_y, parent_z, time_added_to_neuron, is_root, is_childless, is_branch, is_intersection,


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
    code_time+=1 #time displayed is time its been running/time this point got added to the sim

    #######################################
    ### grow the neurons in the lattice ###
    #######################################
    while code_time <= time_steps:
        #method for chosing which direction to go
        for neuron in neurons:
            for point in neuron.fresh_points:
                #node = box[point] #archaic 27/03/2024
                directions = box[point].available_neighbours(box, neuron.neuron_id)
                if directions: #empty lists automatically evaluate false
                    direction = random.choice(directions)
                    directions.remove(direction)
                    #############add code_time delay here, i.e for code_time % interval_size != 0:, would result in propogation along only one direction and 
                    #############could be nice to get a better scale and distance the branching, especially multiple instances of branching, between neurons
                    box[direction].assign_to_neuron(neuron, parent_point=point, local_time=code_time) #assign the next point with this point as parent 
                    box[point].assign_child_for(neuron.neuron_id)
                #in this case, the branch condition is box[point].was_occupied but replace this depending on the run you want to perform
                if box[point].was_occupied and directions: #try to create a second branches, so long as there is somewhere to go
                    total_branch_points += 1
                    direction = random.choice(directions)
                    ##########add code_time delay, to delay the ability for points to branch? same as above?
                    #branches as data strucure here?...
                    box[direction].assign_to_neuron(neuron, parent_point=point, local_time=code_time) #assign the next point with this point as parent 
                    #the child would already have been assigned, just not set to occupied :)
                    box[point].assign_branch_for(neuron.neuron_id)
                    neuron.record_branch_point(point)
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
    export(neurons, run_name, box)
    #include headings in csv's, preconvert???



    #############################################
    ### Export calculations that I plan to do ###
    # to avoid recomputing these things later ###
    #############################################
    #obtain final calculations, must be done after neurons individual values are completed
    
    # folder_path = r'Computation_results'
    # file_path_branched = os.path.join(folder_path, f'lengths_branched_cables_100r_{lattice_type}_{X}by{Y}by{Z}_{num_neurons_in_sim}n.txt')
    # file_path_terminated = os.path.join(folder_path, f'lengths_terminated_cables_100r_{lattice_type}_{X}by{Y}by{Z}_{num_neurons_in_sim}n.txt')

    # lengths_branched_cables = []
    # lengths_terminated_cables = []
    # for neuron in neurons:
    #     lengths_branched_cables += [neuron.cables[branched_cable][1] for branched_cable in neuron.branch_points] #[1] gives the length
    #     lengths_terminated_cables += [neuron.cables[terminated_cable][1] for terminated_cable in neuron.child_points] #[1] gives the length
    #     #cables_lengths = sorted(cables_lengths)
    #     #cables_bar_root_lengths = cables_lengths[:-1] #removed the longest cable, probably the one to the root
    # with open(file_path_branched, 'a') as file:
    #     for length in lengths_branched_cables:
    #         file.write(f'{length}\n')
    # with open(file_path_terminated, 'a') as file:
    #     for length in lengths_terminated_cables:
    #         file.write(f'{length}\n')









    print(f'finished run {run_name}')

if __name__ == "__main__":
    main()