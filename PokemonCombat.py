'''
Should install pip3 install pygame / requests
Should also install Certificates.command
'''
import pygame 
from pygame.locals import *
import time
import math
import random
import requests
import io
from urllib.request import urlopen # To open URLs

pygame.init()
clock = pygame.time.Clock()

game_width = 500
game_height = 500
game = pygame.display.set_mode((game_width, game_height))
pygame.display.set_caption('Pokemon Battle')

black = (0, 0, 0)
gold = (218, 165, 32)
grey = (200, 200, 200)
green = (0, 200, 0)
red = (200, 0, 0)
white = (255, 255, 255)

class APIManager:
    '''
    Represents the management of the API Request to get Pokemon data
    Attributes:
    - BASE_URL (str): the base url for the pokemon api
    '''
    BASE_URL = 'https://pokeapi.co/api/v2'

    @staticmethod
    def get_pokemon_data(name):
        '''
        Gets the pokemon data from the API by name
        Arguments:
        - name(str): the name is the pokemon to get
        Returns:
        - dictionary containing the data
        '''
        response = requests.get(f'{APIManager.BASE_URL}/pokemon/{name.lower()}')
        return response.json() if response.status_code == 200 else None

    @staticmethod
    def get_move_data(url):
        '''
        Gets move data from the API by URL
        Arguments:
        - url(str): the url of the move to get
        Returns:
        - dictionary with the move data
        '''
        response = requests.get(url)
        return response.json() if response.status_code == 200 else None

class Move:
    '''
    Represents the pokemon move
    Attributes:
    - name(str): name of the move
    - power(int): power of the move
    - type(str): type of move
    '''
    def __init__(self, url):
        data = APIManager.get_move_data(url)
        self.name = data['name']
        self.power = data['power']
        self.type = data['type']['name']

class Pokemon(pygame.sprite.Sprite):
    '''
    Represents a pokemon in the game
    Attributes:
    - name(str): name of the pokemon
    - level(int): level of the pokemon
    - x(int): the x-coordinate position of the pokemon
    - y(int): the y-coordinate position of the pokemon
    '''
    def __init__(self, name, level, x, y):
        super().__init__()
        self.size = 200  # Adjusted size for the sprite

        self.json = APIManager.get_pokemon_data(name)  # Assign obtained data to self.json
        if self.json:
            self.name = name
            self.level = level
            self.x = x
            self.y = y
            self.num_potions = 3
            stats = self.json['stats']
            for stat in stats:
                if stat['stat']['name'] == 'hp':
                    self.current_hp = stat['base_stat'] + self.level
                    self.max_hp = stat['base_stat'] + self.level
                elif stat['stat']['name'] == 'attack':
                    self.attack = stat['base_stat']
                elif stat['stat']['name'] == 'defense':
                    self.defense = stat['base_stat']
                elif stat['stat']['name'] == 'speed':
                    self.speed = stat['base_stat']
            self.types = [t['type']['name'] for t in self.json['types']]
            self.size = 150
            self.set_sprite('front_default')
        else:
            # Handle errors if data is not fetched
            print("Failed to retrieve data for", name)
        self.hp_x = 10  
        self.hp_y = 10    

    def set_sprite(self, side):
        '''
        Sets the sprite image (2D Pixel image) for the pokemon
        Arguments:
        - Side(str): the sode of the pokemon sprite (front or back)
        '''
        image = self.json['sprites'][side]
        image_stream = urlopen(image).read()
        image_file = io.BytesIO(image_stream)
        self.image = pygame.image.load(image_file).convert_alpha()
        scale = self.size / self.image.get_width()
        new_width = int(self.image.get_width() * scale)
        new_height = int(self.image.get_height() * scale)
        self.image = pygame.transform.scale(self.image, (new_width, new_height))
        self.rect = self.image.get_rect(topleft=(self.x, self.y))

    def perform_attack(self, other, move):
        '''
        Performs an attack action by the pokemon
        Arguments:
        - other(pokemon): the target pokemon to attack
        - move(pokemon): the move used to attack
        '''
        display_message(f'{self.name} used {move.name}')  # Display the attack message
        pygame.display.update()  # Update the display to show the message
        time.sleep(2)  # Wait for a moment so the message can be read

        damage = (2 * self.level + 10) / 250 * self.attack / other.defense * move.power
        if move.type in self.types:
            damage *= 1.5
        random_num = random.randint(1, 10000)
        if random_num <= 625:
            damage *= 1.5
        damage = math.floor(damage)
        other.take_damage(damage)

    # Additional update and wait, in case further visual updates are needed after the attack
    pygame.display.update()
    time.sleep(2)

    def take_damage(self, damage):
        '''
        Reduces the Pokemon's HP by the specified amount 
        Arguments:
        - damage(int): the amount of damage to deduct from the pokemon's HP
        '''
        self.current_hp -= damage
        if self.current_hp < 0:
            self.current_hp = 0

    def use_potion(self):
        '''
        Uses a potion to restore HP for the pokemon
        '''
        if self.num_potions > 0:
            self.current_hp += 30
            if self.current_hp > self.max_hp:
                self.current_hp = self.max_hp
            self.num_potions -= 1

    def set_moves(self):
        '''
        Sets the moves for the pokemon based on its level and moves
        '''
        try:
            self.moves = []
            for move_info in self.json['moves']:
                versions = move_info['version_group_details']
                for version in versions:
                    if version['version_group']['name'] == 'red-blue' and version['move_learn_method']['name'] == 'level-up':
                        level_learned = version['level_learned_at']
                        if self.level >= level_learned:
                            move = Move(move_info['move']['url'])
                            if move.power is not None:  # To make sure move has power attribute
                                self.moves.append(move)
            if len(self.moves) > 4:
                self.moves = random.sample(self.moves, 4)
        except Exception as e:
            print(f"Error setting moves: {e}")
            self.moves = []  # Assign an empty list if there was an error

    def draw(self, surface):
        '''
        Draws the pokemon on the specified surface
        Arguments:
        - surface(pygame.surface): the surface on which to draw the pokemon
        '''
        surface.blit(self.image, (self.x, self.y))

    def draw_hp(self, surface):
        '''
        Draws the HP bar and HP text for the pokemon
        Arguments:
        - Surface(pygame.surface): the surface on which to draw the HP bar and text
        '''
        # Display the health bar
        bar_scale = 200 // self.max_hp
        for i in range(self.max_hp):
            bar = (self.hp_x + bar_scale * i, self.hp_y, bar_scale, 20)
            pygame.draw.rect(surface, red, bar)
        for i in range(self.current_hp):
            bar = (self.hp_x + bar_scale * i, self.hp_y, bar_scale, 20)
            pygame.draw.rect(surface, green, bar)

        # Display "HP" text
        font = pygame.font.Font(pygame.font.get_default_font(), 16)
        text = font.render(f'HP: {self.current_hp} / {self.max_hp}', True, black)
        text_rect = text.get_rect()
        text_rect.x = self.hp_x
        text_rect.y = self.hp_y + 30
        surface.blit(text, text_rect)

    def get_rect(self):
        '''
        Returns the rect object for the pokemon's image
        Returns: 
        - pygame.rect: the rect object for the pokemon's image
        '''
        return self.rect

def display_message(message):
    '''
    Displays a message on the game screen
    Arguments:
    - message(str): the message to display
    '''
    pygame.draw.rect(game, white, (10, 350, 480, 140))
    pygame.draw.rect(game, black, (10, 350, 480, 140), 3)
    font = pygame.font.Font(pygame.font.get_default_font(), 20)
    text = font.render(message, True, black)
    text_rect = text.get_rect()
    text_rect.x = 30
    text_rect.y = 410
    game.blit(text, text_rect)
    pygame.display.update()

def create_button(width, height, left, top, text_cx, text_cy, label):
    '''
    Creates a button with the specified properties and label text.
    Arguments:
    - width (int): The width of the button.
    - height (int): The height of the button.
    - left (int): The x-coordinate position of the button's top-left corner.
    - top (int): The y-coordinate position of the button's top-left corner.
    - text_cx (int): The x-coordinate position of the center of the label text.
    - text_cy (int): The y-coordinate position of the center of the label text.
    - label (str): The text to display on the button.
    Returns:
    - pygame.Rect: The rectangular object representing the button's position and dimensions.
    '''
    mouse_cursor = pygame.mouse.get_pos()
    button = Rect(left, top, width, height)
    if button.collidepoint(mouse_cursor):
        pygame.draw.rect(game, gold, button)
    else:
        pygame.draw.rect(game, white, button)
    font = pygame.font.Font(pygame.font.get_default_font(), 16)
    text = font.render(label, True, black)
    text_rect = text.get_rect(center = (text_cx, text_cy))
    game.blit(text, text_rect)
    return button

def draw_highlighted_box(pokemon, game_display):
    '''
    Draws a highlighted box around the specified Pokemon.
    Arguments:
    - pokemon (Pokemon): The Pokemon object to highlight.
    - game_display (pygame.Surface): The surface on which to draw the highlighted box.
    '''
    if pokemon:
        rect = pokemon.get_rect()
        pygame.draw.rect(game_display, gold, rect, 2)

def start_prebattle(player, rival):
    '''
    Initializes the pre-battle phase of the game.
    Arguments:
    - player (Pokemon): The player's Pokemon.
    - rival (Pokemon): The rival Pokemon.
    Returns:
    - str: The initial game state ('player_turn').
    '''
    # Set moves for the player and rival Pokémon
    player.set_moves()
    rival.set_moves()

    # Adjust the positions for the pre-battle
    player.x, player.y = 100, game_height - player.image.get_height() - 80
    rival.x, rival.y = game_width - rival.image.get_width() - 100, 30
    
    # Update HP bar positions
    player.hp_x, player.hp_y = game_width - 210, player.y + 70  
    rival.hp_x, rival.hp_y = rival.x - 160, rival.y + 60    
    
    player.set_sprite('back_default')
    rival.set_sprite('front_default')

    display_message(f"A wild {rival.name} appears!")
    pygame.display.update()
    clock.tick(2)
    
    return 'player_turn'
    
def handle_rival_turn(player_pokemon, rival_pokemon):
    '''
    Handles the turn of the rival Pokemon during battle.
    Arguments:
    - player_pokemon (Pokemon): The player's Pokemon.
    - rival_pokemon (Pokemon): The rival's Pokemon.
    Returns:
    - str: The next game state ('end_battle' or 'player_turn').
    '''
    # Rival randomly selects a move
    selected_move = random.choice(rival_pokemon.moves)
    rival_pokemon.perform_attack(player_pokemon, selected_move)
    
    if player_pokemon.current_hp <= 0:
        display_message(f"{player_pokemon.name} fainted! You lost the battle.")
        return 'end_battle'
    else:
        return 'player_turn'
    
def handle_player_turn(player_pokemon, rival_pokemon, selected_move):
    '''
    Handles the turn of the player's Pokemon during battle.
    Arguments:
    - player_pokemon (Pokemon): The player's Pokemon.
    - rival_pokemon (Pokemon): The rival's Pokemon.
    - selected_move (Move): The move selected by the player.
    Returns:
    - str: The next game state ('end_battle' or 'rival_turn').
    '''
    # Implement the action of the selected move
    player_pokemon.perform_attack(rival_pokemon, selected_move)
    
    # Check if the rival's Pokemon has fainted
    if rival_pokemon.current_hp <= 0:
        display_message(f"{rival_pokemon.name} fainted!")
        return 'end_battle'  # This would end the battle if the rival has no more Pokemon
    
    # If the rival Pokemon is still standing, it's their turn
    return 'rival_turn'  # If the rival's Pokémon is still standing, it's their turn next   

def check_battle_end(player_pokemon, rival_pokemon):
    '''
    Checks if the battle has ended.
    Arguments:
    - player_pokemon (Pokemon): The player's Pokemon.
    - rival_pokemon (Pokemon): The rival's Pokemon.
    Returns:
    - str: The game state ('gameover', 'player_turn', or 'gameover').
    '''
    if player_pokemon.current_hp <= 0:
        display_message(f"{player_pokemon.name} fainted! You lost the battle.")
        return 'gameover'
    elif rival_pokemon.current_hp <= 0:
        display_message(f"{rival_pokemon.name} fainted! You won the battle.")
        return 'gameover'
    else:
        return 'player_turn'

def draw_game(game_status, pokemons, player_pokemon, rival_pokemon):
    '''
    Draws the game screen based on the current game state.
    Arguments:
    - game_status (str): The current game state.
    - pokemons (list): The list of Pokemon objects.
    - player_pokemon (Pokemon): The player's Pokemon.
    - rival_pokemon (Pokemon): The rival's Pokemon.
    '''
    game.fill(white)  # Fills the background with white
    if game_status == 'select pokemon':
        highlighted_pokemon = None
        for pokemon in pokemons:
            pokemon.draw(game)
            if pokemon.get_rect().collidepoint(pygame.mouse.get_pos()):
                highlighted_pokemon = pokemon
        if highlighted_pokemon:
            draw_highlighted_box(highlighted_pokemon, game)
    
    elif game_status == 'player_turn':
        # Draw player's and rival's Pokémon and health bars
        player_pokemon.draw(game)
        rival_pokemon.draw(game)
        player_pokemon.draw_hp(game)
        rival_pokemon.draw_hp(game)
        # Adjust the button placement and include the number of potions in the label
        button_y = player_pokemon.y + player_pokemon.image.get_height() + 20  # Adjust this value as needed
        fight_button = create_button(100, 50, 50, button_y, 100, button_y + 25, "Fight")
        potion_button = create_button(100, 50, 200, button_y, 250, button_y + 25, f"Use Potion ({player_pokemon.num_potions})")
    elif game_status == 'select_move':
        # Draw player's and rival's Pokémon and health bars
        player_pokemon.draw(game)
        rival_pokemon.draw(game)
        player_pokemon.draw_hp(game)
        rival_pokemon.draw_hp(game)
    
        # Define the position for the move buttons box
        move_box_top = game_height - 100  # Set this to the desired distance from the bottom of the window
        move_box_height = 90  # Set this to the desired height of the move buttons box
    
        # Draw a background rectangle for the move buttons
        pygame.draw.rect(game, grey, (0, move_box_top, game_width, move_box_height))
    
        # Draw move buttons within the rectangle
        button_width = 100
        button_height = 50
        button_margin = 10  # Space between buttons
        starting_x = (game_width - (button_width * 4 + button_margin * 3)) / 2  # Center the buttons horizontally
    
        for i, move in enumerate(player_pokemon.moves):
            button_x = starting_x + (button_width + button_margin) * i
            button_y = move_box_top + (move_box_height - button_height) / 2  # Center the button vertically within the move box
            create_button(button_width, button_height, button_x, button_y, button_x + button_width / 2, button_y + button_height / 2, move.name.capitalize())

    elif game_status in ['prebattle', 'rival_turn', 'end_battle']:
        # Draw player's and rival's Pokémon and health bars
        player_pokemon.draw(game)
        rival_pokemon.draw(game)
        player_pokemon.draw_hp(game)
        rival_pokemon.draw_hp(game)
    
    pygame.display.update()

initial_positions = {
    'Bulbasaur': (25, 150),
    'Charmander': (175, 150),
    'Squirtle': (325, 150)
}
initial_num_potions = 3  # Define initial number of potions for a new game

# Function to reset the game
def reset_game(pokemons, initial_positions, initial_num_potions):
    '''
    Resets the game by restoring initial positions and attributes of Pokemon.
    Arguments:
    - pokemons (list): The list of Pokemon objects.
    - initial_positions (dict): A dictionary mapping Pokemon names to their initial positions.
    - initial_num_potions (int): The initial number of potions for a new game.
    '''
    for pokemon_name, position in initial_positions.items():
        for pokemon in pokemons:
            if pokemon.name.lower() == pokemon_name.lower():
                pokemon.x, pokemon.y = position
                pokemon.current_hp = pokemon.max_hp
                pokemon.num_potions = initial_num_potions
                pokemon.set_sprite('front_default')

# Initialize pokemons
level = 30
bulbasaur = Pokemon('Bulbasaur', level, 25, 150)
charmander = Pokemon('Charmander', level, 175, 150)
squirtle = Pokemon('Squirtle', level, 325, 150)
pokemons = [bulbasaur, charmander, squirtle]    
player_pokemon = None
rival_pokemon = None
game_status = 'select pokemon'

# Set moves for each Pokemon
for pokemon in pokemons:
    pokemon.set_moves()

last_click_time = 0  # Time of the last mouse click

# Main loop that runs the game
while game_status != 'quit':
    for event in pygame.event.get():
        if event.type == QUIT:
            game_status = 'quit'
        elif event.type == KEYDOWN:
            if event.key == K_y and game_status == 'gameover':
                reset_game(pokemons, initial_positions, initial_num_potions)
                game_status = 'select pokemon'
                game.fill(white)
                pygame.display.update()
            elif event.key == K_n and game_status == 'gameover':
                game_status = 'quit'

        elif event.type == MOUSEBUTTONDOWN:
            current_time = pygame.time.get_ticks()  # Get the current time in milliseconds
            if current_time - last_click_time > 500:  # Check if 500 milliseconds have passed since the last click
                last_click_time = current_time  # Update the last click time

                mouse_click = event.pos
                if game_status == 'select pokemon':
                    for pokemon in pokemons:
                        if pokemon.get_rect().collidepoint(mouse_click):
                            player_pokemon = pokemon
                            rival_pokemon = random.choice([p for p in pokemons if p != player_pokemon])
                            game_status = start_prebattle(player_pokemon, rival_pokemon)
                elif game_status == 'player_turn':
                    button_y = player_pokemon.y + player_pokemon.image.get_height() + 20
                    fight_button = create_button(100, 50, 50, button_y, 100, button_y + 25, "Fight")
                    potion_button = create_button(100, 50, 200, button_y, 250, button_y + 25, f"Use Potion ({player_pokemon.num_potions})")

                    if fight_button.collidepoint(mouse_click):
                        game_status = 'select_move'
                    elif potion_button.collidepoint(mouse_click) and player_pokemon.num_potions > 0:
                        player_pokemon.use_potion()
                        draw_game(game_status, pokemons, player_pokemon, rival_pokemon)

                elif game_status == 'select_move':
                    move_box_top = game_height - 100
                    move_box_height = 90
                    button_width = 100
                    button_height = 50
                    button_margin = 10
                    starting_x = (game_width - (button_width * 4 + button_margin * 3)) / 2

                    move_buttons = []
                    for i, move in enumerate(player_pokemon.moves):
                        button_x = starting_x + (button_width + button_margin) * i
                        button_y = move_box_top + (move_box_height - button_height) / 2
                        button = create_button(button_width, button_height, button_x, button_y, button_x + button_width / 2, button_y + button_height / 2, move.name.capitalize())
                        move_buttons.append((button, move))

                    for button, move in move_buttons:
                        if button.collidepoint(mouse_click):
                            game_status = handle_player_turn(player_pokemon, rival_pokemon, move)
                            break

    if game_status == 'rival_turn':
        game_status = handle_rival_turn(player_pokemon, rival_pokemon)
        time.sleep(2)

    if game_status == 'end_battle':
        game_status = check_battle_end(player_pokemon, rival_pokemon)
        time.sleep(2)

    if game_status == 'gameover':
        display_message("Game Over! Press 'Y' to play again, 'N' to quit")
        pygame.display.update()
        continue

    draw_game(game_status, pokemons, player_pokemon, rival_pokemon)
    clock.tick(60)

pygame.quit()