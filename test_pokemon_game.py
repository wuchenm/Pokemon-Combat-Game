import unittest
from unittest import TestCase, mock
import pygame
from unittest.mock import patch, Mock
from PokemonCombat import Move, Pokemon, APIManager, FirePokemon, WaterPokemon, GrassPokemon

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

if __name__ == '__main__':
    unittest.main()