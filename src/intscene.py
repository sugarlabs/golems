import pygame, kbInput, game_objects, scene, worldmap, sys
from gettext import gettext as _
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

class InteractiveScene(scene.Scene):
    def __init__(self, **specArgs):
        self.movable_characters = []
        self.map = worldmap.Map(30, 15)
        self.font = pygame.font.SysFont("couriernew", 24)
        cmntBlock = game_objects.CommentBlock()
        cmntBlock.setComment("Insert code below.")
        self.main_player = game_objects.MainPlayer(name = "P1",
                                      load_function = pygame.image.load,
                                      # The sprite for the bot will just be the up picture for placeholder.."
                                      list_of_bots = [game_objects.GenericBot("Stefan's Bot", "res/main_player/up.png", pOwned = True, queue_of_code_blocks = [cmntBlock])],
                                      directional_sprites = ["res/main_player/up.png", 
                                                             "res/main_player/right.png", 
                                                             "res/main_player/down.png", 
                                                             "res/main_player/left.png"],
                                      x = 1, 
                                      y = 1,
                                      )
        
        botBlocks = []
        botSays = game_objects.SayBlock()
        botSays.setMessage("Beep boop")
        botBlocks.append(botSays)
        botBlocks.append(game_objects.FireballBlock(10,5)) 

        
        enemyLocations = self.map.getEnemyLocations()
        numEnemies = len(enemyLocations)
        for x in range(0, numEnemies):
            position = enemyLocations[x]
            xLoc = position[0]
            yLoc = position[1]
            self.enemy_player = game_objects.EnemyPlayer(name = "AI-" + str(x),
                                        load_function = pygame.image.load,
                                        list_of_bots = [game_objects.GenericBot("enemy's Bot", "res/main_player/up.png",queue_of_code_blocks = botBlocks,speed=8)],
                                        directional_sprites = ["res/main_player/up.png", 
                                                             "res/main_player/right.png", 
                                                             "res/main_player/down.png", 
                                                             "res/main_player/left.png"], 
                                        x = xLoc,
                                        y = yLoc)
            
            self.enemy_player.change_direction(self.enemy_player.current_direction, override_opt = True)
            self.movable_characters.append(self.enemy_player)

        self.main_player.change_direction(self.main_player.current_direction, override_opt = True)
        self.movable_characters.append(self.main_player)
        
        self.renderMenu = False
        
        self.activity = None
        
        self.menuIndex = 0

    def destroyBot(self, bot):
        for mov in self.movable_characters:
            for bot_ in mov.list_of_bots:
                if bot_ == bot:
                    self.movable_characters.remove(mov)

    def doKeys(self, keys, keysLastFrame, char):
        if char.moving: # Player's currently moving, ignore keypresses
            return
        if self.activity == None and kbInput.isMenuPressed(keys) and not kbInput.isMenuPressed(keysLastFrame):
            self.renderMenu = not self.renderMenu
        if(self.renderMenu):
            if kbInput.isUpPressed(keys) and not kbInput.isUpPressed(keysLastFrame):
                pass  # If we have more items, this decrements the menuIndex
            elif kbInput.isDownPressed(keys) and not kbInput.isDownPressed(keysLastFrame):
                pass  # If we have more items, this increments the menuIndex
            elif kbInput.isOkayPressed(keys) and not kbInput.isOkayPressed(keysLastFrame):
                self.renderMenu = False
                self.manager.go_to(scene.Scenes.CODING, plyr = self.main_player)
            elif kbInput.isBackPressed(keys) and not kbInput.isBackPressed(keysLastFrame):
                self.renderMenu = False
        else:
            # Use change_direction instead of just changing the
            # variable since it also changes the sprite image
            if kbInput.isUpPressed(keys):
                self.move(char,game_objects.Direction.UP)
            elif kbInput.isRightPressed(keys):
                self.move(char,game_objects.Direction.RIGHT)
            elif kbInput.isDownPressed(keys):
                self.move(char,game_objects.Direction.DOWN)
            elif kbInput.isLeftPressed(keys):
                self.move(char,game_objects.Direction.LEFT)
    
    def gotoCoding(self, button = None):
        self.manager.go_to(scene.Scenes.CODING, plyr = self.main_player)

    def render(self, surface):
        surface.fill((0,0,0))
        self.map.render(surface, self.main_player.gridX * 50 + self.main_player.xOffset, self.main_player.gridY * 50 + self.main_player.yOffset)
        width, height = surface.get_size()
        for character in self.movable_characters:
            surface.blit(character.sprite, ((width / 2) - 25 - (self.main_player.gridX * 50 + self.main_player.xOffset) + (character.gridX * 50 + character.xOffset), (height / 2) - 25 - (self.main_player.gridY * 50 + self.main_player.yOffset) + (character.gridY * 50 + character.yOffset)))
        if(self.renderMenu):
            pygame.draw.rect(surface, (0, 230, 180), (width - 266, 10, 256, 512))
            menuItemOne = self.font.render("EDIT CODE", 0, (0, 0, 0), (0, 230, 180))
            surface.blit(menuItemOne, (width - 221, 25))
            if(self.menuIndex == 0):
                pygame.draw.polygon(surface, (0, 0, 0), [(width - 241, 25), (width - 241, 49), (width - 235, 37)], 4)

    def what_character_on_tile(self,x,y):
        for character in self.movable_characters:
            if character.gridX == x and character.gridY == y:
                return character
        return None
    
    def collided_with_another_character(self, char1, char2):
        self.manager.go_to(scene.Scenes.BATTLE, c1 = char1, c2 = char2)

    def move(self,character,direction):
        xMod = yMod = 0
        character.change_direction(direction)
        if direction is game_objects.Direction.UP: yMod = -1
        elif direction is game_objects.Direction.RIGHT: xMod = 1
        elif direction is game_objects.Direction.DOWN: yMod = 1
        elif direction is game_objects.Direction.LEFT: xMod = -1
	
        character_at_loc =  self.what_character_on_tile(character.gridX + xMod, character.gridY + yMod) 
        if character_at_loc is not None:
            if character_at_loc is not character: # This will need to be changed once we have multiple things to interact with.
                self.collided_with_another_character(character,character_at_loc)
                return
        if(not self.map.isSolid(character.gridX + xMod, character.gridY + yMod)):
            character.moving = True

    def update(self, keys, keysLastFrame):
        for character in self.movable_characters:
            if character.moving:
                if character == self.main_player:
                    character.move(10) 
                else:
                    character.move()
        self.doKeys(keys, keysLastFrame, self.main_player)

    def handle_events(self, events):
        pass

    def makeToolbar(self, activity):
        self.activity = activity
        
        toolbar = ToolbarBox()
        
        activity_button = ActivityToolbarButton(activity)
        toolbar.toolbar.insert(activity_button, -1)
        activity_button.show()
        
        editmode = ToolButton('edit-description')
        editmode.set_tooltip(_("Enter Edit Mode"))
        editmode.set_accelerator(_('<ctrl>e'))
        editmode.connect('clicked', self.gotoCoding)
        toolbar.toolbar.insert(editmode, -1)
        editmode.show()
        
        separator = Gtk.SeparatorToolItem()
        separator.props.draw = False
        separator.set_expand(True)
        toolbar.toolbar.insert(separator, -1)
        separator.show()
        
        stop_button = StopButton(activity)
        toolbar.toolbar.insert(stop_button, -1)
        stop_button.show()
        
        return toolbar
