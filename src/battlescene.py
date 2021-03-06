import pygame, kbInput, game_objects, scene, uimgr, time, random, sys
isLinux = sys.platform.startswith("linux")
if(isLinux):
    try:
        from gi.repository import Gtk
        import sugar3.activity.activity
        from sugar3.graphics.toolbarbox import ToolbarBox
        from sugar3.activity.widgets import ActivityToolbarButton
        from sugar3.graphics.toolbutton import ToolButton
        from sugar3.activity.widgets import StopButton
    except ImportError:
        isLinux = False

class BattleScene(scene.Scene):
    
    def __init__(self, char1, char2):
        self.grid = self.makeGrid()
        self.char1 = char1
        self.char2 = char2
        self.startTime = time.time() # returns time as a float
        self.gameSpeed = 3.0 # time between turns in seconds
        self.nextTurnTime = self.startTime + self.gameSpeed
        self.prepBattle()

        self.UI = uimgr.UIManager()
        
        self.golemSprites = self.UI.Image((0,0), "res/golems.png", spriteSheet = True, numSprites = 5)        
 
        self.makeStatBox()
        self.updateStatBox()
        self.makeLogBox()
        
        self.nextTurn() #Actually starts the battle
 
       
    def render(self,surface):
        surface.fill((150,150,150)) # bg color
        pygame.draw.rect(surface,(100,100,100),(0,0,1200,450)) # wall color + size
        surface.blit(self.grid,(0,300))
        
        self.drawBots(surface)
        self.drawStatBox(surface)
        self.drawLogBox(surface)
        #self.UI.render(surface) 
        
    def handle_events(self, events):
        pass

       
    def update(self, keys, keysLastFrame):
        
        currentTime = time.time()
        if currentTime >= self.nextTurnTime:
            self.nextTurn()
            self.nextTurnTime += self.gameSpeed
        
        keys = pygame.key.get_pressed()
            
        if kbInput.isUpPressed(keys):
            self.moveBotByDir(self.c1Bots[0],0,1)
            self.moveBotByDir(self.c2Bots[0],0,1)
        elif kbInput.isRightPressed(keys):
            self.moveBotByDir(self.c1Bots[0],1,0)
            self.moveBotByDir(self.c2Bots[0],1,0)
        elif kbInput.isDownPressed(keys):
            self.moveBotByDir(self.c1Bots[0],0,-1)
            self.moveBotByDir(self.c2Bots[0],0,-1)
        elif kbInput.isLeftPressed(keys):
            self.moveBotByDir(self.c1Bots[0],-1,0)
            self.moveBotByDir(self.c2Bots[0],-1,0)
        
        
    def moveBotByDir(self,bot,xMod,yMod):
        oldX = bot.location[0]
        oldY = bot.location[1]

        x = xMod + oldX
        y = yMod + oldY

        if x > 2: x = 2
        if y > 2: y = 2
        if x < 0: x = 0
        if y < 0: y = 0

        if bot.pOwned is True:
            self.grid1[oldX][oldY] = None
            self.grid1[x][y] = bot
        else:
            self.grid2[oldX][oldY] = None
            self.grid2[x][y] = bot
        bot.location = [x,y]

    def moveToSpace(self,bot,newX,newY):
        x = y = -1
        if bot.location is not None: #if bot has a prev location get its loc. ready
            x = bot.location[0]
            y = bot.location[1]    
        
        if bot.pOwned is True:
            if x is not -1: 
                self.grid1[x][y] = None # remove it from prev. location   
            self.grid1[newX][newY] = bot #add into new space

        else: #same thing for npc bots
            if x is not -1:
                self.grid2[x][y] = None
            self.grid2[newX][newY] = bot
        
        bot.location = [newX,newY] # all bots know their location when in battle
            
    def sendToBattle(self, c1, c2):
        self.char1 = c1
        self.char2 = c2
        self.prepBattle()
        

    def prepBattle(self):
        self.c1Bots = self.char1.list_of_bots
        self.c2Bots = self.char2.list_of_bots
        self.allBots = []
        self.allBots.extend(self.c1Bots)
        self.allBots.extend(self.c2Bots)

        self.c1NB = len(self.c1Bots)
        self.c2NB = len(self.c2Bots) 

        self.grid1 = [[None] * 3 for i in range(3)]
        self.grid2 = [[None] * 3 for i in range(3)]

        
        for bot in self.allBots:
            self.randomlyPlaceBot(bot)
            bot.ready = 0

    def randomlyPlaceBot(self,bot):
        rX = None
        rY = None
        while(True):
            rX = random.randint(0,2)
            rY = random.randint(0,2)
            if(bot.pOwned):
                if self.grid1[rX][rY] is None: break
            else:
                if self.grid2[rX][rY] is None: break
        self.moveToSpace(bot,rX,rY)
    
        
    def doDefeat(self):
        self.manager.go_to(scene.Scenes.INTERACTIVE) 

    def doVictory(self, bot):
        self.manager.go_to(scene.Scenes.INTERACTIVE, deadBot=bot) 

    def testDidLose(self, bot):
        if bot.health <= 0:
            if bot.pOwned:
                self.doDefeat()
            else:
                self.doVictory(bot)

    def nextTurn(self):
        # Readiness increases for all bots.
        for bot in self.allBots:
            bot.ready += bot.speed

        # Determine the fastest bot
        fastestBot = self.allBots[0]
        for bot in self.allBots:
            if bot.ready > fastestBot.ready:
                fastestBot = bot
        slowestBot = self.allBots[map(lambda x: x != fastestBot, self.allBots).index(True)]

        
        self.takeAction(fastestBot, self.getRandomOpponent(fastestBot))
        self.testDidLose(fastestBot)

    def getRandomOpponent(self, bot):
        if bot.pOwned:
            return self.c2Bots[random.randint(0,len(self.c2Bots)-1)]
        else:
            return self.c1Bots[random.randint(0,len(self.c1Bots)-1)]   
 
    #this is where the CodeBlocks stuff will take place?
    def takeAction(self,ownerBot, opponentBot):
        ownerBot.ready -= ownerBot.speed 
       
        # print ("got into takeAction") # works
 
        def log(text):
            # print str(text)
            self.logLineText.append(str(text))

        for cb in ownerBot.queue_of_code_blocks:
            cb.execute(ownerBot, opponentBot, log)
        
        if len(ownerBot.queue_of_code_blocks) is 1: 
            log(ownerBot.name + " doesn't have any programming!")        

        self.updateLogBox()
        self.updateStatBox()
    
    def makeLogBox(self):
        white = (255,255,255)
        black = (0,0,0)
        font  = 20

        self.logBox = self.UI.Container((300,50,600,300),bgColor = white, borderColor = black)
        self.logLineUI = []
        self.logLineText = []

        for i in range(0,10):
            line = self.UI.Text((10,275-i*30),"TestLine", black, font)
            self.logLineUI.append(line)
            self.logBox.addChild(line)
        
    def drawLogBox(self, surface):
        self.logBox.render(surface)
            
    def updateLogBox(self):
        maxLines = 10
        numLines = len(self.logLineText)
        start = 0
        if numLines > maxLines: start = numLines - maxLines

        for i in range(start, start + maxLines):
            if i >= numLines: 
                self.logLineUI[i-start].setText("")
            else:
                line = self.logLineText[numLines - i - 1] # the most recent line is drawn on the bottom
                self.logLineUI[i-start].setText(line)
               

    #This gets called by the renderer, and draws the bots into the proper location on the grid
    def drawBots(self,surface):
        c = (0,255,0)
        c2 = (255,0,255)
        #testBot = pygame.Surface((80,80))
        #pygame.draw.circle(testBot,c2,(40,40),40)
        #testBot.set_colorkey((0,0,0))
       
        baseX = 300
        xInc = 75
        xIncMod = 25
        y0 = 650
        y1 = 575
        y2 = 500
            
        for bot in self.allBots:
            x = bot.location[0]
            y = bot.location[1]
            #print("botX:" + str(x) + ", botY:" + str(y))
            height = y0
            self.golemSprites.setMod(4)
            if y is 1:
                height = y1
                self.golemSprites.setMod(3.5)
            if y is 2:
                height = y2
                self.golemSprites.setMod(3)
                    
           
            xSpec = (2-x)*xIncMod
            if y is 0 : xSpec = 0
            if y is 1 : xSpec = xSpec/2

            xSpec2 = x*xIncMod
            if y is 0 : xSpec2 = 0
            if y is 1 : xSpec2 = xSpec2/2

            golemYAdj = -30
            if y is 1: golemYAdj = -30
            if y is 2: golemYAdj = -20 

            golemXAdj = 0
            if y is 2: golemXAdj = 5                   
            

            xLoc = None
            if bot.pOwned is True:
                xLoc = baseX+xInc*x+xSpec
                self.golemSprites.moveTo((xLoc + golemXAdj, height + golemYAdj))
                self.golemSprites.renderSprite(surface,bot.element)
                
            else:
                xLoc = baseX+370+xInc*x-xSpec2
                self.golemSprites.moveTo((xLoc + golemXAdj, height + golemYAdj))
                self.golemSprites.renderSprite(surface,bot.element,reverse=True)
            
            self.drawHPBar(surface,bot,xLoc,height-30)

    #end drawBots
    

    def makeStatBox(self):
        #o is our team, t is bot team
        oColor = (255,0,0) 
        tColor = (0,0,255)
        bColor = (0,0,0)
        textColor = (0,0,0) 
        fontSizeL = 20
        fontSize = 15
        padL = 50 #large padding
        pad = 10 #padding

        oNum = len(self.c1Bots)
        tNum = len(self.c2Bots)

        sWidth = 1200
        sHeight = 900

        cWidth = 150
        cHeight = 100
        self.oStatContainer = self.UI.Container((padL,padL,cWidth,cHeight*oNum),bgColor = oColor, borderColor = bColor)
        self.oStatBoxes = []
      
        self.tStatContainer = self.UI.Container((sWidth-cWidth-padL,padL,cWidth,cHeight*tNum),bgColor = tColor, borderColor = bColor)
        self.tStatBoxes = []
        
        for i in range(0,oNum+tNum):
           
            statBox = None
            if i < oNum:     
                statBox = self.UI.Container((pad,pad+20,130,60), bgColor = oColor, borderColor = bColor)
            else:
                statBox = self.UI.Container((pad,pad+20,130,60), bgColor = tColor, borderColor = bColor)

            yOff = 15
            #ORDER of these elements matters for updateStatBox! 
            hp = self.UI.Text((pad,pad),"UPDATEDLATER",textColor,fontSize)
            statBox.addChild(hp)
            
            mp = self.UI.Text((pad,pad*2+yOff),"UPDATEDLATER",textColor,fontSize)
            statBox.addChild(mp)

            name = self.UI.Text((pad,-pad*2),"BOT NAME",textColor,fontSize)
            statBox.addChild(name)
            
            if i < oNum:
                self.oStatBoxes.append(statBox) 
                self.oStatContainer.addChild(statBox)
            else:
                self.tStatBoxes.append(statBox)
                self.tStatContainer.addChild(statBox)

    def updateStatBox(self):
        oNum = len(self.c1Bots)
        tNum = len(self.c2Bots)
        
        #update all relevant bot info
        def setTextLabels(bot,statBox):
            hp = statBox[i].child(0)
            hp.setText("Health : "+str(bot.health)+"/"+str(bot.maxHealth))

            mp = statBox[i].child(1)
            mp.setText("Mana : "+str(bot.mana)+"/"+str(bot.maxMana))
            
            name = statBox[i].child(2)
            name.setText(bot.name)
 
        #for all players bots
        for i in range(0,oNum):
            bot = self.c1Bots[i]
            statBox = self.oStatBoxes
            setTextLabels(bot,statBox)

        #for all npc bots
        for i in range(0,tNum):
            bot = self.c2Bots[i]
            statBox = self.tStatBoxes
            setTextLabels(bot,statBox)

    def drawStatBox(self,surface):
        self.oStatContainer.render(surface)
        self.tStatContainer.render(surface)

    def drawHPBar(self,surface,bot,x,y):
        bgColor = (0,0,0)
        hpColor = (255,0,0)
        adj = 20 #Horiz adjustment      
        b = 5  #Border 
        w = 40 #Width
        h = 15 #Height

        botHPPercentage = float(bot.health)/float(bot.maxHealth)

        bgRect = (x+adj-b,y-b,w+b*2,h+b*2)
        hpRect = (x+adj,y,w*botHPPercentage,h)
        pygame.draw.rect(surface, bgColor, bgRect)
        pygame.draw.rect(surface, hpColor, hpRect)

    #called once in init, the return value is stored in self.grid 
    def makeGrid(self):
        color = (255,0,0)
        color2 = (0,0,255)
        lineW = 12
        nDist = 80
        fDist = nDist * 2 / 3
        h0 = 250
        h1 = 150
        h2 = 75
        h3 = 25
        eMod = 5

        grid = pygame.Surface((400,300))
        rgrid = pygame.Surface((400,300))
        rgFix = pygame.Surface((400,300))
        final = pygame.Surface((1200,900))
        
        #left Grid vertical lines
        pygame.draw.line(grid,color,(nDist,h0+eMod),(2*nDist,h3-eMod),lineW)
        pygame.draw.line(grid,color,(nDist*2,h0),(2*nDist+fDist,h3),lineW)  
        pygame.draw.line(grid,color,(nDist*3,h0),(2*nDist+2*fDist,h3),lineW)
        pygame.draw.line(grid,color,(nDist*4,h0+eMod),(nDist*4,h3-eMod),lineW)
        
        #left grid horiz lines
        pygame.draw.line(grid,color,(nDist,h0),(nDist*4,h0),lineW)
        pygame.draw.line(grid,color,(15+nDist+nDist/3,h1),(nDist*4,h1),lineW)
        pygame.draw.line(grid,color,(15+nDist+nDist/3*2,h2),(nDist*4,h2),lineW)
        pygame.draw.line(grid,color,(nDist*2,h3),(nDist*4,h3),lineW)
                
        #right Grid vertical lines
        pygame.draw.line(rgrid,color2,(nDist,h0+eMod),(2*nDist,h3-eMod),lineW)
        pygame.draw.line(rgrid,color2,(nDist*2,h0),(2*nDist+fDist,h3),lineW)  
        pygame.draw.line(rgrid,color2,(nDist*3,h0),(2*nDist+2*fDist,h3),lineW)
        pygame.draw.line(rgrid,color2,(nDist*4,h0+eMod),(nDist*4,h3-eMod),lineW)
        
        #right grid horiz lines
        pygame.draw.line(rgrid,color2,(nDist,h0),(nDist*4,h0),lineW)
        pygame.draw.line(rgrid,color2,(15+nDist+nDist/3,h1),(nDist*4,h1),lineW)
        pygame.draw.line(rgrid,color2,(15+nDist+nDist/3*2,h2),(nDist*4,h2),lineW)
        pygame.draw.line(rgrid,color2,(nDist*2,h3),(nDist*4,h3),lineW)
        
        rgFix.blit(rgrid,(-50,0))
        rgFix = pygame.transform.flip(rgFix,True,False)
        
        final.blit(rgFix,(550,200))
        final.blit(grid,(200,200))
        final.set_colorkey((0,0,0))
        
        return final
    #End makeGrid
    
    def makeToolbar(self, activity):
        toolbar = ToolbarBox()
        
        activity_button = ActivityToolbarButton(activity)
        toolbar.toolbar.insert(activity_button, -1)
        activity_button.show()
        
        separator = Gtk.SeparatorToolItem()
        separator.props.draw = False
        separator.set_expand(True)
        toolbar.toolbar.insert(separator, -1)
        separator.show()
        
        stop_button = StopButton(activity)
        toolbar.toolbar.insert(stop_button, -1)
        stop_button.show()
        
        return toolbar
    #End makeToolbar
