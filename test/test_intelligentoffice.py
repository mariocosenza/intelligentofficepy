import unittest
from datetime import datetime
from unittest.mock import patch, Mock, PropertyMock
import mock.GPIO as GPIO
from mock.SDL_DS3231 import SDL_DS3231
from mock.adafruit_veml7700 import VEML7700
from src.intelligentoffice import IntelligentOffice, IntelligentOfficeError


class TestIntelligentOffice(unittest.TestCase):

    @patch.object(GPIO, "input")
    def test_check_quadrant_occupancy_in_range_11_15_not_14_occupied(self, mock_input: Mock):
        office = IntelligentOffice()
        mock_input.return_value = True
        occupied = office.check_quadrant_occupancy(IntelligentOffice.INFRARED_PIN1)
        mock_input.assert_called_once_with(IntelligentOffice.INFRARED_PIN1)
        self.assertTrue(occupied)
