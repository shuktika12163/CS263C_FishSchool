import random
from qlearning_predator import *
from qlearning_prey import *
import grid
import math


def random_walk():
    return [random.randint(-1, 1), random.randint(-1, 1)]


def distance_diff(reference, target):
    x0 = reference[0]
    y0 = reference[1]
    x1 = target[0]
    y1 = target[1]    
    dist = math.sqrt(math.pow((x0-x1),2) + math.pow((y0-y1),2))

    return dist


class Prey:

    def __init__(self, c1, c2, v1, v2, energy, z):
        self.qlearn = QLearning_Prey()
        self.position = [c1, c2]
        self.velocity = [v1, v2]
        self.energy = energy
        self.speed = 0.5
        self.id = z
        self.turningAngle = 6
        self.hunger_threshold = 70
        self.preyRepulsionRange = 3
        self.preyOrientationRange = 16
        self.preyAttractionRange = 31
        self.preyPredRange = 10
        # Set to true prey dies
        self.killed = False

    def moveForward(self):
        position = [0,0]
        position[0] = (self.position[0] + self.velocity[0]*self.speed) % 100
        position[1] = (self.position[1] + self.velocity[1]*self.speed) % 100
        grid.singleton_world.move_animat(self, position, self.velocity)
    
    def moveAwayFromPred(self,preds):
        dr = [0,0]
        for pred in preds:
            dist = distance_diff(pred.position,self.position)
            dr[0] = dr[0] + (pred.position[0] - self.position[0])/dist
            dr[1] = dr[1] + (pred.position[1] - self.position[1])/dist
        self.calcFinalRes([-dr[0],-dr[1]])
        
    def moveAwayFromPrey(self,preys_repulsion,preys_orientation,preys_attraction):
        if len(preys_attraction) + len(preys_orientation) + len(preys_repulsion) == 0:
            self.moveForward()
        elif len(preys_repulsion)!=0:
            dr = [0,0]
            for prey in preys_repulsion:
                dist = distance_diff(prey.position,self.position)
                dr[0] += (prey.position[0] - self.position[0])/dist
                dr[1] += (prey.position[1] - self.position[1])/dist
            self.calcFinalRes([-dr[0],-dr[1]])
        else:
            do = [0,0]
            da = [0,0]
            for prey in preys_orientation:
                dist = distance_diff(prey.position,self.position)
                do[0] += (prey.position[0] - self.position[0])/dist
                do[1] += (prey.position[1] - self.position[1])/dist
            for prey in preys_attraction:
                dist = distance_diff(prey.position,self.position)
                da[0] += (prey.position[0] - self.position[0])/dist
                da[1] += (prey.position[1] - self.position[1])/dist
            if len(preys_orientation)==0:
                self.calcFinalRes([-da[0],-da[1]])
            elif len(preys_attraction)==0:
                self.calcFinalRes([-do[0],-do[1]])
            else:
                self.calcFinalRes([-0.5*(do[0]+da[0]), -0.5*(do[1]+da[1])])
                
    def orientWithPrey(self,preys_orientation,preys_attraction):
        if len(preys_orientation)+len(preys_attraction) == 0:
            self.moveForward()
        else:
            do = [0,0]
            da = [0,0]
            for prey in preys_orientation:
                do[0] += (prey.velocity[0])/math.sqrt(prey.velocity[0]**2+prey.velocity[1]**2)
                do[1] += (prey.velocity[1])/math.sqrt(prey.velocity[0]**2+prey.velocity[1]**2)
            for prey in preys_attraction:
                dist = distance_diff(prey.position,self.position)
                da[0] += (prey.position[0] - self.position[0])/dist
                da[1] += (prey.position[1] - self.position[1])/dist
            if len(preys_orientation)==0:
                self.calcFinalRes(da)
            elif len(preys_attraction)==0:
                self.calcFinalRes(do)
            else:
                self.calcFinalRes([0.5*(do[0]+da[0]), 0.5*(do[1]+da[1])])
            
    def move(self):
        preys_repulsion = grid.singleton_world.around_point(self.position, self.preyRepulsionRange,True)        
        preys_orientation = grid.singleton_world.around_point(self.position, self.preyOrientationRange,True)        
        preys_attraction = grid.singleton_world.around_point(self.position, self.preyAttractionRange,True)     
        
        preds = grid.singleton_world.around_point(self.position, self.preyPredRange,False)        

        currentState = self.sense_state(preys_repulsion,preys_orientation,preys_attraction,preds)
        if self.id == 0:
            print "Here: " + str(currentState)
        self.qlearn.choose_action(currentState)
  
        if self.qlearn.chosen_action == PreyAction.EatFood:
            GotFood = grid.singleton_world.foodHere(self.position)
            if GotFood: #
                self.energy += 5            
                if currentState[0] == PreyState.Hungry and GotFood:
                    self.qlearn.doQLearning(self.get_reward(4), currentState)
                else:
                    self.qlearn.doQLearning(self.get_reward(2), currentState)
        elif self.qlearn.chosen_action == PreyAction.MoveAwayFromPredator:
            if len(preds) != 0:
                self.moveAwayFromPred(preds)
                self.qlearn.doQLearning(self.get_reward(4),currentState)
            else:
                self.moveForward()
                self.qlearn.doQLearning(self.get_reward(3),currentState)
        elif self.qlearn.chosen_action == PreyAction.MoveAwayFromPrey:
            self.moveAwayFromPrey(preys_repulsion,preys_orientation,preys_attraction)
            if preys_repulsion!=0:
                self.qlearn.doQLearning(self.get_reward(4),currentState)
            else:
                self.qlearn.doQLearning(self.get_reward(3),currentState)
        elif self.qlearn.chosen_action == PreyAction.OrientWithPrey:
            self.orientWithPrey(preys_orientation,preys_attraction)
            if len(preys_orientation)>0:
                self.qlearn.doQLearning(self.get_reward(4),currentState)
            else:
                self.qlearn.doQLearning(self.get_reward(3),currentState)
        elif self.qlearn.chosen_action == PreyAction.MoveTowardsPrey:
            self.orientWithPrey(preys_orientation, preys_attraction) 
            if len(preys_attraction) > 0:
                self.qlearn.doQLearning(self.get_reward(4),currentState)
            else:
                self.qlearn.doQLearning(self.get_reward(3),currentState)
        else:
            self.moveForward()
            self.qlearn.doQLearning(self.get_reward(1),currentState)
            
#        grid.singleton_world.move_animat(self, coord)

    def calcFinalRes(self,da):
        if da[0] > 0:
            di_angle = math.degrees(math.atan(da[1]/da[0]))
        else:
            di_angle = 180 + math.degrees(math.atan(da[1]/da[0]))
#        di_angle = math.degrees(math.atan(da[1]/da[0]))
            
        if self.velocity[0] > 0:
            vi_angle = math.degrees(math.atan(self.velocity[1]/self.velocity[0]))
        else:
            vi_angle = 180 + math.degrees(math.atan(self.velocity[1]/self.velocity[0]))
        
        velocity = [0,0]
        angle_diff = di_angle - vi_angle
        if abs(angle_diff) < self.turningAngle:
            velocity = da
        else:
            if angle_diff < 0:
                angle = vi_angle - self.turningAngle
            else:
                angle = vi_angle + self.turningAngle
            
            velocity[0] = math.cos(math.radians(angle))
            velocity[1] = math.sin(math.radians(angle))
            
        temp = math.sqrt(velocity[0]**2 + velocity[1]**2)
        
        velocity[0] = velocity[0] / temp
        velocity[1] = velocity[1] / temp
        position = [0,0]
        position[0] = (self.position[0] + velocity[0] * self.speed) % 100
        position[1] = (self.position[1] + velocity[1] * self.speed) % 100
        grid.singleton_world.move_animat(self, position, velocity)


    def get_reward(self,x):
        if x == 1:
            return 0.25
        elif x == 2:
            return 1
        elif x == 3:
            return -1
        else:
            return 1.75
            
    def sense_state(self, preys_repulsion,preys_orientation,preys_attraction,preds):
            list_state = []
            
            if self.energy < self.hunger_threshold:
                list_state.append(PreyState.Hungry)
            else:
                list_state.append(PreyState.NotHungry)
            if len(preds)>0:
                list_state.append(PreyState.PredatorDetected)
            else:
                list_state.append(PreyState.PredatorNotDetected)
            if len(preys_repulsion)>0:
                list_state.append(PreyState.PreyInRepulsion)
            if len(preys_orientation) >0:
                list_state.append(PreyState.PreyInOrientation)
            if len(preys_attraction)>0:
                list_state.append(PreyState.PreyInAttraction)

            return list_state
    
    def printqtable(self):
        print(self.qlearn.table)


        
        
        
class Predator:

    def __init__(self, c1, c2, v1, v2, energy, z):
        self.qlearn = QLearning_Predator()
        self.position = [c1, c2]
        self.velocity = [v1, v2]
        self.energy = energy
        self.hunger_threshold = 70
        self.killed = False
        self.wait_time = 5
        self.id = z
        self.predatorRange = 50
        self.speed = 1
        self.turningAngle = 6
    
    def closestPrey(self):
        animats = grid.singleton_world.around_point(self.position, self.predatorRange,True)
        animats.sort(key = lambda x:distance_diff(x.position, self.position))
        diff = distance_diff(animats[0].position, self.position)    
        return animats[0]
        
    def moveForward(self):
        position = [0,0]
        position[0] = (self.position[0] + self.velocity[0]*self.speed) % 100
        position[1] = (self.position[1] + self.velocity[1]*self.speed) % 100
        grid.singleton_world.move_animat(self, position, self.velocity)

    def calcFinalRes(self,da):
        if da[0] > 0:
            di_angle = math.degrees(math.atan(da[1]/da[0]))
        else:
            di_angle = 180 + math.degrees(math.atan(da[1]/da[0]))
#        di_angle = math.degrees(math.atan(da[1]/da[0]))
            
        if self.velocity[0] > 0:
            vi_angle = math.degrees(math.atan(self.velocity[1]/self.velocity[0]))
        else:
            vi_angle = 180 + math.degrees(math.atan(self.velocity[1]/self.velocity[0]))
        
        velocity = [0,0]
        angle_diff = di_angle - vi_angle
        if abs(angle_diff) < self.turningAngle:
            velocity = da
        else:
            if angle_diff < 0:
                angle = vi_angle - self.turningAngle
            else:
                angle = vi_angle + self.turningAngle
            
            velocity[0] = math.cos(math.radians(angle))
            velocity[1] = math.sin(math.radians(angle))
            
        temp = math.sqrt(velocity[0]**2 + velocity[1]**2)
        
        velocity[0] = velocity[0] / temp
        velocity[1] = velocity[1] / temp
        position = [0,0]
        position[0] = (self.position[0] + velocity[0] * self.speed) % 100
        position[1] = (self.position[1] + velocity[1] * self.speed) % 100
        grid.singleton_world.move_animat(self, position, velocity)

    def moveTowardsPrey(self,preyPosition):
        da = [0,0]
        da[0] = (preyPosition[0] - self.position[0])/distance_diff(self.position, preyPosition)
        da[1] = (preyPosition[1] - self.position[1])/distance_diff(self.position, preyPosition)
        self.calcFinalRes(da)
        
    def move(self):
#        print "HERE"
        prey = self.closestPrey()

        currentState = self.sense_state(prey)
        self.qlearn.choose_action(currentState)
        diff = distance_diff(self.position, prey.position)
        
        if self.qlearn.chosen_action == PredatorAction.MoveTowardsPrey:
            if prey is None:
                self.moveForward()
                self.qlearn.doQLearning(self.get_reward(3), currentState)
            else:
                self.moveTowardsPrey(prey.position)
                self.qlearn.doQLearning(self.get_reward(4), currentState)
        elif self.qlearn.chosen_action == PredatorAction.EatPrey:
            if prey is not None:
                self.energy += 3            
                if currentState[0] == PredatorState.Hungry and diff < 3:
                    grid.singleton_world.kill(prey)
                    self.qlearn.doQLearning(self.get_reward(4), currentState)
                else:
                    self.qlearn.doQLearning(self.get_reward(2), currentState)
            else:
                self.qlearn.doQLearning(self.get_reward(3), currentState)
        else:
            self.moveForward()
            self.qlearn.doQLearning(self.get_reward(1), currentState)
            

    def get_reward(self,x):
        if x == 1:
            return 0.25
        elif x == 2:
            return 1
        elif x == 3:
            return -1
        else:
            return 1.75



# --- Return the state of the Animat
    def sense_state(self, closestPrey):
            list_state = []        
            
            if self.energy < self.hunger_threshold:
                list_state.append(PredatorState.Hungry)
            else:
                list_state.append(PredatorState.NotHungry)
            if closestPrey is not None:
                list_state.append(PredatorState.PreyDetected)

            return list_state

    def printqtable(self):
        print(self.qlearn.table)