import unittest
from unittest.mock import patch
from PokemonCombat import Move, Pokemon

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

if __name__ == '__main__':
    unittest.main()