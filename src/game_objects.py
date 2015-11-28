import pygame

class Tile:
    def __init__(self, image, solid = False):
        self.sprite = image
        self.solid = solid

class MovableCharacter:
    def move(self,speed = 2):
        direction = self.current_direction
        if direction == Direction.UP:
            self.yOffset -= speed
        elif direction == Direction.RIGHT:
            self.xOffset += speed
        elif direction == Direction.DOWN:
            self.yOffset += speed
        elif direction == Direction.LEFT:
            self.xOffset -= speed
        if ((direction == Direction.UP or direction == Direction.DOWN) and (self.yOffset % 50 == 0)) or ((direction == Direction.LEFT or direction == Direction.RIGHT) and (self.xOffset % 50 == 0)):
            if(self.yOffset < 0):
                self.gridY -= 1
            elif(self.yOffset > 0):
                self.gridY += 1
            self.yOffset = 0;
            if(self.xOffset < 0):
                self.gridX -= 1
            elif(self.xOffset > 0):
                self.gridX += 1
            self.xOffset = 0;
            self.moving = False;


    def change_direction(self, direction, override_opt = False):
        # Optimization
        if not override_opt and self.current_direction == direction:
            return
        self.current_direction = direction
        name = self.directional_sprites[direction]
        self.sprite = self.load_function(name)

    def __init__(self, name, load_function, directional_sprites,x=0,y=0, gold=0):
        self.moving = False
        self.load_function = load_function
        self.directional_sprites = directional_sprites
        self.gridX = x
        self.gridY = y
        self.xOffset = 0
        self.yOffset = 0
        self.name = name
        self.gold = gold
        self.current_direction = Direction.UP
        
class MainPlayer(MovableCharacter):
    pass

class EnemyPlayer(MovableCharacter):
    def move(self,speed = 2):
        pass # for now.. but implement ai

class Direction:
    UP    = 0
    RIGHT = 1
    DOWN  = 2
    LEFT  = 3

class Element:
    NEUTRAL = 0
    FIRE    = 1
    NATURE  = 2
    WATER   = 3

class GenericBot:
    def __init__(self, name, sprite, speed=0, health=100,mana=100,element=Element.NEUTRAL,spell_xp=dict(),list_of_spells=[]):
        self.name = name
        self.sprite = sprite 
        self.speed = speed
        self.health = health
        self.mana = mana
        self.element = element
        self.spell_xp = spell_xp
        self.list_of_spells = list_of_spells

class Spells:
    def __init__(self, name, mana_cost=25, attack_power=5,multiplier=dict(),accuracy=0.5):
        self.name = name
        self.mana_cost = mana_cost
        self.attack_power = attack_power
        self.multiplier = multiplier
        self.accuracy = accuracy

class CodeBlock:
    def __init__(self):
        self.font = pygame.font.SysFont(None, 20)
    # Renders the Block to the screen.  Should return the total height of the block.
    def render(self, surface, xOffset = 0, yOffset = 0):
        raise NotImplementedError
    # Executes the Block, taking into consideration whether or not this is a calc-mana-cost-only dry run.  Should return mana spent in total.
    def execute(self, ownerBot, opponentBot, dryRun = False):
        raise NotImplementedError

class CommentBlock(CodeBlock):
    def __init__(self):
        super(CommentBlock, self).__init__()
        self.comment = "";
        self.cwidth, self.cheight = self.font.size("# ")
        self.fontRender = self.font.render("# ", 0, (0, 0, 0), (255, 255, 0))
    def render(self, surface, xOffset = 0, yOffset = 0):
        pygame.draw.rect(surface, (255, 255, 0), (xOffset. yOffset, self.fwidth + 16, self.fheight + 8))
        surface.blit(self.fontRender, (xOffset + 4, yOffset + 4))
        return self.fheight + 8
    def execute(self, ownerBot, opponentBot, dryRun = False):
        return 0
    def setComment(self, newComment):
        self.comment = newComment
        self.cwidth, self.cheight = self.font.size("# " + self.comment)
        self.fontRender = self.font.render("# ", 0, (0, 0, 0), (255, 255, 0))

class SayBlock(CodeBlock):
    def __init__(self):
        pass
    def render(self, surface, xOffset = 0, yOffset = 0):
        return 0
    def execute(self, ownerBot, opponentBot, dryRun = False):
        return 0

class WhileBlock(CodeBlock):
    def __init__(self):
        pass
    def render(self, surface, xOffset = 0, yOffset = 0):
        return 0
    def execute(self, ownerBot, opponentBot, dryRun = False):
        return 0

class IfManaBlock(CodeBlock):
    def __init__(self):
        pass
    def render(self, surface, xOffset = 0, yOffset = 0):
        return 0
    def execute(self, ownerBot, opponentBot, dryRun = False):
        return 0

class IfOwnHealthBlock(CodeBlock):
    def __init__(self):
        pass
    def render(self, surface, xOffset = 0, yOffset = 0):
        return 0
    def execute(self, ownerBot, opponentBot, dryRun = False):
        return 0

class HealBlock(CodeBlock):
    def __init__(self):
        pass
    def render(self, surface, xOffset = 0, yOffset = 0):
        return 0
    def execute(self, ownerBot, opponentBot, dryRun = False):
        return 0

class ForBlock(CodeBlock):
    def __init__(self):
        pass
    def render(self, surface, xOffset = 0, yOffset = 0):
        return 0
    def execute(self, ownerBot, opponentBot, dryRun = False):
        return 0

class EndTurnBlock(CodeBlock):
    def __init__(self):
        pass
    def render(self, surface, xOffset = 0, yOffset = 0):
        return 0
    def execute(self, ownerBot, opponentBot, dryRun = False):
        return 0

class FireballBlock(CodeBlock):
    def __init__(self):
        pass
    def render(self, surface, xOffset = 0, yOffset = 0):
        return 0
    def execute(self, ownerBot, opponentBot, dryRun = False):
        return 0

class MossLeechBlock(CodeBlock):
    def __init__(self):
        pass
    def render(self, surface, xOffset = 0, yOffset = 0):
        return 0
    def execute(self, ownerBot, opponentBot, dryRun = False):
        return 0

class DouseBlock(CodeBlock):
    def __init__(self):
        pass
    def render(self, surface, xOffset = 0, yOffset = 0):
        return 0
    def execute(self, ownerBot, opponentBot, dryRun = False):
        return 0

