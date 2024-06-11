#Neuron.py Max Galettis

#Neuron is the class for non intersecting branching lattice paths moving on a .lat file which is a dictionary of key, TreeNode pairs.


#up to initial week 7 standards, 27/03/2024
class Neuron: #neurons are made of many points aka TreeNodes
    def __init__(self, box, point, local_time):
        #sets typically store points here

        #variables for neuron growth
        self.neuron_id = id(self)  # Unique identifier for the neuron
        self.root = point
        self.points = set()
        self.fresh_points = set() # set of points that were added last, these are the points to propogate
        self.future_points = set() # set of points that will be moved into .points after all is done, but first go to fresh points in the next iteration of the growing loop
        
        #necessary init method for neuron growth:
        box[point].assign_to_neuron(self, self.root, local_time)
        self.migrate_future_points() #make sure the box's points are set was_occupied to true after each growth
    
        #variables for neuron property calculation
        self.branch_points = set()
        self.child_points = set() #only updated by get points with no children
        self.cables = {} #self.cables[end_point] = (start_point, cable_length)
        #self.branches = set()
        self.intersection_points = set()
    
    
    def record_branch_point(self, branch_point):
        self.branch_points.add(branch_point)

    def migrate_fresh_points(self, box): 
        #can branch upon contact if migrate fresh_points is run imediately after all points for one neuron have propogated, but will need to randomise order of neurons in the neurons list to avoid bias stemming from this method
        #if two heads meet, only the second head to arrive to that location would branch at that location
        #   this is technically consistent with behaviour when a head meets a body nodes, but whether this is desired is another question
        self.points.update(self.fresh_points)
        for fresh_point in self.fresh_points:
            box[fresh_point].was_occupied=True
        self.fresh_points.clear()

    def migrate_future_points(self):
        self.fresh_points.update(self.future_points)
        self.future_points.clear()


    #methods for calulating quantities: cable length, contact points#, branch points#, cable length of branches
    #len(self.child_points)
    #cable_length = self.cables[end_point][2]
    #total cable length = len(self.points)
    #contact points, calculated when plotting
    def get_points_with_no_children(self, box):
        self.child_points = set()
        for point in self.points:
            if self.neuron_id not in box[point].is_parent_point_for:
                self.child_points.add(point)
        return self.child_points
    

    def get_cables(self, box):
        self.cables = {}
        for point in self.branch_points.union(self.child_points):
            end_point = point
            cable_length = 1
            parent_point=box[point].neurons[self.neuron_id][0] #0 is the point (spatial) of the parent
            while parent_point not in self.branch_points and parent_point != self.root:
            #while self.neuron_id not in box[parent_point].is_branch_point_for and parent_point != self.root: other method is slightly faster i think
                cable_length+=1
                new_parent_point = box[parent_point].neurons[self.neuron_id][0]
                parent_point = new_parent_point
            start_point = parent_point
            self.cables[end_point] = (start_point, cable_length)
