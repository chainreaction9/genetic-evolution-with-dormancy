from math import factorial as f
from matplotlib import cm
import numpy as np
from numpy.random import binomial as binom
from math import *
import random
import time,os,sys,copy
import pygame
import pyGameUtilities as pgUtils
from pyGameUtilities import SMALLFONT, BASICFONT
import mathUtilities as mUtils

class customButton():
    def __init__(self, name, handler, argList, keyID = None):
        assert type(name)==str and len(name)>1
        try:
            handler.__getattribute__('__call__')
        except: raise AssertionError('`handler` attached to this button must be callable!')
        if keyID != None: assert type(keyID)==int and keyID > 0
        self.__name = name
        self.__handler = handler
        self.__args = argList
        self.__lefttop = (0,0)
        self.__fontColor = (255, 0, 0)
        self.__bgColor = (255, 255, 0)
        self.__keyID = keyID
        self.__btnObject, self.__btnRect = pgUtils.makeText(self.__name, self.__fontColor, self.__bgColor, self.__lefttop[0], self.__lefttop[1])
    def setFontColor(self, r, g, b):
        assert type(r)==int and 0<=r<=255
        assert type(g)==int and 0<=g<=255
        assert type(b)==int and 0<=b<=255
        self.__fontColor = (r, g, b)
        self.__btnObject, self.__btnRect = pgUtils.makeText(self.__name, self.__fontColor, self.__bgColor, self.__lefttop[0], self.__lefttop[1])
    def setBackgroundColor(self, r, g, b):
        assert type(r)==int and 0<=r<=255
        assert type(g)==int and 0<=g<=255
        assert type(b)==int and 0<=b<=255
        self.__bgColor = (r, g, b)
        self.__btnObject, self.__btnRect = pgUtils.makeText(self.__name, self.__fontColor, self.__bgColor, self.__lefttop[0], self.__lefttop[1])
    def setEventHandler(self, handler, argList):
        self.__handler = handler
        self.__args = argList
    def setLeftTop(self, left, top):
        assert type(left)==int and type(top)==int
        self.__lefttop = (left, top)
        self.__btnRect.left = left
        self.__btnRect.top = top
    def setKeyID(self, keyID):
        assert type(keyID)==int and keyID > 0
        self.__keyID = keyID
    def setCenter(self, x, y):
        assert type(x)==int and type(y)==int
        self.__btnRect.center = (x,y)
        self.__lefttop = self.__btnRect.lefttop
    def draw(self, window):
        try:
            drawFunction = object.__getattribute__(window, 'blit')
            drawFunction(self.__btnObject, self.__btnRect)
        except:
            raise ValueError("window object must have `blit` attribute for drawing surface object!")
    def updateLabel(self, newID):
        assert type(newID)==str and len(newID)>2
        if newID == self.__name: return
        self.__name = newID
        self.__btnObject, self.__btnRect = pgUtils.makeText(self.__name, self.__fontColor, self.__bgColor, self.__lefttop[0], self.__lefttop[1])
        
    def getCenter(self): return self.__btnRect.center
    def getLeftTop(self): return (self.__btnRect.left, self.__btnRect.top)
    def getWidth(self): return self.__btnRect.width
    def getHeight(self): return self.__btnRect.height
    def getKeyID(self): return self.__keyID
    def invoke(self): return self.__handler(**self.__args)
    def isClicked(self, x, y):
        ''' Verifies if the button is clicked based on the mousepointer location'''
        assert type(x)==int and type(y)==int
        return self.__btnRect.collidepoint(x,y)
    
class customPyWindow():
    def __init__(self, numberOfGridX, numberOfGridY, numberOfColors = 10, colormap = 'PiYG', saveImages = False, imagePrefix = 'pic', outputFolder = 'image'):
    
        ''' Initialize default GUI parameters '''
        
        #************ Specify geographic space ***********
        #number of colonies in the x-direction
        assert type(numberOfGridX)==int and numberOfGridX > 0
        self.grid_x=numberOfGridX
        #number of colonies in the y-direction
        assert type(numberOfGridY)==int and numberOfGridY > 0
        self.grid_y=numberOfGridY # if grid_y is set to 1, the geograhpic space is one dimensional and the simulation is drawn differently.
        #number of colors in the colormap
        assert type(numberOfColors)==int and numberOfColors >= 2
        self.NUMBER_OF_COLORS = numberOfColors
        #name of the colormap (must be available in the matplotlib colormaps (see the list of all available colormaps with matplotlib.cm._colormaps())
        assert type(colormap)==str and colormap in cm._colormaps()
        self.COLOR_MAP = colormap
        #save pictures of the ongoing simulation?
        assert type(saveImages) == bool
        self.SAVE_FILE = saveImages
        #if SAVE_FILE is set to True, set prefix in the file name of each picture:
        assert type(imagePrefix)==str and len(imagePrefix) > 0
        self.FILE_PREFIX = imagePrefix
        #if SAVE_FILE is set to True, specify folder name in which pictures are saved:
        assert type(outputFolder)==str and len(outputFolder) > 0
        if self.SAVE_FILE:
            if not os.path.exists(outputFolder): os.mkdir(outputFolder)
            else:
                if os.path.isfile(outputFolder): os.mkdir(outputFolder)
        self.FOLDER_NAME = outputFolder
        
        #******************* Specify parameters for pygame GUI *********************************
        self.resolution = (400,400) #default resolution of the geograhpic space in pixel coordinates
        self.padding=(25,25) #default padding outside the windows.        
        self.width=2*self.resolution[0]+4*self.padding[0] #total width of the pygame window
        self.textBox=[self.width-2*self.padding[0],200] #resolution of the control box below the windows displaying geograhpic spaces.
        self.height=self.resolution[1]+3*self.padding[1]+self.textBox[1]+10 #total height of the pygame window
        self.totalResolution=[self.width,self.height] #final resolution of the top level pygame window.
        self.colorPadding = 10 #left and right padding (in pixels) for the color-map.
        self.colorStripHeight = 40 #height of the color-map
        self.colorResolution = self.textBox[0] - 2*self.colorPadding #width of the color-map
        self.tickHeight = self.colorStripHeight + 10 #height of the ticks showing percentage in the color-map
        self.numDivision = 10 #distance between tick marks in interval range 0% -100% (i.e., number of subdivision in the color-map)
        self.FPS=60 #frame rate per second.
        self.frameCount = 0 #counts the number of rendered frame
        self.box = (round(self.resolution[0]/self.grid_x),round(self.resolution[1]/self.grid_y)) #resolution (in pixels) of each grid
        self.__buttonList = {} # a dictionary containing all buttons
        self.__leftBottomOfButtonWindow = [self.padding[0], self.padding[1]]
        self.__allDataString = {} # a dictionary (key=colony, value=array containing (str) data) containing string data for each colony
        self.NUMBER_OF_COLORS = 10 # number of colors in color-map
        self.color_map = cm.get_cmap(self.COLOR_MAP,self.NUMBER_OF_COLORS)
        
        #******************** The following variables will be initiated by calling the `initDisplay` method of this class *************
        self.window = None #main handle to the pygame display
        self.win1 = None #handle to the first window in pygame display
        self.win2 = None #handle to the second window in pygame display
        self.win3 = None #handle to the control window in pygame display
        self.color_win = None #handle to the colormap in pygame display
    
    def get_box(self, i, reverseConversion = False):
        '''
        If the parameter `reverseConversion` is set to False (default value),
        it converts a 2D location of colony i from box coordinates (row number, column number) to pygame Rect object 
        corresponding to that colony on the pygame window.
        If `reverseConversion` is True,
        the coordinates of colony i are assumed to be in pixel coordinates and it returns the box coordinates (row number, column number)
        of the colony location.
        '''
        if not reverseConversion:
            if (i[0]<0) or (i[0]>self.grid_x) or (i[1]<0) or (i[1]>self.grid_y): return None
            return pygame.Rect(i[0]*self.box[0],i[1]*self.box[1],self.box[0],self.box[1])
        else:
            return (int(i[0]/self.box[0]),int(i[1]/self.box[1]))
            
    def addButton(self, buttonName, onclick, argList = {}, boundKeyID = None):
        '''
        Adds a pygame button in the control window.
        @param buttonName: name of the button (must be unique)
        @param onclick: a callback function which is invoked when the button is clicked.
        @argList: a dictionary containing all the arguments of the `onclick` callback. It is passed to `onclick` when the callback is called.
        @boundKeyID: pygame key ID to which this button is bound. (i.e., if that key is pressed, the callback attached to this button will be called)
        '''
        if buttonName in self.__buttonList: raise ValueError("A button with name `{}` already exists!".format(buttonName))
        btnObject = customButton(buttonName, onclick, argList)
        w = btnObject.getWidth()
        h = btnObject.getHeight()
        leftCoordinate = self.__leftBottomOfButtonWindow[0]
        topCoordinate = 0
        for btnId, btnHandle in self.__buttonList.items():
            keyID = btnHandle.getKeyID()
            if keyID and boundKeyID == keyID:
                raise AssertionError("A button `{}` is already attached to the given `boundKeyID`={}".format(btnID, boundKeyID))
            currentW = btnHandle.getWidth()
            currentH = btnHandle.getHeight()
            if currentH > h: h = currentH
            leftCoordinate += currentW + self.padding[1]
            if leftCoordinate + w > self.textBox[0]:
                leftCoordinate = self.__leftBottomOfButtonWindow[0]
                topCoordinate += round(0.5 * self.padding[1] + h)
        if boundKeyID: btnObject.setKeyID(boundKeyID)
        btnObject.setLeftTop(leftCoordinate, topCoordinate)
        btnObject.setFontColor(0, 0, 230)
        btnObject.setBackgroundColor(150, 150, 180)
        self.__buttonList[buttonName] = btnObject
        self.__leftBottomOfButtonWindow[1] = topCoordinate + h + 10
    def updateButtonList(self):
        if not self.win3: return
        pygame.draw.rect(self.win3, (255, 255, 255), (self.__leftBottomOfButtonWindow[0], 0, self.textBox[0], self.__leftBottomOfButtonWindow[1]))
        for btnID, btnHandle in self.__buttonList.items(): btnHandle.draw(self.win3)
    def updateButtonLabel(self, btnID, newID):
        assert type(btnID)==str and len(btnID) > 1 and type(newID)==str and len(newID)>1
        assert btnID in self.__buttonList and newID not in self.__buttonList
        oldButtonHandle = self.__buttonList[btnID]
        oldButtonHandle.updateLabel(newID)
        self.__buttonList.pop(btnID)
        self.__buttonList[newID]=oldButtonHandle
        self.updateButtonList()
    def createColorMap(self):
        dt=0.0
        rect=pygame.Rect(0,0,1,self.colorStripHeight)
        dvd=self.colorResolution*self.numDivision/100
        currentDiv = 0
        pygame.draw.line(self.win3,(0,0,0),(self.colorPadding, self.textBox[1]),(self.colorPadding, self.textBox[1]-self.tickHeight))
        temp_txt,temp_rect=pgUtils.makeText("%d%%"%(currentDiv,),(0,0,0),(255,255,255),0,0,SMALLFONT)
        temp_rect.center=(self.colorPadding,self.textBox[1] - self.tickHeight - 5)
        self.win3.blit(temp_txt,temp_rect)
        for l in range(0, self.colorResolution):
            rect.topleft=(self.colorPadding+l,self.textBox[1]-self.colorStripHeight)
            color_a = self.color_map(dt)
            color_a = (round(255*color_a[0]),round(255*color_a[1]),round(255*color_a[2]))
            self.win3.fill(color_a,rect)
            dt += 1/self.colorResolution
            if (l//dvd != currentDiv):
                currentDiv = l//dvd
                pygame.draw.line(self.win3,(0,0,0),(self.colorPadding+currentDiv*dvd,self.textBox[1]),(self.colorPadding+currentDiv*dvd,self.textBox[1]-self.tickHeight))
                temp_txt,temp_rect=pgUtils.makeText("%d%%"%(self.numDivision*currentDiv,),(0,0,0),(255,255,255),0,0,SMALLFONT)
                temp_rect.center=(self.colorPadding+currentDiv*dvd,self.textBox[1]-self.tickHeight-5)
                self.win3.blit(temp_txt,temp_rect)
        pygame.draw.line(self.win3,(0,0,0),(self.colorPadding+self.colorResolution,self.textBox[1]),(self.colorPadding+self.colorResolution,self.textBox[1]-self.tickHeight))
        temp_txt,temp_rect=pgUtils.makeText("%d%%"%(100,),(0,0,0),(255,255,255),0,0,SMALLFONT)
        temp_rect.center=(self.colorPadding+self.colorResolution,self.textBox[1]-self.tickHeight-5)
        self.win3.blit(temp_txt,temp_rect)
        self.color_win=self.win3.subsurface((self.colorPadding,self.textBox[1]-100,self.textBox[0]-2*self.colorPadding,100)).copy()
    
    def clearColorMap(self):
        if (self.color_win and self.win3):
            self.win3.blit(self.color_win,(self.colorPadding,self.textBox[1]-100,self.textBox[0]-2*self.colorPadding,100))
            
    def addTickMark(self, tickValue, tickColor = (0, 0, 255), percentage = True):
        '''
        Draws a tickmark with label `tickValue %` in the colormap at position corresponding to the tickValue.
        @param tickValue: a percentage value where the tickmark is added.
        @tickColor: color of the tickmark (in rgb)
        @param percentage: a boolean flag to indicate if tickValue is in percentage or is a probability (between 0-1)
        '''
        if percentage:
            assert (type(tickValue)==int or type(tickValue)==float) and 0 <= tickValue <= 100
        else:
            assert (type(tickValue)==int or type(tickValue)==float) and 0 <= tickValue <= 1
        assert len(tickColor)==3
        assert 0 <= tickColor[0] <= 255 and 0 <= tickColor[1] <= 255 and 0 <= tickColor[2] <= 255
        tickValuePercentage = tickValue if percentage else 100 * tickValue
        tickValueFloat = tickValuePercentage / 100.0
        tickValueInteger = round(tickValuePercentage)
        locationX = round(self.colorPadding+(self.textBox[0]-2*self.colorPadding)*tickValueFloat)
        locationY = self.textBox[1]-self.tickHeight-10
        pygame.draw.line(self.win3, tickColor,(locationX, locationY), (locationX, locationY + self.tickHeight + 10), 2)
        temp_txt,temp_rect=pgUtils.makeText("%d%%"%(tickValueInteger,),(0,0,0),(255,255,255),0,0,SMALLFONT)
        temp_rect.center=(locationX, locationY - 5)
        self.win3.blit(temp_txt,temp_rect)
        
    def setLabelOfFirstWindow(self, label, fontSize = 12, fontColor = (0,0,250), backgroundColor = (255,255,255)):
        assert type(label)==str and type(fontSize)==int
        assert len(fontColor)==3 and len(backgroundColor)==3
        assert 0 <= fontColor[0] <=255 and 0 <= fontColor[1] <=255 and 0 <= fontColor[2] <=255
        assert 0 <= backgroundColor[0] <=255 and 0 <= backgroundColor[1] <=255 and 0 <= backgroundColor[2] <=255
        tmpTxt,tmpRect=pgUtils.makeText(label,fontColor,backgroundColor,0,0,pygame.font.Font("freesansbold.ttf",fontSize))
        tmpRect.center=(round(self.padding[0]+self.resolution[0]/2),round(self.padding[1]+self.resolution[1]+self.padding[1]/2+5))
        self.window.blit(tmpTxt,tmpRect)
        
    def setLabelOfSecondWindow(self, label, fontSize = 12, fontColor = (0,0,250), backgroundColor = (255,255,255)):
        assert type(label)==str and type(fontSize)==int
        assert len(fontColor)==3 and len(backgroundColor)==3
        assert 0 <= fontColor[0] <=255 and 0 <= fontColor[1] <=255 and 0 <= fontColor[2] <=255
        assert 0 <= backgroundColor[0] <=255 and 0 <= backgroundColor[1] <=255 and 0 <= backgroundColor[2] <=255
        tmpTxt,tmpRect=pgUtils.makeText(label,fontColor,backgroundColor,0,0,pygame.font.Font("freesansbold.ttf",fontSize))
        tmpRect.center=(round(3*self.padding[0]+3*self.resolution[0]/2),round(self.padding[1]+self.resolution[1]+self.padding[1]/2+5))
        self.window.blit(tmpTxt,tmpRect)
    
    def updateColor(self, i, color, windowNumber=1):
        '''
        Updates the color of the grid in window `windowNumber`  corresponding to colony i
        @param i: box coordinates (row number, column number) of colony i. Row and column counting starts at 0.
        @param color: RGB value of the color
        @windowNumber: number of window (value: 1 or 2)
        '''
        assert len(i)==2 and len(color)==3 and windowNumber in [1,2]
        assert type(i[0])==int and 0 <= i[0] <= self.grid_x - 1
        assert type(i[1])==int and 0 <= i[1] <= self.grid_y - 1
        assert type(color[0])==int and 0 <= color[0] <= 255
        assert type(color[1])==int and 0 <= color[1] <= 255
        assert type(color[2])==int and 0 <= color[2] <= 255
        rect_box = self.get_box(i)
        windowList = [self.win1, self.win2]
        if rect_box:
            center=rect_box.center
            rect_box.width = rect_box.width - 1
            rect_box.height = rect_box.height - 1
            rect_box.center=center
            windowList[windowNumber - 1].fill(color,rect_box)
            
    def saveScreenshot(self):
        if not self.window: return False
        copy_window = self.window.copy()
        for btnID, btnHandle in self.__buttonList.items():
            left, top = btnHandle.getLeftTop()
            w = btnHandle.getWidth()
            h = btnHandle.getHeight()
            pygame.draw.rect(copy_window,(255,255,255),(left, top, w, h))
        copy_window.fill((255,255,255),pygame.Rect(self.__leftBottomOfButtonWindow[0], 2*self.padding[0]+self.resolution[1],round(0.5*self.owin_3.width),self.owin_3.height-self.color_win.get_rect().height))
        #copy_window.fill((255,255,255),pygame.Rect(self.padding[0]+5,15+2*self.padding[0]+self.resolution[1],300,110))
        pygame.image.save(copy_window,"./%s/%s-%d.png"%(self.FOLDER_NAME,self.FILE_PREFIX,self.frameCount))
        return True
        
    def setSaveImageFlag(self, flagValue):
        assert type(flagValue)==bool
        self.SAVE_FILE=flagValue
        if self.SAVE_FILE:
            if not os.path.exists(outputFolder): os.mkdir(outputFolder)
            else:
                if os.path.isfile(outputFolder): os.mkdir(outputFolder)
        
    def initDisplay(self, title = "Multi colony model", labelOfFirstWindow = "Window 1", labelOfSecondWindow = "Window 2"):
        if not pygame.get_init(): pygame.init()
        pygame.display.set_caption(title)
        self.window=pygame.display.set_mode(self.totalResolution) #main handle to the pygame window
        self.clock=pygame.time.Clock()
        
        win_1=pygame.Rect((0,0,self.resolution[0]+2,self.resolution[0]+2))
        win_1.center=(int(self.padding[0]+self.resolution[0]/2+1),int(1+self.padding[1]+self.resolution[1]/2))
        win_2=pygame.Rect((0,0,self.resolution[0]+2,self.resolution[1]+2))
        win_2.center=(int(2+2*self.padding[0]+self.resolution[0]+1+self.padding[0]+self.resolution[0]/2),int(1+self.padding[1]+self.resolution[1]/2))
        win_3=pygame.Rect((self.padding[0],self.resolution[1]+2*self.padding[1]+10,self.textBox[0],self.textBox[1]))
        self.owin_1=win_1.copy()
        self.owin_2=win_2.copy()
        self.owin_3=win_3.copy()
        center=self.owin_1.center
        self.owin_1.height=win_1.height-2; self.owin_1.width=win_1.width-2; self.owin_1.center=center
        center=self.owin_2.center
        self.owin_2.height=win_2.height-2; self.owin_2.width=win_2.width-2; self.owin_2.center=center
        self.win1=self.window.subsurface(self.owin_1)
        self.win2=self.window.subsurface(self.owin_2)
        self.win3=self.window.subsurface(win_3)
        self.window.fill((255,255,255))
        self.createColorMap()
        self.setLabelOfFirstWindow(labelOfFirstWindow)
        self.setLabelOfSecondWindow(labelOfSecondWindow)
        for x in range(1,self.grid_x):
            pygame.draw.line(self.window,(170,170,170),(self.owin_1.topleft[0]+x*self.box[0],self.owin_1.topleft[1]),(self.owin_1.topleft[0]+x*self.box[0],self.owin_1.topleft[1]+self.resolution[1]))
            pygame.draw.line(self.window,(170,170,170),(self.owin_2.topleft[0]+x*self.box[0],self.owin_2.topleft[1]),(self.owin_2.topleft[0]+x*self.box[0],self.owin_2.topleft[1]+self.resolution[1]))
        
        for y in range(1,self.grid_y):
            pygame.draw.line(self.window,(170,170,170),(self.owin_1.topleft[0],self.owin_1.topleft[1]+y*self.box[1]),(self.owin_1.topleft[0]+self.resolution[0],self.owin_1.topleft[1]+y*self.box[1]))
            pygame.draw.line(self.window,(170,170,170),(self.owin_2.topleft[0],self.owin_2.topleft[1]+y*self.box[1]),(self.owin_2.topleft[0]+self.resolution[0],self.owin_2.topleft[1]+y*self.box[1]))
        
        for btnID, btnHandle in self.__buttonList.items(): btnHandle.draw(self.win3)
    def setDataString(self, i, dataString):
        '''
           Stores an array containing information about colony i
        '''
        assert len(i)==2 and type(i[0])==int and 0 <= i[0] <= self.grid_x - 1
        assert type(i[1])==int and 0 <= i[1] <= self.grid_y - 1
        self.__allDataString[(i[0],i[1])] = tuple(dataString)
    
    def showData(self, i, dataString=None, fontSize=14):
        '''
        Displays the current data associated to colony i
        '''
        assert len(i)==2 and type(i[0])==int and 0 <= i[0] <= self.grid_x - 1
        assert type(i[1])==int and 0 <= i[1] <= self.grid_y - 1
        dataToBeShown = dataString if dataString else self.__allDataString.get((i[0],i[1]))
        if not dataToBeShown: return
        self.win3.fill((255,255,255),pygame.Rect(self.__leftBottomOfButtonWindow[0], self.__leftBottomOfButtonWindow[1],self.owin_3.width-self.__leftBottomOfButtonWindow[0]+5,self.owin_3.height-self.color_win.get_rect().height))
        locationX = self.__leftBottomOfButtonWindow[0]+10
        locationY = self.__leftBottomOfButtonWindow[1]
        tmpSurf,tmpRect=pgUtils.makeText("Colony: (%d,%d)"%(1+i[1], 1+i[0]),(255,0,0),(255,255,255), locationX, locationY, pygame.font.Font("freesansbold.ttf",fontSize))
        self.win3.blit(tmpSurf,tmpRect)
        for entry in dataToBeShown:
            assert type(entry)==str
            locationY += tmpRect.height + 5
            tmpSurf,tmpRect=pgUtils.makeText(entry,(255,0,0),(255,255,255), locationX, locationY,pygame.font.Font("freesansbold.ttf", fontSize))
            self.win3.blit(tmpSurf,tmpRect)
            
    def processEvent(self):
        for event in pygame.event.get():
            if event.type==pygame.QUIT: return False
            elif event.type==pygame.MOUSEBUTTONUP:
                x,y=event.pos
                if self.owin_3.collidepoint(x,y): # possibly a button is clicked
                    x -= self.owin_3.left
                    y -= self.owin_3.top
                    allButtons = list(self.__buttonList.keys())
                    for btnID in allButtons:
                        btnHandle = self.__buttonList[btnID]
                        if btnHandle.isClicked(x,y):
                            btnHandle.invoke()
                            break
                else: # possibly a colony is clicked
                    windowList = [self.owin_1, self.owin_2]
                    for win in windowList:
                        x,y=event.pos
                        if win.collidepoint(x,y):
                            x -= win.left
                            y -= win.top
                            clickedColony = self.get_box((x,y),True)
                            if clickedColony:
                                self.showData(clickedColony, fontSize=10)
            elif event.type==pygame.KEYUP:
                for btnID, btnHandle in self.__buttonList.items():
                    if btnHandle.getKeyID() == event.key:
                        btnHandle.invoke()
                        break
        return True
    def updateDisplay(self):
        '''Displays random noise from colormap 'PiYG'
        '''
        totalRedColorValue = 0
        totalBlueColorValue = 0
        totalGreenColorValue = 0
        for x_index in range(self.grid_x):
            for y_index in range(self.grid_y):
                i = (x_index,y_index) #get colony location 
                randomColor1 = np.random.uniform()
                randomColor2 = np.random.uniform()
                color_a=self.color_map(randomColor1) #show a random color in each colony in the first window
                color_d=self.color_map(randomColor2) #show a random color in each colony in the second window
                color_a = (round(255*color_a[0]),round(255*color_a[1]),round(255*color_a[2]))
                totalRedColorValue += color_a[0]; totalGreenColorValue += color_a[1]; totalBlueColorValue += color_a[2]
                color_d = (round(255*color_d[0]),round(255*color_d[1]),round(255*color_d[2]))
                dataString = ["Color value at colony ({},{}) in window {}: ({},{},{}).".format(1+i[1],1+i[0], k+1, (1-k)*color_a[0] + k*color_d[0], (1-k)*color_a[1] + k*color_d[1], (1-k)*color_a[2] + k*color_d[2]) for k in range(2)]
                self.setDataString(i, dataString)
                self.updateColor(i, color_a, 1)
                self.updateColor(i, color_d, 2)
        totalRedPercentage = round(100 * totalRedColorValue /(255 * (self.grid_x * self.grid_y)))
        totalGreenPercentage = round(100 * totalGreenColorValue /(255 * (self.grid_x * self.grid_y)))
        totalBluePercentage = round(100 * totalBlueColorValue /(255 * (self.grid_x * self.grid_y)))
        self.clearColorMap()
        self.win3.fill((round(totalRedPercentage*255/100),round(totalGreenPercentage*255/100),round(totalBluePercentage*255/100)),pygame.Rect(self.__leftBottomOfButtonWindow[0]+self.resolution[0], self.__leftBottomOfButtonWindow[1],self.owin_3.width-self.__leftBottomOfButtonWindow[0]+5-self.resolution[0],self.owin_3.height-self.color_win.get_rect().height))
        self.addTickMark(totalRedPercentage, (255, 0, 0))
        self.addTickMark(totalGreenPercentage, (0, 255, 0))
        self.addTickMark(totalBluePercentage, (0, 0, 255))
        self.frameCount += 1
        
    def tick(self): self.clock.tick(self.FPS)
if __name__=="__main__":
    savePictures = False #save screenshots on local directory?
    guiWindow = customPyWindow(25, 25)
    guiWindow.initDisplay()
    guiWindow.addButton("Start", lambda : print("Start button clicked!"), {})
    guiWindow.addButton("Reset", lambda : print("Reset button clicked!"), {})
    guiWindow.updateButtonList()
    continueSimulation = True
    while continueSimulation:
        guiWindow.updateDisplay()
        if savePictures: guiWindow.saveScreenshot()
        continueSimulation = guiWindow.processEvent()
        pygame.display.update()
        guiWindow.tick()
    pygame.display.quit()