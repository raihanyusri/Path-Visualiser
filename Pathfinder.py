from tkinter import Frame, messagebox, Tk
import pygame
import sys
import random

pygame.init()

window_width = 800
window_height = 800

window = pygame.display.set_mode((window_width, window_height))

columns = 16
rows = 16

box_width = window_width // columns
box_height = window_height // rows

grid = []
queue = []
path = []
captures = []

# Clickable button
class Button():
	def __init__(self, image, pos, text_input, font, base_color, hovering_color):
		self.image = image
		self.x_pos = pos[0]
		self.y_pos = pos[1]
		self.font = font
		self.base_color, self.hovering_color = base_color, hovering_color
		self.text_input = text_input
		self.text = self.font.render(self.text_input, True, self.base_color)
		if self.image is None:
			self.image = self.text
		self.rect = self.image.get_rect(center=(self.x_pos, self.y_pos))
		self.text_rect = self.text.get_rect(center=(self.x_pos, self.y_pos))

	def update(self, screen):
		if self.image is not None:
			screen.blit(self.image, self.rect)
		screen.blit(self.text, self.text_rect)

	def checkForInput(self, position):
		if position[0] in range(self.rect.left, self.rect.right) and position[1] in range(self.rect.top, self.rect.bottom):
			return True
		return False

	def changeColor(self, position):
		if position[0] in range(self.rect.left, self.rect.right) and position[1] in range(self.rect.top, self.rect.bottom):
			self.text = self.font.render(self.text_input, True, self.hovering_color)
		else:
			self.text = self.font.render(self.text_input, True, self.base_color)

# Each box in the grid
class Box:
    def __init__(self, i, j):
        self.x = i
        self.y = j
        self.start = False
        self.wall = False
        self.endpoint = False
        self.queued = False
        self.visited = False
        self.neighbours = []
        self.prior = None

    def draw(self, win, color):
        pygame.draw.rect(win, color, (self.x * box_width, self.y * box_height, box_width-2, box_height-2))

    def set_neighbours(self):
        if self.x > 0:
            self.neighbours.append(grid[self.x - 1][self.y])
        if self.x < columns - 1:
            self.neighbours.append(grid[self.x + 1][self.y])
        if self.y > 0:
            self.neighbours.append(grid[self.x][self.y - 1])
        if self.y < rows - 1:
            self.neighbours.append(grid[self.x][self.y + 1])


# Create grid
for i in range(columns):
    arr = []
    for j in range(rows):
        arr.append(Box(i, j))
    grid.append(arr)

# Set neighbours of each box
for i in range(columns):
    for j in range(rows):
        grid[i][j].set_neighbours()

# Initialise start box
start_box = grid[0][0]
start_box.start = True
start_box.visited = True
endpoint_box = None
queue.append(start_box)

def main():
    begin_search = False
    endpoint_box_set = False
    searching = True
    start_playing = False

    while True:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()
            elif event.type == pygame.MOUSEMOTION:
                x = pygame.mouse.get_pos()[0]
                y = pygame.mouse.get_pos()[1]

                # Left click to create a wall
                if event.buttons[0]:
                    i = x // box_width
                    j = y // box_height
                    grid[i][j].wall = True

                # Right click to set endpoint
                if event.buttons[2] and not endpoint_box_set:
                    i = x // box_width
                    j = y // box_height
                    endpoint_box = grid[i][j]
                    endpoint_box.endpoint = True
                    endpoint_box_set = True

            # Start algorithm
            if event.type == pygame.KEYDOWN and endpoint_box_set:
                begin_search = True

        # Dijkstra's algorithm
        if begin_search:
            if len(queue) > 0 and searching:
                current_box = queue.pop(0)
                current_box.visited = True
                if current_box == endpoint_box:
                    searching = False
                    while current_box.prior != start_box:
                        path.append(current_box.prior)
                        current_box = current_box.prior
                else:
                    for neighbour in current_box.neighbours:
                        if not neighbour.queued and not neighbour.wall:
                            neighbour.queued = True
                            neighbour.prior = current_box
                            queue.append(neighbour)
            
            # No solution found
            else:
                if searching:
                    no_solution()

        window.fill((0, 0, 0))

        # Handle colouring of boxes
        for i in range(columns):
            for j in range(rows):
                box = grid[i][j]
                box.draw(window, (100, 100, 100))

                if box.queued:
                    box.draw(window, (200, 0, 0))
                if box.visited:
                    box.draw(window, (0, 200, 0))
                if box in path:
                    box.draw(window, (0, 0, 200))
                    start_playing = True

                if box.start:
                    box.draw(window, (0, 200, 200))
                if box.wall:
                    box.draw(window, (0, 0, 0))
                if box.endpoint:
                    box.draw(window, (200, 200, 0))

                if start_playing:
                    current = grid[0][0]

                    for event in pygame.event.get():
                        if event.type == pygame.KEYDOWN:
                            if event.key == pygame.K_RIGHT and current.x < columns - 2:
                                current.x = current.x + 1
                            if event.key == pygame.K_LEFT and current.x > 0:
                                current.x = current.x - 1
                            if event.key == pygame.K_UP and current.y > 0:
                                current.y = current.y - 1
                            if event.key == pygame.K_DOWN and current.y < rows - 2:
                                current.y = current.y + 1

                    current.draw(window, (0, 200, 200))

                    if current.x == endpoint_box.x and current.y == endpoint_box.y:
                        start_playing = False
                        current.x = 0
                        current.y = 0
                        id = random.randint(1, 151)
                        wild_pokemon(id)

        pygame.display.update()

def get_font(size): 
    return pygame.font.SysFont("arial", size)

# Handle encounters
def wild_pokemon(id):
    back_to_main = False
    while True:
        PLAY_MOUSE_POS = pygame.mouse.get_pos()
        pokemon = {'bulbasaur': '1', 'ivysaur': '2', 'venusaur': '3', 'charmander': '4', 'charmeleon': '5', 'charizard': '6', 'squirtle': '7', 'wartortle': '8', 'blastoise': '9', 'caterpie': '10', 'metapod': '11', 'butterfree': '12', 'weedle': '13', 'kakuna': '14', 'beedrill': '15', 'pidgey': '16', 'pidgeotto': '17', 'pidgeot': '18', 'rattata': '19', 'raticate': '20', 'spearow': '21', 'fearow': '22', 'ekans': '23', 'arbok': '24', 'pikachu': '25', 'raichu': '26', 'sandshrew': '27', 'sandslash': '28', 'nidoran-f': '29', 'nidorina': '30', 'nidoqueen': '31', 'nidoran-m': '32', 'nidorino': '33', 'nidoking': '34', 'clefairy': '35', 'clefable': '36', 'vulpix': '37', 'ninetales': '38', 'jigglypuff': '39', 'wigglytuff': '40', 'zubat': '41', 'golbat': '42', 'oddish': '43', 'gloom': '44', 'vileplume': '45', 'paras': '46', 'parasect': '47', 'venonat': '48', 'venomoth': '49', 'diglett': '50', 'dugtrio': '51', 'meowth': '52', 'persian': '53', 'psyduck': '54', 'golduck': '55', 'mankey': '56', 'primeape': '57', 'growlithe': '58', 'arcanine': '59', 'poliwag': '60', 'poliwhirl': '61', 'poliwrath': '62', 'abra': '63', 'kadabra': '64', 'alakazam': '65', 'machop': '66', 'machoke': '67', 'machamp': '68', 'bellsprout': '69', 'weepinbell': '70', 'victreebel': '71', 'tentacool': '72', 'tentacruel': '73', 'geodude': '74', 'graveler': '75', 'golem': '76', 'ponyta': '77', 'rapidash': '78', 'slowpoke': '79', 'slowbro': '80', 'magnemite': '81', 'magneton': '82', 'farfetchd': '83', 'doduo': '84', 'dodrio': '85', 'seel': '86', 'dewgong': '87', 'grimer': '88', 'muk': '89', 'shellder': '90', 'cloyster': '91', 'gastly': '92', 'haunter': '93', 'gengar': '94', 'onix': '95', 'drowzee': '96', 'hypno': '97', 'krabby': '98', 'kingler': '99', 'voltorb': '100', 'electrode': '101', 'exeggcute': '102', 'exeggutor': '103', 'cubone': '104', 'marowak': '105', 'hitmonlee': '106', 'hitmonchan': '107', 'lickitung': '108', 'koffing': '109', 'weezing': '110', 'rhyhorn': '111', 'rhydon': '112', 'chansey': '113', 'tangela': '114', 'kangaskhan': '115', 'horsea': '116', 'seadra': '117', 'goldeen': '118', 'seaking': '119', 'staryu': '120', 'starmie': '121', 'mr-mime': '122', 'scyther': '123', 'jynx': '124', 'electabuzz': '125', 'magmar': '126', 'pinsir': '127', 'tauros': '128', 'magikarp': '129', 'gyarados': '130', 'lapras': '131', 'ditto': '132', 'eevee': '133', 'vaporeon': '134', 'jolteon': '135', 'flareon': '136', 'porygon': '137', 'omanyte': '138', 'omastar': '139', 'kabuto': '140', 'kabutops': '141', 'aerodactyl': '142', 'snorlax': '143', 'articuno': '144', 'zapdos': '145', 'moltres': '146', 'dratini': '147', 'dragonair': '148', 'dragonite': '149', 'mewtwo': '150', 'mew': '151'}

        window.fill("black")
        PLAY_TEXT = get_font(20).render("You encountered a " + list(pokemon.keys())[id].upper(), True, (255, 255, 255))
        window.blit(PLAY_TEXT, (10,10))

        PLAY_BACK = Button(image=None, pos=(600, 460), 
                            text_input="BACK", font=get_font(40), base_color="White", hovering_color="Green")
        PLAY_BACK.changeColor(PLAY_MOUSE_POS)
        PLAY_BACK.update(window)

        PLAY_CATCH = Button(image=None, pos=(200, 460), 
                            text_input="Catch", font=get_font(40), base_color="White", hovering_color="Green")
        PLAY_CATCH.changeColor(PLAY_MOUSE_POS)
        PLAY_CATCH.update(window)

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()
            if event.type == pygame.MOUSEBUTTONDOWN:
                if PLAY_BACK.checkForInput(PLAY_MOUSE_POS):
                    back_to_main = True
                if PLAY_CATCH.checkForInput(PLAY_MOUSE_POS):
                    catch(list(pokemon.keys())[id].upper())
                    back_to_main = True
        
        if back_to_main:
            break

        pygame.display.update()

# Handle capture
def catch(pokemon):

    id = random.randint(1, 10)
    back = False
    appended = False
    while True:
        PLAY_MOUSE_POS = pygame.mouse.get_pos()

        window.fill("black")
        if (id < 7):
            PLAY_TEXT = get_font(20).render(pokemon + " ran away...", True, (255, 255, 255))
        else:
            PLAY_TEXT = get_font(20).render("Congratulations! You caught the " + pokemon + "!", True, (255, 255, 255))
            if appended == False:
                captures.append(pokemon)
            appended = True
            if len(captures) == 6:
                show_victory()
        window.blit(PLAY_TEXT, (10,10))

        PLAY_BACK = Button(image=None, pos=(600, 460), 
                            text_input="BACK", font=get_font(40), base_color="White", hovering_color="Green")
        PLAY_BACK.changeColor(PLAY_MOUSE_POS)
        PLAY_BACK.update(window)

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()
            if event.type == pygame.MOUSEBUTTONDOWN:
                if PLAY_BACK.checkForInput(PLAY_MOUSE_POS):
                    back = True
        
        if back:
            break

        pygame.display.update()

# Handle final team showcase
def show_victory():
    while True:
        window.fill("black")
        output = "Your team: "
        for pkmn in captures:
            output = output + pkmn + " "
        PLAY_TEXT = get_font(20).render(output, True, (255, 255, 255))
        window.blit(PLAY_TEXT, (10,10))

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()
    

        pygame.display.update()

# Handle no solution
def no_solution():
    while True:
        window.fill("black")
        PLAY_TEXT = get_font(20).render("There is no solution :(", True, (255, 255, 255))
        window.blit(PLAY_TEXT, (10,10))

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()    

        pygame.display.update()

main()
