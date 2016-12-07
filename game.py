#import pygame
#from grid import World
import grid
import matplotlib.pyplot as plt
import time

#pygame.init()
#pygame.display.set_caption('Predators attack!')
#clock = pygame.time.Clock()

done = False

grid.singleton_world = grid.World()
#myWorld = World()
#hl, = plt.plot([],[])

while(True):
    preys = grid.singleton_world.preys# myWorld.preys
    predators = grid.singleton_world.predators#myWorld.predators
    food = grid.singleton_world.food
    plt.close()
    plt.xlim(0,100)
    plt.ylim(0,100)    
    for f in food:
        plt.scatter(f[0],f[1],color='g')
    for prey in preys:
        prey.move()
        plt.arrow(prey.position[0],prey.position[1],prey.velocity[0]*2,prey.velocity[1]*2,head_width=1)
    #preys[0].printqtable()
    for predator in predators:
        predator.move()
        print predator.position
        predator.printqtable()
#        print predator.velocity
        plt.arrow(predator.position[0],predator.position[1],predator.velocity[0]*5,predator.velocity[1]*5,head_width=2,color='r')
    plt.show()
    time.sleep(0.1)
