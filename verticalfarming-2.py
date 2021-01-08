#################################################
# Vertical Farming Simulation
#
# Nathalie Jeans
# Andrew ID: njeans
#################################################

from cmu_112_graphics import *
# source: http://www.cs.cmu.edu/~112/notes/notes-animations-part1.html
import tkinter as tk
import random, string, copy, math, time
import PIL
import requests

# HOME PAGE MODE
# Purpose: Beginning screen and introduction
# Begin button remembers and updates progress from last time
# Plants will have grown in the background while app is closed
class Homepage(Mode):
    def appStarted(mode):
        mode.textHeight = -100 
        mode.timerDelay = 1
        # all image code adapted from: 
        # http://www.cs.cmu.edu/~112/notes/notes-animations-part3.html#flipImage
        mode.image1 = mode.scaleImage(mode.loadImage('background-2.jpg'), 1/6.25)
        # mode.image1 from https://unsplash.com/photos/Rfe8w1FRM4U
        mode.plantPic = mode.loadImage('plant.png')
        # # source: https://gallery.yopriceville.com/Free-Clipart-Pictures/Spring-PNG/Small_Plant_PNG_Clipart
        mode.cabbagePic = mode.loadImage('cabbage.png')
        # source: http://www.pngall.com/cabbage-png
        mode.flowerPic = mode.loadImage('flower.png')
        # source: https://www.cleanpng.com/png-mexican-marigold-plant-flower-clip-art-flower-tree-761230/
        mode.rosePic = mode.loadImage('rose.png')
        # source: http://clipart-library.com/clipart/6Tp5EXo6c.htm
        mode.tropicPic = mode.loadImage('tropic.png')
        # source: https://www.deviantart.com/gareng92/art/Clear-cut-PNG-TROPICAL-PLANT-5-802444100
        mode.timeDifference = 0

    def mousePressed(mode, event):
        (x, y) = (event.x, event.y)
        if (x >=400 and x<=550) and (y>=400 and y<=450):
            mode.app.setActiveMode(mode.app.PlantingMode)
            mode.start()
            print('Saved!')

    # how to read from files from:
    # source: https://realpython.com/read-write-files-python/#opening-and-closing-a-file-in-python
    # getting the information from the text file
    def start(mode):
        with open('settings.txt', 'r') as readingfile:
            # order --> time, data (use readPlanterData), $, money, plantBought, planterBought
            listOfFile = readingfile.read().splitlines()
            prevtime = listOfFile[0]
            mode.timeDifference = time.time()-float(prevtime)

            # finding the lines where our data is for plants/planters
            endOfData = 0
            for i in range(len(listOfFile)):
                if listOfFile[i] == '$ ':
                    endOfData = i
                    break
            data = ''
            for line in range(1, endOfData):
                data += f'{listOfFile[line]}\n'

            # finding the lines from the text file where our data is the points list
            endOfPointData = 0
            for i in range(len(listOfFile)):
                if listOfFile[i] == '%':
                    endOfPointData = i
                    break
            pointData = ''
            for line in range(endOfData+13, endOfPointData):
                pointData += f'{listOfFile[line]}\n'
            
            User.plantsInPlanterList = mode.readPlanterData(data)
            User.money = int(listOfFile[endOfData+1])
            User.plantBought = int(listOfFile[endOfData+2])
            User.planterBought = int(listOfFile[endOfData+3])
            User.cabbageBought = int(listOfFile[endOfData+4])
            User.plantHarvested = int(listOfFile[endOfData+5])
            User.cabbageHarvested = int(listOfFile[endOfData+6])
            User.flowerBought = int(listOfFile[endOfData+7])
            User.flowerHarvested = int(listOfFile[endOfData+8])
            User.roseBought = int(listOfFile[endOfData+9])
            User.roseHarvested = int(listOfFile[endOfData+10])
            User.tropicBought = int(listOfFile[endOfData+11])
            User.tropicHarvested = int(listOfFile[endOfData+12])
            User.pointsList = mode.readCoordinateData(pointData)
    
    # getting the information from the textfile about the plants
    def readPlanterData(mode, data):
        newPlanterList = []
        stuff = data.splitlines()
        for planterData in stuff:
            numFish = int(planterData.split(' ')[-1])
            newPlantList = []
            for plantData in planterData.split(' ')[:-1]:
                if plantData != 'None':
                    plantStats = plantData.split(',')
                    newPlant = Plant(mode,plantStats[0],float(plantStats[1]))
                    newPlantList += [newPlant]
                else:
                    newPlantList += [None]
            planter = Planter()
            
            # must multiply the size by some increment of the time
            # and call the grow() function to make up for lost time
            for plant in newPlantList:
                for i in range(int(mode.timeDifference//(10**7))):
                    plant.grow()

            planter.plants = newPlantList
            planter.numFish = numFish
            newPlanterList += [planter]
        return newPlanterList
    
    # getting the information from the textfile about the points on the graph
    # transforming it into a format that we can use
    def readCoordinateData(mode, data):
        newCoordList = []
        stuff = data.splitlines()
        for pointData in stuff:
            y = int(pointData.split(' ')[1])
            x = int(pointData.split(' ')[0])
            newCoordList.append([x, y])
        return newCoordList

    def timerFired(mode):
        if mode.textHeight < 200:
            mode.textHeight += 10

    def drawHomepage(mode, canvas):
        canvas.create_image(500, 350, image=ImageTk.PhotoImage(mode.image1))
        text1 = "VERTICAL FARMING SIMULATION"
        text2 = "Explore aquaponic systems."
        text3 = "Grow and sell plants in real time."
        canvas.create_text(mode.width//2, mode.textHeight, fill='white', \
                text=text1, font='Lato 40 bold')
        canvas.create_text(mode.width//2, mode.textHeight+50, fill='white', \
                text=text2, font='Lato 30 italic')
        canvas.create_text(mode.width//2, mode.textHeight+85, fill='white', \
                text=text3, font='Lato 30 italic')
    
    def redrawAll(mode, canvas):
        mode.drawHomepage(canvas)
        canvas.create_rectangle(400, 400, 550, 450, width=0, fill='white')
        canvas.create_text(475, 425, text='BEGIN', font='Lato 16 bold italic')

# PLANTING MODE
# This page is the garden: where your plants are located, where you can grow them,
# harvest them, plant them, etc.
class PlantingMode(Mode):
    def appStarted(mode):
        mode.counter = 0
        mode.plantingBckgnd = mode.scaleImage(mode.loadImage('brickwall-2.jpg'), 1/5)
        # brick wall source: https://unsplash.com/photos/t4DuoDHjxrQ
        mode.boxPlanter = mode.scaleImage(mode.loadImage('fishtank2.png'), 1/2.7)
        # fish tank from: fish tank from https://moolashore.com/submerged-in-water/
        mode.plantPic = mode.scaleImage(mode.loadImage('plant.png'), 1/3)
        # source: https://gallery.yopriceville.com/Free-Clipart-Pictures/Spring-PNG/Small_Plant_PNG_Clipart
        mode.cabbagePic = mode.scaleImage(mode.loadImage('cabbage.png'), 1)
        # source: http://www.pngall.com/cabbage-png
        # setting the margin values
        mode.sideMargin = 50
        mode.topMargin = 20
        mode.bottomMargin = 5
        # initializing the shelf
        mode.shelfHeight = mode.height/3-mode.topMargin-mode.bottomMargin
        mode.shelfWidth = mode.width/3-mode.sideMargin
        mode.shelfCenter = mode.shelfWidth/2
        mode.cols = mode.rows = 3
        mode.water = mode.scaleImage(mode.loadImage('underwater-2.jpg'), 1/10)
        # initializing the fish
        mode.fishPic = mode.scaleImage(mode.loadImage('fish.png'), 1/50)
        mode.flipFishPic = mode.fishPic.transpose(Image.FLIP_LEFT_RIGHT)
        # plant and cabbage pictures are cited above
        mode.plantPic = mode.loadImage('plant.png')
        mode.cabbagePic = mode.loadImage('cabbage.png')
        mode.flowerPic = mode.loadImage('flower.png')
        # source: https://www.cleanpng.com/png-mexican-marigold-plant-flower-clip-art-flower-tree-761230/
        mode.rosePic = mode.loadImage('rose.png')
        # source: http://clipart-library.com/clipart/6Tp5EXo6c.htm
        mode.tropicPic = mode.loadImage('tropic.png')
        # source: https://www.deviantart.com/gareng92/art/Clear-cut-PNG-TROPICAL-PLANT-5-802444100

# initializes the number of fish needed depending on the tank that you clicked
# these variables will be accessed in the Aquaponics Mode section
    def initFishScreen(mode):
        mode.margin = 100 # tank margin
        mode.fish = []
        mode.xTankTopLeft = (mode.width/2)-350
        mode.yTankTopLeft = (mode.height/2)-200
        mode.xTankBottomRight = (mode.width/2)+350
        mode.yTankBottomRight = (mode.height/2)+200
        mode.numFishInTank = User.plantsInPlanterList[User.tankNum].numFish

        for i in range(mode.numFishInTank):
            Fish.addFish(mode)

    def keyPressed(mode, event):
        if event.key.isdigit(): # accessing the individual tanks to add fish
            if (int(event.key) <= len(User.plantsInPlanterList)):
                User.tankNum = int(event.key)
                mode.initFishScreen()
                mode.app.setActiveMode(mode.app.AquaponicsMode)

        elif (event.key=='p'):
            if User.planterBought > 0:
                planter1 = Planter()
                User.plantsInPlanterList.append(planter1)
                User.planterBought -= 1
        elif (event.key == 'a'):
            if User.plantBought > 0:
                mode.addToPlanter('plant')
                User.plantBought -= 1
        elif (event.key == 'c'):
            if User.cabbageBought > 0:
                mode.addToPlanter('cabbage')
                User.cabbageBought -= 1
        elif (event.key == 'f'):
            if User.flowerBought > 0:
                mode.addToPlanter('flower')
                User.flowerBought -= 1
        elif (event.key == 'o'):
            if User.roseBought > 0:
                mode.addToPlanter('rose')
                User.roseBought -= 1
        elif (event.key == 'i'):
            if User.tropicBought > 0:
                mode.addToPlanter('tropic')
                User.tropicBought -= 1
        # remove plant
        elif (event.key == 'r'):
            for planter in User.plantsInPlanterList:
                for plant in planter.plants:
                    if plant != None:
                        if plant.name == 'plant':
                            mode.removeFromPlanter('plant')
                            User.plantHarvested += 1
                            return 'end the function'
        # remove cabbage
        elif (event.key == 't'):
            for planter in User.plantsInPlanterList:
                for cabbage in planter.plants:
                    if cabbage != None:
                        if cabbage.name == 'cabbage':
                            mode.removeFromPlanter('cabbage')
                            User.cabbageHarvested += 1
                            return 'end the function'
        # remove flower
        elif (event.key == 'w'):
            for planter in User.plantsInPlanterList:
                for flower in planter.plants:
                    if flower != None:
                        if flower.name == 'flower':
                            mode.removeFromPlanter('flower')
                            User.flowerHarvested += 1
                            return 'end the function'
        # remove rose
        elif (event.key == 's'):
            for planter in User.plantsInPlanterList:
                for rose in planter.plants:
                    if rose != None:
                        if rose.name == 'rose':
                            mode.removeFromPlanter('rose')
                            User.roseHarvested += 1
                            return 'end the function'
        # remove tropic
        elif (event.key == 'k'):
            for planter in User.plantsInPlanterList:
                for tropic in planter.plants:
                    if tropic != None:
                        if tropic.name == 'tropic':
                            mode.removeFromPlanter('tropic')
                            User.tropicHarvested += 1
                            return 'end the function'

    def mousePressed(mode, event):
        (x, y) = (event.x, event.y)
        if (x >=(mode.width-175) and x<=mode.width) and (y>=250 and y<=350):
            mode.app.setActiveMode(mode.app.MarketplaceMode)
        elif (x >=(mode.width-175) and x<=mode.width) and (y>=350 and y<=450):
            mode.app.setActiveMode(mode.app.GraphAnalysisMode)
        elif (x >=(mode.width-175) and x<=mode.width) and (y>=450 and y<=550):
            User.save()
            # add temporary message HERE about saving

    # adds plant of any type to a planter
    def addToPlanter(mode, plant):
        for planter in User.plantsInPlanterList:
            if None in planter.plants:
                planter.addPlant(mode,plant)
                break
    
    # removes plant of any type to a planter
    def removeFromPlanter(mode,name):
        for planter in User.plantsInPlanterList:
            for plant in planter.plants:
                if plant != None:
                    if plant.name == name:
                        planter.removePlant(plant.name)
                        return None

    # drawing the fish tanks on thr garden screen
    def drawPlanters(mode,canvas):
        row = 0
        col = 0
        for planter in User.plantsInPlanterList:
            (x,y) = mode.getCenterXY(row,col)
            planter.drawPlanter(mode,canvas,x,y)
            col += 1
            if col == mode.cols:
                col = 0
                row += 1

    # center location of the planter based on row and column
    def getCenterXY(mode, row, col):
        x = mode.shelfCenter+(mode.shelfWidth*row)
        y = mode.shelfHeight/2+(mode.shelfHeight*col)+40
        return (x, y)
    
    def timerFired(mode):
        if mode.counter % (100) == 0:
            for planter in User.plantsInPlanterList:
                for plant in planter.plants:
                    if plant != None:
                        plant.grow()
        mode.counter += 1

    def redrawAll(mode, canvas):
        canvas.create_image(mode.width/2, mode.height/2, image=ImageTk.PhotoImage(mode.plantingBckgnd))

        # drawing the menu
        canvas.create_rectangle(mode.width-175, 85, mode.width, 150, fill='black')
        canvas.create_rectangle(mode.width-175, 150, mode.width, 250, fill=rgbString(155, 184, 167)) # money balance
        canvas.create_rectangle(mode.width-175, 250, mode.width, 350, fill=rgbString(123, 146, 133)) # marketplace
        canvas.create_rectangle(mode.width-175, 350, mode.width, 450, fill=rgbString(90, 109, 98)) # graph analysis
        canvas.create_rectangle(mode.width-175, 450, mode.width, 550, fill=rgbString(55, 65, 59)) # save progress
        # drawing the shelves
        for i in range(1,4):
            canvas.create_line(0, mode.shelfHeight*i, mode.width-200, mode.shelfHeight*i, width=10)
        # drawing the planters
        mode.drawPlanters(canvas)
        # writing the menu
        canvas.create_text(mode.width-90, 120, text=f'MENU', font="Lato 30 bold italic", fill='white')
        canvas.create_text(mode.width-90, 200, text=f'${User.money} BALANCE', font="Lato 15 bold", fill='white') # money balance
        canvas.create_text(mode.width-90, 300, text=f'MARKETPLACE', font="Lato 15 bold", fill='white') # marketplace
        canvas.create_text(mode.width-90, 400, text=f'PROFIT ANALYSIS', font="Lato 15 bold", fill='white') # graph analysis
        canvas.create_text(mode.width-90, 500, text=f'SAVE PROGRESS', font="Lato 15 bold", fill='white') # save progress
        # displaying personal inventory
        canvas.create_rectangle(0, mode.height-50, mode.width, mode.height, fill='black')
        canvas.create_rectangle(0, mode.height-50, mode.width/2, mode.height, fill=rgbString(55, 65, 59))
        # labels
        canvas.create_rectangle(10, (mode.height-50)-10, 90, (mode.height-50)+10, fill='pink')
        canvas.create_rectangle((mode.width/2)+10, (mode.height-50)-10, (mode.width/2)+90, (mode.height-50)+10, fill='pink')
        canvas.create_text(50, mode.height-50, text='BOUGHT', fill='black')
        canvas.create_text((mode.width/2)+50, mode.height-50, text='HARVESTED', fill='black')

        canvas.create_text(50, mode.height-25, text=f'Planters: {User.planterBought}', fill='white',font="Lato 10 bold")
        canvas.create_text(130, mode.height-25, text=f'Plants: {User.plantBought}', fill='white', font="Lato 10 bold")
        canvas.create_text(210, mode.height-25, text=f'Cabbages: {User.cabbageBought}', fill='white', font="Lato 10 bold")
        canvas.create_text(300, mode.height-25, text=f'Flower: {User.flowerBought}', fill='white', font="Lato 10 bold")
        canvas.create_text(380, mode.height-25, text=f'Rose: {User.roseBought}', fill='white', font="Lato 10 bold")
        canvas.create_text(460, mode.height-25, text=f'Tropic: {User.tropicBought}', fill='white', font="Lato 10 bold")
        canvas.create_text(560, mode.height-25, text=f'Plants: {User.plantHarvested}', fill='white', font="Lato 10 bold")
        canvas.create_text(650, mode.height-25, text=f'Cabbages: {User.cabbageHarvested}', fill='white', font="Lato 10 bold")
        canvas.create_text(740, mode.height-25, text=f'Flower: {User.flowerBought}', fill='white', font="Lato 10 bold")
        canvas.create_text(830, mode.height-25, text=f'Rose: {User.roseBought}', fill='white', font="Lato 10 bold")
        canvas.create_text(920, mode.height-25, text=f'Tropic: {User.tropicBought}', fill='white', font="Lato 10 bold")    
        # showing the planter numbers
        for i in range(0,3):
            canvas.create_text(30, 50+(i*mode.shelfHeight), text=i ,fill='white', font='Lato 14 bold')
        for num in range(3,6):
            canvas.create_text(320, 50+((num-3)*mode.shelfHeight), text=num ,fill='white', font='Lato 14 bold')
        for k in range(6,9):
            canvas.create_text(610, 50+((k-6)*mode.shelfHeight), text=k ,fill='white', font='Lato 14 bold')

# AQUAPONICS MODE
# This is the mode where any fish tank chosen (as specified in the planting mode)
# is initialized – you can add fish which will be added also in your garden
# when you go back to the garden page
class AquaponicsMode(Mode):
    def appStarted(mode):
        # image code from
        # http://www.cs.cmu.edu/~112/notes/notes-animations-part3.html#flipImage
        mode.water = mode.scaleImage(mode.loadImage('underwater-2.jpg'), 1/3)
        # underwater picture from: https://moolashore.com/submerged-in-water/
        mode.boxPlanter = mode.scaleImage(mode.loadImage('fishtank2.png'), 1.3)
        # fish tank from https://moolashore.com/submerged-in-water/
        mode.fishPic = mode.scaleImage(mode.loadImage('fish.png'), 1/18)
        # fish picture from https://www.jing.fm/iclip/whJb_tropical-fish-clipart-under-sea-fish-png/
        mode.wood = mode.scaleImage(mode.loadImage('darkwood.jpg'), 1/6)
        # wood picture from: https://unsplash.com/photos/6vvIBTvL90A
        mode.flipFishPic = mode.fishPic.transpose(Image.FLIP_LEFT_RIGHT)
    
    def timerFired(mode):
        for fish in mode.app.PlantingMode.fish:
            Fish.moveFish(fish, mode)

    def drawTank(mode, canvas):
        canvas.create_image(mode.width/2, mode.height/2, image=ImageTk.PhotoImage(mode.water))
        canvas.create_image(mode.width/2, mode.height/2, image=ImageTk.PhotoImage(mode.boxPlanter))
    
    def keyPressed(mode, event):
        if (event.key=='a'):
            Fish.addFish(mode)
            User.plantsInPlanterList[User.tankNum].numFish += 1
        elif (event.key=='1'):
            mode.app.setActiveMode(mode.app.Homepage)
        elif (event.key=='2'):
            mode.app.setActiveMode(mode.app.PlantingMode)
        elif (event.key=='4'):
            mode.app.setActiveMode(mode.app.MarketplaceMode)
        elif (event.key=='5'):
            mode.app.setActiveMode(mode.app.GraphAnalysisMode)

    def redrawAll(mode, canvas):
        canvas.create_rectangle(0,0, mode.width, mode.height, fill=rgbString(137, 184, 137))
        canvas.create_image(mode.width/2, mode.height+50, image=ImageTk.PhotoImage(mode.wood))
        mode.drawTank(canvas)
        for fish in mode.app.PlantingMode.fish:
            fish.drawFish(mode, canvas)
        canvas.create_text(mode.width/2, 65, text=f'You are currently looking at tank #{User.tankNum}', font='Lato 20 bold italic')
        canvas.create_text(mode.width/2, 90, text=f'Press 2 to return to garden.', font='Lato 20 bold italic')

# MARKETPLACE MODE
# Where you can buy and sell plants
class MarketplaceMode(Mode):

    def appStarted(mode):
        mode.plantshop = mode.scaleImage(mode.loadImage('plantshop.jpg'), 1/4)
        # background image from : https://unsplash.com/photos/hHCxKyjEk_k
        mode.plantPic = mode.scaleImage(mode.loadImage('plant.png'), 1/2) # cited in
        # source: https://gallery.yopriceville.com/Free-Clipart-Pictures/Spring-PNG/Small_Plant_PNG_Clipart
        mode.cabbagePic = mode.scaleImage(mode.loadImage('cabbage.png'), 1/2)
        # source: http://www.pngall.com/cabbage-png
        mode.planterPic = mode.scaleImage(mode.loadImage('fishtank2.png'), 1/4)
        # fish tank from: fish tank from https://moolashore.com/submerged-in-water/
        mode.flowerPic = mode.loadImage('flower.png')
        # source: https://www.cleanpng.com/png-mexican-marigold-plant-flower-clip-art-flower-tree-761230/
        mode.rosePic = mode.loadImage('rose.png')
        # source: http://clipart-library.com/clipart/6Tp5EXo6c.htm
        mode.tropicPic = mode.loadImage('tropic.png')
        # source: https://www.deviantart.com/gareng92/art/Clear-cut-PNG-TROPICAL-PLANT-5-802444100

    def mousePressed(mode, event):
        (x, y) = (event.x, event.y)
        if (x>100 and x<=200) and (y>250 and y<280): # buy planters
            User.planterBought += 1
            User.money -= 400
        elif (x>275 and x<=375) and (y>220 and y<350): # buy plants
            User.plantBought += 1
            User.money -= 20
        elif (x>275 and x<=375) and (y>270 and y<300): # sell plants
            if User.plantHarvested > 0:
                User.plantHarvested -= 1
                User.money += 30
        elif (x>650 and x<=750) and (y>220 and y<250): # buy cabbages
            User.cabbageBought += 1
            User.money -= 50
        elif (x>650 and x<=750) and (y>270 and y<300): # sell cabbages
            if User.cabbageHarvested > 0:
                User.cabbageHarvested -= 1
                User.money += 80
        # flower buy and sell
        elif (x>75 and x<=175) and (y>350 and y<380): # buy flower
            User.flowerBought += 1
            User.money -= 150
        elif (x>75 and x<=175) and (y>400 and y<430): # sell flower
            if User.flowerHarvested > 0:
                User.flowerHarvested -= 1
                User.money += 180      
        # rose buy and sell
        elif (x>350 and x<=450) and (y>350 and y<380): # buy rose
            User.roseBought += 1
            User.money -= 175
        elif (x>350 and x<=450) and (y>400 and y<430): # sell rose
            if User.roseHarvested > 0:
                User.roseHarvested -= 1
                User.money += 210
        # tropic buy and sell
        elif (x>600 and x<=700) and (y>350 and y<380): # buy tropic
            User.tropicBought += 1
            User.money -= 200
        elif (x>600 and x<=700) and (y>400 and y<430): # sell tropic
            if User.tropicHarvested > 0:
                User.tropicHarvested -= 1
                User.money += 250

        # navigating the menu
        elif (x >=(mode.width-175) and x<=mode.width) and (y>=350 and y<=450):
            mode.app.setActiveMode(mode.app.Homepage)
        elif (x >=(mode.width-175) and x<=mode.width) and (y>=450 and y<=550):
            mode.app.setActiveMode(mode.app.PlantingMode)
        elif (x >=(mode.width-175) and x<=mode.width) and (y>=550 and y<=650):
            mode.app.setActiveMode(mode.app.GraphAnalysisMode)
    
    def redrawAll(mode, canvas):
        canvas.create_image(mode.width/2, mode.height/2, image=ImageTk.PhotoImage(mode.plantshop))
        text="THE MARKETPLACE"
        canvas.create_rectangle(0, 185, mode.width-175, 650, fill=rgbString(217, 236, 234), width=0)

        # drawing another menu
        canvas.create_rectangle(mode.width-175, 185, mode.width, 250, fill='black')
        canvas.create_rectangle(mode.width-175, 250, mode.width, 350, fill=rgbString(155, 184, 167)) # money balance
        canvas.create_rectangle(mode.width-175, 350, mode.width, 450, fill=rgbString(123, 146, 133)) # home
        canvas.create_rectangle(mode.width-175, 450, mode.width, 550, fill=rgbString(90, 109, 98)) # garden
        canvas.create_rectangle(mode.width-175, 550, mode.width, 650, fill=rgbString(55, 65, 59)) # profit analysis
        canvas.create_text(mode.width-90, 220, text=f'MENU', font="Lato 30 bold italic", fill='white')
        canvas.create_text(mode.width-90, 300, text=f'${User.money} BALANCE', font="Lato 15 bold", fill='white') # money balance
        canvas.create_text(mode.width-90, 400, text=f'HOME PAGE', font="Lato 15 bold", fill='white') # home
        canvas.create_text(mode.width-90, 500, text=f'MY GARDEN', font="Lato 15 bold", fill='white') # garden
        canvas.create_text(mode.width-90, 600, text=f'PROFIT ANALYSIS', font="Lato 15 bold", fill='white') # graph analysis

        # creating the images of the products on "sale"
        # planter
        canvas.create_image(150, 250, image=ImageTk.PhotoImage(mode.planterPic))
        canvas.create_rectangle(100, 250, 200, 280, fill='black')
        canvas.create_text(150, 265, text="BUY", fill='white')
        
        # plant and location
        canvas.create_image(300, 250, image=ImageTk.PhotoImage(mode.plantPic))
        canvas.create_rectangle(375, 220, 475, 250, fill='black')
        canvas.create_text(425, 235, text="BUY", fill='white')
        canvas.create_rectangle(375, 270, 475, 300, fill='black')
        canvas.create_text(425, 285, text="SELL", fill='white')
        
        # cabbage and location
        canvas.create_image(575, 250, image=ImageTk.PhotoImage(mode.cabbagePic))
        canvas.create_rectangle(650, 220, 750, 250, fill='black')
        canvas.create_text(700, 235, text="BUY", fill='white')
        canvas.create_rectangle(650, 270, 750, 300, fill='black')
        canvas.create_text(700, 285, text="SELL", fill='white')

        # flower and location
        canvas.create_image(150, 600, image=ImageTk.PhotoImage(mode.flowerPic))
        canvas.create_rectangle(75, 350, 175, 380, fill='black')
        canvas.create_text(125, 365, text="BUY", fill='white')
        canvas.create_rectangle(75, 400, 175, 430, fill='black')
        canvas.create_text(125, 415, text="SELL", fill='white')

        # rose and location
        canvas.create_image(450, 600, image=ImageTk.PhotoImage(mode.rosePic))
        canvas.create_rectangle(350, 350, 450, 380, fill='black')
        canvas.create_text(400, 365, text="BUY", fill='white')
        canvas.create_rectangle(350, 400, 450, 430, fill='black')
        canvas.create_text(400, 415, text="SELL", fill='white')

        # tropic and location
        canvas.create_image(700, 550, image=ImageTk.PhotoImage(mode.tropicPic))
        canvas.create_rectangle(600, 350, 700, 380, fill='black')
        canvas.create_text(650, 365, text="BUY", fill='white')
        canvas.create_rectangle(600, 400, 700, 430, fill='black')
        canvas.create_text(650, 415, text="SELL", fill='white')

        # title
        canvas.create_text(mode.width-305, 100, text=text, font="Lato 40 bold italic", fill='pink')
        canvas.create_text(mode.width-300, 100, text=text, font="Lato 40 bold italic")

        # displaying personal inventory
        canvas.create_rectangle(0, mode.height-50, mode.width, mode.height, fill='black')
        canvas.create_rectangle(0, mode.height-50, mode.width/2, mode.height, fill=rgbString(55, 65, 59))
        # labels
        canvas.create_rectangle(10, (mode.height-50)-10, 90, (mode.height-50)+10, fill='pink')
        canvas.create_rectangle((mode.width/2)+10, (mode.height-50)-10, (mode.width/2)+90, (mode.height-50)+10, fill='pink')
        canvas.create_text(50, mode.height-50, text='BOUGHT', fill='black')
        canvas.create_text((mode.width/2)+50, mode.height-50, text='HARVESTED', fill='black')

        canvas.create_text(50, mode.height-25, text=f'Planters: {User.planterBought}', fill='white',font="Lato 10 bold")
        canvas.create_text(130, mode.height-25, text=f'Plants: {User.plantBought}', fill='white', font="Lato 10 bold")
        canvas.create_text(210, mode.height-25, text=f'Cabbages: {User.cabbageBought}', fill='white', font="Lato 10 bold")
        canvas.create_text(300, mode.height-25, text=f'Flower: {User.flowerBought}', fill='white', font="Lato 10 bold")
        canvas.create_text(380, mode.height-25, text=f'Rose: {User.roseBought}', fill='white', font="Lato 10 bold")
        canvas.create_text(460, mode.height-25, text=f'Tropic: {User.tropicBought}', fill='white', font="Lato 10 bold")
        canvas.create_text(560, mode.height-25, text=f'Plants: {User.plantHarvested}', fill='white', font="Lato 10 bold")
        canvas.create_text(650, mode.height-25, text=f'Cabbages: {User.cabbageHarvested}', fill='white', font="Lato 10 bold")
        canvas.create_text(740, mode.height-25, text=f'Flower: {User.flowerBought}', fill='white', font="Lato 10 bold")
        canvas.create_text(830, mode.height-25, text=f'Rose: {User.roseBought}', fill='white', font="Lato 10 bold")
        canvas.create_text(920, mode.height-25, text=f'Tropic: {User.tropicBought}', fill='white', font="Lato 10 bold")    

# GRAPH ANALYSIS MODE
# Plots the user's money automatically whenever it changes (from marketplace mode)
# "Getting prediction" means predicting the next 3 steps the user should take to optimize garden/profit
# Can zoom into each point by clicking on it and also scale up and down the axes
class GraphAnalysis(Mode):
    def appStarted(mode):
        # background image: source --> https://unsplash.com/photos/TFyi0QOx08c
        mode.misty = mode.scaleImage(mode.loadImage('misty.jpg'), 1/2)
        mode.originX = 100
        mode.originY = mode.height-100
        mode.upperY = 200
        mode.upperX = mode.width-500
        mode.cols = 5 # y axis
        mode.rows = 7 # x axis
        # initialize grid
        gridWidth  = mode.width - 2*mode.originX
        gridHeight = mode.height - mode.upperY - mode.originX
        # scale
        mode.number = 250
        # number of random boards generated
        mode.boardsNum = 5
        # all options of what you can do
        mode.options = ["buyplant", "buycabbage", "sellplant", "sellcabbage", "buyplanter", "sellflower", "buyflower", "sellrose", "buyrose", "selltropic", "buytropic"]
        # dictionary of the action items as keys, mapped to a list of [impact on wealth (aka worth), long-run profit score]
        mode.pricesDict = {"buyplant": [-20, -4], "buycabbage": [-50, -6], "sellplant": [30, 1], "sellcabbage": [80, 1], "buyplanter":[-400, -20], \
            "buyflower": [-150, -8], "buyrose": [-175, -9], "buytropic": [-200, -10], "sellflower": [180, 2], "sellrose": [175, 2], "selltropic": [200, 2]}
        # taking into account that these will be sold and grown
        # looking at the eventual profits that will be received
        mode.profitDict = {"buyplant": 10, "buycabbage": 30, "sellplant": 30, 'sellcabbage': 80, 'buyplanter': 400, "buyflower": 30, "sellflower": 100, \
                            "buyrose": 35, "sellrose": 150, "buytropic": 50, "selltropic": 200}
        # checking if user wants to get a prediction
        mode.getPrediction = False
        mode.task1 = ''
        mode.task2 = ''
        mode.task3 = ''
        mode.predictionX = None
        mode.predictionY = None
        mode.pointClicked = False
        mode.pointClickedX = None
        mode.pointClickedY = None
    
    def keyPressed(mode, event):
        if (event.key == 'a'):
            mode.number -= 50
        elif (event.key == 's'):
            mode.number += 50
    
    def mousePressed(mode, event):
        (x, y) = (event.x, event.y)
        if (x>700 and x<840) and (y>575 and y<625):
            mode.getPrediction = not mode.getPrediction
            result = mode.predictionPoint()
            (mode.predictionX, mode.predictionY) = (result[0], result[1])
            mode.formatPrediction()
            if mode.getPrediction==True:
                User.money -= 30
        elif (x>0 and x<200) and (y>0 and y<50): # home
            mode.app.setActiveMode(mode.app.Homepage)
        elif (x>200 and x<400) and (y>0 and y<50): # garden
            mode.app.setActiveMode(mode.app.PlantingMode)
        elif (x>400 and x<600) and (y>0 and y<50): # marketplace
            mode.app.setActiveMode(mode.app.MarketplaceMode)
        elif (mode.getPrediction == True) and (mode.predictionX != None) and (mode.predictionY != None) and \
        (x > mode.predictionX-5) and (x < mode.predictionX+5) \
        and (y > mode.predictionY-5) and (y < mode.predictionY+5):
            # zoom into the graph
            (mode.pointClickedX, mode.pointClickedY) = mode.pixelToPoint(mode.predictionX, mode.predictionY)
            # point clicked X/Y are coordinates
            mode.pointClicked = not mode.pointClicked
        elif (mode.pointClicked == True) and (x>250) and (x<350) and (y>165) and (y<190):
            mode.pointClicked = False
        
        # going through every point in the points list
        # if clicked on value is within the dot
        for i in range(len(User.pointsList)):
            (coordinateX, coordinateY) = mode.pointToPixel(User.pointsList[i][0], User.pointsList[i][1])
            radius = 5
            if (x > coordinateX-5) and (x < coordinateX+5) and (y > coordinateY-5) and (y < coordinateY+5):
                # zoom into the graph
                (mode.pointClickedX, mode.pointClickedY) = mode.pixelToPoint(coordinateX, coordinateY)
                # point clicked X/Y are coordinates
                mode.pointClicked = not mode.pointClicked
                break

    # from https://www.cs.cmu.edu/~112/notes/notes-animations-part1.html#exampleGrids
    def getCellBounds(mode, row, col):
        gridWidth  = mode.width - 2*mode.originX
        gridHeight = mode.height - mode.upperY - mode.originX
        mode.cellWidth = (gridWidth//2) / mode.cols
        mode.cellHeight = gridHeight / mode.rows
        x0 = mode.originX + col * mode.cellWidth
        x1 = mode.originX + (col+1) * mode.cellWidth
        y0 = mode.upperY + row * mode.cellHeight
        y1 = mode.upperY + (row+1) * mode.cellHeight
        return (x0, y0, x1, y1)

    # from https://www.cs.cmu.edu/~112/notes/notes-animations-part1.html#exampleGrids  
    def drawGrid(mode, canvas):
        for row in range(mode.rows):
            for col in range(mode.cols):
                (x0, y0, x1, y1) = mode.getCellBounds(row, col)
                canvas.create_rectangle(x0, y0, x1, y1)
    
    def labelAxis(mode, canvas):
        i = 0
        for row in range(mode.rows, -1, -1):
            canvas.create_text(mode.originX-25, mode.originY-(i*mode.cellHeight), text=mode.number*i)
            i += 1 # increment of 10
        canvas.create_text(40, 400, text='TOTAL WEALTH', font='Lato 15 bold', angle=90)
    
    # converting the point (x,y) on the graph to a pixel
    def pointToPixel(mode, x, y):
        pixelY = mode.originY-((((mode.originY-mode.upperY)/mode.rows)*y)/mode.number)
        pixelX = mode.originX+((((mode.upperX-mode.originX)/mode.cols)*x))
        return (pixelX, pixelY)
    
    # converting the pixel (pixelX, pxelY) to a point on the graph
    def pixelToPoint(mode, pixelX, pixelY):
        y = ((pixelY - mode.originY)*((-mode.rows)/(mode.originY-mode.upperY)))
        x = ((pixelX - mode.originX)*((mode.cols)/(mode.upperX-mode.originX)))
        return (x, y)
    
    # drawing the point on the graph
    # not drawing the line if it surpasses the maximum y axis value
    def plotPoint(mode, x, y, canvas):
        r = 5
        (pixelX, pixelY) = mode.pointToPixel(x, y)
        if (pixelY > mode.upperY):
            canvas.create_oval(pixelX-r, pixelY-r, pixelX+r, pixelY+r, fill='pink')
    
    # drawing lines between the points
    # not drawing the line if it surpasses the maximum y axis value
    def drawLine(mode, canvas):
        for i in range(len(User.pointsList)-1):
            (x1, y1) = mode.pointToPixel(User.pointsList[i][0], User.pointsList[i][1])
            (x2, y2) = mode.pointToPixel(User.pointsList[i+1][0], User.pointsList[i+1][1])
            intersectX = ((mode.upperY-y1)*((x2-x1)/(y2-y1))+x1)

            if (y1 < mode.upperY) and (y2 < mode.upperY):
                continue
            elif (y1 < mode.upperY):
                canvas.create_line(intersectX, mode.upperY, x2, y2, fill='pink', width=4)
            elif (y2 < mode.upperY):
                canvas.create_line(x1, y1, intersectX, mode.upperY, fill='pink', width=4)
            else:
                canvas.create_line(x1, y1, x2, y2, fill='pink', width=4)

    # every time money updated, removing the most recent value so that
    # the graph updates
    def doStep(mode):
        User.pointsList.pop(0) # making the graph move relative to today
        for i in range(len(User.pointsList)):
            User.pointsList[i][0] -= 1
        x = len(User.pointsList)
        y = User.money
        User.pointsList += [[x, y]]

    def timerFired(mode):
        # keeping track of the money to see if it changed
        (x4, y4) = User.pointsList[4]
        if y4 != User.money:
            mode.doStep()
    
    # drawing a line between predicted value for profit --> 
    def predictionPoint(mode):
        mode.profitDict
        winpath = mode.getProphet(mode.boardsNum)
        profit = 0
        for task in winpath:
            profit += mode.profitDict[task]
        y = User.money+profit
        x = len(User.pointsList)
        return [x, y]
    
    # drawing the line for profit based on the potential prediction
    # not drawing the line or dot if it surpasses the maximum y axis value
    def drawPredictionLine(mode, canvas):
        (x1, y1) = (mode.pointToPixel(User.pointsList[4][0], User.pointsList[4][1]))
        (x2, y2) = mode.pointToPixel(mode.predictionX, mode.predictionY)

        intersectX = ((mode.upperY-y1)*((x2-x1)/(y2-y1))+x1)

        if (y1 > mode.upperY) and (y2 > mode.upperY):
            canvas.create_line(x1, y1, x2, y2, fill=rgbString(180, 200, 184), width=4)
        elif (y1 < mode.upperY):
            canvas.create_line(intersectX, mode.upperY, x2, y2, fill=rgbString(180, 200, 184), width=4)
        elif (y2 < mode.upperY):
            canvas.create_line(x1, y1, intersectX, mode.upperY, fill=rgbString(180, 200, 184), width=4)
        
        if (y2 > mode.upperY):
            canvas.create_oval(x2-5, y2-5, x2+5, y2+5, fill=rgbString(180, 200, 184))

    # this is the function that combines all of the prediction functions
    # to get the most ultimate path, including the conditions
    def getProphet(mode, n):
        boards = mode.makeBoard(n)
        paths = []
        maxscore = 0
        winpath = []
        maxPlanters = 9
        copyOfPlanterList = copy.deepcopy(User.plantsInPlanterList)
        
        # initializing a list of plant types : i.e. plant or cabbage or flower or rose or tropic or None
        for planter in copyOfPlanterList:
            for i in range(len(planter.plants)):
                if planter.plants[i] != None:
                    planter.plants[i] = planter.plants[i].name

        # initializing number of plants, cabbages, and planters, flowers, roses, tropics
        plantCount = 0
        cabbageCount = 0
        flowerCount = 0
        roseCount = 0
        tropicCount = 0
        planterCount = len(User.plantsInPlanterList) + User.planterBought
        for element in copyOfPlanterList:
                for item in element.plants:
                    if item == 'plant':
                        plantCount += 1
                    elif item == 'cabbage':
                        cabbageCount += 1  
                    elif item == 'flower':
                        flowerCount += 1
                    elif item == 'rose':
                        roseCount += 1
                    elif item == 'tropic':
                        tropicCount += 1      
        plantCount += User.plantHarvested
        cabbageCount += User.cabbageHarvested
        flowerCount += User.flowerHarvested
        roseCount += User.roseHarvested
        tropicCount += User.tropicHarvested

        for board in boards:
            paths += [mode.getMostProfit(board, mode.pricesDict)]
        for path in paths:
            if path[1] > maxscore:
                maxscore = path[1]
                winpath = path[2]
        
        # enable conditions on the suggestion engine -->
        # cannot sell plants if no plants to sell
        # cannot sell cabbages if no cabbages to sell
        # cannot buy planters if already own 9 planters (maximum)
        plantNeeded = 0
        cabbageNeeded = 0
        flowerNeeded = 0
        roseNeeded = 0
        tropicNeeded = 0

        planterOffered = 0
        for task in winpath:
            if task == 'sellplant':
                plantNeeded += 1
            elif task == 'sellcabbage':
                cabbageNeeded += 1
            elif task == 'sellflower':
                flowerNeeded += 1
            elif task == 'sellrose':
                roseNeeded += 1
            elif task == 'selltropic':
                tropicNeeded += 1
            elif task == 'buyplanter':
                planterOffered += 1
        if (plantNeeded > plantCount) or (cabbageNeeded > cabbageCount) or \
            (flowerNeeded > flowerCount) or (roseNeeded > roseCount) or \
                (tropicNeeded > tropicCount) or (planterOffered + planterCount > maxPlanters):
            return mode.getProphet(n)
        return winpath

    # creates a 3x3 board of the different action items possible
    # every action item will be included
    def makeBoard(mode, n):
        rows = cols = 3
        board = []
        if n == 0:
            return []
        else:
            for row in range(rows):
                board.append([None]*cols)
            temp = []
            for row in range(rows):
                for col in range(cols):
                    if len(temp) == 0:
                        temp = copy.copy(mode.options)
                    chosen = random.randint(0,len(temp)-1)
                    board[row][col] = temp[chosen]
                    temp.remove(temp[chosen])
            board[0][0] = mode.options[n-1]
            return [board] + mode.makeBoard(n-1)

    # this returns the profit for the row, column, diagonal based on the worth
    # worth is initialized in the dictionary
    def getMostProfit(mode, board, pricesDict):
        total = []
        for row in board:
            total.append(row)
        for col in range(len(board[0])):
            temp = []
            for row in range(len(board)):
                temp += [board[row][col]]
            total.append(temp)
        temp2 = []
        temp3 = []
        for i in range(len(board)):
            temp2 += [board[row][row]]
            temp3 += [board[len(board)-1-row][len(board)-1-row]]
        total.append(temp2)
        total.append(temp3)
        return mode.calculateProfit(total, pricesDict)
    
    # calculates the weighted profit of the tasks, returning with the one that has
    # the best profit and the list of the best tasks
    def calculateProfit(mode, total, pricesDict, healthyMoney=200):
        bestProfit = 0

        for taskList in total:
            streakProfit = 0
            actualCost = 0

            for task in taskList:
                streakProfit += (pricesDict[task][0] * pricesDict[task][1])   
                actualCost += pricesDict[task][0]
            if ((streakProfit > bestProfit) and ((User.money + actualCost)>healthyMoney)):
                    bestProfit = streakProfit
                    bestTasks = taskList
                    finalCost = actualCost
        return [finalCost, bestProfit, bestTasks]

    def formatPrediction(mode):
        winpath = mode.getProphet(mode.boardsNum)
        formattedList = []
        for task in winpath:
            addString = ''
            if task == 'sellplant':
                addString = 'Sell Plant'
            elif task == 'sellcabbage':
                addString = 'Sell Cabbage'
            elif task == 'buyplant':
                addString = 'Buy Plant'
            elif task == 'buycabbage':
                addString = 'Buy Cabbage'
            elif task == 'buyplanter':
                addString = 'Buy Planter'
            elif task == 'buyflower':
                addString = 'Buy Flower'
            elif task == 'buyrose':
                addString = 'Buy Rose'
            elif task == 'buytropic':
                addString = 'Buy Tropic'
            elif task == 'sellflower':
                addString = 'Sell Flower'
            elif task == 'sellrose':
                addString = 'Sell Rose'
            elif task == 'selltropic':
                addString = 'Sell Tropic'
            formattedList += [addString]
        mode.task1 = formattedList[0]
        mode.task2 = formattedList[1]
        mode.task3 = formattedList[2]

    # draw new grid and coordinates when user clicks on the a pink point
    def drawZoomedGrid(mode, canvas):

        # labelling the axis
        # mode.pointClickedX, mode.pointClickedY
        bestDifference = 10**6 # set to a random initially high number
        closestNum = 0

        for i in range(7):
            if (abs((i*mode.number)-(mode.pointClickedY*mode.number)) < bestDifference):
                bestDifference = abs((i*mode.number)-(mode.pointClickedY*mode.number))
                closestNum = i*mode.number
        
        low = closestNum-mode.number
        high = closestNum+mode.number
        interval = mode.number/4

        # drawing the grid
        heightY = (mode.originY-mode.upperY)/8
        widthX = mode.originX + (mode.upperX-mode.originX)/2

        canvas.create_text(mode.originX-25, mode.originY, text=0)

        for i in range(8):
            canvas.create_rectangle(mode.originX, mode.upperY+((i)*heightY), widthX, mode.upperY+((i+1)*heightY), fill='white')
            canvas.create_text(mode.originX-25, mode.upperY+((i)*heightY), text=round(high-(interval*i)))
        for i in range(8):
            canvas.create_rectangle(widthX, mode.upperY+((i)*heightY), mode.upperX, mode.upperY+((i+1)*heightY), fill='white')

        midX = mode.originX + (mode.upperX-mode.originX)/2
        pixelY = mode.originY - ((mode.originY-mode.upperY)*((mode.pointClickedY*mode.number)-(low))/(2*mode.number))
        canvas.create_oval(midX-10, pixelY-10, midX+10, pixelY+10, fill='pink')
        canvas.create_text(40, 400, text='TOTAL WEALTH', font='Lato 15 bold', angle=90)

    def redrawAll(mode, canvas):
        canvas.create_image(500, 350, image=ImageTk.PhotoImage(mode.misty))
        canvas.create_rectangle(20, 150, 550, 650, fill='white', width = 0)
        # draw axis
        canvas.create_rectangle(0, 50, mode.width, 150, fill=rgbString(228, 236, 245), width=0)
        canvas.create_text(mode.width/2-5, 100, text='PROFIT TRACKER AND GARDEN ANALYSIS', font='Lato 30 bold italic', fill='pink')
        canvas.create_text(mode.width/2, 100, text='PROFIT TRACKER AND GARDEN ANALYSIS', font='Lato 30 bold italic')
        canvas.create_line(mode.originX, mode.originY, mode.originX, mode.upperY, width=3)
        canvas.create_line(mode.originX, mode.originY, mode.upperX, mode.originY, width=3)
        
        if mode.pointClicked == False:
            mode.drawGrid(canvas)
            mode.labelAxis(canvas)
            mode.drawLine(canvas)
            # plotting the different points
            for (x, y) in User.pointsList:
                mode.plotPoint(x, y, canvas)
        
        if mode.pointClicked == True:
            mode.drawZoomedGrid(canvas)
            canvas.create_rectangle(250,165,350, 190, fill='pink')
            canvas.create_text(300, 165+(190-165)/2, text='BACK')

        # draw button to get prediction
        canvas.create_rectangle(700, 575, 840, 625, fill='black', width = 0)
        canvas.create_text(770, 600, text='GET PREDICTION', font="Lato 12", fill='white')
        canvas.create_text(770, 650, text='A prediction costs $30.', font="Lato 12", fill='white')
        canvas.create_text(mode.width-50, 25, text=f'$ {User.money}')

        if (mode.getPrediction == True) and (mode.pointClicked == False):
            mode.drawPredictionLine(canvas)
            canvas.create_text(800, 225, text="YOUR NEXT THREE STEPS", font='Lato 20 bold')
            canvas.create_text(800, 265, text=f'{mode.task1}', font='Lato 15 italic')
            canvas.create_text(800, 295, text=f'{mode.task2}', font='Lato 15 italic')
            canvas.create_text(800, 325, text=f'{mode.task3}', font='Lato 15 italic')
        
        # drawing a menu at the top: home, my garden, marketplace
        canvas.create_rectangle(0, 0, 200, 50, fill='white')
        canvas.create_rectangle(200, 0, 400, 50, fill='white')
        canvas.create_rectangle(400, 0, 600, 50, fill='white')
        canvas.create_text(100, 25, text='HOME')
        canvas.create_text(300, 25, text='MY GARDEN')
        canvas.create_text(500, 25, text='MARKETPLACE')

class Planter(object):
    def __init__(self):
        self.plants = [None, None, None]
        self.numFish = 2
    
    def addPlant(self, mode, plantName):
        plant1 = Plant(mode, plantName, 0.1)
        for element in range(len(self.plants)):
            if self.plants[element] == None:
                self.plants[element] = plant1
                break

    def removePlant(self, plant):
        for i in range(len(self.plants)):
            if self.plants[i] != None:
                if self.plants[i].name == plant:
                    self.plants[i] = None
                    break

    def __repr__(self):
        return f'{self.plants}'

    # drawing the planter image, plants, and fish
    def drawPlanter(self, mode, canvas, x, y):
        canvas.create_image(x, y, image=ImageTk.PhotoImage(mode.water))
        canvas.create_image(x, y, image=ImageTk.PhotoImage(mode.boxPlanter))
        self.fishInPlanter = []
        # using the number of fish per planter to draw the fish
        for i in range(self.numFish):
            self.configureFishInPlanter(x,y)
        for fish in self.fishInPlanter:
            fish.drawFish(mode, canvas)
        # drawing the plants within the planters
        for i in range(len(self.plants)):
            if self.plants[i] != None:
                px = i*75+(x - 75)
                py = y-70
                self.plants[i].drawPlant(mode,canvas,px,py)
    
    def configureFishInPlanter(self,x,y):
        fishx = random.randint(int(x-75), int(x+75))
        fishy = random.randint(int(y-30), int(y+30))
        tx = random.randint(int(x-75), int(x+50))
        ty = random.randint(int(y-30), int(y+75))
        speed = random.randint(1, 40)
        fish1 = Fish(fishx, fishy, tx, ty, speed)
        self.fishInPlanter.append(fish1)

class Plant(object):
    def __init__(self, mode, name, size):
        self.name = name
        self.size = size
        if self.name == 'plant':
            self.worth = 20
            self.img = mode.plantPic
        elif self.name == 'cabbage':
            self.worth = 50
            self.img = mode.cabbagePic
        elif self.name == 'flower':
            self.img = mode.flowerPic
        elif self.name == 'rose':
            self.img = mode.rosePic
        elif self.name == 'tropic':
            self.img = mode.tropicPic
        self.shift = 0
    
    def __repr__(self):
        return f'{self.name},{self.size}'

    def drawPlant(self, mode, canvas, x, y):
        image = mode.scaleImage(self.img, self.size)
        canvas.create_image(x, y-self.shift, image=ImageTk.PhotoImage(image))
    
    def grow(self):
        if not(self.size >= 0.5):
            self.size += 0.1
            self.shift += 10 # shifting the y axis up when it grows

class Fish(object):
    # adding type of fish
    def __init__(self, x, y, tx, ty, speed):
        self.x = x
        self.y = y
        self.tx = tx
        self.ty = ty
        self.speed = speed
    
    def moveFish(self, mode):
        if abs(self.x - self.tx) < 10:
            (self.tx, self.ty) = (random.randint(mode.app.PlantingMode.xTankTopLeft+mode.app.PlantingMode.margin, \
            mode.app.PlantingMode.xTankBottomRight-mode.app.PlantingMode.margin), random.randint( \
            mode.app.PlantingMode.yTankTopLeft+mode.app.PlantingMode.margin, \
            mode.app.PlantingMode.yTankBottomRight-mode.app.PlantingMode.margin))
        else:
            self.x += (self.tx - self.x)/self.speed
            self.y += (self.ty - self.y)/self.speed

    def addFish(mode):
        cx = random.randint(mode.app.PlantingMode.xTankTopLeft+mode.app.PlantingMode.margin, mode.app.PlantingMode.xTankBottomRight-mode.app.PlantingMode.margin)
        cy = random.randint(mode.app.PlantingMode.yTankTopLeft+mode.app.PlantingMode.margin, mode.app.PlantingMode.yTankBottomRight-mode.app.PlantingMode.margin)
        tx = random.randint(mode.app.PlantingMode.xTankTopLeft+mode.app.PlantingMode.margin, mode.app.PlantingMode.xTankBottomRight-mode.app.PlantingMode.margin)
        ty = random.randint(mode.app.PlantingMode.yTankTopLeft+mode.app.PlantingMode.margin, mode.app.PlantingMode.yTankBottomRight-mode.app.PlantingMode.margin)
        speed = random.randint(1, 40)
        fish1 = Fish(cx, cy, tx, ty, speed)
        mode.app.PlantingMode.fish += [fish1]
    
    def drawFish(self, mode, canvas):
        if self.tx < self.x:
            canvas.create_image(self.x, self.y, image=ImageTk.PhotoImage(mode.fishPic))
        else:
            canvas.create_image(self.x, self.y, image=ImageTk.PhotoImage(mode.flipFishPic))

class User(object):
    money = 500
    plantBought = 0
    cabbageBought = 0
    planterBought = 0
    plantHarvested = 0
    cabbageHarvested = 0
    flowerBought = 0
    flowerHarvested = 0
    roseBought = 0
    roseHarvested = 0
    tropicBought = 0
    tropicHarvested = 0
    # 2D list consisting of the planters, and the number of plants
    # e.g. = [None, plant, cabbage]
    plantsInPlanterList = []
    tankNum = 0
    pointsList = [[0,400],[1,500],[2,20],[3,455],[4,597]]
    
    # how to write to files idea extracted from:
    # https://realpython.com/read-write-files-python/#opening-and-closing-a-file-in-python
    @staticmethod
    def save(): # path is /Users/nathaliejeans/Documents/VSCode/termproject/settings.txt
        with open('settings.txt', 'w') as file:
            prevtime = time.time()
            data = User.getPlanterData() # gets planter data, returns as type string
            pointData = User.writePointData()
            file.writelines(f'{prevtime} \n')
            file.writelines(data)
            file.writelines('$ \n')
            file.writelines(f'{User.money}\n')
            file.writelines(f'{User.plantBought}\n')
            file.writelines(f'{User.planterBought}\n')
            file.writelines(f'{User.cabbageBought}\n')
            file.writelines(f'{User.plantHarvested}\n')
            file.writelines(f'{User.cabbageHarvested}\n')
            # additional plants: flower, rose, tropic
            file.writelines(f'{User.flowerBought}\n')
            file.writelines(f'{User.flowerHarvested}\n')
            file.writelines(f'{User.roseBought}\n')
            file.writelines(f'{User.roseHarvested}\n')
            file.writelines(f'{User.tropicBought}\n')
            file.writelines(f'{User.tropicHarvested}\n')
            file.writelines(pointData)
            file.writelines('%\n')
    
    # formats the data before writing it so that we can read it
    # and then can transform it to make use of the data that was written in the files
    @staticmethod
    def getPlanterData():
        data = ''
        for planter in User.plantsInPlanterList:
            tempList = []
            for plant in planter.plants:
                temp = str(plant)
                tempList += temp + ' '
            writeME = "".join(tempList)
            writeME += str(planter.numFish)
            data += writeME +'\n'
        return data
    
    # formatting the data before writing into the file for the coordinates list
    @staticmethod
    def writePointData():
        pointData = ''
        for coordinates in User.pointsList:
            tempList = []
            for point in coordinates:
                temp = str(point)
                tempList += temp + ' '
            writeME = "".join(tempList)
            pointData += writeME +'\n'
        return pointData

# rgbString function from https://www.cs.cmu.edu/~112/notes/notes-graphics.html
def rgbString(r, g, b):
    return f'#{r:02x}{g:02x}{b:02x}'

class VerticalFarming(ModalApp):w
    def appStarted(app):
        app.Homepage = Homepage()
        app.AquaponicsMode = AquaponicsMode()
        app.PlantingMode = PlantingMode()
        app.MarketplaceMode = MarketplaceMode()
        app.GraphAnalysisMode = GraphAnalysis()
        app.setActiveMode(app.Homepage)
        app.hello = False

        app._title = 'Vertical Farming Simulation by Nathalie Jeans'
        app.updateTitle()

app = VerticalFarming(width=1000, height=700)