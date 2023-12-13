import unittest
from unittest import TestCase, mock
import pygame
from unittest.mock import patch, Mock
from PokemonCombat import Move, Pokemon, APIManager, FirePokemon, WaterPokemon, GrassPokemon
from PokemonCombat import handle_rival_turn, handle_player_turn, check_battle_end

class TestMove(unittest.TestCase):

    @patch('PokemonCombat.APIManager.get_move_data')
    def test_move_initialization(self, mock_get_move_data):
        # Mock the API response
        mock_get_move_data.return_value = {
            'name': "tackle",
            'power': 40,
            'type': {'name': "normal"}
        }

        # URL doesn't matter here since we are mocking the response
        move = Move("super random URL :)")

        # Verify the items
        self.assertEqual(move.name, "tackle")
        self.assertEqual(move.power, 40)
        self.assertEqual(move.type, "normal")

    @patch('PokemonCombat.APIManager.get_move_data')
    def test_different_move_types(self, mock_get_move_data):
        # Mock different move types
        mock_get_move_data.side_effect = [
            {'name': "flamethrower", 'power': 90, 'type': {'name': "fire"}},
            {'name': "surf", 'power': 90, 'type': {'name': "water"}}
        ]

        fire_move = Move("fire move URL")
        water_move = Move("water move URL")

        self.assertEqual(fire_move.type, "fire")
        self.assertEqual(water_move.type, "water")

class TestPokemon(unittest.TestCase):
    '''
    Perform_attack method is not tested due to the complexity:
    - a lot of interaction with pokemon and move instances
    - involves random elements and conveys side effects (printing in console, updating display...)
    '''
    def setUp(self):
        # Initialize Pygame and its display module
        pygame.init()
        pygame.display.set_mode((1, 1))  # Minimal display size

        # Create a test Pokemon instance for testing
        self.pokemon = Pokemon('Pikachu', 10, 100, 100)
        self.attacker = Pokemon('Charmander', 10, 100, 100)
        self.defender = Pokemon('Squirtle', 10, 100, 100)

    def test_initialization(self):
        self.assertEqual(self.pokemon.name, 'Pikachu')
        self.assertEqual(self.pokemon.level, 10)

    def test_take_damage(self):
        initial_hp = self.pokemon.current_hp
        self.pokemon.take_damage(10)
        self.assertEqual(self.pokemon.current_hp, initial_hp - 10)

    def test_use_potion(self):
        self.pokemon.current_hp -= 20  # Simulate damage
        initial_potions = self.pokemon.num_potions
        self.pokemon.use_potion()
        self.assertEqual(self.pokemon.current_hp, self.pokemon.max_hp)
        self.assertEqual(self.pokemon.num_potions, initial_potions - 1)

    def test_set_moves(self):
        self.pokemon.set_moves()
        self.assertIsNotNone(self.pokemon.moves)
        self.assertTrue(len(self.pokemon.moves) > 0)

class TestAPIManager(unittest.TestCase):

    @patch('requests.get')
    def test_get_pokemon_data(self, mock_get):
        # Mock a API response
        mock_get.return_value = unittest.mock.Mock(status_code=200, json=lambda: {"name": "pikachu"})
        result = APIManager.get_pokemon_data("pikachu")

        self.assertIsNotNone(result)
        self.assertEqual(result['name'], "pikachu")

    @patch('requests.get')
    def test_get_move_data(self, mock_get):
        # Mock a API response for move data
        mock_get.return_value = unittest.mock.Mock(status_code=200, json=lambda: {"name": "tackle", "power": 40})
        result = APIManager.get_move_data("http://example.com/move/tackle")

        self.assertIsNotNone(result)
        self.assertEqual(result['name'], "tackle")
        self.assertEqual(result['power'], 40)

# Mock classes and functions for some tests of the actions in the game
class MockMove:
    def __init__(self, name, power):
        self.name = name
        self.power = power

class MockPokemon:
    def __init__(self, name, current_hp, moves):
        self.name = name
        self.current_hp = current_hp
        self.moves = moves
        self.max_hp = current_hp

    def perform_attack(self, other, move):
        # Simplified attack logic for testing
        other.current_hp -= move.power
        if other.current_hp < 0:
            other.current_hp = 0

    def take_damage(self, damage):
        self.current_hp -= damage
        if self.current_hp < 0:
            self.current_hp = 0

class TestPokemonBattle(unittest.TestCase):

    @patch('PokemonCombat.display_message')
    def test_handle_rival_turn(self, mock_display_message):
        player = MockPokemon('Pikachu', 100, [])
        rival = MockPokemon('Charmander', 100, [MockMove('Tackle', 10)])
        result = handle_rival_turn(player, rival)
        self.assertTrue(player.current_hp < 100)
        self.assertIn(result, ['player_turn', 'end_battle'])

    @patch('PokemonCombat.display_message')
    def test_handle_player_turn(self, mock_display_message):
        player = MockPokemon('Pikachu', 100, [MockMove('Thunderbolt', 20)])
        rival = MockPokemon('Charmander', 100, [])
        result = handle_player_turn(player, rival, player.moves[0])
        self.assertTrue(rival.current_hp < 100)
        self.assertIn(result, ['rival_turn', 'end_battle'])

    @patch('PokemonCombat.display_message')
    def test_check_battle_end(self, mock_display_message):
        player = MockPokemon('Pikachu', 0, [])
        rival = MockPokemon('Charmander', 100, [])
        result = check_battle_end(player, rival)
        self.assertEqual(result, 'gameover')

        player.current_hp = 100
        rival.current_hp = 0
        result = check_battle_end(player, rival)
        self.assertEqual(result, 'gameover')

if __name__ == '__main__':
    unittest.main()