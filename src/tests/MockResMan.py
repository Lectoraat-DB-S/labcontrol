import pyvisa
from unittest.mock import patch, MagicMock
import unittest

class MockerRM(MagicMock):
    @patch('visa.ResourceManager')  
    def list_resources(self):
        
        theVal = {"blabal", "bladiebladie", "Niks"} 
        self.return_value = theVal
        self.list_resources.return_value = {"blabal", "bladiebladie", "Niks"}
        return theVal
        
    def open_resource(url):
        pass
    