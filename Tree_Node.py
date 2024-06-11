#tree_node.py Max Galettis
#treenode is the class for lattice points

#up to wk7 standards, 27/03/2024
class TreeNode:
    def __init__(self, point, neighbours): 
        #sets typically store neuron ids here
        #x can be an int(tetra, cube, octahedra) or a list corresponding to [1, phi, phi^2](dodecahedron and icosahedron), this simalirly applies to the elements in the tuples for neighbours
        self.point = point
        #a set of points that this point is connected to on the lattice
        self.neighbours = neighbours 
        #set of neuron_ids that this point is a parent for
        self.is_parent_point_for = set() # use in method to test, use .add to add childrens neuron_id
        #set of neuron_ids that this point has more than one child for
        self.is_branch_point_for = set() #stores NEURON IDS

        #{neuron.neuron_id : (parent_point,time_assigned,...otheruseful_stuff_at_some_point)} , neuron.neuron_id in self.neurons_parent will return true and false on the keys just like a set
        self.neurons = {}  #used to check if this point is occupied by a neuron

        self.was_occupied = False # updates to true when neuron.FRESH_points are pushed to neuron.pointss, this allows for propogation in the next iteration to generate 2 branches.

    def assign_to_neuron(self, parent_neuron, parent_point, local_time):
        parent_neuron.future_points.add(self.point)
        self.neurons[parent_neuron.neuron_id] = (parent_point, local_time) 
        #self.was_occupied = False, not yet

    def assign_child_for(self, neuron_id):
        #tracks children in the parent point
        self.is_parent_point_for.add(neuron_id)

    def assign_branch_for(self, neuron_id):
        #tracks branching points at the piint level
        self.is_branch_point_for.add(neuron_id)

    def available_neighbours(self, box, neuron_id): #box is the lattice/dictionary of all the treenodes
        candidate_points = [] #needs to be list so that the random method can operate on it
        for neighbor in self.neighbours: 
            #neighbour has already been checked that it is inside the box
            if (
                neuron_id not in box[neighbor].neurons and 
                len(box[neighbor].neurons) < 2
                ): #only allow at most 2 neurons per point
                candidate_points.append(neighbor)
        return candidate_points
        #random.choices(candidate_points)
    

    #variation of above
    def unoccupied_neighbours(self, box, neuron_id): #box is the lattice/dictionary of all the treenodes
        unoccupied_points = [] #needs to be list so that the random method can operate on it
        for neighbor in self.neighbours: 
            #neighbour has already been checked that it is inside the box
            if (
                not box[neighbor].neurons
                ): #returns neighbours without any neurons in them, empty dictionaries evaluate false
                unoccupied_points.append(neighbor)
        return unoccupied_points
    

    #variation of above
    def not_neuron_id_neighbours(self, box, neuron_id): #box is the lattice/dictionary of all the treenodes
        #allow any number of neurons at a neighbour, only exclude a neibour for which the neuron(neuron_id) occupies 
        candidate_points = [] #needs to be list so that the random method can operate on it
        for neighbor in self.neighbours: 
            #neighbour has already been checked that it is inside the box
            if (
                neuron_id not in box[neighbor].neurons 
                ): #only allow any number of neurons per point
                candidate_points.append(neighbor)
        return candidate_points
    