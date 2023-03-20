from math import factorial as f
from matplotlib import cm
import numpy as np
from numpy.random import binomial as binom
from math import *
import random
import time,os,sys,copy
import pygame
from guiFrame import *
import pyGameUtilities as pgUtils
from pyGameUtilities import SMALLFONT, BASICFONT
import mathUtilities as mUtils

class geneticModel(customPyWindow):
    def __init__(self, numberOfGridX = 4, numberOfGridY = 4, meanActiveSize = 50, meanDormantSize = 30, meanActiveDensity = 0.1, meanDormantDensity = 0.5, resampleRate = 1, exchangeRate = 0.01, migrationSpeed = 1):
    
        ''' Initialize default parameters '''
        #average number (E[N_i]) of total individuals in each active population
        self.MEAN_VAL_ACTIVE=meanActiveSize
        #average number (E[M_i]) of total individuals in each dormant population
        self.MEAN_VAL_DORMANT=meanDormantSize
        #average density of type A (green) individuals in each active population
        self.MEAN_DENSITY_ACTIVE=meanActiveDensity
        #average density of type A (green) individuals in each dormant population
        self.MEAN_DENSITY_DORMANT=meanDormantDensity
        #number of colors in the colormap
        self.NUMBER_OF_COLORS = 10
        #name of the colormap (must be available in the matplotlib colormaps (see the list of all available colormaps with matplotlib.cm._colormaps())
        self.COLOR_MAP = 'PiYG'
        #rate at which each active individual resample gene types from their own colony
        self.resamp_active=resampleRate
        #rate at which each active individual exchange positions with dormant individuals
        self.lamb=exchangeRate
        #total rate at which each active individual resample gene types from other colonies (migration)
        self.speed=migrationSpeed
        #specify seed value
        self.SEED_VALUE = 2581621813797181287
        #save pictures of the ongoing simulation?
        self.SAVE_FILE = False
        #if SAVE_FILE is set to True, set prefix in the file name of each picture:
        self.FILE_PREFIX = 'pic'
        #if SAVE_FILE is set to True, specify folder name in which pictures are saved:
        self.FOLDER_NAME = 'image'
        
        #************ Specify geographic space ***********
        #number of colonies in the x-direction
        self.grid_x=numberOfGridX
        #number of colonies in the y-direction
        self.grid_y=numberOfGridY
        
        # verify if the above parameters are valid
        assert type(self.grid_x)==int and self.grid_x > 0
        assert type(self.grid_y)==int and self.grid_y > 0
        assert self.MEAN_VAL_ACTIVE > 0
        assert self.MEAN_VAL_DORMANT > 0
        assert self.MEAN_DENSITY_ACTIVE >= 0 and self.MEAN_DENSITY_ACTIVE <= 1
        assert self.MEAN_DENSITY_DORMANT >= 0 and self.MEAN_DENSITY_DORMANT <= 1
        assert type(self.SAVE_FILE) == bool
        assert type(self.FILE_PREFIX)==str and type(self.FOLDER_NAME)==str and type(self.COLOR_MAP)==str
        
        #a numpy array which stores the active and dormant population sizes in each colony.
        self.PopData=np.zeros((self.grid_x,self.grid_y,2), dtype="int32")
        #******************* Specify parameters for pygame GUI *********************************
        super().__init__(self.grid_x, self.grid_y, self.NUMBER_OF_COLORS, self.COLOR_MAP, saveImages = self.SAVE_FILE, imagePrefix = self.FILE_PREFIX, outputFolder = self.FOLDER_NAME)
        self.initDisplay("Multi colony model on torus Z_%d x Z_%d"%(self.grid_x, self.grid_y))
        self.setLabelOfFirstWindow("Active population", fontColor=(0,0,250))
        self.setLabelOfSecondWindow("Dormant population", fontColor=(250, 0, 0))
        self.data = None
        self.init_data = None
        self.initializeModel()
        
    def initializeModel(self):
        #contains the initial number of type A active and dormant individuals in each colony
        self.init_data=np.ndarray(shape=(self.grid_x, self.grid_y, 2), dtype = "int32")
        self.data=self.init_data.copy() #contains the time-evolving genetic data, i.e., the number of type A active and dormant individuals in each colony
        self.totalActiveSize = 0 #Total size of the initial active populations
        self.maximumActiveSize = 0 #Maximum of active population sizes
        self.maximumDormantSize = 0 #Maximum of dormant population sizes
        self.totalDormantSize = 0 #Total size of the initial dormant populations
        self.totalActiveTypeA = 0 #Total number of initial type A active individuals
        self.totalDormantTypeA = 0 #Total number of initial type A active individuals
        for x in range(self.grid_x):
            for y in range(self.grid_y):
                N,M=self.pop_val((x,y)) #generate initial population sizes randomly sampled from Geometric distribution
                if N > self.maximumActiveSize: self.maximumActiveSize = N
                if M > self.maximumDormantSize: self.maximumDormantSize = M
                self.totalActiveSize += N
                self.totalDormantSize += M
                val_x,val_y=binom(N,self.MEAN_DENSITY_ACTIVE),binom(M,self.MEAN_DENSITY_DORMANT) #assign type A to the active (dormant) individuals w.p. MEAN_DENSITY_ACTIVE (resp., MEAN_DENSITY_DORMANT), and type B w.p. 1-MEAN_DENSITY_ACTIVE (resp. 1-MEAN_DENSITY_DORMANT)
                self.init_data[(x,y)]=(val_x,val_y)
                self.totalActiveTypeA += val_x
                self.totalDormantTypeA += val_y
                color_a=self.color_map(val_x/N)
                color_d=self.color_map(val_y/M)
                color_a = (round(255*color_a[0]),round(255*color_a[1]),round(255*color_a[2]))
                color_d = (round(255*color_d[0]),round(255*color_d[1]),round(255*color_d[2]))
                self.updateColor((x,y), color_a, 1)
                self.updateColor((x,y), color_d, 2)
                dataString = []
                dataString.append("Total active and dormant individuals: {}, {}".format(N,M))
                dataString.append("Seed bank strength: %.2f"%(M/N))
                dataString.append("Total Type A active individuals: {}".format(val_x))
                dataString.append("Total Type A dormant individuals: {}".format(val_y))
                self.setDataString((x,y), dataString)
        self.totalInitialActiveTypeA = self.totalActiveTypeA
        self.totalInitialDormantTypeA = self.totalDormantTypeA
        self.resetVariables()
        self.addButton("Start", self.OnStart, {}, pygame.K_SPACE)
        self.addButton("Reset", self.OnReset, {}, pygame.K_r)
        self.addButton("Save image: {}".format(self.SAVE_FILE), self.OnSaveImage)
        self.updateButtonList()
        
    def updateWholeDisplay(self):
        for x in range(self.grid_x):
            for y in range(self.grid_y):
                N,M=self.pop_val((x,y)) #generate initial population sizes randomly sampled from Geometric distribution
                val_x,val_y=self.data[(x,y)]
                color_a=self.color_map(val_x/N)
                color_d=self.color_map(val_y/M)
                color_a = (round(255*color_a[0]),round(255*color_a[1]),round(255*color_a[2]))
                color_d = (round(255*color_d[0]),round(255*color_d[1]),round(255*color_d[2]))
                self.updateColor((x,y), color_a, 1)
                self.updateColor((x,y), color_d, 2)
                dataString = []
                dataString.append("Total active and dormant individuals: {}, {}".format(N,M))
                dataString.append("Seed bank strength: %.2f"%(M/N))
                dataString.append("Total Type A active individuals: {}".format(val_x))
                dataString.append("Total Type A dormant individuals: {}".format(val_y))
                self.setDataString((x,y), dataString)
                
    def resetVariables(self):
        mUtils.setSeed(self.SEED_VALUE)
        self.frameCount = 0
        self.data=self.init_data.copy()
        self.totalActiveTypeA = self.totalInitialActiveTypeA
        self.totalDormantTypeA = self.totalInitialDormantTypeA
        activeTypeAPercent=round((self.totalActiveTypeA)*100/self.totalActiveSize)
        dormantTypeAPercent=round((self.totalDormantTypeA)*100/self.totalDormantSize)
        self.clearColorMap()
        self.addTickMark(activeTypeAPercent, (0, 0, 250))
        self.addTickMark(dormantTypeAPercent, (250, 0, 0))
        self.updateWholeDisplay()
        
        self.hasPopulationClustered = False #indicates whether the population has reached global clustering.
        self.mig_range = 1 #default migration range of each individual
        self.max_dist=False #should the model use max-distance as default distance function to compute neighbourhood of each colony
        self.wait = 0 #first random time until an event happens.
        self.init_exp=random.expovariate(1) #sample expovariate of mean 1
        self.prob_lst, self.rate = self.get_next_event() #generate the possible events and their probability in the next jump time.
        self.cur_list = self.prob_lst
        if self.rate!=0: #if there is a positive rate of some event happening, then clustering has not occurred yet.
            self.wait=self.init_exp/self.rate #update the next jump time
        else:
            self.wait=0 #otherwise the system has reached clustering
            self.hasPopulationClustered = True
        self.continueSimulation = False
        self.pause=True
        
    def OnStart(self):
        if (self.pause):
            self.pause = False
            self.updateButtonLabel("Start","Pause")
        else:
            self.pause = True
            self.updateButtonLabel("Pause", "Start")
    def OnReset(self):
        if not self.pause:
            self.updateButtonLabel("Pause", "Start")
            self.pause = True
        self.resetVariables()
    def OnSaveImage(self):
        if (self.SAVE_FILE):
            self.SAVE_FILE = False
            self.updateButtonLabel("Save image: True", "Save image: False")
        else:
            self.SAVE_FILE = True
            self.updateButtonLabel("Save image: False", "Save image: True")
    def pop_val(self, i):
        '''Returns (N,M), where N~Geometric(MEAN = MEAN_VAL_ACTIVE), M~Geometric(MEAN = MEAN_VAL_DORMANT)'''
        if self.PopData.any(): return (self.PopData[i][0], self.PopData[i][1])
        pA=1/self.MEAN_VAL_ACTIVE
        pD=1/self.MEAN_VAL_DORMANT
        self.PopData=np.ndarray(shape=(self.grid_x, self.grid_y, 2), dtype="int32")
        for dummyVar in range(self.grid_x):
            self.PopData[dummyVar,:,:1] = np.random.geometric(pA,(self.grid_y,1))
            self.PopData[dummyVar,:,1:] = np.random.geometric(pD,(self.grid_y,1))
        return (self.PopData[i][0], self.PopData[i][1])
        
    def get_next_event(self):
        '''Returns a list of possible next events and their probabilities on the next jump time.
        @param data: list containing initial number of type A active and dormant individuals in each colony.
        '''
        sample_prob_lst=[] #an element is [rate,[colony,position,change]]
        for x_index in range(self.grid_x):
            for y_index in range(self.grid_y):
                i = (x_index,y_index) #box coordinates of colony i. 1 + x_index -> column number, 1 + y_index -> row number
                X,Y=self.data[i] # X -> number of type A active individuals, Y -> number of type A dormant individuals
                N,M=self.pop_val(i) # N -> size of active population at colony i., M -> size of dormant population at colony i.
                d_rate=self.resamp_active*X*(N-X)/(2.0*N) # death rate of type A active individuals at colony i
                b_rate=self.resamp_active*X*(N-X)/(2.0*N) # birth rate of type A active individuals at colony i.
                for m_x_index in range(self.grid_x):
                    for m_y_index in range(self.grid_y):
                        j = (m_x_index, m_y_index)
                        a_ij=mUtils.finite_migrate(i,j,self.grid_x,self.grid_y)
                        if a_ij>0: #includes i != j case
                            X_j,Y_j=self.data[j]
                            N_j,M_j=self.pop_val(j)
                            d_rate+=self.speed*a_ij*X*((N_j-X_j)/N_j)
                            b_rate+=self.speed*a_ij*(N-X)*(X_j/N_j)
                w_rate=self.lamb*(N-X)*(Y/M) # wake up rate of type A dormant individuals
                s_rate=self.lamb*X*((M-Y)/M) # sleep rate of type A active individuals
                if w_rate> 0: sample_prob_lst.append([w_rate,[i,(X+1,Y-1),(1,-1)]]) # event that a type A active individual wakes up
                if s_rate> 0: sample_prob_lst.append([s_rate,[i,(X-1,Y+1),(-1,1)]]) # event that a type A active individual goes to sleep.
                if d_rate> 0: sample_prob_lst.append([d_rate,[i,(X-1,Y),(-1,0)]]) #event that a type A active individual dies
                if b_rate> 0: sample_prob_lst.append([b_rate,[i,(X+1,Y),(1,0)]]) #event that a type A active individual is born
        total_rate=sum(i[0] for i in sample_prob_lst)
        return sample_prob_lst, total_rate
            
    def __repr__(self):
        representation = ""
        representation+="Model parameters are initialized as following:\n"
        representation+="Resampling rate: {}\n".format(self.resamp_active)
        representation+="Exchange rate: {}\n".format(self.lamb)
        representation+="Total migration rate: {}\n".format(self.speed)
        representation+="Colonies are labelled with their boxCoordinates given by (row number, column number).\n"
        representation+="Population sizes are drawn from Geometric(%d),Geometric(%d)\n"%(self.MEAN_VAL_ACTIVE, self.MEAN_VAL_DORMANT)
        representation+="\nPopulation sizes in each colony (N,M,M/N): \n"
        for x in range(self.grid_x):
            for y in range(self.grid_y):
                N,M=self.pop_val((x,y))
                representation += "Colony ({},{}): {},{},{}\n".format(1+y,1+x,N,M,round(M/N,2))
        representation += "\nPopulation size in the whole lattice (N, M, M/N): {},{},{}\n".format(self.totalActiveSize, self.totalDormantSize, round(self.totalDormantSize/self.totalActiveSize,2))
        return representation
        
    def runSimulation(self):
        self.eventColony=None
        self.continueSimulation = True
        self.pause=True
        while self.continueSimulation:
            if self.eventColony!=None and not self.pause:
                N,M=self.pop_val(self.eventColony)
                x,y=self.data[self.eventColony]
                color_a=self.color_map(x/N)
                color_d=self.color_map(y/M)
                color_a = (round(255*color_a[0]),round(255*color_a[1]),round(255*color_a[2]))
                color_d = (round(255*color_d[0]),round(255*color_d[1]),round(255*color_d[2]))
                dataString = []
                dataString.append("Total active and dormant individuals: {}, {}".format(N,M))
                dataString.append("Seed bank strength: %.2f"%(M/N))
                dataString.append("Total Type A active individuals: {}".format(x))
                dataString.append("Total Type A dormant individuals: {}".format(y))
                self.setDataString(self.eventColony, dataString)
                self.updateColor(self.eventColony, color_a, 1)
                self.updateColor(self.eventColony, color_d, 2)
                self.clearColorMap()
                activeTypeAPercent=round((self.totalActiveTypeA)*100/self.totalActiveSize)
                dormantTypeAPercent=round((self.totalDormantTypeA)*100/self.totalDormantSize)
                self.addTickMark(activeTypeAPercent, (0, 0, 250))
                self.addTickMark(dormantTypeAPercent, (250, 0, 0))
                if (self.SAVE_FILE): self.saveScreenshot()
                self.eventColony = None
            self.continueSimulation = self.processEvent()
            pygame.display.update()
            if self.hasPopulationClustered or self.pause: continue
            coin=random.uniform(0,1)
            event_number=mUtils.sample_event([i[0] for i in self.prob_lst],coin)
            if not event_number: continue
            outcome=self.prob_lst[event_number-1]
            destin=outcome[1]
            self.eventColony=destin[0]
            active_increment, dormant_increment = destin[2]
            self.data[self.eventColony] = destin[1]
            self.totalActiveTypeA += active_increment
            self.totalDormantTypeA += dormant_increment
            self.prob_lst, self.rate=self.get_next_event()
            if (self.rate == 0):
                self.hasPopulationClustered = True
                fixatedType = "Type B (Purple)"
                if self.data[(0,0)][0] > 0: fixatedType = "Type A (Green)"
                print("Clustering occurred at frame number: {}. Fixated type: {}".format(self.frameCount, fixatedType))
                continue
            self.frameCount += 1
                
if __name__=="__main__":
    numberOfGridX = 2
    numberOfGridY = 2
    meanActiveSize = 50
    meanDormantSize = 30
    meanActiveDensity = 0.1
    meanDormantDensity = 0.9
    resampleRate = 1
    exchangeRate = 0.01
    migrationSpeed = 1
    model = geneticModel(numberOfGridX, numberOfGridY, meanActiveSize, meanDormantSize, meanActiveDensity, meanDormantDensity, resampleRate, exchangeRate, migrationSpeed)
    print(model)
    model.runSimulation()
    pygame.display.quit()