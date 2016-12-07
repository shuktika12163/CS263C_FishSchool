from random import randint
import random
from animat import Prey
from animat import Predator
import math

def distance_diff(reference, target):
        x0 = reference[0]
        y0 = reference[1]
        x1 = target[0]
        y1 = target[1]    
        dist = math.sqrt(math.pow((x0-x1),2) + math.pow((y0-y1),2))
        
        return dist

class World:

    def __init__(self):
        #self.grid = position_grid
        self.preys = []
        self.predators = []
        self.food = []
        self.clock = 0
        self.width = 100
        self.height = 100
        self.foodCount = 30
        self.preyCount = 50
        self.predatorCount = 1
        self.__init_prey(self.preyCount)
        self.__init_predator(self.predatorCount)
        self.__set_food()

    def __set_food(self):
        for i in range(self.foodCount):
            coord = [random.uniform(0, self.height-1), random.uniform(0, self.width-1)]
            self.food.append(coord)

    def __init_prey(self,count):
        for i in range(count):
            coord = [random.uniform(0.0, self.height-1), random.uniform(0.0, self.width-1)]
            velocity = [random.uniform(-1.0, 1.0), random.uniform(-1.0, 1.0)]
            temp = math.sqrt(velocity[0]**2 + velocity[1]**2)
            velocity[0] = velocity[0] / temp
            velocity[1] = velocity[1] / temp
            energy = randint(0,100)
            prey = Prey(coord[0], coord[1], velocity[0], velocity[1], energy, i)
            self.preys.append(prey)

    def __init_predator(self,count):
        for i in range(count):
            coord = [random.uniform(0.0, self.height-1), random.uniform(0.0, self.width-1)]
            velocity = [random.uniform(-1.0, 1.0), random.uniform(-1.0, 1.0)]
            temp = math.sqrt(velocity[0]**2 + velocity[1]**2)
            velocity[0] = velocity[0] / temp
            velocity[1] = velocity[1] / temp
            energy = 10
            predator = Predator(coord[0], coord[1], velocity[0], velocity[1], energy, i)
            self.predators.append(predator)
            
    def move_animat(self, animat, new_coord, new_velocity):
        animat.position = new_coord
        animat.velocity = new_velocity
        animat.energy = animat.energy - 1;
    
    def around_point(self, coord, view_range, isPrey):
        ranged_animats = []     # Will contain animats in order of ranges.
        if isPrey:
            for prey in self.preys:
                distance = distance_diff(coord, prey.position)
                if distance < view_range and distance!=0:
                    ranged_animats.append(prey)
        else:
            for pred in self.predators:
                distance = distance_diff(coord, pred.position)
                if distance < view_range and distance!=0:
                    ranged_animats.append(pred)
        return ranged_animats

    def kill(self, animat):
        #self.grid.remove_from_position(animat)
        if animat in self.preys:
            print "Prey died at " + str(animat.position)
            new_prey = animat
            self.preys.remove(animat)
            new_prey.position = [-100,-100]
            new_prey.energy = randint(0,100)
            self.preys.append(new_prey)
            
        if animat in self.predators:
            print "Predator died at " + str(animat.position)
            new_predator = animat
            self.predators.remove(animat)
            new_predator.position = [random.uniform(0.0, self.height-1), random.uniform(0.0, self.width-1)]
            new_predator.energy = 100
            self.predators.append(new_predator)

    def foodHere(self,position):
        for f in self.food:
            if distance_diff(position,f) < 3:
                self.food.remove(f)
                self.food.append([random.uniform(0, self.height-1), random.uniform(0, self.width-1)])
                return True
        return False
            
    def printqtables(self):
        for predator in self.predators:
            predator.printqtable()

    def tick(self):
        # Pick the next step
        for easy in self.easy_preys:
            easy.move(self.clock)
        for hard in self.hard_preys:
            hard.move(self.clock)
        for predator in self.predators:
            predator.move(self.clock)
        # Process the movement and results
        # Right now only Predators can take actions of their movement.
        for predator in self.predators:
            # Reduce wait time
            predator.act()
        self.clock += 1  # increment timer.

singleton_world = None
