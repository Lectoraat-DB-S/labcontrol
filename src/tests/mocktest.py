from unittest.mock import patch
import unittest
from typing import Dict
import requests
from typing import Dict


def get_data(url: str) -> Dict[str, str]:
    response = requests.get(url)
    return response.json()


class TestGetData(unittest.TestCase):
    @patch('requests.get')
    def test_get_data(self, mock_get: patch) -> None:
        mock_response = mock_get.return_value  # Create a mock response object
        mock_response.json.return_value = {'key': 'value'}  # Define the return value of the mock response's json method
        
        url = 'http://example.com/api'
        result = get_data(url)  # Call the function with the mocked response
        
        self.assertEqual(result, {'key': 'value'})  # Assert the returned value is as expected
        mock_get.assert_called_once_with(url)  # Ensure the get method was called once with the correct URL

if __name__ == '__main__':
    unittest.main()