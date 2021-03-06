import pygame

class Singleton(object):
    _instances = {}
    
    def __new__(cls, *args, **kwargs):
        if cls not in cls._instances:
            cls._instances[cls] = object.__new__(cls, *args, **kwargs)
        return cls._instances[cls]

# Any class can use this by importing uimgr and getting an instance of the manager.
# I know the singleton stuff is weird, but just call uimgr.UIManager() to get this instance
class UIManager(Singleton):
       
    # has a position, size, background, border, on/off switch for rendering
    # usually you don't use these (you can though) everything else subclasses it.
    class UIElement(object):
        def __init__(self, rect, bgColor = None, borderColor = None, borderSize = 5):
            self.rect = rect
            self.offset = (0,0)
            self.position = (rect[0], rect[1])
            self.size = (rect[2], rect[3])
            self.bgColor = bgColor
            self.borderColor = borderColor
            self.parent = None # changes when placed in a container
            self.fullLoc = None # updated when parent exists
            self.enabled = True
            self.bSize = borderSize 

        def setEnabled(self, state):
            self.enabled = state

        def getFullLocation(self):
            if self.parent is None:
                return self.rect
            else:
                pRect = self.parent.getFullLocation()
                pX = pRect[0]
                pY = pRect[1]

                sX = self.position[0]
                sY = self.position[1]
                sW = self.size[0]
                sH = self.size[1]
                
                newX = pX + sX
                newY = pY + sY
                return (newX,newY,sW,sH)
        
        def moveTo(self, position):
            self.rect = (position[0], position[1], self.rect[2], self.rect[3])

        def render(self, surface):
            if self.bgColor is not None:
                pygame.draw.rect(surface, self.bgColor, self.rect)

            if self.borderColor is not None:
                pygame.draw.rect(surface, self.borderColor, self.rect, self.bSize)
    
            

    class Image(UIElement):
        def __init__(self, position, spriteSrc, sizeMod = 1, spriteSheet = False, numSprites = 1):
            self.image = pygame.image.load(spriteSrc).convert()
            self.position = position
            self.isSpriteSheet = spriteSheet
            if spriteSheet:
                size = self.image.get_size()
                self.spriteWidth = size[0]/numSprites
                self.spriteHeight = size[1]
                self.spriteNum = 0
                
            self.setMod(sizeMod)                     
            super(type(self),self).__init__(self.rect)
        
        def setMod(self, mod):
            self.mod = mod
            self.scaleImage()
            self.setRect()

        def setRect(self):
            x = self.position[0]
            y = self.position[1]
            size = self.scaledImg.get_size()
            self.rect = (x,y,size[0],size[1])

        def scaleImage(self):
            if self.isSpriteSheet:
                size = (self.spriteWidth, self.spriteHeight)
                sprite = pygame.Surface(size).convert()
                sprite.blit(self.image,(0,0),(self.spriteNum*self.spriteWidth,0,size[0],size[1]))
                self.scaledImg = pygame.transform.scale(sprite,(int(size[0]*self.mod),int(size[1]*self.mod)))
            else:
                size = self.image.get_size() 
                self.scaledImg = pygame.transform.scale(self.image,(int(size[0]*self.mod),int(size[1]*self.mod)))
            self.scaledImg.set_colorkey((0,0,0))
 
        def renderSprite(self, surface, spriteNum, reverse = False):
            self.spriteNum = spriteNum
            self.scaleImage()
            super(type(self),self).render(surface)
            if reverse:
                flipped = pygame.transform.flip(self.scaledImg,True,False) # flip on X axis
                surface.blit(flipped, self.rect)
            else:
                surface.blit(self.scaledImg, self.rect)

        def render(self, surface):
            super(type(self),self).render(surface)
            surface.blit(self.scaledImg, self.rect)

    # Text element
    class Text(UIElement):
        def __init__(self, position, text, color, size):       
            self.font = pygame.font.SysFont("arial", size)
            self.text = text
            self.fontSize = size
            self.color = color
            self.position = position
            
            self.rText = self.preRender() # sets the self.rect attr
            
            super(type(self),self).__init__((position[0],position[1],self.width,self.height))
        
        def preRender(self):
            self.width, self.height = self.font.size(self.text) 
            renderedText = self.font.render(self.text, 0, self.color)
            return renderedText

        def setText(self, text):
            self.text = text
            self.rText = self.preRender()

        def render(self, surface):
            super(type(self),self).render(surface)
            surface.blit(self.rText, self.rect)
    
     

    # Used for grouping things
    class Container(UIElement):
        def __init__(self, rect, bgColor = None, borderColor = None):
            super(type(self),self).__init__(rect,bgColor,borderColor)
            self.children = []

        #Has an optional return value if u want the index ID to get it later.
        def addChild(self, ele):
            self.children.append(ele)
            ele.parent = self
            self.offsetChild(ele)
            return self.children.index(ele)

        def offsetChild(self, ele):
            ele.offset = (self.offset[0]+self.position[0],self.offset[1]+self.position[1])
            ele.rect = (ele.offset[0]+ele.position[0],ele.offset[1]+ele.position[1],ele.size[0],ele.size[1])
            
            if hasattr(ele, 'children'):
                for i in range (0,len(ele.children)):
                    ele.offsetChild(ele.children[i])
 
        def child(self, ID):
            return self.children[ID]

        def render(self,surface):
            super(type(self),self).render(surface)            
            for i in range(0,len(self.children)):
                self.children[i].render(surface)

    
#End UIManager
